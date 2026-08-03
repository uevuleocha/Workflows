#!/usr/bin/env python3
"""Focused deterministic verification for the Brainstorm lifecycle helper."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HELPER = Path(__file__).with_name("brainstorm_state.py")


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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="brainstorm-fixture-") as temporary:
        root = Path(temporary)
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
            )
        )
        active = Path(created["artifact_path"])
        assert created["number"] == 5
        assert active.name == "5.) Durable Brainstorm_chivita.md"
        assert active.exists()
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
        run(
            "resolve-contradiction",
            "--artifact",
            str(active),
            "--index",
            "1",
            "--disposition",
            "Superseded by per-answer checkpointing.",
        )
        run("pause", "--artifact", str(active), "--reason", "User stepped away.")
        run("checkpoint", "--artifact", str(active), "--question", "Blocked?",
            "--recommendation", "Yes.", "--answer", "Yes.",
            "--captured", "Paused blocks questions.", expect=1)
        run("resume", "--artifact", str(active))
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
        status = payload(run("status", "--artifact", str(active_again)))
        assert status["number"] == 5
        assert status["questions"] == 2
        assert status["north_star"]["status"] == "provisional"
        text = active_again.read_text(encoding="utf-8")
        assert "REOPENED" in text
        assert "Checkpoint each answer before the next question." in text

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

    print("Brainstorm lifecycle fixtures passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
