# Session Summary — Adoption Guide

Creates durable chat/session summary files (verbose 🎭 ACTS format) as `Archive/Summaries/…`
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
`Archive/Summaries/Migration/…`, with an availability guard that falls back to a plain markdown
summary if this skill is not loaded.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.
