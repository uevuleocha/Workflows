---
name: session-summary
description: Create chat/session summary files for continuity after implementation, debugging, planning, or architecture sessions. Use when explicitly invoked with /session-summary or when the user asks to use the session-summary skill. For natural phrases like "session summary", "chat summary", "wrap up", "handoff", or "summarize this session", first confirm the user wants the saved session-summary workflow before creating or editing files. Produces durable markdown summaries with verbose 🎭 ACTS breakdowns, project/topic/session metadata, active plan status, and next-session pickup context.
---

# Session Summary

Create a durable session summary so a future agent can restore context from the written file without needing the original chat.

This is a continuity artifact for future agents working inside the project. It is not a short status report.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the skill workflow:

- `/session-summary`
- `use the session-summary skill`
- clear equivalents where the user explicitly names this skill

For natural trigger phrases, confirm first before running the saved-summary workflow or creating/editing files:

- `session summary`
- `chat session summary`
- `chat summary`
- `handoff`
- `wrap up`
- `summarize before I clear`
- `summarize this session`
- `give me an exhaustive summary`
- `break it down into 🎭 ACTS`
- near-equivalent requests asking to preserve session context

Use this confirmation wording:

```text
Do you want me to run the `session-summary` skill and create a saved session summary file?
```

If the user only wants a quick chat answer, do not create a file.

## Required Inputs

Before writing the summary file, make sure these are known.

If the Project Name, Topic, Session Number, or Directory is missing or unclear, present this exact structured template for the user to copy, fill out, and return, followed by the Key block beneath it:

```text
1. Project Name: 
2. Topic: 
3. Session Number: 
4. Directory: [Default | specific path]
```

```text
Key:
5.) If user says Default, use <project root>\Archive\Summaries\[Project Name]\
6.) x.) [Project Name] [Topic] Summary [Session Number].md
7.) <project root>\Archive\Summaries\[Project Name]\
8.) Where "x.)" = [Session Number] also
```

- Project name, e.g. `SR`, `KL`, `TRUTH`
- Topic, e.g. `Drawing Engine pt2`, `Zone Engine Port`, `Discord Alerts Imp`
- Session Number, e.g. `9`, `10`, `11`
- Directory choice:
  - If user says `Default`, use `<project root>\Archive\Summaries\[Project Name]\`
  - If user gives a specific directory, use that exact directory if it is inside the project root
  - If the directory is outside the project root, stop and ask before proceeding

Do not guess these values. Wait for the user to return the filled template before proceeding to create the file.

## Required Review

Review only the sources needed to summarize the current session accurately:

1. Current conversation/session history
2. The project's canonical contract (e.g. `CLAUDE.md`)
3. Active implementation plan only if it was used in the session or mentioned by the user

Optional review when the user asks or context requires it:

- Prior summaries
- Explicitly named source files

This skill summarizes the current conversation first. Do not perform a broad repo audit.

## Active Plan Handling

If an active plan drove the session, inspect it before writing the summary.

If the user asked for a session summary and the active plan is part of the session:

- Mark successfully completed items as `Complete`
- Mark unfinished items as `Pending`
- Preserve the plan's structure and wording as much as possible
- Do not finalize or rename the plan unless the user explicitly says the plan is complete, finalized, or done

If direct file edits are not allowed in the current agent mode, explain that the plan update must wait for execution mode or user approval.

## Output Location And Filename

Default directory format:

```text
<project root>\Archive\Summaries\[Project Name]\
```

Filename format:

```text
x.) [Project Name] [Topic] Summary [Session Number].md
```

Where `x` is the Session Number (starting from `1` for the first summary).

Example:

```text
<project root>\Archive\Summaries\SR\9.) SR Drawing Engine pt2 Summary 9.md
```

If the directory does not exist, create it only after the required inputs are confirmed and file creation is allowed.

After writing the file, do not paste the full finished summary into chat. Tell the user the file path.

### "In House" / "In Chat" Only Mode

If the user explicitly asks for the summary "in house", "in chat", or "chat only", do **not** create a file. Instead, render the entire formatted 🎭 ACTS summary directly in the chat response.

## Summary Style

Use the 🎭 ACTS format.

**CRITICAL**: Every single ACT heading must explicitly include the `🎭` emoji. You must prefix every act heading with this emoji without exception (e.g., `## 🎭 ACT I: ...`).

The summary must be verbose, granular, and chronological. Explain:

- Where the session started
- What the user asked
- What files were read
- What the assistant concluded
- What was implemented or planned
- What was rejected, corrected, or clarified
- Any user challenges and how they changed the design
- Any bugs, mistakes, misunderstandings, or protocol violations
- Verification performed
- Current status
- What remains next

Use headings like:

```markdown
## 🎭 ACT I: The Session Re-Entry and Canonical Contract Reload

## 🎭 ACT II: The Drawing Engine Reality Check

## 🎭 ACT III: The `_showArchivedSrCounts` Debate
```

