#!/usr/bin/env python3
"""Prepare, review, stage, and commit one saved Git patch without editing work files."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


class PatchError(Exception):
    pass


def git(*arguments, data=None, environment=None, check=True):
    result = subprocess.run(['git', '--literal-pathspecs', *arguments], input=data, capture_output=True,
                            env=environment)
    if check and result.returncode:
        raise PatchError(result.stderr.decode(errors='replace').strip() or
                         result.stdout.decode(errors='replace').strip())
    return result


def output(*arguments, **kwargs):
    return git(*arguments, **kwargs).stdout.decode().strip()


def head():
    result = git('rev-parse', '--verify', 'HEAD', check=False)
    return result.stdout.decode().strip() if result.returncode == 0 else None


def index_tree():
    return output('write-tree')


def checked_path(raw):
    path = PurePosixPath(raw)
    if path.is_absolute() or '..' in path.parts or '.git' in path.parts or not path.parts:
        raise PatchError(f'Expected a repository-relative file path: {raw}')
    return path.as_posix()


def metadata_path(patch):
    return patch.with_name(patch.name + '.json')


def prepare(args, root):
    patch = Path(args.patch).absolute()
    receipt = metadata_path(patch)
    if patch.exists() or receipt.exists():
        raise PatchError('Patch or metadata already exists; use a new patch name.')
    base = index_tree()
    revision = head()
    committed = output('rev-parse', 'HEAD^{tree}') if revision else output('mktree', data=b'')
    if base != committed:
        raise PatchError('The index contains staged changes. Preserve them and resolve their ownership before preparing another commit.')

    entries = []
    for raw_path, raw_snapshot in args.file:
        path = checked_path(raw_path)
        snapshot = Path(raw_snapshot).absolute()
        entries.append((path, snapshot))
    entries.extend((checked_path(path), None) for path in args.delete)
    paths = [path for path, _ in entries]
    if not paths or len(paths) != len(set(paths)):
        raise PatchError('Supply distinct explicit file paths for this commit.')

    with tempfile.TemporaryDirectory(prefix='commit-patch-index-') as temporary:
        environment = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
        git('read-tree', base, environment=environment)
        for path, snapshot in entries:
            tracked = git('ls-files', '--stage', '-z', '--', path).stdout
            mode = tracked.split(b' ', 1)[0].decode() if tracked else None
            if snapshot is None:
                if not tracked:
                    raise PatchError(f'Cannot delete an untracked path: {path}')
                git('update-index', '--force-remove', '--', path, environment=environment)
                continue
            if snapshot.is_symlink():
                data = os.fsencode(os.readlink(snapshot))
                mode = '120000'
            else:
                data = snapshot.read_bytes()
                mode = mode or ('100755' if snapshot.stat().st_mode & 0o111 else '100644')
            filters = [] if mode == '120000' else [f'--path={path}']
            blob = output('hash-object', '-w', '--stdin', *filters, data=data)
            git('update-index', '--add', '--cacheinfo', mode, blob, path, environment=environment)
        target = output('write-tree', environment=environment)
        if target == base:
            raise PatchError('The selected content produces an empty patch.')
        git('diff', '--cached', '--check', base, '--', environment=environment)
        content = git('diff', '--cached', '--binary', '--full-index', '--no-color',
                      '--no-ext-diff', '--no-textconv', '--no-renames',
                      '--src-prefix=a/', '--dst-prefix=b/', base, '--', environment=environment).stdout
    digest = hashlib.sha256(content).hexdigest()
    record = {'repository': str(root), 'head': revision, 'base_tree': base,
              'target_tree': target, 'sha256': digest, 'paths': paths}
    # Exclusive creation preserves earlier review artifacts instead of silently replacing them.
    with patch.open('xb') as destination:
        destination.write(content)
    with receipt.open('x') as destination:
        json.dump(record, destination, indent=2)
        destination.write('\n')
    print(f'Prepared {patch}\nSHA256 {digest}\nReview the complete patch before staging.')


def load(args, root):
    patch = Path(args.patch).absolute()
    record = json.loads(metadata_path(patch).read_text())
    digest = hashlib.sha256(patch.read_bytes()).hexdigest()
    if record['repository'] != str(root):
        raise PatchError('This patch belongs to another repository.')
    if digest != record['sha256']:
        raise PatchError('The saved patch changed. Prepare and review a new patch.')
    supplied = getattr(args, 'reviewed_sha256', None)
    if supplied is not None and supplied != digest:
        raise PatchError('The reviewed SHA256 does not match this patch.')
    committed = output('rev-parse', f'{record["head"]}^{{tree}}') if record['head'] else output('mktree', data=b'')
    if record['base_tree'] != committed:
        raise PatchError('Patch metadata does not match its base commit.')
    # Reconstruct from the reviewed bytes; metadata alone cannot authorize a staged tree.
    with tempfile.TemporaryDirectory(prefix='commit-patch-verify-') as temporary:
        environment = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
        git('read-tree', record['base_tree'], environment=environment)
        git('apply', '--cached', '--whitespace=error', str(patch), environment=environment)
        if output('write-tree', environment=environment) != record['target_tree']:
            raise PatchError('Patch metadata target does not match the reviewed patch.')
    return patch, record


def require_head(record):
    if head() != record['head']:
        raise PatchError('HEAD changed after preparation. Prepare and review the next patch against the current index.')


def verify(record):
    require_head(record)
    if index_tree() != record['target_tree']:
        raise PatchError('The complete staged tree differs from the reviewed patch. Do not commit; preserve and inspect the index.')
    git('diff', '--cached', '--check')


def run(args, root):
    if args.command == 'prepare':
        prepare(args, root)
        return
    patch, record = load(args, root)
    if args.command == 'review':
        sys.stdout.buffer.write(patch.read_bytes())
        sys.stdout.buffer.flush()
        print(f'\nSHA256 {record["sha256"]}')
        return
    if args.command == 'stage':
        require_head(record)
        if index_tree() != record['base_tree']:
            raise PatchError('The index changed after preparation. Preserve staged work and prepare a new patch after resolving it.')
        git('apply', '--cached', '--check', '--whitespace=error', str(patch))
        git('apply', '--cached', '--whitespace=error', str(patch))
    verify(record)
    sys.stdout.buffer.write(git('diff', '--cached', '--no-color', '--no-ext-diff', '--no-textconv').stdout)
    sys.stdout.buffer.flush()
    if args.command != 'commit':
        print(f'Verified staged tree for SHA256 {record["sha256"]}')
        return
    message = args.message
    pattern = r'(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)\n]+\))?!?: [a-z][^\n]*'
    if not re.fullmatch(pattern, message) or len(message) > 50 or message.endswith(('.', '!', '?')):
        raise PatchError('Use a Conventional Commit subject of at most 50 characters, with a lowercase imperative verb and no body or trailing punctuation.')
    arguments = ['commit', '-m', message]
    if args.amend:
        arguments.append('--amend')
    git(*arguments)
    if output('rev-parse', 'HEAD^{tree}') != record['target_tree']:
        raise PatchError('The committed tree differs from the reviewed patch, possibly because a hook changed the index. Inspect the new commit; do not automatically reset or amend it.')
    if output('log', '-1', '--format=%s') != message or output('log', '-1', '--format=%b'):
        raise PatchError('The committed message differs from the approved subject. Inspect the commit.')
    print(output('log', '-1', '--format=%h %s'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'review', 'stage', 'verify', 'commit'):
        command = commands.add_parser(name)
        command.add_argument('patch', help='Explicit patch artifact path; metadata is saved beside it')
        if name == 'prepare':
            command.add_argument('--file', nargs=2, action='append', default=[], metavar=('REPO_PATH', 'CONTENT_FILE'))
            command.add_argument('--delete', action='append', default=[], metavar='REPO_PATH')
        if name in ('stage', 'verify', 'commit'):
            command.add_argument('--reviewed-sha256', required=True, help='SHA256 from the complete patch review')
        if name == 'commit':
            command.add_argument('--message', required=True)
            command.add_argument('--amend', action='store_true')
    args = parser.parse_args()
    try:
        args.patch = str(Path(args.patch).absolute())
        if args.command == 'prepare':
            args.file = [(path, str(Path(snapshot).absolute())) for path, snapshot in args.file]
        root = Path(output('rev-parse', '--show-toplevel')).resolve()
        os.chdir(root)
        run(args, root)
    except (PatchError, OSError, ValueError, KeyError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
