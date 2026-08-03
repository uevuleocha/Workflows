# Session Name — Adoption Guide

Suggests exactly four rich, descriptive **chat-session names** (the label in
the platform's session sidebar/UI), grounded in the work the current session
actually did. Usable at session end or midway through. The user picks one and
the skill confirms the exact final string.

## What it does — and does not do

- Produces **exactly four** distinct options, presented as choices 1–4.
- The `N.)` session-identifier prefix is **opt-in**: the skill asks whether
  the user wants it before generating. If wanted, the identifier must be
  supplied by the user — used **verbatim, including lowercase child suffixes**
  (`17a` → `17a.)`, never normalized to `17.)`) — and the skill **stops and
  asks** for it if absent, **never** guessing or inferring it from workspace
  file numbering.
- Options are **facet-built**: each combines the applicable facets — Outcome,
  Artifact/Tool, Method, Headline Result — with each option leading on a
  different facet.
- Length: a **150-character soft ceiling** (excluding the prefix) — a ceiling
  to reach toward when the session's substance earns it, never a quota to pad
  toward; accurate longer names are not rejected.
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
