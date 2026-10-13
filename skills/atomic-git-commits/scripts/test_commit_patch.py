import hashlib
import json
import os
from pathlib import Path
import shlex
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

    def test_worktree_files_support_printed_paged_workflow(self):
        script = self.repo / 'helper.sh'
        script.write_text('#!/bin/sh\necho ready\n')
        script.chmod(0o755)
        before = self.git('write-tree')
        result = self.run_helper('prepare', self.patch, '--worktree', 'settings.txt',
                                 '--worktree', 'helper.sh')
        self.assertEqual(self.git('write-tree'), before)
        for step in ('review', 'finalize'):
            command = shlex.split(result.stdout.rsplit('next: ', 1)[-1]
                                  if 'next: ' in result.stdout else result.stdout.rsplit('Next: ', 1)[-1])
            self.assertEqual(command[2], step)
            if step == 'finalize':
                command[-1] = 'feat(helper): add ready command'
            result = subprocess.run(command, cwd=self.repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('show', 'HEAD:settings.txt'), (self.repo / 'settings.txt').read_bytes())
        self.assertTrue(self.git('ls-files', '--stage', 'helper.sh').startswith(b'100755'))

    def test_finalize_commits_reviewed_selection_without_second_delivery(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        result = self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                                 '--message', 'fix(settings): increase timeout')
        self.assertNotIn('diff --git', result.stdout)
        self.assertFalse(Path(str(checksum) + '.verify.json').exists())
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())
        self.assertIn(b'+color=green', self.git('diff'))

    def test_finalize_requires_complete_paged_review_before_staging(self):
        self.snapshot.write_text(''.join(f'setting_{i}=value\n' for i in range(180)))
        digest = self.prepare()
        checksum = self.root / 'review.sha256'
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        checksum.write_text(digest + '\n')
        before = self.git('write-tree')
        result = self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                                 '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn('review', result.stderr)
        self.assertEqual(self.git('write-tree'), before)

    def test_finalize_rejects_unpaged_checksum_before_staging(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.run_helper('review', self.patch, '--sha256-file', checksum)
        before = self.git('write-tree')
        self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                        '--message', 'fix(settings): increase timeout', ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_finalize_rejects_invalid_subject_before_staging(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        before = self.git('write-tree')
        self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                        '--message', 'invalid subject', ok=False)
        self.assertEqual(self.git('write-tree'), before)

    def test_finalize_preserves_unrelated_staged_work(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        (self.repo / 'notes.txt').write_text('unrelated\n')
        self.git('add', 'notes.txt')
        before = self.git('write-tree')
        revision = self.git('rev-parse', 'HEAD')
        self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                        '--message', 'fix(settings): increase timeout', ok=False)
        self.assertEqual(self.git('write-tree'), before)
        self.assertEqual(self.git('rev-parse', 'HEAD'), revision)

    def test_finalize_can_retry_after_hook_failure_without_restaging(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho hook-failed >&2\nexit 1\n')
        hook.chmod(0o755)
        revision = self.git('rev-parse', 'HEAD')
        result = self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                                 '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn('hook-failed', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), revision)
        self.assertEqual(self.git('show', ':settings.txt').decode(), self.snapshot.read_text())
        hook.unlink()
        self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                        '--message', 'fix(settings): increase timeout')
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())

    def test_finalize_reports_hook_changes_to_committed_content(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nprintf "extra\\n" > extra.txt\ngit add extra.txt\n')
        hook.chmod(0o755)
        result = self.run_helper('finalize', self.patch, '--reviewed-sha256-file', checksum,
                                 '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn('committed tree', result.stderr)

    def test_missing_snapshot_explains_input_and_worktree_alternative(self):
        before = self.git('write-tree')
        result = self.run_helper('prepare', self.patch, '--file', 'settings.txt',
                                 self.root / 'missing.txt', ok=False)
        self.assertIn('existing input file', result.stderr)
        self.assertIn('--worktree settings.txt', result.stderr)
        self.assertEqual(self.git('write-tree'), before)
        self.assertFalse(self.patch.exists())

    def test_continuation_preserves_invoked_symlink_path(self):
        alias = self.root / 'linked-helper.py'
        alias.symlink_to(SCRIPT.resolve())
        result = subprocess.run([sys.executable, str(alias), 'prepare', str(self.patch),
                                 '--file', 'settings.txt', str(self.snapshot)], cwd=self.repo,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(alias), result.stdout)

    def test_worktree_path_is_relative_to_repository_from_subdirectory(self):
        nested = self.repo / 'nested'
        nested.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), 'prepare', str(self.patch),
                                 '--worktree', 'settings.txt'], cwd=nested,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('+color=green', self.patch.read_text())

    def test_duplicate_worktree_and_snapshot_path_preserves_index(self):
        before = self.git('write-tree')
        result = self.run_helper('prepare', self.patch, '--worktree', 'settings.txt',
                                 '--file', 'settings.txt', self.snapshot, ok=False)
        self.assertIn('distinct', result.stderr)
        self.assertEqual(self.git('write-tree'), before)

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

    def test_seventy_character_subject_is_accepted(self):
        digest = self.prepare()
        self.stage(digest)
        message = 'fix(settings): increase timeout for slow connections to the API server'
        self.assertEqual(len(message), 70)
        self.run_helper('commit', self.patch, '--reviewed-sha256', digest, '--message', message)
        self.assertEqual(self.git('log', '-1', '--format=%s').decode().strip(), message)

    def test_seventy_one_character_subject_is_rejected(self):
        digest = self.prepare()
        self.stage(digest)
        before = self.git('rev-parse', 'HEAD')
        message = 'fix(settings): increase timeout for slow connections to the API servers'
        self.assertEqual(len(message), 71)
        result = self.run_helper('commit', self.patch, '--reviewed-sha256', digest,
                                 '--message', message, ok=False)
        self.assertIn('71', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_checksum_file_supports_complete_commit_workflow(self):
        digest = self.prepare()
        checksum = self.root / 'review.sha256'
        review = self.run_helper('review', self.patch, '--sha256-file', checksum)
        self.assertIn(self.patch.read_text(), review.stdout)
        self.assertEqual(checksum.read_text(), digest + '\n')
        staged = self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum)
        self.assertNotIn('diff --git', staged.stdout)
        verified = self.run_helper('verify', self.patch, '--reviewed-sha256-file', checksum)
        self.assertIn('+timeout=60', verified.stdout)
        committed = self.run_helper('commit', self.patch, '--reviewed-sha256-file', checksum,
                                     '--message', 'fix(settings): increase timeout')
        self.assertNotIn('diff --git', committed.stdout)
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())

    def test_review_preserves_existing_checksum_file(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        checksum.write_text('earlier review\n')
        result = self.run_helper('review', self.patch, '--sha256-file', checksum, ok=False)
        self.assertIn('already exists', result.stderr)
        self.assertEqual(checksum.read_text(), 'earlier review\n')

    def test_broken_review_output_does_not_save_checksum(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            result = subprocess.run([sys.executable, str(SCRIPT), 'review', str(self.patch),
                                     '--sha256-file', str(checksum)], cwd=self.repo,
                                    stdout=write_fd, stderr=subprocess.PIPE)
        finally:
            os.close(write_fd)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(checksum.exists())

    def test_changed_patch_is_rejected_with_checksum_file(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.run_helper('review', self.patch, '--sha256-file', checksum)
        self.patch.write_text(self.patch.read_text().replace('+timeout=60', '+timeout=90'))
        result = self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum, ok=False)
        self.assertIn('saved patch changed', result.stderr.lower())
        self.assertEqual(self.git('diff', '--cached'), b'')

    def test_truncated_checksum_reports_length_and_preserves_index(self):
        digest = self.prepare()
        before = self.git('write-tree')
        result = self.run_helper('stage', self.patch, '--reviewed-sha256', digest[:59], ok=False)
        self.assertIn('59', result.stderr)
        self.assertIn('64', result.stderr)
        self.assertEqual(self.git('write-tree'), before)

    def test_wrong_checksum_file_preserves_index(self):
        self.prepare()
        checksum = self.root / 'wrong.sha256'
        checksum.write_text('0' * 64 + '\n')
        before = self.git('write-tree')
        result = self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum, ok=False)
        self.assertIn('does not match', result.stderr)
        self.assertEqual(self.git('write-tree'), before)

    def test_relative_checksum_file_resolves_from_invocation_directory(self):
        self.prepare()
        nested = self.repo / 'nested'
        nested.mkdir()
        for arguments in [('review', self.patch, '--sha256-file', 'review.sha256'),
                          ('stage', self.patch, '--reviewed-sha256-file', 'review.sha256')]:
            result = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                                    cwd=nested, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('show', ':settings.txt').decode(), self.snapshot.read_text())

    def review_pages(self, command, checksum):
        for page in range(1, 100):
            option = '--sha256-file' if command == 'review' else '--reviewed-sha256-file'
            result = self.run_helper(command, self.patch, option, checksum, '--page', page)
            if 'complete' in result.stdout.lower():
                return
        self.fail('Paged review did not finish')

    def test_paged_review_delays_checksum_until_every_page_is_printed(self):
        self.snapshot.write_text(''.join(f'setting_{i}=value\n' for i in range(180)))
        self.prepare()
        checksum = self.root / 'review.sha256'
        first = self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        self.assertIn('+setting_0=value', first.stdout)
        self.assertNotIn('+setting_179=value', first.stdout)
        self.assertFalse(checksum.exists())
        self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum, ok=False)
        for page in (2, 3):
            self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', page)
        self.assertTrue(checksum.exists())
        self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum)
        self.assertEqual(self.git('show', ':settings.txt').decode(), self.snapshot.read_text())

    def test_paged_review_rejects_skipped_pages(self):
        self.snapshot.write_text(''.join(f'setting_{i}=value\n' for i in range(180)))
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 3, ok=False)
        self.assertFalse(checksum.exists())

    def test_paged_workflow_requires_staged_diff_delivery_before_commit(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum)
        before = self.git('rev-parse', 'HEAD')
        error = self.run_helper('commit', self.patch, '--reviewed-sha256-file', checksum,
                                '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn(' verify ', error.stderr)
        self.assertIn('--page 1', error.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.review_pages('verify', checksum)
        self.run_helper('commit', self.patch, '--reviewed-sha256-file', checksum,
                        '--message', 'fix(settings): increase timeout')
        self.assertEqual(self.git('show', 'HEAD:settings.txt').decode(), self.snapshot.read_text())

    def test_partial_staged_diff_delivery_blocks_commit(self):
        self.snapshot.write_text(''.join(f'setting_{i}=value\n' for i in range(180)))
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum)
        self.run_helper('verify', self.patch, '--reviewed-sha256-file', checksum, '--page', 1)
        before = self.git('rev-parse', 'HEAD')
        error = self.run_helper('commit', self.patch, '--reviewed-sha256-file', checksum,
                                '--message', 'fix(settings): increase timeout', ok=False)
        self.assertIn('--page 2', error.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_verify_with_empty_index_reports_stage_as_next_step(self):
        digest = self.prepare()
        result = self.run_helper('verify', self.patch, '--reviewed-sha256', digest, ok=False)
        self.assertIn('Nothing is staged', result.stderr)
        self.assertIn(' stage ', result.stderr)

    def test_missing_checksum_reports_review_as_next_step(self):
        self.prepare()
        result = self.run_helper('stage', self.patch, '--reviewed-sha256-file',
                                 self.root / 'missing.sha256', ok=False)
        self.assertIn(' review ', result.stderr)
        self.assertEqual(self.git('diff', '--cached'), b'')

    def test_page_progress_is_not_saved_when_output_pipe_breaks(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            result = subprocess.run([sys.executable, str(SCRIPT), 'review', str(self.patch),
                                     '--sha256-file', str(checksum), '--page', '1'], cwd=self.repo,
                                    stdout=write_fd, stderr=subprocess.PIPE)
        finally:
            os.close(write_fd)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(checksum.exists())
        result = self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        self.assertIn('+timeout=60', result.stdout)

    def test_paged_review_cannot_switch_to_changed_patch_and_metadata(self):
        self.snapshot.write_text(''.join(f'setting_{i}=value\n' for i in range(180)))
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        replacement = self.root / 'replacement.patch'
        self.snapshot.write_text(self.snapshot.read_text().replace('setting_0=value', 'setting_0=other'))
        self.run_helper('prepare', replacement, '--file', 'settings.txt', self.snapshot)
        self.patch.write_bytes(replacement.read_bytes())
        self.patch.with_name(self.patch.name + '.json').write_bytes(
            replacement.with_name(replacement.name + '.json').read_bytes())
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 2, ok=False)
        self.assertFalse(checksum.exists())

    def test_paged_review_bounds_long_lines_without_losing_unicode_content(self):
        self.snapshot.write_text('description=' + 'é' * 6000 + '\n')
        self.prepare()
        checksum = self.root / 'review.sha256'
        delivered = ''
        for page in range(1, 20):
            result = self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', page)
            self.assertLess(len(result.stdout.encode()), 9000)
            payload = result.stdout.split('\n', 1)[1]
            if '\nReview delivery complete.' in payload:
                delivered += payload.split('\nReview delivery complete.', 1)[0]
                break
            delivered += payload.split('\nRead this page. Next:', 1)[0]
        self.assertEqual(delivered, self.patch.read_text())

    def test_final_review_can_resume_if_checksum_creation_was_interrupted(self):
        self.prepare()
        checksum = self.root / 'review.sha256'
        self.review_pages('review', checksum)
        checksum.unlink()
        error = self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum, ok=False)
        self.assertIn('--page 1', error.stderr)
        self.run_helper('review', self.patch, '--sha256-file', checksum, '--page', 1)
        self.run_helper('stage', self.patch, '--reviewed-sha256-file', checksum)
        self.assertEqual(self.git('show', ':settings.txt').decode(), self.snapshot.read_text())


if __name__ == '__main__':
    unittest.main()
