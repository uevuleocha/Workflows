# Verify This — Adoption Guide

Confirms that work done by an implementation agent actually met its goals and Definitions of Done, then writes the verdict back into the durable artifact's feedback section so the orchestrator is never blocked waiting. Anti-over-sabi by design: report unmet goals and blatant defects, never hunt edge cases or nitpick.

Use when an implementation agent (Agent B) has finished work against a prompt/plan/task/North Star and the orchestrator (or a sub-agent it spawns) needs to confirm the work before moving on. The default verdict is "did they do what we asked, well?" — not "what can I find wrong?"

## Related skills

- `inspect` — read-only audit/verification when you want defect-hunting or a general quality audit instead of goal-focused confirmation.
- `subagent-verification-loops` — heavy independent reviewer+resolver loop with proposed corrections when you want genuinely independent multi-agent review.
- `prompt-this` / `plan-this` / `task-this` / `north-star` — produce the durable artifacts whose goals/DoD this skill verifies against and writes feedback into.
- `finalize-prompt` / `finalize-plan` / `finalize-task` / `finalize-north-star` — own finalization once a `READY` verdict is reached.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.
