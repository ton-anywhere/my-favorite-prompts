import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name('backup_work.py')
SPEC = importlib.util.spec_from_file_location('backup_work', SCRIPT)
backup_work = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup_work)


class BackupWorkTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='backup-work-test-')
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Backup Test')
        self.git('config', 'user.email', 'backup@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        (self.repo / 'settings').write_text('base\n')
        (self.repo / 'deleted').write_text('delete me\n')
        (self.repo / '.gitignore').write_text('ignored\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'chore: initialize fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo,
                                       stderr=subprocess.STDOUT)

    def run_script(self, ok=True, cwd=None):
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=cwd or self.repo,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stderr)
        return result

    def test_clean_tree_keeps_existing_stash_without_claiming_it_as_backup(self):
        (self.repo / 'settings').write_text('older work\n')
        self.git('stash', 'push', '-m', 'older backup')
        previous = self.git('rev-parse', 'refs/stash')
        result = self.run_script()
        self.assertIn('BACKUP_OK stash=none', result.stdout)
        self.assertEqual(self.git('rev-parse', 'refs/stash'), previous)
        self.assertFalse(self.git('status', '--porcelain'))

    def test_restores_mixed_binary_untracked_modes_symlinks_and_deletions(self):
        (self.repo / 'settings').write_bytes(b'staged\x00bytes\n')
        self.git('add', 'settings')
        (self.repo / 'settings').write_bytes(b'staged\x00bytes\nunstaged\n')
        (self.repo / 'settings').chmod(0o755)
        (self.repo / 'deleted').unlink()
        (self.repo / 'new directory').mkdir()
        (self.repo / 'new directory' / 'line\nbreak').write_bytes(b'\x00new\xff')
        (self.repo / 'new directory' / 'empty').touch()
        (self.repo / 'link').symlink_to('settings')
        (self.repo / 'ignored').write_bytes(b'ignored data')
        before = backup_work.snapshot(self.repo)
        result = self.run_script(cwd=self.repo / 'new directory')
        self.assertEqual(backup_work.snapshot(self.repo), before)
        stash = self.git('rev-parse', 'refs/stash').decode().strip()
        self.assertIn(f'BACKUP_OK stash={stash}', result.stdout)
        self.assertEqual((self.repo / 'ignored').read_bytes(), b'ignored data')
        self.assertEqual(self.git('show', f'{stash}^3:new directory/line\nbreak'),
                         b'\x00new\xff')

    def test_repeated_backups_retain_both_stashes_and_original_state(self):
        (self.repo / 'settings').write_text('pending\n')
        before = backup_work.snapshot(self.repo)
        self.run_script()
        first = self.git('rev-parse', 'refs/stash')
        self.run_script()
        self.assertNotEqual(self.git('rev-parse', 'refs/stash'), first)
        self.assertEqual(self.git('rev-parse', 'stash@{1}'), first)
        self.assertEqual(backup_work.snapshot(self.repo), before)

    def test_private_file_and_directory_permissions_are_restored(self):
        private = self.repo / 'private'
        private.mkdir(mode=0o750)
        (private / 'secret').write_text('private data\n')
        (private / 'secret').chmod(0o600)
        (self.repo / 'settings').write_text('pending\n')
        (self.repo / 'settings').chmod(0o640)
        before = backup_work.snapshot(self.repo)
        self.run_script()
        self.assertEqual(backup_work.snapshot(self.repo), before)

    def test_autocrlf_is_rejected_before_losing_mixed_newlines(self):
        self.git('config', 'core.autocrlf', 'true')
        self.git('config', 'core.safecrlf', 'false')
        (self.repo / 'mixed').write_bytes(b'first\r\nsecond\n')
        before = backup_work.snapshot(self.repo)
        result = self.run_script(ok=False)
        self.assertIn('can transform bytes', result.stderr)
        self.assertEqual(backup_work.snapshot(self.repo), before)
        self.assertFalse((self.repo / '.git' / 'refs' / 'stash').exists())

    def test_attribute_filter_is_rejected_before_stashing(self):
        (self.repo / '.gitattributes').write_text('secret filter=strip\n')
        self.git('config', 'filter.strip.clean', 'tr -d x')
        (self.repo / 'secret').write_text('xxxdata\n')
        before = backup_work.snapshot(self.repo)
        result = self.run_script(ok=False)
        self.assertIn('filter can transform', result.stderr)
        self.assertEqual(backup_work.snapshot(self.repo), before)
        self.assertFalse((self.repo / '.git' / 'refs' / 'stash').exists())

    def test_backup_recovers_work_after_a_later_hard_reset(self):
        (self.repo / 'obsolete').write_text('obsolete alias\n')
        self.git('add', 'obsolete')
        self.git('commit', '-qm', 'feat: add obsolete alias')
        (self.repo / 'settings').write_text('staged\n')
        self.git('add', 'settings')
        (self.repo / 'settings').write_text('staged\nunstaged\n')
        before = backup_work.snapshot(self.repo)
        self.run_script()
        stash = self.git('rev-parse', 'refs/stash').decode().strip()
        self.git('reset', '--hard', 'HEAD~1')
        self.git('stash', 'apply', '--index', stash)
        self.assertEqual(backup_work.snapshot(self.repo)[1:], before[1:])
        self.assertFalse((self.repo / 'obsolete').exists())
        self.assertEqual(self.git('rev-parse', 'refs/stash').decode().strip(), stash)

    def test_untracked_files_surviving_reset_require_inspection_before_recovery(self):
        (self.repo / 'new').write_text('untracked work\n')
        self.run_script()
        stash = self.git('rev-parse', 'refs/stash').decode().strip()
        self.git('reset', '--hard', 'HEAD')
        result = subprocess.run(['git', 'stash', 'apply', '--index', stash],
                                cwd=self.repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.repo / 'new').read_text(), 'untracked work\n')
        self.assertEqual(self.git('show', f'{stash}^3:new'), b'untracked work\n')

    def run_with_git_failure(self, failing_args, after_command=False):
        original_git = backup_work.git

        def failing_git(repo, *args, **kwargs):
            if args[:len(failing_args)] == failing_args:
                if after_command:
                    original_git(repo, *args, **kwargs)
                raise backup_work.BackupError('injected command failure')
            return original_git(repo, *args, **kwargs)

        stdout, stderr = io.StringIO(), io.StringIO()
        previous_cwd = Path.cwd()
        try:
            os.chdir(self.repo)
            with mock.patch.object(backup_work, 'git', side_effect=failing_git), \
                    mock.patch.object(sys, 'argv', [str(SCRIPT)]), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(backup_work.main(), 1)
        finally:
            os.chdir(previous_cwd)
        self.assertNotIn('BACKUP_OK', stdout.getvalue())
        return stdout.getvalue(), stderr.getvalue()

    def test_apply_failure_reports_retained_backup_without_retrying(self):
        (self.repo / 'settings').write_text('pending\n')
        stdout, stderr = self.run_with_git_failure(('stash', 'apply'))
        stash = self.git('rev-parse', 'refs/stash').decode().strip()
        self.assertIn(f'BACKUP_CREATED stash={stash}', stdout)
        self.assertIn(f'BACKUP_FAILED stash={stash}', stderr)
        self.assertEqual(self.git('show', f'{stash}:settings'), b'pending\n')
        self.assertFalse(self.git('status', '--porcelain'))

    def test_push_failure_after_stash_creation_still_reports_hash(self):
        (self.repo / 'settings').write_text('pending\n')
        (self.repo / 'settings').chmod(0o600)
        _, stderr = self.run_with_git_failure(('stash', 'push'), after_command=True)
        stash = self.git('rev-parse', 'refs/stash').decode().strip()
        self.assertIn(f'BACKUP_FAILED stash={stash}', stderr)
        self.assertEqual(self.git('show', f'{stash}:settings'), b'pending\n')
        self.assertEqual((self.repo / 'settings').stat().st_mode & 0o777, 0o600)

    def test_push_failure_keeps_work_and_does_not_claim_an_older_stash(self):
        (self.repo / 'settings').write_text('older work\n')
        self.git('stash', 'push', '-m', 'older backup')
        previous = self.git('rev-parse', 'refs/stash')
        (self.repo / 'settings').write_text('current work\n')
        before = backup_work.snapshot(self.repo)
        _, stderr = self.run_with_git_failure(('stash', 'push'))
        self.assertIn('BACKUP_FAILED stash=none', stderr)
        self.assertEqual(backup_work.snapshot(self.repo), before)
        self.assertEqual(self.git('rev-parse', 'refs/stash'), previous)

    def test_active_operation_is_rejected_without_changing_work(self):
        (self.repo / 'settings').write_text('pending\n')
        (self.repo / '.git' / 'MERGE_HEAD').write_bytes(self.git('rev-parse', 'HEAD'))
        before = backup_work.snapshot(self.repo)
        result = self.run_script(ok=False)
        self.assertIn('Active Git operation', result.stderr)
        self.assertEqual(backup_work.snapshot(self.repo), before)
        self.assertFalse((self.repo / '.git' / 'refs' / 'stash').exists())

    def test_unborn_repository_is_rejected_without_changing_untracked_work(self):
        empty = self.repo / 'unborn'
        empty.mkdir()
        subprocess.check_call(['git', 'init', '-q'], cwd=empty)
        (empty / 'new').write_text('keep me\n')
        self.run_script(ok=False, cwd=empty)
        self.assertEqual((empty / 'new').read_text(), 'keep me\n')


if __name__ == '__main__':
    unittest.main()
