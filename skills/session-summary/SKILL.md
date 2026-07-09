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

Four values drive the summary file: **Project Name**, **Topic**, **Session Number**, and **Directory**.

**Inference is mandatory and compulsory.** Before asking the user anything, you MUST attempt to infer all four values from the session and the workspace. Do not present a blank template, and do not ask the user to supply a value you could have derived yourself. Presenting empty fields, or asking without having first inferred, is a protocol violation. Your job is to do the legwork so the user can simply approve — not to make the user fill out a form.

How to infer each value:

- **Project Name** — Derive it from what the session was actually about, scoped to the workspace. First check the existing subfolders under `<project root>\Archive\Summaries\`; if this session clearly continues one of them, reuse that exact folder name. If the workspace name itself would be redundant as the project name (e.g. the workspace is "Workflows" and every summary would trivially read "Workflows"), infer a more specific project label from the session's actual focus (e.g. "Workspace Setup").
- **Topic** — Derive it from the concrete work done this session (e.g. `Session-Summary Inference Update`). Keep it short and specific, matching the example style below.
- **Session Number** — Look inside the resolved `<project root>\Archive\Summaries\[Project Name]\` folder, find the highest existing summary number, and use the next integer. If the folder is empty or does not exist, this is `1`.
- **Directory** — Default to `<project root>\Archive\Summaries\[Project Name]\` unless the user explicitly named a specific in-project path.

Reference examples:

- Project name, e.g. `Skills`, `Skill Maintenance`, `Uzzy TRUTH`, `cTrader MCP`
- Topic, e.g. `Codex Migration session-summary Integration`, `New Skills + Global-Sync + Hermes Target`, `Zone Evaluation & Invalidation Logic Audit`, `V2 Control-Based Card Build`
- Session Number, e.g. `2`, `5`, `36`, `2`
- Directory choice:
  - Default: `<project root>\Archive\Summaries\[Project Name]\`
  - A specific in-project directory the user named: use it exactly
  - A directory outside the project root: stop and ask before proceeding

**Present inferred suggestions, never blanks.** Unless the user already gave every value explicitly, present the template **pre-filled with your inferred suggestions** and ask the user to confirm or adjust. Use this wording:

```text
Here are my inferred values — green-light to use them as-is, or change any single line:

1. Project Name: [inferred value]
2. Topic: [inferred value]
3. Session Number: [inferred value]
4. Directory: [Default -> <resolved absolute path>]
```

```text
Key:
5.) If user says Default, use <project root>\Archive\Summaries\[Project Name]\
6.) x.) [Topic].md
7.) <project root>\Archive\Summaries\[Project Name]\
8.) Where "x.)" = [Session Number]
```

Fill every numbered line with a concrete inferred value, never a blank — the user should be able to green-light the whole block without typing anything, and if they disagree with one line they overwrite only that line. If, after honestly trying, you genuinely cannot infer a single value (rare), mark that one line `[unable to infer - please provide]` and still pre-fill the other three.

Wait for the user's confirmation or corrections before creating the file, unless the user has told you to proceed without confirming.

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
x.) [Topic].md
```

Where `x` is the Session Number (starting from `1` for the first summary). `[Project Name]` is not repeated in the filename — the parent folder (`Archive\Summaries\[Project Name]\`) already identifies the project.

Example:

```text
<project root>\Archive\Summaries\Uzzy TRUTH\9.) QS LCA Extraction.md
```

If the directory does not exist, create it only after the required inputs are confirmed and file creation is allowed.

**Archive folder rule.** Session summaries always live under `Archive/` (in `Archive/Summaries/[Project Name]/`). If the `Archive/` folder does not yet exist in the workspace, create it yourself — along with the needed `Summaries/[Project Name]/` subfolders — when file creation is allowed. Never redirect the summary into any other folder (such as `Documentation/`) as a fallback. The summary folder always nests inside `Archive/`.

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
# [Topic]

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
