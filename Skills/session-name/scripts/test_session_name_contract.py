"""Deterministic contract checks for the session-name skill."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
OPENAI_YAML = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
FINALIZE_SESSION = (ROOT.parent / "finalize-session" / "SKILL.md").read_text(encoding="utf-8")


def require(text: str, needle: str, source: str) -> None:
    if needle not in text:
        raise AssertionError(f"{source} is missing required contract text: {needle!r}")


def reject(text: str, needle: str, source: str) -> None:
    if needle.lower() in text.lower():
        raise AssertionError(f"{source} still carries legacy contract text: {needle!r}")


def measured_length(label: str, prefix: str, host: str) -> int:
    full = f"{prefix}{label}"
    if host in {"antigravity", "hermes"}:
        return len(full)
    if host == "general":
        return len(label)
    raise ValueError(f"unknown host: {host}")


def fits(label: str, prefix: str, host: str) -> bool:
    caps = {"antigravity": 70, "hermes": 100, "general": 240}
    return measured_length(label, prefix, host) <= caps[host]


def check_contract_text() -> None:
    required_skill = [
        "Build the session fact map",
        "Resolve the narrative center",
        "Draft exactly eight names directly",
        "Do not draft a larger candidate pool",
        "Rank the strongest overall representation first",
        "Do not default to an opening shaped as `From X to Y`",
        "Subject plus meaning",
        "Earned detail",
        "Antigravity/Gemini: 70 characters including any optional prefix",
        "Hermes: 100 characters including any optional prefix",
        "Claude/Codex/zCode: 240 characters by default, excluding any optional prefix",
    ]
    for needle in required_skill:
        require(SKILL, needle, "SKILL.md")

    for legacy in [
        "foundation set",
        "adaptive syntheses",
        "**Outcome-led**",
        "**Artifact/Tool-led**",
        "**Method-led**",
        "**Headline Result-led**",
        "From Prompt 13",
    ]:
        reject(SKILL, legacy, "SKILL.md")

    require(README, "exactly eight directly generated", "README.md")
    require(README, "narrative center", "README.md")
    require(README, "hidden candidate pools", "README.md")
    require(OPENAI_YAML, "exactly eight directly generated", "openai.yaml")
    require(OPENAI_YAML, "no hidden candidate pool or fixed option slots", "openai.yaml")
    reject(FINALIZE_SESSION, "foundation/synthesis naming algorithm", "finalize-session/SKILL.md")
    require(FINALIZE_SESSION, "direct context-rich eight-option naming algorithm", "finalize-session/SKILL.md")

    output_numbers = re.findall(r"^([1-8])\. \[materially distinct grounded name\]$", SKILL, re.MULTILINE)
    if output_numbers != ["2", "3", "4", "5", "6", "7", "8"]:
        raise AssertionError("Output Shape must contain one best option plus options 2 through 8")


def check_cap_accounting() -> None:
    prefix = "48.) "

    exact_antigravity = "A" * (70 - len(prefix))
    exact_hermes = "H" * (100 - len(prefix))
    exact_general = "G" * 240

    assert fits(exact_antigravity, prefix, "antigravity")
    assert not fits(exact_antigravity + "A", prefix, "antigravity")
    assert fits(exact_hermes, prefix, "hermes")
    assert not fits(exact_hermes + "H", prefix, "hermes")
    assert fits(exact_general, prefix, "general")
    assert not fits(exact_general + "G", prefix, "general")

    if measured_length(exact_general, prefix, "general") != 240:
        raise AssertionError("General-host accounting must exclude the optional prefix")
    if measured_length(exact_antigravity, prefix, "antigravity") != 70:
        raise AssertionError("Antigravity accounting must include the optional prefix")
    if measured_length(exact_hermes, prefix, "hermes") != 100:
        raise AssertionError("Hermes accounting must include the optional prefix")

    representative = {
        "antigravity": [
            "Autonomous GitHub Sync Proven Across Two zCode Workspaces",
            "GitHub Sync Ends Approval Churn Without Weakening Safety",
            "Exact Particular Scope with Automatic Hub-Pointer Sync",
            "Diff, Commit, Push, and Hub Sync Run as One Safe Workflow",
            "Five-Harness GitHub Sync Shipped with Verified Parity",
            "Disposable Git Tests Prove Autonomous Repository Delivery",
            "Prompt 30 Closed on Deterministic Git Automation Evidence",
            "Idea 52 Delivers Safe GitHub Sync Without Routine Pauses",
        ],
        "hermes": [
            "Autonomous GitHub Sync Replaces Approval Churn with Exact Scope and Proven Safety",
            "GitHub-Sync Joins Diff Evidence, Safe Pushes, and Automatic Hub-Pointer Updates",
            "Particular Scope Fixed While Automatic Pointer-Only Hub Synchronization Stays On",
            "Disposable Git Tests and Two zCode Workspaces Prove Autonomous Repository Delivery",
            "Five-Harness GitHub Sync Ships with Exact Parity and Real Cross-Workspace Proof",
            "Git-Diff and Stage-Commit-Push Now Run Continuously Behind One GitHub-Sync Call",
            "Prompt 30 Closes After Deterministic Tests Prove Safe Autonomous Git Operations",
            "Idea 52 Delivers End-to-End Git Automation with Genuine Safety Stops Preserved",
        ],
        "general": [
            "Autonomous GitHub Sync Replaces Approval Churn with Exact Particular Scope, Genuine Safety Stops, Five-Harness Parity, and Real zCode Proof",
            "GitHub-Sync Unifies Read-Only Diff Evidence, Scope-Safe Commit and Push, Automatic Hub-Pointer Updates, and Verified Cross-Workspace Delivery",
            "Idea 52 Becomes an Autonomous Git Workflow After the Particular-Scope Contradiction Is Repaired and Prompt 30 Is Closed on Deterministic Evidence",
            "Git-Diff, Stage-Commit-Push, and GitHub-Sync Now Form One Continuous Workflow That Pauses Only for Genuine Repository Safety Conditions",
            "Disposable Repository Tests, Exact Global Parity, and Two Successful zCode Runs Prove Autonomous GitHub Sync Across the Full Five-Harness Fleet",
            "Particular Staging Now Governs Only the Nested Commit While Automatic Pointer-Only Hub Synchronization Completes the Safe End-to-End Workflow",
            "Prompt 30 and Idea 52 Close with GitHub-Sync Built Locally, Validated Deterministically, Synchronized Globally, and Confirmed in Two Real Workspaces",
            "Autonomous Repository Delivery Now Covers Diff Review, Exact Scope, Generated Commits, Remote Proof, Hub Gitlinks, and Cross-Harness Validation Without Routine Approval Stops",
        ],
    }
    for host, labels in representative.items():
        for label in labels:
            if not fits(label, prefix, host):
                raise AssertionError(f"representative {host} label exceeds its cap: {label}")
            if label.startswith("From "):
                raise AssertionError(f"representative {host} label defaults to journey framing: {label}")
            if not label[0].isupper():
                raise AssertionError(f"representative {host} label lacks an uppercase lead: {label}")


def main() -> None:
    check_contract_text()
    check_cap_accounting()
    print("session-name contract checks passed")


if __name__ == "__main__":
    main()
