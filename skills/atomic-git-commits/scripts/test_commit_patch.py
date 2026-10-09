import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('commit_patch.py')


class CommitPatchTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='commit-patch-test-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Patch Test')
        self.git('config', 'user.email', 'patch@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        (self.repo / 'settings.txt').write_text('timeout=30\ncolor=blue\n')
        self.git('add', 'settings.txt')
        self.git('commit', '-qm', 'chore: initialize fixture')
        (self.repo / 'settings.txt').write_text('timeout=60\ncolor=green\n')
        self.snapshot = self.root / 'timeout.txt'
        self.snapshot.write_text('timeout=60\ncolor=blue\n')
        self.patch = self.root / 'timeout.patch'

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.STDOUT)

    def run_helper(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=self.repo,
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def prepare(self, *extra):
        self.run_helper('prepare', self.patch, '--file', 'settings.txt', self.snapshot, *extra)
        return hashlib.sha256(self.patch.read_bytes()).hexdigest()

    def stage(self, digest):
        return self.run_helper('stage', self.patch, '--reviewed-sha256', digest)

    def test_preparation_preserves_real_index_and_worktree(self):
        before = self.git('write-tree')
        self.prepare()
        self.assertEqual(self.git('write-tree'), before)
        self.assertEqual((self.repo / 'settings.txt').read_text(), 'timeout=60\ncolor=green\n')

    def test_review_prints_complete_patch_and_checksum(self):
        digest = self.prepare()
        output = self.run_helper('review', self.patch).stdout
        self.assertIn(self.patch.read_text(), output)
        self.assertIn(digest, output)

    def test_adjacent_changes_are_split_without_rewriting_worktree(self):
        self.stage(self.prepare())
        self.assertEqual(self.git('show', ':settings.txt').decode(), 'timeout=60\ncolor=blue\n')
        self.assertEqual((self.repo / 'settings.txt').read_text(), 'timeout=60\ncolor=green\n')

    def test_preexisting_staged_work_is_preserved_and_blocks_preparation(self):
        (self.repo / 'notes.txt').write_text('unrelated\n')
        self.git('add', 'notes.txt')
        before = self.git('write-tree')
        self.run_helper('prepare', self.patch, '--file', 'settings.txt', self.snapshot, ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_whitespace_errors_are_rejected_before_staging(self):
        self.snapshot.write_text('timeout=60 \ncolor=blue\n')
        before = self.git('write-tree')
        self.run_helper('prepare', self.patch, '--file', 'settings.txt', self.snapshot, ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_wrong_review_checksum_blocks_staging(self):
        self.prepare()
        before = self.git('write-tree')
        self.run_helper('stage', self.patch, '--reviewed-sha256', '0' * 64, ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_patch_modified_after_review_is_rejected(self):
        digest = self.prepare()
        self.patch.write_text(self.patch.read_text().replace('+timeout=60', '+timeout=90'))
        self.run_helper('stage', self.patch, '--reviewed-sha256', digest, ok=False)
        self.assertEqual(self.git('diff', '--cached'), b'')

    def test_index_drift_after_preparation_blocks_staging(self):
        digest = self.prepare()
        self.git('add', 'settings.txt')
        before = self.git('write-tree')
        self.run_helper('stage', self.patch, '--reviewed-sha256', digest, ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_unrelated_staged_content_blocks_commit(self):
        digest = self.prepare()
        self.stage(digest)
        (self.repo / 'notes.txt').write_text('unrelated\n')
        self.git('add', 'notes.txt')
        before = self.git('rev-parse', 'HEAD')
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                        '--message', 'fix(settings): increase timeout', ok=False)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_commit_contains_only_selected_change_and_supports_next_patch(self):
        digest = self.prepare()
        self.stage(digest)
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                        '--message', 'fix(settings): increase timeout')
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())
        self.assertIn(b'+color=green', self.git('diff'))
        self.patch = self.root / 'color.patch'
        self.snapshot.write_text((self.repo / 'settings.txt').read_text())
        self.stage(self.prepare())
        self.assertEqual(self.git('diff'), b'')

    def test_patch_cannot_be_overwritten(self):
        self.prepare()
        before = self.patch.read_bytes()
        self.run_helper('prepare', self.patch, '--file', 'settings.txt', self.snapshot, ok=False)
        self.assertEqual(self.patch.read_bytes(), before)

    def test_binary_creation_and_deletion_use_git_patches(self):
        binary = self.root / 'image.bin'
        binary.write_bytes(b'\x00\xff\x01\x00')
        self.run_helper('prepare', self.patch, '--file', 'image.bin', binary, '--delete', 'settings.txt')
        digest = hashlib.sha256(self.patch.read_bytes()).hexdigest()
        self.stage(digest)
        self.assertEqual(self.git('show', ':image.bin'), binary.read_bytes())
        self.assertEqual(self.git('ls-files', 'settings.txt'), b'')
        self.assertTrue((self.repo / 'settings.txt').exists())

    def test_path_outside_repository_is_rejected(self):
        self.run_helper('prepare', self.patch, '--file', '../outside', self.snapshot, ok=False)
        self.assertEqual(self.git('diff', '--cached'), b'')

    def test_empty_patch_is_rejected(self):
        self.snapshot.write_bytes(self.git('show', ':settings.txt'))
        self.run_helper('prepare', self.patch, '--file', 'settings.txt', self.snapshot, ok=False)

    def test_existing_executable_mode_is_preserved(self):
        self.git('update-index', '--chmod=+x', 'settings.txt')
        self.git('commit', '-qm', 'chore: mark settings executable')
        self.stage(self.prepare())
        self.assertTrue(self.git('ls-files', '--stage', 'settings.txt').startswith(b'100755'))

    def test_hook_that_changes_index_is_reported_after_commit(self):
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nprintf "extra\\n" > extra.txt\ngit add extra.txt\n')
        hook.chmod(0o755)
        digest = self.prepare()
        self.stage(digest)
        result = self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                                 '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn('committed tree', result.stderr.lower())

    def test_relative_artifacts_resolve_from_invocation_directory(self):
        nested = self.repo / 'nested'
        nested.mkdir()
        (nested / 'snapshot.txt').write_text(self.snapshot.read_text())
        (self.repo / 'snapshot.txt').write_text('wrong content\n')
        result = subprocess.run([sys.executable, str(SCRIPT), 'prepare', 'selected.patch',
                                 '--file', 'settings.txt', 'snapshot.txt'], cwd=nested,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((nested / 'selected.patch').exists())
        self.assertIn('+timeout=60', (nested / 'selected.patch').read_text())

    def test_modified_metadata_cannot_authorize_unreviewed_staged_content(self):
        digest = self.prepare()
        self.stage(digest)
        (self.repo / 'notes.txt').write_text('unrelated\n')
        self.git('add', 'notes.txt')
        receipt_path = self.patch.with_name(self.patch.name + '.json')
        receipt = json.loads(receipt_path.read_text())
        receipt['target_tree'] = self.git('write-tree').decode().strip()
        receipt_path.write_text(json.dumps(receipt))
        before = self.git('rev-parse', 'HEAD')
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                        '--message', 'fix(settings): increase timeout', ok=False)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_git_attributes_apply_to_selected_content(self):
        (self.repo / '.gitattributes').write_text('*.txt text eol=lf\n')
        self.git('add', '.gitattributes')
        self.git('commit', '-qm', 'chore: normalize text files')
        self.snapshot.write_bytes(b'timeout=60\r\ncolor=blue\r\n')
        self.stage(self.prepare())
        self.assertEqual(self.git('show', ':settings.txt'), b'timeout=60\ncolor=blue\n')

    def test_head_changed_after_preparation_blocks_staging(self):
        digest = self.prepare()
        self.git('commit', '--allow-empty', '-qm', 'chore: move head')
        self.run_helper('stage', self.patch, '--reviewed-sha256', digest, ok=False)
        self.assertEqual(self.git('diff', '--cached'), b'')

    def test_invalid_message_blocks_commit(self):
        digest = self.prepare()
        self.stage(digest)
        before = self.git('rev-parse', 'HEAD')
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                        '--message', 'fix(settings): increase timeout\n\nunapproved body', ok=False)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_content_amend_uses_the_reviewed_tree(self):
        digest = self.prepare()
        self.stage(digest)
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                        '--message', 'fix(settings): increase timeout', '--amend')
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())
        self.assertEqual(self.git('rev-list', '--count', 'HEAD').strip(), b'1')


if __name__ == '__main__':
    unittest.main()
