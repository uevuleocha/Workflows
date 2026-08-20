#!/usr/bin/env python3
"""Regression tests for the wiki-sync coverage reconciliation helper."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reconcile_wiki_sources import _load_contract, build_inventory, reconcile


class ReconciliationFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self._temporary.name).resolve()
        (self.workspace / "Archive").mkdir()
        (self.workspace / "wiki" / "sources").mkdir(parents=True)
        self.contract_path = self.workspace / "coverage-contract.json"
        self.write_contract()

    def close(self) -> None:
        self._temporary.cleanup()

    def write_contract(self, **overrides: object) -> None:
        contract: dict[str, object] = {
            "version": 1,
            "case_sensitive_paths": True,
            "nested_workspace_markers": ["CLAUDE.md", "AGENTS.md", ".git"],
            "allowed_skip_reasons": ["schema-excluded", "user-deferred"],
            "source_roots": [
                {
                    "id": "archive",
                    "path": "Archive",
                    "identity_mode": "file",
                    "include": ["*.md", "**/*.md"],
                    "exclude": [],
                }
            ],
            "wiki": {
                "path": "wiki",
                "page_globs": ["*.md", "**/*.md"],
                "exclude": ["index.md", "log.md", "wiki-schema.md"],
                "provenance_field": "sources",
            },
        }
        contract.update(overrides)
        self.contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

    def source(self, relative: str, text: str = "source") -> Path:
        path = self.workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def page(self, name: str, sources: list[str], block: bool = False) -> Path:
        path = self.workspace / "wiki" / "sources" / name
        if block:
            source_lines = "sources:\n" + "\n".join(f"  - {item}" for item in sources)
        else:
            source_lines = "sources: " + json.dumps(sources)
        path.write_text(f"---\ntype: source\n{source_lines}\n---\n", encoding="utf-8")
        return path

    def contract(self) -> dict[str, object]:
        return _load_contract(self.workspace, self.contract_path)

    def check(
        self,
        entries: list[dict[str, object]],
        *,
        scope: str = "workspace-full",
        root_id: str | None = None,
        source_ids: list[str] | None = None,
        claim: str = "none",
        phase: str = "before",
    ) -> tuple[dict[str, object], bool]:
        return reconcile(
            self.workspace,
            self.contract(),
            {"version": 1, "entries": entries},
            scope,
            root_id,
            source_ids or [],
            claim,
            phase,
        )


class ReconcileWikiSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = ReconciliationFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    @staticmethod
    def entry(identity: str, status: str, **extra: object) -> dict[str, object]:
        return {"identity": identity, "status": status, **extra}

    def test_new_source_after_last_sync_must_be_classified(self) -> None:
        self.fixture.source("Archive/known.md")
        self.fixture.page("known.md", ["Archive/known.md"])
        self.fixture.source("Archive/new.md")
        result, failed = self.fixture.check(
            [self.entry("archive:Archive/known.md", "represented-unchanged")]
        )
        self.assertTrue(failed)
        self.assertEqual(result["omissions"], ["archive:Archive/new.md"])

    def test_complete_manifest_allows_workspace_claim(self) -> None:
        self.fixture.source("Archive/known.md")
        self.fixture.source("Archive/new.md")
        self.fixture.page("known.md", ["Archive/known.md"])
        entries = [
            self.entry("archive:Archive/known.md", "represented-unchanged"),
            self.entry("archive:Archive/new.md", "new"),
        ]
        self.fixture.page("new.md", ["Archive/new.md"])
        result, failed = self.fixture.check(
            entries,
            claim="workspace-synced",
            phase="after",
        )
        self.assertFalse(failed)
        self.assertTrue(result["coverage_complete"])
        self.assertTrue(result["claim_allowed"])

    def test_renamed_source_explains_stale_provenance(self) -> None:
        self.fixture.source("Archive/new-name.md")
        self.fixture.page("old.md", ["Archive/old-name.md"])
        entry = self.entry(
            "archive:Archive/new-name.md",
            "changed",
            previous_paths=["Archive/old-name.md"],
        )
        result, failed = self.fixture.check([entry])
        self.assertFalse(failed)
        self.assertEqual(result["explained_stale_provenance"], ["Archive/old-name.md"])

    def test_after_phase_requires_renamed_provenance_to_be_repaired(self) -> None:
        self.fixture.source("Archive/new-name.md")
        self.fixture.page("old.md", ["Archive/old-name.md"])
        entry = self.entry(
            "archive:Archive/new-name.md",
            "changed",
            previous_paths=["Archive/old-name.md"],
        )
        result, failed = self.fixture.check([entry], phase="after")
        self.assertTrue(failed)
        self.assertEqual(result["unrepaired_stale_provenance"], ["Archive/old-name.md"])
        self.fixture.page("old.md", ["Archive/new-name.md"])
        repaired, repaired_failed = self.fixture.check(
            [entry],
            phase="after",
            claim="workspace-synced",
        )
        self.assertFalse(repaired_failed)
        self.assertEqual(repaired["unrepaired_stale_provenance"], [])

    def test_unexplained_stale_provenance_fails(self) -> None:
        self.fixture.source("Archive/new-name.md")
        self.fixture.page("old.md", ["Archive/old-name.md"])
        result, failed = self.fixture.check(
            [self.entry("archive:Archive/new-name.md", "new")]
        )
        self.assertTrue(failed)
        self.assertEqual(result["unexplained_stale_provenance"], ["Archive/old-name.md"])

    def test_unreliable_timestamps_are_disclosed_as_uncertain(self) -> None:
        source = self.fixture.source("Archive/uncertain.md")
        self.fixture.page("uncertain.md", ["Archive/uncertain.md"])
        os.utime(source, (1, 1))
        entries = [self.entry("archive:Archive/uncertain.md", "uncertain")]
        result, failed = self.fixture.check(entries)
        self.assertFalse(failed)
        self.assertEqual(result["uncertain"], ["archive:Archive/uncertain.md"])
        claimed, claim_failed = self.fixture.check(entries, claim="workspace-synced")
        self.assertTrue(claim_failed)
        self.assertFalse(claimed["claim_allowed"])

    def test_nested_workspace_is_pruned_case_sensitively(self) -> None:
        self.fixture.source("Archive/in-scope.md")
        self.fixture.source("Archive/nested/CLAUDE.md")
        self.fixture.source("Archive/nested/hidden.md")
        self.fixture.source("Archive/lower/claude.md")
        inventory = build_inventory(self.fixture.workspace, self.fixture.contract())
        identities = {item["identity"] for item in inventory["eligible"]}
        self.assertIn("archive:Archive/in-scope.md", identities)
        self.assertIn("archive:Archive/lower/claude.md", identities)
        self.assertNotIn("archive:Archive/nested/hidden.md", identities)

    def test_historical_source_provenance_is_not_special_cased(self) -> None:
        identity = "archive:Archive/Historical/Summaries/1.) Session.md"
        self.fixture.source("Archive/Historical/Summaries/1.) Session.md")
        self.fixture.page(
            "session-history.md",
            ["Archive/Historical/Summaries/1.) Session.md"],
            block=True,
        )
        result, failed = self.fixture.check(
            [self.entry(identity, "represented-unchanged")]
        )
        self.assertFalse(failed)
        self.assertEqual(result["status_counts"]["represented-unchanged"], 1)

    def test_manually_truncated_manifest_fails(self) -> None:
        for name in ("one.md", "two.md", "three.md"):
            self.fixture.source(f"Archive/{name}")
        entries = [
            self.entry("archive:Archive/one.md", "new"),
            self.entry("archive:Archive/two.md", "new"),
        ]
        result, failed = self.fixture.check(entries)
        self.assertTrue(failed)
        self.assertEqual(result["omissions"], ["archive:Archive/three.md"])

    def test_named_source_cannot_claim_workspace_sync(self) -> None:
        self.fixture.source("Archive/one.md")
        self.fixture.page("one.md", ["Archive/one.md"])
        identity = "archive:Archive/one.md"
        result, failed = self.fixture.check(
            [self.entry(identity, "new")],
            scope="named-source",
            source_ids=[identity],
            claim="workspace-synced",
            phase="after",
        )
        self.assertTrue(failed)
        self.assertIn("workspace-synced claim requires workspace-full scope", result["claim_errors"])

    def test_named_source_can_make_only_scoped_claim(self) -> None:
        self.fixture.source("Archive/one.md")
        self.fixture.source("Archive/two.md")
        self.fixture.page("one.md", ["Archive/one.md"])
        identity = "archive:Archive/one.md"
        result, failed = self.fixture.check(
            [self.entry(identity, "new")],
            scope="named-source",
            source_ids=[identity],
            claim="scoped-synced",
            phase="after",
        )
        self.assertFalse(failed)
        self.assertTrue(result["claim_allowed"])

    def test_immediate_directory_identity_models_semantic_bundle(self) -> None:
        (self.fixture.workspace / "Skills").mkdir()
        self.fixture.source("Skills/wiki-sync/SKILL.md")
        self.fixture.source("Skills/wiki-sync/README.md")
        self.fixture.write_contract(
            source_roots=[
                {
                    "id": "skills",
                    "path": "Skills",
                    "identity_mode": "immediate-directory",
                    "include": ["*"],
                    "exclude": [],
                }
            ]
        )
        self.fixture.page("wiki-sync.md", ["Skills/wiki-sync/SKILL.md"])
        inventory = build_inventory(self.fixture.workspace, self.fixture.contract())
        self.assertEqual(len(inventory["eligible"]), 1)
        self.assertIn("skills:Skills/wiki-sync", inventory["represented"])

    def test_source_added_between_manifest_build_and_check_is_caught(self) -> None:
        self.fixture.source("Archive/first.md")
        manifest = [self.entry("archive:Archive/first.md", "new")]
        self.fixture.source("Archive/appeared-during-run.md")
        result, failed = self.fixture.check(manifest)
        self.assertTrue(failed)
        self.assertEqual(result["omissions"], ["archive:Archive/appeared-during-run.md"])

    def test_skipped_identity_requires_schema_supported_reason(self) -> None:
        self.fixture.source("Archive/deferred.md")
        valid = self.entry(
            "archive:Archive/deferred.md",
            "skipped",
            skip_reason="user-deferred",
        )
        result, failed = self.fixture.check([valid])
        self.assertFalse(failed)
        self.assertEqual(result["skipped"], ["archive:Archive/deferred.md"])
        invalid = dict(valid, skip_reason="invented-reason")
        invalid_result, invalid_failed = self.fixture.check([invalid])
        self.assertTrue(invalid_failed)
        self.assertTrue(any("invalid or missing skip_reason" in item for item in invalid_result["errors"]))

    def test_root_full_ignores_stale_provenance_in_another_root(self) -> None:
        (self.fixture.workspace / "Notes").mkdir()
        self.fixture.source("Archive/current.md")
        self.fixture.write_contract(
            source_roots=[
                {
                    "id": "archive",
                    "path": "Archive",
                    "identity_mode": "file",
                    "include": ["*.md", "**/*.md"],
                    "exclude": [],
                },
                {
                    "id": "notes",
                    "path": "Notes",
                    "identity_mode": "file",
                    "include": ["*.md", "**/*.md"],
                    "exclude": [],
                },
            ]
        )
        self.fixture.page("mixed.md", ["Archive/current.md", "Notes/missing.md"])
        result, failed = self.fixture.check(
            [self.entry("archive:Archive/current.md", "represented-unchanged")],
            scope="root-full",
            root_id="archive",
        )
        self.assertFalse(failed)
        self.assertEqual(result["out_of_scope_stale_provenance"], ["Notes/missing.md"])

    def test_cli_exit_codes_distinguish_findings_and_operational_failure(self) -> None:
        self.fixture.source("Archive/unclassified.md")
        manifest_path = self.fixture.workspace / "manifest.json"
        manifest_path.write_text(
            json.dumps({"version": 1, "entries": []}),
            encoding="utf-8",
        )
        script = Path(__file__).with_name("reconcile_wiki_sources.py")
        finding = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(script),
                "check",
                "--workspace",
                str(self.fixture.workspace),
                "--contract",
                str(self.fixture.contract_path),
                "--manifest",
                str(manifest_path),
                "--scope",
                "workspace-full",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(finding.returncode, 1)
        self.assertEqual(json.loads(finding.stdout)["omissions"], ["archive:Archive/unclassified.md"])
        self.assertEqual(finding.stderr, "")
        broken_contract = self.fixture.workspace / "broken-contract.json"
        broken_contract.write_text('{"version": 99}', encoding="utf-8")
        operational = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(script),
                "inventory",
                "--workspace",
                str(self.fixture.workspace),
                "--contract",
                str(broken_contract),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(operational.returncode, 2)
        self.assertEqual(operational.stdout, "")
        self.assertIn("operational_error", json.loads(operational.stderr))


if __name__ == "__main__":
    unittest.main()
