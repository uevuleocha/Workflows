"""Validate exact-model gate coverage across Workflows local masters."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = {
    "agent-chatrooms",
    "antigravity-workspace-chat-migration",
    "brainstorm",
    "claude-workspace-chat-migration",
    "codex-workspace-chat-migration",
    "debug",
    "delegate-this",
    "doc-this",
    "finalize-brainstorm",
    "finalize-delegation",
    "finalize-north-star",
    "finalize-plan",
    "finalize-prompt",
    "finalize-report",
    "finalize-session",
    "finalize-task",
    "global-skills-creator",
    "global-skills-creator-auto",
    "github-file-this",
    "github-involvement",
    "hermes-workspace-chat-migration",
    "html-this",
    "manifest-this",
    "model-chat",
    "north-star",
    "pdf-this",
    "plan-this",
    "prompt-this",
    "report-this",
    "session-summary",
    "stochastic-multi-agent-consensus",
    "subagent-verification-loops",
    "task-this",
    "terminology-this",
    "video-to-action",
    "wiki-sync",
    "wiki-this",
    "zcode-workspace-chat-migration",
}


def section(text: str) -> str | None:
    match = re.search(r"(?ms)^## Exact Model Attribution\n.*?(?=^## |\Z)", text.replace("\r\n", "\n"))
    return match.group(0).rstrip() if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, required=True)
    args = parser.parse_args()
    skills = args.workspace_root.resolve() / "Skills"
    canonical = (skills / "exact-model-confirmation-gate" / "references" / "canonical-caller-block.md").read_text(encoding="utf-8").replace("\r\n", "\n").rstrip()
    found: set[str] = set()
    failures: list[str] = []

    for path in sorted(skills.glob("*/SKILL.md")):
        current = section(path.read_text(encoding="utf-8"))
        if current is None:
            continue
        name = path.parent.name
        found.add(name)
        if current != canonical:
            failures.append(f"{name}: canonical caller block differs")
        readme = path.parent / "README.md"
        if not readme.is_file() or "exact-model-confirmation-gate" not in readme.read_text(encoding="utf-8"):
            failures.append(f"{name}: README dependency missing")

    if found != EXPECTED:
        failures.append(f"carrier set mismatch: missing={sorted(EXPECTED - found)} unexpected={sorted(found - EXPECTED)}")

    for creator in ("global-skills-creator", "global-skills-creator-auto"):
        text = (skills / creator / "SKILL.md").read_text(encoding="utf-8")
        if "## Required Exact-Model Confirmation Gate" not in text or "future carriers" not in text or "exact-model-confirmation-gate" not in text:
            failures.append(f"{creator}: future-carrier governance missing")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print(f"Validated {len(found)} canonical exact-model gate carriers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
