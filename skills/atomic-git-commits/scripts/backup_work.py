#!/usr/bin/env python3
"""Retain a Git stash backup and verify that applying it restores working changes."""

import argparse
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import uuid


class BackupError(Exception):
    pass


def git(repo, *args, check=True):
    result = subprocess.run(
        ['git', *args], cwd=repo, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        detail = (result.stderr or result.stdout).decode(errors='replace').strip()
        raise BackupError(f"git {' '.join(args)} failed: {detail}")
    return result


def stash_hash(repo):
    result = git(repo, 'rev-parse', '--verify', '--quiet', 'refs/stash', check=False)
    if result.returncode == 1:
        return None
    if result.returncode:
        raise BackupError(result.stderr.decode(errors='replace').strip())
    return result.stdout.decode().strip()


def private_stash(repo, *args):
    # Both saving and applying a stash can recreate private working files.
    previous_umask = os.umask(0o077)
    try:
        return git(repo, 'stash', *args)
    finally:
        os.umask(previous_umask)


def status(repo):
    return git(repo, 'status', '--porcelain=v1', '-z', '--untracked-files=all').stdout


def head(repo):
    return git(repo, 'rev-parse', '--verify', 'HEAD').stdout.decode().strip()


def file_state(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(info.st_mode):
        return ('symlink', os.readlink(os.fsencode(path)))
    if not stat.S_ISREG(info.st_mode):
        raise BackupError(f'Cannot back up non-file path: {path}')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return ('file', stat.S_IMODE(info.st_mode), digest.digest())


def snapshot(repo):
    diff_args = ('--no-ext-diff', '--no-textconv', '--binary', '--full-index',
                 '--no-renames', '--ignore-submodules=none')
    paths = set()
    for args in [('diff', '--name-only', '-z', '--no-renames'),
                 ('diff', '--cached', '--name-only', '-z', '--no-renames'),
                 ('ls-files', '--others', '--exclude-standard', '-z')]:
        paths.update(git(repo, *args).stdout.split(b'\0'))
    paths.discard(b'')
    directories = {}
    for path in paths:
        parent = (repo / os.fsdecode(path)).parent
        while parent != repo:
            directories[parent] = stat.S_IMODE(parent.stat().st_mode)
            parent = parent.parent
    return (
        head(repo), status(repo),
        git(repo, 'diff', '--cached', *diff_args).stdout,
        git(repo, 'diff', *diff_args).stdout,
        {path: file_state(repo / os.fsdecode(path)) for path in paths},
        directories,
    )


def check_transformations(repo, files):
    # Stash stores filtered Git blobs, so a later comparison cannot recover lost bytes.
    for option in ('core.autocrlf', 'core.eol'):
        result = git(repo, 'config', '--get', option, check=False)
        if result.returncode not in (0, 1):
            raise BackupError(f'Cannot inspect {option}')
        value = result.stdout.decode().strip().lower()
        if (option == 'core.autocrlf' and value not in ('', 'false', 'no', 'off', '0')) \
                or (option == 'core.eol' and value == 'crlf'):
            raise BackupError(f'{option}={value} can transform bytes; no stash created')
    for path, state in files.items():
        if state is None or state[0] != 'file':
            continue
        attrs = git(repo, 'check-attr', '-z', 'text', 'eol', 'filter',
                    'working-tree-encoding', 'ident', '--', os.fsdecode(path)).stdout
        fields = attrs.split(b'\0')[:-1]
        for offset in range(0, len(fields), 3):
            if fields[offset + 2] not in (b'unspecified', b'unset'):
                attribute = os.fsdecode(fields[offset + 1])
                raise BackupError(f'{attribute} can transform {os.fsdecode(path)!r}; '
                                  'no stash created')


def restore_permissions(repo, before):
    for path, state in before[4].items():
        if state is not None and state[0] == 'file':
            restored = repo / os.fsdecode(path)
            if not stat.S_ISREG(restored.lstat().st_mode):
                raise BackupError(f'Restored file type differs: {restored}')
            restored.chmod(state[1])
    for directory, mode in before[5].items():
        directory.chmod(mode)


def check_operation(repo):
    for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD',
                 'rebase-merge', 'rebase-apply', 'sequencer'):
        path = git(repo, 'rev-parse', '--git-path', name).stdout.decode().strip()
        if (repo / path).exists():
            raise BackupError(f'Active Git operation ({name}); preserve state and stop')
    if git(repo, 'ls-files', '--unmerged', '-z').stdout:
        raise BackupError('Unmerged index; preserve state and stop')


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    repo = None
    original_head = 'unknown'
    previous_stash = None
    backup = None
    attempted = False
    try:
        root = git(None, 'rev-parse', '--show-toplevel').stdout
        repo = Path(os.fsdecode(root.rstrip(b'\n')))
        check_operation(repo)
        original_head = head(repo)
        previous_stash = stash_hash(repo)
        if not status(repo):
            print(f'BACKUP_OK stash=none head={original_head}')
            return 0
        before = snapshot(repo)
        if before[0] != original_head:
            raise BackupError('HEAD changed during inspection')
        check_transformations(repo, before[4])
        attempted = True
        private_stash(repo, 'push', '--include-untracked', '--message',
                      f'atomic-commits backup {uuid.uuid4().hex}')
        backup = stash_hash(repo)
        if not backup or backup == previous_stash:
            backup = None
            raise BackupError('No new stash was created')
        # Emit the durable recovery reference before attempting restoration.
        print(f'BACKUP_CREATED stash={backup} head={original_head}', flush=True)
        if status(repo) or head(repo) != original_head:
            raise BackupError('Tree is not clean or HEAD changed after stash push')
        private_stash(repo, 'apply', '--index', backup)
        restore_permissions(repo, before)
        if snapshot(repo) != before:
            raise BackupError('Restored HEAD, status, diffs, or file contents differ')
        print(f'BACKUP_OK stash={backup} head={original_head}')
        return 0
    except (BackupError, OSError) as error:
        # A failed push can still leave a new stash; never hide that reference.
        if attempted and not backup:
            try:
                candidate = stash_hash(repo)
                if candidate != previous_stash:
                    backup = candidate
            except (BackupError, OSError):
                pass
        print(f'BACKUP_FAILED stash={backup or "none"} head={original_head}',
              file=sys.stderr)
        print(f'{error}\nStop. Preserve the stash and current state.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
