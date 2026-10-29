"""Inventory and migrate flat video archives with hash and pointer recovery evidence.

Run --workspace PATH --evidence PATH to inventory, then repeat with --apply.
Evidence is machine-owned JSON; it contains no credentials or video bodies.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

from subject_outputs import atomic_json, pointer_lock, subject_path


def hashes(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink() or path.resolve() != path.absolute():
            raise ValueError('Redirected archive entry')
        if path.is_file():
            result[str(path.relative_to(folder))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def inventory(workspace):
    workspace = workspace.resolve()
    root = workspace / 'Archive/Historical/Video-to-action'
    if root.resolve() != root or not root.is_dir():
        raise ValueError('Archive root missing or redirected')
    legacy = subject_path(root, 'Legacy')
    moves = []
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or not re.match(r'^\d{8}-\d{6}(?:-\d+)? - ', folder.name):
            continue
        destination = legacy / folder.name
        if destination.exists():
            raise ValueError('Legacy destination collision')
        moves.append({'source': str(folder), 'destination': str(destination), 'hashes': hashes(folder)})
    pointer = root / 'latest.json'
    if pointer.is_symlink():
        raise ValueError('Redirected pointer')
    return {'workspace': str(workspace), 'root': str(root), 'moves': moves,
            'pointer_before': base64.b64encode(pointer.read_bytes()).decode() if pointer.exists() else None,
            'status': 'inventoried'}


def migrate(workspace, evidence, apply=False):
    snapshot = inventory(workspace)
    if not evidence.exists():
        evidence.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(evidence, snapshot)
    previous = json.loads(evidence.read_text(encoding='utf-8'))
    if previous.get('status') == 'complete':
        for move in previous['moves']:
            assert not Path(move['source']).exists()
            assert hashes(Path(move['destination'])) == move['hashes']
        current = json.loads((Path(previous['root']) / 'latest.json').read_text(encoding='utf-8'))
        if current != previous['pointer_after']:
            raise ValueError('Latest pointer changed since migration; do not overwrite it')
        if previous['moves']:
            legacy_pointer = Path(previous['root']) / 'Legacy/latest.json'
            if json.loads(legacy_pointer.read_text(encoding='utf-8')) != current:
                raise ValueError('Legacy pointer changed since migration')
        return previous
    if previous != snapshot:
        raise ValueError('Inventory changed or migration interrupted; review evidence before recovery')
    if not apply:
        return snapshot
    root = Path(snapshot['root'])
    legacy = subject_path(root, 'Legacy')
    raw = base64.b64decode(snapshot['pointer_before']) if snapshot['pointer_before'] is not None else b''
    try:
        metadata = json.loads(raw)
    except (ValueError, UnicodeError):
        metadata = None
    if snapshot['moves']:
        # Reconstruct only from an existing report, never manufacture model history.
        if not isinstance(metadata, dict) or not metadata.get('run_dir'):
            folder = Path(snapshot['moves'][-1]['source'])
            report = next((folder / name for name in ('report.md', 'procedure.md') if (folder / name).exists()), None)
            if report is None:
                raise ValueError('Cannot reconstruct pointer from this legacy format')
            text = report.read_text(encoding='utf-8')
            source = re.search(r'\*\*Source:?\*\*:?\s*(https?://\S+)', text)
            if not source:
                raise ValueError('Missing source metadata for pointer reconstruction')
            metadata = {'latest_run': folder.name.split(' - ')[0], 'run_dir': str(folder),
                        'url': source[1], 'title': folder.name.split(' - ', 1)[1],
                        'completed': bool(re.search(r'\*\*Status:?\*\*:?\s*complete\b', text)),
                        'reconstructed': True}
        old = Path(metadata['run_dir'])
        old = old if old.is_absolute() else workspace / old
        match = next((m for m in snapshot['moves'] if Path(m['source']).resolve() == old.resolve()), None)
        if match is None:
            raise ValueError('Latest pointer does not reference inventoried run')
        metadata = dict(metadata, run_dir=str(Path(match['destination']).relative_to(workspace)), subject=legacy.name)
    elif raw.strip():
        if not isinstance(metadata, dict) or metadata.get('run_dir') is not None:
            raise ValueError('Nonempty archive pointer without flat runs requires review')
    else:
        metadata = {'latest_run': None, 'run_dir': None, 'completed': False, 'subject': None}
    with pointer_lock(root):
        if inventory(workspace) != snapshot:
            raise ValueError('Archive changed before migration')
        if snapshot['moves']:
            legacy.mkdir(exist_ok=True)
        for move in snapshot['moves']:
            source, destination = Path(move['source']), Path(move['destination'])
            if source.resolve().parent != root or destination.resolve().parent != legacy.resolve():
                raise ValueError('Move containment failed')
            if hashes(source) != move['hashes'] or destination.exists():
                raise ValueError('Concurrent edit or destination collision')
            source.rename(destination)
            if hashes(destination) != move['hashes']:
                raise ValueError('Post-move hash mismatch')
        if snapshot['moves']:
            atomic_json(legacy / 'latest.json', metadata)
        atomic_json(root / 'latest.json', metadata)
    snapshot.update(status='complete', pointer_after=metadata)
    atomic_json(evidence, snapshot)
    return snapshot


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    result = migrate(args.workspace.resolve(), args.evidence, args.apply)
    print(f"{result['status']}: {len(result['moves'])} runs; evidence: {args.evidence}")