Use as many 🎭 ACTS as needed. Do not compress separate events into one ACT if doing so would hide important context.

The **last** ACT of every summary must always be the Definition of Done ACT, titled `🎭 FINAL ACT: Definition of Done`. It comes after every chronological ACT and before the `Final State At End Of Session` block. See the `Definition of Done ACT` section below for required contents.

## Required Summary Template

Use this structure unless the user explicitly asks for a different one:

```markdown
# [Project Name] [Topic] Summary [Session Number]

**Topic:** [Topic]  
**Date:** [YYYY-MM-DD]  
**Project:** [Project Name]  
**Plan File:** `[absolute path or none]`  
**Primary File:** `[absolute path or none]`  
**Reference Files:** [short list of important references]

---

## 🎭 ACT I: [Specific Act Title]

[Granular narrative of what happened.]

---

## 🎭 ACT II: [Specific Act Title]

[Granular narrative of what happened.]

---

## 🎭 FINAL ACT: Definition of Done

**Phase [N] - [Phase Name]**

DoD met when:

1. [Success criterion] - **Met** | **Missed** | **Partial** ([brief evidence or reason])
2. [Success criterion] - **Met** | **Missed** | **Partial** ([brief evidence or reason])

(Repeat the phase block for each distinct phase of the session. Single-phase sessions get one block.)

**Out of scope (intentional)**

- [Item the agent deliberately did not treat as DoD, so future agents do not assume it was forgotten]
- none, if nothing was held out of scope

---

## Final State At End Of Session

[Explain exactly where the project stands now.]

## Files Created Or Modified

- `[absolute path]` - [what changed]
- none, if no files were modified

## Verification Performed

- [command/check/review] - [result]
- none, if no verification was performed

## Known Issues / Pending Work

- [pending item]
- none, if no pending work remains

## Next Session Pickup

[Concrete next action for the next agent.]
```

## Definition of Done ACT

The Definition of Done ACT is mandatory in every summary. It is always the **last** ACT, titled exactly:

```text
## 🎭 FINAL ACT: Definition of Done
```

The DoD is normally held internally during the session per the project's canonical contract. The session summary is the canonical place to surface it for the record so future agents can see what "done" meant for the prior session.

Required sub-parts:

1. **Phase breakdown.** If the session had distinct phases (e.g., Design vs. Build, Plan vs. Implement, Investigate vs. Fix), each phase gets its own DoD block. Single-phase sessions get one block.
2. **DoD items.** Numbered list of the success criteria the agent held during the session. Use the exact criteria, not a paraphrase.
3. **Met / Missed / Partial status.** For each DoD item, mark explicit status (**Met**, **Missed**, or **Partial**) with brief evidence (e.g., "validator passed", "stopped per CLAUDE.md local-first rule", "user deferred to next session").
4. **Out of scope (intentional).** Bulleted list of items the agent deliberately did **not** treat as DoD, so future agents do not assume they were forgotten. Write `none` if nothing was held out of scope.

If the DoD was implicit (no formal criteria given by the user), reconstruct it honestly from what the agent was actually aiming for during the session. Do not invent stricter criteria after the fact.

## Writing Rules

Be exhaustive, but stay useful.

Do:

- Preserve technical names exactly
- Include method names, field names, enum names, file names, plan phase names, and command names
- Use absolute paths for important files
- Mention user decisions and objections
- Mention assistant mistakes if they affected the session
- Mention rejected approaches and why they were rejected
- Explain why final decisions were made
- Include current project status and next action

Do not:

- Invent state
- Claim a file was modified if it was only discussed
- Claim tests passed if they were not run
- Summarize only the last few turns
- Skip conflicts, corrections, or backtracking
- Dump the whole summary into chat after creating the file
- Create memory/documentation updates unless the user explicitly approves

## Style Notes

Existing summaries are detailed narrative records. They often include:

- A metadata header
- A chronological 🎭 ACTS structure
- Specific references to the project's canonical contract, plans, summaries, and source files when relevant
- Explicit "what was confirmed" lists
- Explicit "the problem / the fix / why it mattered" breakdowns
- Detailed explanations of user challenges and final decisions

Match that style.

If the user asks for "EVERY SINGLE THING", interpret that as:

- Include all meaningful technical discussion
- Include all implementation decisions
- Include all changes delivered or applied
- Include all review corrections
- Include all unresolved items
- Do not include irrelevant filler or generic chat

## Antigravity Safety Note

If this skill is being used by Antigravity, follow the user's Antigravity 2FA rule from `AGENTS.md` before creating or editing any file.

Antigravity must first propose the exact file creation/edit and ask permission, then wait for one of the greenlight phrases:

```text
"make the edit" | "greenlight" | "approved" | "execute plan" | "go ahead" | "apply changes" | "do it" | "push to drive"
```

Claude and Codex must still follow their own current execution mode and tool safety rules.