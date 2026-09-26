# Session Summary — Adoption Guide

Creates durable chat/session summary files (verbose 🎭 ACTS format) as `Archive/Historical/Summaries/…` artifacts, so a future agent can restore context from the written file without the original chat.

Explicit invocation runs in one pass: the skill infers the required values, saves the file, and then displays the completed-values template as a receipt. Users can correct the path, filename, categorization, or content afterward.

## Buzz continuity mode

The skill selects its mode automatically from runtime context. Outside Buzz it stays platform-neutral (Mode A). When authoritative runtime context establishes that the writer is a named agent operating inside Buzz, Mode B activates automatically: the ACTS narrative additionally names material actors and preserves assignment, contribution, correction, approval, handoff, and ownership context, and the summary gains a compact `## Buzz Resume Cues` section (per-agent prior contribution, open ownership, first pickup source). Mode B is evidence-honest - it records only evidenced participation and never reconstructs hidden reasoning or lost session state.

## Depended on by

Other skills call `session-summary` as a mandatory closing step. If you adopt any of these, adopt `session-summary` too:

| Skill                                  | Use                                         |
| -------------------------------------- | ------------------------------------------- |
| `claude-workspace-chat-migration`      | Handoff summary -> see note [Claude]        |
| `codex-workspace-chat-migration`       | Codex-scoped handoff summary                |
| `antigravity-workspace-chat-migration` | Antigravity-scoped handoff summary          |
| `finalize-session`                     | Combined closing run -> see note [Finalize] |

Note [Claude]: Hard dependency that closes both workflows with a handoff/report summary through `## Session Summary Integration`.

Note [Finalize]: Hard child dependency. The wrapper runs `session-name` and `session-summary` in one pass and may pass Subject, Topic, summary number, and Directory overrides.

`finalize-session` is the convenience caller for combined chat-naming plus durable recap. It is a thin orchestrator and owns none of this skill's logic — `session-summary` keeps full ownership of inference, safe numbering, ACTS structure, provenance, clarification rights, and the completed-values receipt. Direct `session-summary` invocation is unchanged and never routes through the wrapper.

Each caller invokes `session-summary` pre-filled and saves under a platform subfolder of `Archive/Historical/Summaries/Migration/…`, with an availability guard that falls back to a plain markdown summary if this skill is not loaded.

## Delegated Return Reports

`delegate-this` reserves and mandates one **delegated return report** per returning assignment, as a session-summary family member. A return report:

- uses session-summary structure (this skill owns the shape), plus an **append-only `## Feedback` ledger**;
- carries a lowercase child prefix (`Na.)`, `Nb.)`, …) from the **Summary family** master `N` (the Summary Subject namespace), reserved by the orchestrator — independent of the delegation's Plan/Task or Delegation number;
- has a filename ending in `Report.md`, under `Archive/Historical/Summaries/<Subject>/`.

This skill owns the report/feedback **shape only**. It does not know about delegation routing, packets, or lifecycle moves — `delegate-this` reserves and mandates the report, and `finalize-delegation` freezes it (and its `## Feedback` ledger) when the delegation closes.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
