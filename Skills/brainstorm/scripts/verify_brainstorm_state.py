#!/usr/bin/env python3
"""Focused deterministic verification for the Brainstorm lifecycle helper."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True


HELPER = Path(__file__).with_name("brainstorm_state.py")
WORKSPACE_ROOT = HELPER.parents[3]
FIXTURE_PARENT = WORKSPACE_ROOT / "tmp"
STATE_RE = re.compile(
    r"<!-- BRAINSTORM_STATE_START\n(?P<json>.*?)\nBRAINSTORM_STATE_END -->",
    re.DOTALL,
)


def run(*arguments: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(HELPER), *arguments],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"Expected exit {expect}, got {result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def payload(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def state_from(path: Path) -> dict:
    match = STATE_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        raise AssertionError(f"Missing state block: {path}")
    return json.loads(match.group("json"))


def change_count(path: Path) -> int:
    return len(state_from(path)["change_log"])


def assert_fresh_change_log(path: Path) -> None:
    now = datetime.now()
    for row in state_from(path)["change_log"]:
        timestamp = datetime.strptime(row["at"], "%Y-%m-%d-%H:%M:%S")
        assert abs((now - timestamp).total_seconds()) < 60


def v1_state_from(path: Path) -> dict:
    state = state_from(path)
    state["version"] = 1
    for key in ("provenance", "feedback", "change_log", "preserved_sections"):
        state.pop(key, None)
    return state


def write_v1(path: Path, state: dict, visible: str) -> None:
    path.write_text(
        visible.rstrip()
        + "\n\n<!-- BRAINSTORM_STATE_START\n"
        + json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True)
        + "\nBRAINSTORM_STATE_END -->\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    FIXTURE_PARENT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="brainstorm-fixture-", dir=FIXTURE_PARENT
    ) as temporary:
        root = Path(temporary)
        print(f"fixture_workspace={root}")
        historical = root / "Archive" / "Historical" / "Brainstorms" / "Skills"
        historical.mkdir(parents=True)
        (historical / "4.) Existing_fini.md").write_text(
            "fixture", encoding="utf-8"
        )

        created = payload(
            run(
                "create",
                "--workspace-root",
                str(root),
                "--subject",
                "Skills",
                "--topic",
                "Durable Brainstorm",
                "--working-direction",
                "Explore a reliable interview workflow.",
                "--agent",
                "Codex Agent",
                "--model",
                "GPT-5.6 Sol",
            )
        )
        active = Path(created["artifact_path"])
        assert created["number"] == 5
        assert active.name == "5.) Durable Brainstorm_chivita.md"
        assert active.exists()
        assert change_count(active) == 1
        created_text = active.read_text(encoding="utf-8")
        provenance_at = created_text.index("## Agent Provenance")
        working_at = created_text.index("## Working Direction")
        feedback_at = created_text.index("## Feedback Section")
        change_log_at = created_text.index("## Agent Change Log")
        trailer_at = created_text.index("<!-- BRAINSTORM_STATE_START")
        assert provenance_at < working_at
        assert feedback_at < change_log_at < trailer_at
        assert not created_text[feedback_at + len("## Feedback Section"):change_log_at].strip()
        run(
            "create",
            "--workspace-root",
            str(root),
            "--subject",
            "Skills",
            "--topic",
            "Durable Brainstorm",
            expect=1,
        )

        checkpoint = payload(
            run(
                "checkpoint",
                "--artifact",
                str(active),
                "--topic",
                "Capture order",
                "--question",
                "What must happen before Q2?",
                "--recommendation",
                "Persist Q1.",
                "--answer",
                "Persist every answer first.",
                "--captured",
                "Q1 must be durable before Q2.",
                "--summary",
                "Durable checkpointing is mandatory.",
                "--decision",
                "Checkpoint each answer before the next question.",
                "--flag",
                "Confirm stakeholder wording::Uzo",
                "--contradiction",
                "Earlier draft allowed batched questions.",
                "--coverage",
                "Checkpoint cadence",
            )
        )
        assert checkpoint["checkpointed_q"] == 1
        assert change_count(active) == 2
        status = payload(run("status", "--artifact", str(active)))
        assert status["questions"] == 1
        assert status["open_flags"] == ["F1"]
        assert status["unresolved_contradictions"] == [1]

        run(
            "set-ready",
            "--artifact",
            str(active),
            "--north-star",
            "Create a durable Brainstorm.",
            "--user-accepted",
            expect=1,
        )
        assert change_count(active) == 2
        feedback = payload(
            run(
                "feedback",
                "--artifact",
                str(active),
                "--agent",
                "Verifier Agent",
                "--model",
                "GPT-5.6 Sol",
                "--descriptor",
                "Regression evidence",
                "--body",
                "Preserve this finding through later mutations.",
            )
        )
        assert feedback["feedback"] == 1
        assert change_count(active) == 3
        run(
            "resolve-flag",
            "--artifact",
            str(active),
            "--flag-id",
            "F1",
            "--status",
            "deferred",
            "--disposition",
            "Owner will confirm later; accepted as non-blocking.",
        )
        assert change_count(active) == 4
        run(
            "resolve-contradiction",
            "--artifact",
            str(active),
            "--index",
            "1",
            "--disposition",
            "Superseded by per-answer checkpointing.",
        )
        assert change_count(active) == 5
        run("pause", "--artifact", str(active), "--reason", "User stepped away.")
        assert change_count(active) == 6
        assert "Preserve this finding" in active.read_text(encoding="utf-8")
        run("checkpoint", "--artifact", str(active), "--question", "Blocked?",
            "--recommendation", "Yes.", "--answer", "Yes.",
            "--captured", "Paused blocks questions.", expect=1)
        assert change_count(active) == 6
        run("resume", "--artifact", str(active))
        assert change_count(active) == 7
        run(
            "checkpoint",
            "--artifact",
            str(active),
            "--topic",
            "Correction history",
            "--question",
            "Should the earlier batch rule survive?",
            "--recommendation",
            "No; preserve it only as superseded history.",
            "--answer",
            "Correct. Keep the trail, not the old rule.",
            "--captured",
            "The earlier rule is superseded but remains visible.",
            "--summary",
            "Per-answer persistence replaced the earlier batch rule.",
            "--decision",
            "Preserve corrected decisions as history.",
            "--coverage",
            "Correction handling",
        )
        assert change_count(active) == 8
        assert "Preserve this finding" in active.read_text(encoding="utf-8")
        corrected = payload(run("status", "--artifact", str(active)))
        assert corrected["questions"] == 2
        run(
            "set-ready",
            "--artifact",
            str(active),
            "--north-star",
            "Make every Brainstorm durable, personal, and implementation-ready.",
            "--user-accepted",
        )
        assert change_count(active) == 9

        collision = historical / "5.) Durable Brainstorm_fini.md"
        collision.write_text("collision", encoding="utf-8")
        run(
            "finalize",
            "--artifact",
            str(active),
            "--acceptance",
            "User accepted the North Star.",
            expect=1,
        )
        assert change_count(active) == 9
        collision.unlink()
        finalized = payload(
            run(
                "finalize",
                "--artifact",
                str(active),
                "--acceptance",
                "User accepted the North Star.",
            )
        )
        fini = Path(finalized["artifact_path"])
        assert fini.name == "5.) Durable Brainstorm_fini.md"
        assert fini.exists() and not active.exists()
        assert change_count(fini) == 10

        reopened = payload(
            run(
                "reopen",
                "--artifact",
                str(fini),
                "--reason",
                "A later breakthrough changed the design.",
            )
        )
        active_again = Path(reopened["artifact_path"])
        assert active_again.name == "5.) Durable Brainstorm_chivita.md"
        assert change_count(active_again) == 11
        status = payload(run("status", "--artifact", str(active_again)))
        assert status["number"] == 5
        assert status["questions"] == 2
        assert status["north_star"]["status"] == "provisional"
        text = active_again.read_text(encoding="utf-8")
        assert "REOPENED" in text
        assert "Checkpoint each answer before the next question." in text
        assert_fresh_change_log(active_again)

        second = payload(
            run(
                "create",
                "--workspace-root",
                str(root),
                "--subject",
                "Skills",
                "--topic",
                "Second Brainstorm",
            )
        )
        assert second["number"] == 6

        plain_v1 = root / "plain-v1.md"
        plain_state = v1_state_from(active_again)
        write_v1(
            plain_v1,
            plain_state,
            "# Plain v1: Brainstorm\n\nStatus: CHIVITA",
        )
        sys.path.insert(0, str(HELPER.parent))
        import brainstorm_state  # pylint: disable=import-outside-toplevel

        unattributed = brainstorm_state.read_state(plain_v1)
        assert unattributed["provenance"]["Original writing agent"] == "Not recorded"
        assert unattributed["provenance"]["Original writing LLM"] == "Not recorded"
        assert unattributed["change_log"][0]["agent"] == "Not recorded"
        assert unattributed["change_log"][0]["model"] == "Not recorded"
        migrated = brainstorm_state.read_state(
            plain_v1, "Codex Agent", "GPT-5.6 Sol"
        )
        assert migrated["version"] == 2
        assert migrated["feedback"] == []
        assert len(migrated["change_log"]) == 1
        assert migrated["change_log"][0]["action"] == "Migrated"
        assert migrated["provenance"]["Original writing agent"] == "Codex Agent"
        assert migrated["provenance"]["Original writing LLM"] == "GPT-5.6 Sol"

        repaired_v1 = root / "hand-repaired-v1.md"
        repaired_state = v1_state_from(active_again)
        write_v1(
            repaired_v1,
            repaired_state,
            """# Hand repaired v1: Brainstorm

