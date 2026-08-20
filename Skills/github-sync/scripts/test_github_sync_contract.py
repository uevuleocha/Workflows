from __future__ import annotations

from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "A direct invocation with an unambiguous scope authorizes the ordinary safe workflow end to end.",
        "If the scope is missing or genuinely ambiguous, ask for it before mutation.",
        "Immediately invoke `stage-commit-push` with the exact All or Particular scope",
        "Do not insert a preview, approval, or handoff pause between the two child skills.",
        "automatically perform eligible pointer-only hub synchronization",
        "Never bypass remote-ahead/diverged",
    ]
    for fragment in required:
        assert fragment in text, f"missing contract fragment: {fragment}"

    diff_step = text.index("Resolve the current repository through `git-diff`")
    push_step = text.index("Immediately invoke `stage-commit-push`")
    assert diff_step < push_step
    assert "Both `git-diff` and `stage-commit-push` must be installed and available." in text
    assert "allow_implicit_invocation: false" in (SKILL.parent / "agents" / "openai.yaml").read_text(encoding="utf-8")
    print("github-sync orchestration contract scenarios passed")


if __name__ == "__main__":
    main()
