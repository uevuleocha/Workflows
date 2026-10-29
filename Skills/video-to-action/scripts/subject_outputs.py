"""Subject containment and recoverable, serialized latest-pointer publication."""

import hashlib
import json
import os
import re
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path


def subject_path(root: Path, subject: str) -> Path:
    """Validate a single portable Windows folder name and reuse existing casing."""
    if (not subject or subject != subject.strip() or subject.endswith('.')
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', subject)
            or subject in ('.', '..') or len(subject) > 100
            or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)',
                        subject, re.I)):
        raise ValueError('Subject must be a safe, nonempty single folder name')
    matches = [p for p in root.iterdir() if p.name.casefold() == subject.casefold()] if root.exists() else []
    if len(matches) > 1:
        raise ValueError('Ambiguous subject casing')
    path = matches[0] if matches else root / subject
    if path.exists() and not path.is_dir():
        raise ValueError('Subject collides with a file')
    if path.resolve().parent != root.resolve():
        raise ValueError('Subject escapes output root')
    return path


def atomic_json(path: Path, data: dict) -> None:
    """Replace one JSON file atomically with a flushed sibling temporary file."""
    if path.is_symlink() or (path.exists() and path.resolve().parent != path.parent.resolve()):
        raise ValueError('Refusing redirected pointer')
    fd, name = tempfile.mkstemp(prefix='.latest-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def pointer_lock_path(root: Path) -> Path:
    """Place a stable per-output-root lock in the owning workspace's tmp folder."""
    resolved = root.resolve()
    workspace = next((p for p in (resolved, *resolved.parents)
                      if any((p / marker).exists() for marker in ('CLAUDE.md', 'AGENTS.md', '.git'))),
                     Path.cwd().resolve())
    directory = workspace / 'tmp' / 'video-to-action-locks'
    key = hashlib.sha256(os.path.normcase(str(resolved)).encode('utf-8')).hexdigest()
    return directory / f'{key}.lock'


@contextmanager
def pointer_lock(root: Path):
    """Use an OS lock in workspace tmp; recreate its file after idle cleanup."""
    lock_path = pointer_lock_path(root)
    workspace = lock_path.parent.parent.parent
    for directory in (workspace / 'tmp', lock_path.parent):
        if directory.exists() and not directory.resolve().is_relative_to(workspace):
            raise ValueError('Lock directory escapes workspace')
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    if not lock_path.parent.resolve(strict=True).is_relative_to(workspace):
        raise ValueError('Lock directory escapes workspace')
    if lock_path.is_symlink():
        raise ValueError('Refusing redirected lock')
    with lock_path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        deadline = time.monotonic() + 30
        while True:
            stream.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Latest-pointer lock busy; retry pointer repair only')
                time.sleep(.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def _recover(root: Path) -> bool:
    journal = root / '.latest-pending.json'
    if not journal.exists():
        return False
    data = json.loads(journal.read_text(encoding='utf-8'))
    folder = subject_path(root, data['subject'])
    run = Path(data['run_dir']).resolve()
    if run.parent != folder.resolve() or not run.is_dir():
        raise ValueError('Pending pointer does not resolve to a subject run')
    atomic_json(folder / 'latest.json', data)
    atomic_json(root / 'latest.json', data)
    journal.unlink()
    return True


def repair_pointers(root: Path) -> bool:
    """Replay a pending pointer transaction without calling Gemini."""
    if not root.is_dir():
        raise ValueError('Output root does not exist')
    with pointer_lock(root):
        return _recover(root)


def publish_pointers(root: Path, subject: str, data: dict) -> None:
    """Serialize both pointer writes and retain a journal on any partial failure."""
    with pointer_lock(root):
        _recover(root)
        folder = subject_path(root, subject)
        payload = dict(data, subject=folder.name)
        atomic_json(root / '.latest-pending.json', payload)
        _recover(root)
