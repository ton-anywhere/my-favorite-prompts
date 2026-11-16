#!/usr/bin/env python3
"""Prepare, review, stage, and commit one saved Git patch without editing work files."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
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


def next_command(command, patch, *arguments):
    return shlex.join([sys.executable, str(Path(__file__).absolute()), command,
                       str(patch), *map(str, arguments)])


def checksum_arguments(args):
    if args.reviewed_sha256_file:
        return ['--reviewed-sha256-file', args.reviewed_sha256_file]
    return ['--reviewed-sha256', args.reviewed_sha256]


def progress_path(checksum, kind):
    return Path(str(checksum) + f'.{kind}.json')


def read_progress(checksum, kind):
    path = progress_path(checksum, kind)
    return json.loads(path.read_text()) if path.exists() else None


def progress_identity(content, record):
    return {'patch_sha256': record['sha256'],
            'content_sha256': hashlib.sha256(content).hexdigest(),
            'head': record['head'], 'target_tree': record['target_tree']}


def require_delivery(checksum, kind, content, record, patch):
    progress = read_progress(checksum, kind)
    identity = progress_identity(content, record)
    if progress and any(progress.get(key) != value for key, value in identity.items()):
        raise PatchError('Review content or base state changed. Preserve work and prepare a new patch and review checksum file.')
    if not progress or progress['next_page'] != progress['total_pages'] + 1:
        page = progress['next_page'] if progress else 1
        option = '--sha256-file' if kind == 'review' else '--reviewed-sha256-file'
        raise PatchError(f'Complete the paged {kind} before continuing. Next: ' + next_command(
            kind, patch, option, checksum, '--page', page))


def print_page(content, record, checksum, kind, page, patch):
    pages = []
    start = 0
    while start < len(content):
        end = min(start + 8000, len(content))
        lines = content[start:end].splitlines(keepends=True)
        if len(lines) > 80:
            end = start + len(b''.join(lines[:80]))
        elif end < len(content) and b'\n' in content[start:end]:
            end = start + content[start:end].rfind(b'\n') + 1
        boundary = end
        while end < len(content) and end > start and content[end] & 0xc0 == 0x80:
            end -= 1
        if end == start:
            end = boundary
        pages.append(content[start:end])
        start = end
    identity = progress_identity(content, record)
    progress = read_progress(checksum, kind)
    expected = progress['next_page'] if progress else 1
    if kind == 'review' and progress and not Path(checksum).exists():
        # Final output can succeed before checksum creation is interrupted.
        expected = min(expected, progress['total_pages'])
    if progress and any(progress.get(key) != value for key, value in identity.items()):
        raise PatchError('Review content or base state changed. Preserve earlier artifacts and start a new review checksum file.')
    if page != expected or not 1 <= page <= len(pages):
        raise PatchError(f'Expected {kind} page {expected} of {len(pages)}; received {page}.')
    print(f'{kind.capitalize()} page {page}/{len(pages)} | SHA256 {record["sha256"]}', flush=True)
    sys.stdout.buffer.write(pages[page - 1])
    sys.stdout.buffer.flush()
    complete = page == len(pages)
    if complete:
        print(f'\n{kind.capitalize()} delivery complete. Read this page before continuing.')
    else:
        option = '--sha256-file' if kind == 'review' else '--reviewed-sha256-file'
        print('\nRead this page. Next: ' + next_command(kind, patch, option, checksum, '--page', page + 1))
    sys.stdout.flush()
    # Record only flushed output. A broken pipe leaves the page available to retry.
    path = progress_path(checksum, kind)
    with path.open('w' if progress else 'x') as destination:
        json.dump({**identity, 'next_page': page + 1, 'total_pages': len(pages)}, destination)
    return complete


def prepare(args, root):
    patch = Path(args.patch).absolute()
    receipt = metadata_path(patch)
    if patch.exists() or receipt.exists():
        raise PatchError('Patch or metadata already exists; preserve both and use a new patch name in a fresh mktemp directory.')
    base = index_tree()
    revision = head()
    committed = output('rev-parse', 'HEAD^{tree}') if revision else output('mktree', data=b'')
    if base != committed:
        raise PatchError('The index contains staged changes. Preserve them and resolve their ownership before preparing another commit.')

    entries = []
    for raw_path, raw_snapshot in args.file:
        path = checked_path(raw_path)
        snapshot = Path(raw_snapshot).absolute()
        if not snapshot.is_file() and not snapshot.is_symlink():
            raise PatchError(f'CONTENT_FILE must be an existing input file: {snapshot}. '
                             'Create it with the selected content first. '
                             f'For all working-file changes, use --worktree {shlex.quote(path)} instead.')
        entries.append((path, snapshot))
    entries.extend((checked_path(path), root / checked_path(path)) for path in args.worktree)
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
    print('Next: ' + next_command('review', patch, '--sha256-file', str(patch) + '.sha256', '--page', 1))


def load(args, root):
    patch = Path(args.patch).absolute()
    record = json.loads(metadata_path(patch).read_text())
    digest = hashlib.sha256(patch.read_bytes()).hexdigest()
    if record['repository'] != str(root):
        raise PatchError('This patch belongs to another repository.')
    if digest != record['sha256']:
        raise PatchError('The saved patch changed. Prepare and review a new patch.')
    supplied = getattr(args, 'reviewed_sha256', None)
    checksum_file = getattr(args, 'reviewed_sha256_file', None)
    if checksum_file is not None:
        if not Path(checksum_file).exists():
            progress = read_progress(checksum_file, 'review')
            page = min(progress['next_page'], progress['total_pages']) if progress else 1
            raise PatchError('Review checksum is not ready. Next: ' + next_command(
                'review', patch, '--sha256-file', checksum_file, '--page', page))
        supplied = Path(checksum_file).read_text().strip()
    if supplied is not None and not re.fullmatch(r'[0-9a-f]{64}', supplied):
        raise PatchError(f'Expected 64 lowercase hexadecimal characters for the reviewed SHA256; received {len(supplied)} characters. Use the checksum file saved by review to avoid transcription errors.')
    if supplied is not None and supplied != digest:
        raise PatchError('The reviewed SHA256 does not match this patch. Check that you used the checksum from this patch review; preserve the patch and index.')
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
    if checksum_file and read_progress(checksum_file, 'review'):
        require_delivery(checksum_file, 'review', patch.read_bytes(), record, patch)
    return patch, record


def require_head(record):
    if head() != record['head']:
        raise PatchError('HEAD changed after preparation. Prepare and review the next patch against the current index.')


def verify(record):
    require_head(record)
    if index_tree() != record['target_tree']:
        raise PatchError('The complete staged tree differs from the reviewed patch. Do not commit; preserve and inspect the index.')
    git('diff', '--cached', '--check')


def validate_message(message):
    pattern = r'(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)\n]+\))?!?: [a-z][^\n]*'
    if not re.fullmatch(pattern, message) or len(message) > 70 or message.endswith(('.', '!', '?')):
        raise PatchError(f'Use a Conventional Commit subject of at most 70 characters, with a lowercase imperative verb and no body or trailing punctuation. Received {len(message)} characters.')


def run(args, root):
    if args.command == 'prepare':
        prepare(args, root)
        return
    patch, record = load(args, root)
    if args.command == 'review':
        checksum_file = Path(args.sha256_file) if args.sha256_file else None
        if checksum_file is not None and checksum_file.exists():
            raise PatchError('Checksum file already exists; use a new review file name.')
        if args.page is not None:
            if checksum_file is None:
                raise PatchError('Paged review requires --sha256-file.')
            if not print_page(patch.read_bytes(), record, checksum_file, 'review', args.page, patch):
                return
        else:
            if checksum_file and read_progress(checksum_file, 'review'):
                raise PatchError('Continue the paged review with --page; preserve its progress.')
            sys.stdout.buffer.write(patch.read_bytes())
            sys.stdout.buffer.flush()
            print(f'\nSHA256 {record["sha256"]}')
            sys.stdout.flush()
        if checksum_file is not None:
            # A broken output pipe must fail before a review checksum is saved.
            with checksum_file.open('x') as destination:
                destination.write(record['sha256'] + '\n')
            print(f'Checksum saved to {checksum_file}. Read the complete patch before staging.')
            if args.page is not None:
                print('Once authorized, next: ' + next_command(
                    'finalize', patch, '--reviewed-sha256-file', checksum_file,
                    '--message', 'TYPE(SCOPE): imperative subject'))
            else:
                print('Next: ' + next_command('stage', patch, '--reviewed-sha256-file', checksum_file))
        return
    if args.command == 'finalize':
        require_delivery(args.reviewed_sha256_file, 'review', patch.read_bytes(), record, patch)
        validate_message(args.message)
        require_head(record)
        tree = index_tree()
        if tree not in (record['base_tree'], record['target_tree']):
            raise PatchError('The index changed after preparation. Preserve staged work and inspect it before retrying finalize.')
        if tree == record['base_tree']:
            git('apply', '--cached', '--check', '--whitespace=error', str(patch))
            git('apply', '--cached', '--whitespace=error', str(patch))
    elif args.command == 'stage':
        require_head(record)
        if index_tree() != record['base_tree']:
            raise PatchError('The index changed after preparation. Preserve staged work and prepare a new patch after resolving it.')
        git('apply', '--cached', '--check', '--whitespace=error', str(patch))
        git('apply', '--cached', '--whitespace=error', str(patch))
    elif index_tree() == record['base_tree']:
        raise PatchError('Nothing is staged. Next: ' + next_command('stage', patch, *checksum_arguments(args)))
    verify(record)
    checksum_file = args.reviewed_sha256_file
    paged = checksum_file and read_progress(checksum_file, 'review')
    staged_diff = (git('diff', '--cached', '--no-color', '--no-ext-diff', '--no-textconv').stdout
                   if args.command != 'finalize' else None)
    if args.command == 'verify':
        if paged:
            if args.page is None:
                progress = read_progress(checksum_file, 'verify')
                page = progress['next_page'] if progress else 1
                raise PatchError('Paged verification required. Next: ' + next_command(
                    'verify', patch, *checksum_arguments(args), '--page', page))
            if not print_page(staged_diff, record, checksum_file, 'verify', args.page, patch):
                return
        else:
            if args.page is not None:
                raise PatchError('Start with review --page 1 --sha256-file to use paged verification.')
            sys.stdout.buffer.write(staged_diff)
            sys.stdout.buffer.flush()
    if args.command not in ('commit', 'finalize'):
        print(f'Verified staged tree for SHA256 {record["sha256"]}')
        if args.command == 'stage':
            page_arguments = ['--page', '1'] if paged else []
            print('Next: ' + next_command('verify', patch, *checksum_arguments(args), *page_arguments))
        else:
            print('Read the complete staged diff. Once authorized, next: ' + next_command(
                'commit', patch, *checksum_arguments(args), '--message', 'TYPE(SCOPE): imperative subject'))
        return
    if paged and args.command == 'commit':
        require_delivery(checksum_file, 'verify', staged_diff, record, patch)
    message = args.message
    validate_message(message)
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
    for name in ('prepare', 'review', 'stage', 'verify', 'commit', 'finalize'):
        command = commands.add_parser(name)
        command.add_argument('patch', help='Explicit patch artifact path; metadata is saved beside it')
        if name == 'prepare':
            command.add_argument('--worktree', action='append', default=[], metavar='REPO_PATH',
                                 help='Include all changes in this working file; repeat for each repository-relative path')
            command.add_argument('--file', nargs=2, action='append', default=[], metavar=('REPO_PATH', 'CONTENT_FILE'),
                                 help='Read selected content from an existing input file; does not create CONTENT_FILE')
            command.add_argument('--delete', action='append', default=[], metavar='REPO_PATH')
        if name == 'review':
            command.add_argument('--sha256-file', help='Save the checksum to a new file after printing the complete patch')
        if name in ('review', 'verify'):
            command.add_argument('--page', type=int, help='Print the next bounded page and track delivery; start at 1')
        if name in ('stage', 'verify', 'commit'):
            checksum = command.add_mutually_exclusive_group(required=True)
            checksum.add_argument('--reviewed-sha256', help='SHA256 from the complete patch review')
            checksum.add_argument('--reviewed-sha256-file', help='Checksum file saved by review; read the complete patch before using it')
        if name == 'finalize':
            command.add_argument('--reviewed-sha256-file', required=True,
                                 help='Checksum from completed paged review; stage, check, and commit without repeating the diff')
        if name in ('commit', 'finalize'):
            command.add_argument('--message', required=True)
            command.add_argument('--amend', action='store_true')
    args = parser.parse_args()
    try:
        args.patch = str(Path(args.patch).absolute())
        for attribute in ('sha256_file', 'reviewed_sha256_file'):
            if getattr(args, attribute, None) is not None:
                setattr(args, attribute, str(Path(getattr(args, attribute)).absolute()))
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
