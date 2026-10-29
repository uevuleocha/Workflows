"""No-API behavioral checks for subjects, pointers, and Legacy migration."""
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import subject_outputs as outputs
from migrate_legacy import migrate
import video_to_action as video


class SubjectTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / 'tmp'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'AGENTS.md').write_text('Fixture workspace', encoding='utf-8')

    def test_lock_location_and_idle_recreation(self):
        data = self.payload('A')
        outputs.publish_pointers(self.root, 'A', data)
        lock = outputs.pointer_lock_path(self.root)
        self.assertEqual(lock.parent, self.root / 'tmp/video-to-action-locks')
        self.assertTrue(lock.is_file())
        self.assertFalse((self.root / '.latest.lock').exists())
        before = (self.root / 'latest.json').read_bytes()
        lock.unlink()  # No writer holds it: same action as idle temporary cleanup.
        lock.parent.rmdir()
        self.assertFalse(outputs.repair_pointers(self.root))
        self.assertTrue(lock.is_file())
        self.assertEqual(before, (self.root / 'latest.json').read_bytes())
        self.assertEqual(lock, outputs.pointer_lock_path(self.root / '.'))
        self.assertNotEqual(lock, outputs.pointer_lock_path(self.root / 'other-output'))

    def test_nearest_workspace_owns_lock(self):
        child = self.root / 'nested'
        child.mkdir()
        (child / 'CLAUDE.md').write_text('Child workspace', encoding='utf-8')
        archive = child / 'Archive/Historical/Video-to-action'
        self.assertEqual(outputs.pointer_lock_path(archive).parent,
                         child / 'tmp/video-to-action-locks')

    def payload(self, subject, name='run', completed=True):
        run = self.root / subject / name
        run.mkdir(parents=True)
        return dict(run_dir=str(run), latest_run=name, completed=completed)

    def test_paths(self):
        for name in ('', ' ', '../escape', 'A/B', 'A\\B', 'C:evil', '.', '..',
                     'CON', 'con.txt', 'LPT9', 'COM¹', 'trailing.', 'trail ', ' tab', 'a\n', 'x' * 101):
            with self.subTest(name=name), self.assertRaises(ValueError):
                outputs.subject_path(self.root, name)
        (self.root / 'Knowledge').mkdir()
        self.assertEqual(outputs.subject_path(self.root, 'knowledge').name, 'Knowledge')
        (self.root / 'file').write_text('x')
        with self.assertRaises(ValueError):
            outputs.subject_path(self.root, 'file')
        # Resolve containment independently of whether this Windows account can create links.
        original = Path.resolve
        with patch.object(Path, 'resolve', lambda p: self.root.parent / 'escape' if p.name == 'Escape' else original(p)):
            with self.assertRaises(ValueError):
                outputs.subject_path(self.root, 'Escape')

    def test_pointer_subject_isolation_and_failure_status(self):
        a = self.payload('A')
        outputs.publish_pointers(self.root, 'A', a)
        saved = (self.root / 'A/latest.json').read_bytes()
        b = self.payload('B', completed=False)
        outputs.publish_pointers(self.root, 'B', b)
        self.assertEqual((self.root / 'A/latest.json').read_bytes(), saved)
        latest = json.loads((self.root / 'latest.json').read_text())
        self.assertEqual(latest['subject'], 'B')
        self.assertFalse(latest['completed'])
        self.assertEqual(latest, json.loads((self.root / 'B/latest.json').read_text()))

    def test_interrupted_transaction_recovery(self):
        data = self.payload('A')
        original = outputs.atomic_json
        def fail_root(path, payload):
            if path == self.root / 'latest.json':
                raise OSError('fixture failure')
            return original(path, payload)
        with patch.object(outputs, 'atomic_json', fail_root), self.assertRaises(OSError):
            outputs.publish_pointers(self.root, 'A', data)
        self.assertTrue((self.root / '.latest-pending.json').exists())
        self.assertTrue(outputs.repair_pointers(self.root))
        self.assertFalse(outputs.repair_pointers(self.root))
        self.assertTrue(Path(json.loads((self.root / 'latest.json').read_text())['run_dir']).is_dir())

    def test_concurrent_writers(self):
        entries = [(f'S{i}', self.payload(f'S{i}')) for i in range(6)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda entry: outputs.publish_pointers(self.root, *entry), entries))
        root = json.loads((self.root / 'latest.json').read_text())
        self.assertEqual(root, json.loads((self.root / root['subject'] / 'latest.json').read_text()))
        for subject, data in entries:
            self.assertEqual(json.loads((self.root / subject / 'latest.json').read_text())['run_dir'], data['run_dir'])

    def test_cli_requires_subject_without_api(self):
        helper = Path(video.__file__)
        result = subprocess.run([sys.executable, str(helper), 'https://youtu.be/abcdefghijk',
                                 '--title', 'Fixture', '--duration', '01:00'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('subject (--subject)', result.stderr)

    def test_saved_run_status_and_relative_custom_root(self):
        root = self.root.relative_to(Path.cwd()) / 'custom'
        policy = video.resolve_model_policy('free', video.DEFAULT_MODEL, video.DEFAULT_FALLBACK_MODEL)
        effective = video.build_effective_prompts(video.selected_phase_defs(False, False, False), 'Test', '01:00')
        transcript = {'status': 'failed', 'video_id': 'abcdefghijk',
                      'reason': 'offline fixture', 'snippets': []}
        for index, results in enumerate(({}, {'procedure': 'fixture result'})):
            report = video.save_outputs(root, 'Test', '01:00', 'https://youtu.be/abcdefghijk',
                'summarize', policy, effective, results, [], [], {}, transcript,
                'default', 'full video', run_ts=f'20000101-00000{index}', subject='Testing')
            pointer = json.loads((root / 'latest.json').read_text())
            self.assertEqual(pointer['completed'], bool(results))
            self.assertFalse(Path(pointer['run_dir']).is_absolute())
            self.assertEqual(Path(pointer['run_dir']).resolve(), report.parent.resolve())
            self.assertEqual(report.parent.parent.name, 'Testing')
            self.assertEqual(set(p.name for p in report.parent.iterdir()), {'report.md', 'prompts.md', 'transcript.md'})

    def test_invalid_subject_precedes_client_creation(self):
        with self.assertRaises(ValueError):
            video.run_extraction('url', 'summarize', video.DEFAULT_MODEL, video.DEFAULT_FALLBACK_MODEL,
                'free', None, None, False, self.root, 'Title', '01:00', False, False, False, '../escape')

    def test_migration_preserves_bytes_and_reruns(self):
        root = self.root / 'Archive/Historical/Video-to-action'
        run = root / '20000101-000000 - Fixture'
        run.mkdir(parents=True)
        (run / 'procedure.md').write_bytes(b'historical bytes\r\n')
        original = {'run_dir': str(run.relative_to(self.root)), 'latest_run': '20000101-000000',
                    'completed': True, 'primary_model': 'old-model', 'timestamp': 'old-time'}
        outputs.atomic_json(root / 'latest.json', original)
        evidence = self.root / 'migration.json'
        migrate(self.root, evidence)
        result = migrate(self.root, evidence, True)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual((root / 'Legacy' / run.name / 'procedure.md').read_bytes(), b'historical bytes\r\n')
        pointer = json.loads((root / 'latest.json').read_text())
        self.assertEqual(pointer['primary_model'], 'old-model')
        self.assertEqual(pointer['timestamp'], 'old-time')
        self.assertEqual(pointer, json.loads((root / 'Legacy/latest.json').read_text()))
        self.assertEqual(migrate(self.root, evidence, True), result)

    def test_empty_pointer_and_collision(self):
        root = self.root / 'Archive/Historical/Video-to-action'
        root.mkdir(parents=True)
        (root / 'latest.json').write_bytes(b'')
        result = migrate(self.root, self.root / 'evidence.json', True)
        self.assertIsNone(result['pointer_after']['run_dir'])
        self.assertFalse((root / 'Legacy/latest.json').exists())
        for prefix in (root, root / 'Legacy'):
            (prefix / '20000101-000000 - Collision').mkdir(parents=True)
        with self.assertRaises(ValueError):
            migrate(self.root, self.root / 'collision.json', True)

    def test_migration_rejects_concurrent_edit(self):
        root = self.root / 'Archive/Historical/Video-to-action'
        run = root / '20000101-000000 - Test'
        run.mkdir(parents=True)
        artifact = run / 'procedure.md'
        artifact.write_text('before')
        evidence = self.root / 'evidence.json'
        migrate(self.root, evidence)
        artifact.write_text('after')
        with self.assertRaises(ValueError):
            migrate(self.root, evidence, True)
        self.assertTrue(run.is_dir())


if __name__ == '__main__':
    unittest.main()
