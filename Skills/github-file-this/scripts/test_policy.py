from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
TEMPLATES = (ROOT / "references" / "issue-and-review-templates.md").read_text(
    encoding="utf-8"
)
CANONICAL = (
    ROOT.parent
    / "exact-model-confirmation-gate"
    / "references"
    / "canonical-caller-block.md"
)


def require(text: str, needle: str, label: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"missing {label}: {needle!r}")


def main() -> int:
    failures: list[str] = []

    ordered = [f"### {number}." for number in range(1, 11)]
    positions = [SKILL.find(marker) for marker in ordered]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        failures.append("the ten workflow stages are missing or out of order")

    required_skill_tokens = {
        "preflight auth": "gh auth status",
        "issues enabled": "hasIssuesEnabled",
        "all issue states": "--state all",
        "title and body search": "in:title,body",
        "new issue body file": "gh issue create --repo OWNER/REPO",
        "issue body-file flag": "--body-file",
        "OG comment command": "gh issue comment NUMBER",
        "duplicate branch": "Duplicate-Found Stop",
        "type-first rule": "Classify by type",
        "age-second rule": "Choose by age",
        "triage comments": "Explicit triage comments",
        "cross-reference density": "Cross-reference density",
        "title grammar": "Title grammar",
        "label sets": "Label sets",
        "linked pull requests": "Linked pull requests",
        "ordinary earliest rule": "choose the earliest-created report without asking",
        "narrow conflict": "maintainers visibly consolidated",
        "explicit review": "Stop For Explicit Review",
        "no pre-approval body file": "Do not write a body file yet",
        "approval binds exact text": "Approval is bound to the exact displayed title",
        "ambiguous approval excluded": "Ambiguous enthusiasm or action language",
        "redaction": "Redact Before Publishing",
        "redaction re-review": "return to stage 5 for approval of the redacted version",
        "report handoff": "invoke `report-this`",
        "finalize handoff": "invoke `finalize-report`",
        "same-pass exception": "Public Outcome Same-Pass Finalization Exception",
        "credential safety": "invoke `tread-lightly`",
        "partial success": "partial multi-item success",
        "actual command URL": "returned URL directly from successful `gh` stdout",
        "no URL reconstruction": "never reconstruct one",
        "per-item state": "Maintain a separate state for each involvement",
        "only OG receives comment": "Only the OG Bug Report may receive",
        "comment approval is separate": "Approval of the new-issue draft does not approve",
        "fix ticket rationale": "A fix ticket is never the evidence destination",
        "no report on no action": "create no outcome report because no public action occurred",
        "no report on failure": "Never finalize a report for a failed or unperformed public action",
        "supersedes": "supersedes `github-issue-this`",
        "recording stage": "Record In The Involvements Document",
        "involvements document": "GitHub Involvements document",
        "pull request scope": "gh pr create",
        "discussion scope": "Discussion",
        "tracking scope": "Tracking (Passive Involvement)",
        "active marker": "`active`",
        "passive marker": "`passive`",
        "done read-only": "never touches Done",
        "full markdown link": "bare `#NNNN`",
    }
    for label, needle in required_skill_tokens.items():
        require(SKILL, needle, label, failures)

    required_template_tokens = {
        "matches": "### Matches found",
        "named OG": "### OG Bug Report",
        "new issue draft": "### New-issue draft",
        "comment draft": "### OG comment draft",
        "file choice": "`file it anyway`",
        "comment choice": "`post the comment`",
        "multi-repository review": "## Multi-Repository Review",
        "post-nothing recommendation": "I recommend posting nothing.",
        "unchanged draft": "[Exact, unchanged issue title and body]",
        "single-reply branch": "answerable in one reply",
    }
    for label, needle in required_template_tokens.items():
        require(TEMPLATES, needle, label, failures)

    require(README, "exact-model-confirmation-gate", "README model gate", failures)
    require(README, "report-this", "README report dependency", failures)
    require(README, "finalize-report", "README finalizer dependency", failures)
    require(README, "tread-lightly", "README redaction dependency", failures)
    require(README, "github-involvement", "README paired-skill dependency", failures)

    if not CANONICAL.is_file():
        failures.append(f"canonical model block is unavailable: {CANONICAL}")
    else:
        canonical = CANONICAL.read_text(encoding="utf-8").strip()
        if canonical not in SKILL:
            failures.append("Exact Model Attribution block is not byte-identical")

    forbidden = [
        "gh issue create --body ",
        "gh issue comment NUMBER --repo OWNER/REPO --body ",
    ]
    for token in forbidden:
        if token in SKILL:
            failures.append(f"unsafe inline publication form present: {token!r}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("github-file-this policy validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