Status: CHIVITA

## Agent Provenance

| Field                  | Value                    |
| ---------------------- | ------------------------ |
| Content owner          | Uzo                      |
| Original writing agent | Claude Agent             |
| Original writing LLM   | Claude Opus 5            |
| Created                | 2026-08-21               |
| Artifact role          | Existing capture         |

## Final Roster

- Preserve this unmodelled section.

## Feedback Section

### Feedback 7 - 2026-08-21 - Verifier Agent - Existing finding

This hand-added feedback must survive migration.

## Agent Change Log

| Date and Time       | Agent        | Model         | Action   | Scope          |
| ------------------- | ------------ | ------------- | -------- | -------------- |
| 2026-08-21-22:00:00 | Claude Agent | Claude Opus 5 | Repaired | Added sections |
""",
        )
        repaired = brainstorm_state.read_state(
            repaired_v1, "Codex Agent", "GPT-5.6 Sol"
        )
        assert repaired["version"] == 2
        assert repaired["provenance"]["Original writing agent"] == "Claude Agent"
        assert len(repaired["change_log"]) == 2
        assert repaired["change_log"][0]["action"] == "Repaired"
        assert repaired["change_log"][1]["action"] == "Migrated"
        assert any("## Final Roster" in item for item in repaired["preserved_sections"])
        added = payload(
            run(
                "feedback",
                "--artifact",
                str(repaired_v1),
                "--agent",
                "Codex Agent",
                "--model",
                "GPT-5.6 Sol",
                "--descriptor",
                "Migration response",
                "--body",
                "Feedback numbering and history remain append-only.",
            )
        )
        assert added["feedback"] == 8
        assert len(state_from(repaired_v1)["change_log"]) == 3
        run(
            "checkpoint",
            "--artifact",
            str(repaired_v1),
            "--question",
            "Does migration preserve hand repairs?",
            "--recommendation",
            "Yes.",
            "--answer",
            "Yes.",
            "--captured",
            "Hand-added content survives.",
            "--agent",
            "Codex Agent",
            "--model",
            "GPT-5.6 Sol",
        )
        repaired_text = repaired_v1.read_text(encoding="utf-8")
        assert "## Final Roster" in repaired_text
        assert "This hand-added feedback must survive migration." in repaired_text
        assert "### Feedback 8 " in repaired_text
        assert "| 2026-08-21-22:00:00 " in repaired_text
        assert state_from(repaired_v1)["version"] == 2
        assert len(state_from(repaired_v1)["change_log"]) == 4

    print("regression=feedback_survives_three_mutations_and_checkpoint")
    print("Brainstorm lifecycle and schema-v2 fixtures passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
