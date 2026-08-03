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

A direct invocation is authorization to infer the required values, create any
needed in-project summary directories, write the summary, and return the
completed-values template in the same turn. Do not add a separate preview,
confirmation, or greenlight step.

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

For natural trigger phrases, the affirmative answer to the confirmation
question authorizes the complete saved-summary workflow. Do not ask for a
second confirmation after inferring the required values.

## Required Inputs

Four values drive the summary file: **Subject**, **Topic**, **Session Number**, and **Directory**.

**Inference is mandatory and compulsory.** You MUST infer all four values from
the session and the workspace. Do not present a blank template, and do not ask
the user to supply a value you could have derived yourself. Presenting empty
fields, or asking for approval of inferred values, is a protocol violation.
Your job is to do the legwork and save the summary in the same turn.

How to infer each value:

- **Subject** — the broad category folder for this summary. Derive it from what the session was actually about, scoped to the workspace. First check the existing subfolders under `<project root>\Archive\Historical\Summaries\`; if this session clearly continues one of them, reuse that exact folder name. If the workspace name itself would be redundant as the Subject (e.g. the workspace is "Workflows" and every summary would trivially read "Workflows"), infer a more specific Subject from the session's actual focus (e.g. "Workspace Setup"). The Subject folder is never numbered — only the files inside it carry the `N.) ` prefix.
- **Topic** — Derive it from the concrete work done this session (e.g. `Session-Summary Inference Update`). Keep it short and specific, matching the example style below.
- **Session Number** — Look inside the resolved `<project root>\Archive\Historical\Summaries\[Subject]\` folder, find the highest existing summary number, and use the next integer. If the folder is empty or does not exist, this is `1`.
- **Directory** — Default to `<project root>\Archive\Historical\Summaries\[Subject]\` unless the user explicitly named a specific in-project path.

Reference examples:

- Subject, e.g. `Skills`, `Skill Maintenance`, `Uzzy TRUTH`, `cTrader MCP`
- Topic, e.g. `Codex Migration session-summary Integration`, `New Skills + Global-Sync + Hermes Target`, `Zone Evaluation & Invalidation Logic Audit`, `V2 Control-Based Card Build`
- Session Number, e.g. `2`, `5`, `36`, `2`
- Directory choice:
  - Default: `<project root>\Archive\Historical\Summaries\[Subject]\`
  - A specific in-project directory the user named: use it exactly
  - A directory outside the project root: stop and ask before proceeding

Immediately before writing, verify that the resolved filename is still
available. Never overwrite an existing summary accidentally. If another file
already occupies the inferred number, advance to the next available integer
and use that number consistently in the filename, summary metadata, and
completion receipt.

**Save first, then present the completed-values template.** After writing the
file, always show the template pre-filled with the values actually used. This
is a completion receipt, not an approval request. Use this wording:

```text
Created and saved using these inferred values:

1. Subject: [used value]
2. Topic: [used value]
3. Session Number: [used value]
4. Directory: [resolved absolute path]
```

```text
Key:
5.) Default = <project root>\Archive\Historical\Summaries\[Subject]\
6.) Saved file = x.) [Topic].md
7.) Saved directory = <resolved absolute path>
8.) Where "x.)" = [Session Number]
```

Fill every numbered line with a concrete value, never a blank. Also provide a
clickable path to the saved artifact when the current interface supports local
file links. If the user dislikes the inferred Subject, Topic, Session Number,
Directory, filename, or content, treat their follow-up as a normal correction:
update or move the artifact as requested and return the revised completed-values
template. Do not make uncertainty about naming or categorization into a
pre-write approval gate. Pause only when a higher-priority project contract,
filesystem restriction, unsafe overwrite, or explicitly requested
outside-project destination genuinely requires user input.

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
<project root>\Archive\Historical\Summaries\[Subject]\
```

Filename format:

```text
x.) [Topic].md
```

