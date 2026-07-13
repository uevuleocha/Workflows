---
name: session-name
description: Suggest exactly four short, descriptive chat-session names grounded in the work this session actually did, at session end or midway through. Use when the user invokes /session-name, use session-name, "name this session", "give me session name options", "suggest a name for this chat", "top four names for this session", or clear equivalents asking for chat-session-name suggestions. Offers an OPT-IN N.) session-number prefix (asks first; if wanted, requires the user-supplied session number and never guesses it), presents choices 1-4, and confirms the final string. Suggestion-only — it never renames the chat, claims platform-side changes, or creates, moves, or renames any file. Not for naming files, plans, tasks, prompts, or reports, and not a recap (session-summary owns that).
---

# Session Name

Offer the user the top four suggestions for a short, descriptive **chat-session
name** — the label shown in the platform's session sidebar/UI — grounded in what
this session actually did. The user picks one; the skill confirms the exact
final string. Nothing is renamed and nothing is written to disk.

## Invocation

Treat these as direct invocation and begin the skill:

- `/session-name`
- `use session-name`
- `use the session-name skill`
- "name this session"
- "give me session name options"
- "suggest a name for this chat"
- "top four names for this session"
- clear equivalents asking for chat-session-name suggestions

The skill may be invoked at **session end** or **midway through** a session.

## When NOT to use it

- **Naming a file, plan, task, prompt, or report** → that is the relevant
  `-this` skill's job (`plan-this`, `task-this`, `prompt-this`, `report-this`).
  `session-name` is strictly for the chat session's UI label. If the user asks
  it to name a file or plan, decline and point to the right skill.
- **A written recap of the session** → that is `session-summary`, the durable
  document. `session-name` is only the short label. They are commonly run
  back-to-back at session close (name first, then summary), but they are
  separate skills.

## Workflow

1. **Read the session.** Review what this conversation actually did so far —
   the work performed, decisions made, problems solved. Use only the real
   content of *this* session; never a generic guess.
2. **Confirm the prefix (opt-in).** Before generating any suggestions, ask
   whether the user wants the `N.)` session-number prefix on the names. The
   prefix is **opt-in**, not assumed.
   - If the user already made the choice clear at invocation (e.g. "this is
     session 20" implies yes-with-number; "no prefix" implies no), skip the
     question and honor it.
3. **Resolve the number (only if the prefix is wanted).** The number must come
   from the user:
   - If the user supplied it ("run session-name, this is session 20"), use it.
   - If not, **stop and ask** "What number is this chat session?" and wait for
     the answer before presenting any options. Continue next turn. Where the
     host supports an AskUserQuestion-style runtime prompt, that is an
     acceptable way to ask.
   - **Never guess or infer the number** — not from workspace file numbering,
     folder indexes, or any other source. Ask-or-tell only.
4. **Produce exactly four options.** Short, accurate, decently descriptive,
   and meaningfully distinct — four different angles (tool, outcome, method,
   headline result), not four rewordings of one phrase. When the prefix is in
   use, all four carry the **identical** `N.)` prefix; only the descriptive
   part varies. Present them as a numbered list of choices 1–4.
5. **Confirm the pick.** After the user selects one, echo the exact final
   string for them to paste into the platform UI. The skill does **not**
   rename the session and never claims the platform-side name changed.

## Naming Style Rules

- **Short.** A UI label, not a sentence. Soft guidance: about eight
  descriptive words or ~60 characters, **excluding** the `N.)` prefix. This is
  guidance only — do not hard-fail or truncate a longer name that is the
  accurate one.
- **Accurate.** Grounded in what the session genuinely did; do not inflate or
  misdescribe.
- **Distinct.** The four options vary in emphasis so the user has a real
  choice.
- **Exactly four.** No more, no fewer, in this version.

## Mid-Session Use

When invoked midway through a session, name only the work **completed so
far**, and briefly note that the name may evolve and the skill can be re-run
at session close.

## Scope and Safety

- **Read-only.** Produces chat output only. Creates, moves, and renames no
  files. Does not rename the chat in any platform UI and never claims to.
- **Platform-neutral.** It may recommend the string as a UI label, but must
  not claim it can rename chats in Claude Code, Codex, zCode, Hermes,
  Antigravity, or any other host.
- **One-shot helper, not a mode.** It emits no Mode footer of its own and does
  not persist. It still obeys any mandatory response footers required by the
  host workspace contract (e.g. Glossary/Mode footers).

## Output Shape

```text
This is session 20. Top four name options:

1. 20.) ChatGPT Codex in Hermes — Subscription Connected
2. 20.) Hermes on ChatGPT: OpenAI Codex OAuth Setup
3. 20.) GPT-5.6-sol as Hermes Default via Codex OAuth
4. 20.) Connecting ChatGPT to Hermes (no API key)

Pick one and I'll confirm it.
```

Without the prefix, the same block simply omits `20.)` from each option.

## Examples

### 1. Known session number

> **User:** run session-name, this is session 20
> **Agent:** *(prefix implied yes, number supplied — generates immediately)*
> presents four `20.)`-prefixed options as choices 1–4.

### 2. Prefix wanted, number missing — stop and ask

> **User:** /session-name — yes, use the number prefix
> **Agent:** "What number is this chat session?" *(stops; no options yet;
> continues next turn once the user answers — an AskUserQuestion-style prompt
> is fine where the host supports it)*

### 3. User declines the prefix

> **User:** name this session, no numbering
> **Agent:** presents four unprefixed options, e.g.
> `1. Hermes OAuth Setup for ChatGPT Codex`, as choices 1–4.

### 4. Mid-session invocation

> **User:** give me session name options *(session still ongoing)*
> **Agent:** asks about the prefix if unclear, then names only the work done
> so far and adds: "This names the session so far — re-run me at session close
> if the focus shifts."

### 5. Final user selection

> **User:** option 2
> **Agent:** "Confirmed. Final name: `20.) Hermes on ChatGPT: OpenAI Codex
> OAuth Setup` — paste it into the session label in your platform's UI. I
> haven't renamed anything myself."

### 6. Refusal — naming a plan/file instead

> **User:** use session-name to name my new plan file
> **Agent:** "session-name only labels the chat session itself. For naming a
> plan file, use `plan-this` (or the matching `-this` skill for the artifact
> type)."

### 7. Separation from session-summary

> **User:** name this session and write the wrap-up
> **Agent:** runs session-name for the label only, then: "For the durable
> recap, that's `session-summary` — want me to run it next?"

## Related Skills

- `session-summary` — the durable written recap; companion at session close.
- `plan-this`, `task-this`, `prompt-this`, `report-this` and their finalizers —
  the durable-artifact family. `session-name` is **not** in that family: it
  creates no artifact and needs no finalizer.

## Future Hook

A hard word/character cap and an automatic platform-derived session number are
deliberately **not** implemented in this version. Number source is ask-or-tell
only; the ~8-word/~60-character guidance is the documented hook for a future
hard cap once usage settles.
