# Session Name — Adoption Guide

Suggests exactly four short, descriptive **chat-session names** (the label in
the platform's session sidebar/UI), grounded in the work the current session
actually did. Usable at session end or midway through. The user picks one and
the skill confirms the exact final string.

## What it does — and does not do

- Produces **exactly four** distinct options, presented as choices 1–4.
- The `N.)` session-number prefix is **opt-in**: the skill asks whether the
  user wants it before generating. If wanted, the number must be supplied by
  the user — the skill **stops and asks** for it if absent and **never**
  guesses or infers it from workspace file numbering.
- Length is soft guidance only (~8 descriptive words / ~60 characters,
  excluding `N.)`); accurate longer names are not rejected.
- **Suggestion-only.** It never renames the chat, never claims platform-side
  changes, and creates, moves, and renames no files during invocation.
- **Platform-neutral.** It recommends a UI label but does not claim it can
  rename chats in Claude Code, Codex, zCode, Hermes, or Antigravity.
- **One-shot helper, not a persistent mode.** It still obeys any mandatory
  response footers the host workspace contract requires.

## Boundaries with sibling skills

- Naming a **file/plan/task/prompt/report** belongs to the matching `-this`
  skill (`plan-this`, `task-this`, `prompt-this`, `report-this`), not here.
- A written session recap belongs to `session-summary`. Typical close
  sequence: `session-name` for the label, then `session-summary` for the
  durable record. `session-name` creates no durable artifact and needs no
  finalizer.

## Adoption Prompt

```text
Read this README and SKILL.md. session-name is a standalone one-shot helper —
no hard dependencies. It pairs naturally with session-summary at session close;
install both if you want the full close routine. It renames nothing itself:
the platform UI owns the actual rename.
```