Where `x` is the Session Number (starting from `1` for the first summary). `[Subject]` is not repeated in the filename — the parent folder (`Archive\Historical\Summaries\[Subject]\`) already identifies the project.

Example:

```text
<project root>\Archive\Historical\Summaries\Uzzy TRUTH\9.) QS LCA Extraction.md
```

If the directory does not exist, create it as part of the same authorized
summary pass when file creation is allowed.

**Archive folder rule.** Session summaries always live under `Archive/` (in `Archive/Historical/Summaries/[Subject]/`). If the `Archive/` folder does not yet exist in the workspace, create it yourself — along with the needed `Summaries/[Subject]/` subfolders — when file creation is allowed. Never redirect the summary into any other folder (such as `Documentation/`) as a fallback. The summary folder always nests inside `Archive/`.

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
**Subject:** [Subject]
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

## Delegated Return Reports (Session-Summary Family)

A **delegated return report** is a session-summary family member that a
returning agent writes when its delegation assignment completes. It is reserved
and mandated by `delegate-this`, but its **shape** lives here because it is a
session summary.

A return report:

- uses **session-summary structure** — the 🎭 ACTS narrative, metadata header,
  Definition of Done ACT, and final-state block — exactly as a normal summary;
- carries a **lowercase child prefix** (`Na.)`, `Nb.)`, …) from the **Summary
  family** master `N` (the Summary Subject namespace), reserved by the
  orchestrator. The orchestrator/master summary is `N.)`; return reports inherit
  that Summary master number (e.g. `9.)` → reports `9a.)`, `9b.)`, …);
- has a filename that **ends in `Report.md`** (for example,
  `9a.) claude_packet1_wave1_Report.md`);
- lives under `<project root>\Archive\Historical\Summaries\<Subject>\`, beside
  the orchestrator/master summary;
- adds one delegation-specific section: an **append-only `## Feedback`
  ledger**, placed after the session-summary body (after the `## Next Session
  Pickup` block).

**Separate namespace anchor.** The Summary family's master `N` comes from the
Summary Subject namespace only — it is independent of the delegation's Plan/Task
number and of the Delegation record's own number. The families are connected by
explicit path pointers, not a shared number; do not expect the Summary master
`N` to match the Plan or Delegation `N`.

### Feedback ledger rules

The `## Feedback` section is append-only:

- **Existing report content is immutable.** Never rewrite a returned
  deliverable, ACT, or earlier line of the report.
- **Earlier feedback entries are immutable.** Once written, a feedback line is
  never edited or deleted — corrections are added as new lines.
- **Feedback is appendable only while the delegation is active.** The
  orchestrator (and, when relevant, the returning worker) may append feedback
  lines while the delegation is `_dispatched`.
- **The entire report freezes when `finalize-delegation` closes the
  delegation.** After the record becomes `_completed`, no further feedback may
  be appended — the report is a closed historical artifact.

Example:

```markdown
## Feedback

- [2026-07-11] Orchestrator: deliverable matched DoD; one nit — rename helper.
- [2026-07-11] Worker: helper renamed; re-validated, clean.
```

### Thin dependency

This skill owns the **report/feedback shape** only. It does **not** know about
delegation routing, packets, or lifecycle moves — that is `delegate-this`
(reserve + mandate) and `finalize-delegation` (freeze on close). When asked to
write a return report, use the reserved prefix supplied by the orchestrator,
use session-summary structure, append `## Feedback`, and stop there.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to session summaries, including migration handoffs and execution reports.

For every in-scope artifact:

- place an `## Agent Provenance` section near the top with `Content owner`,
  `Original writing agent`, `Created`, and `Artifact role`;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`,
  `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` near the bottom, recording the date,
  acting agent, action, and concise scope for every material edit;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather
  than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves
to `Uzo`; do not confuse content ownership with the agent that performed the
filesystem write. Do not inject provenance into product source, third-party
files, databases, generated caches, skill definitions, schema-sensitive or
machine-consumed files, or other operational files unless their schema
explicitly supports it.

## Durable Artifact Format Handling

This skill owns summary scope, ACTS structure, metadata, Subject, permanent
number, path, delegation-report shape, and content. When co-invoked with
`html-this` or `pdf-this`, run the complete summary workflow but save only the
requested `.html` or `.pdf` artifact unless the user requests multiple formats.
Pass the requested format through when this skill is called by a migration or
delegation workflow.

Treat same-stem `.md`, `.html`, and `.pdf` variants as one summary-family
artifact and one reserved prefix. Update every existing sibling consistently.
Return-report names use `Report.html` or `Report.pdf` in the requested format.
This section overrides `.md`-only examples only for the co-invoked run.
