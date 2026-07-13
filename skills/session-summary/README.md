# Session Summary — Adoption Guide

Creates durable chat/session summary files (verbose 🎭 ACTS format) as `Archive/Historical/Summaries/…`
artifacts, so a future agent can restore context from the written file without the original chat.

## Depended on by

Other skills call `session-summary` as a mandatory closing step. If you adopt any of these, adopt
`session-summary` too:

| Skill | How it uses `session-summary` |
|---|---|
| `claude-workspace-chat-migration` | Hard — closes both workflows with a handoff/report summary (`## Session Summary Integration`) |
| `codex-workspace-chat-migration` | Hard — same, Codex-scoped |
| `antigravity-workspace-chat-migration` | Hard — same, Antigravity-scoped |

Each caller invokes `session-summary` pre-filled and saves under a platform subfolder of
`Archive/Historical/Summaries/Migration/…`, with an availability guard that falls back to a plain markdown
summary if this skill is not loaded.

## Delegated Return Reports

`delegate-this` reserves and mandates one **delegated return report** per
returning assignment, as a session-summary family member. A return report:

- uses session-summary structure (this skill owns the shape), plus an
  **append-only `## Feedback` ledger**;
- carries a lowercase child prefix (`Na.)`, `Nb.)`, …) from the **Summary
  family** master `N` (the Summary Subject namespace), reserved by the
  orchestrator — independent of the delegation's Plan/Task or Delegation number;
- has a filename ending in `Report.md`, under
  `Archive/Historical/Summaries/<Subject>/`.

This skill owns the report/feedback **shape only**. It does not know about
delegation routing, packets, or lifecycle moves — `delegate-this` reserves and
mandates the report, and `finalize-delegation` freezes it (and its `## Feedback`
ledger) when the delegation closes.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.
