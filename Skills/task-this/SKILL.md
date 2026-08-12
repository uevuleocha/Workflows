---
name: task-this
description: Create or update pending workspace housekeeping and admin task files with mandatory Markdown action and verification checklists at every depth, Definition of Done, scope boundaries, validation steps, mandatory colored estimated-effort tables, and pending/done lifecycle handling. Use when the user asks for /task-this, create task, update task, task checklist, housekeeping task, admin task, or clear equivalents.
---

# Task This

Create or update a workspace task file for general housekeeping and admin work. A task here is non-product backbone work that keeps files, folders, skills, plans, summaries, documentation, workflows, or workspace structure organized and in sync.

This skill is a lighter sibling to implementation-plan workflows. Use it for operational tasks and maintenance checklists, not for durable implementation plans that require phased product or architecture work.

If the user asks for a task "in house", "in chat", "chat only", or clearly says they do not want a durable file, do not create or update a task artifact. Provide the task/checklist in chat only and make clear that no file was changed.

## Prompt Contract Integration (Mandatory)

Every task created or updated with this skill MUST carry a Prompt Contract authored through the `prompt-contracts` skill. This is compulsory at every task depth, including Compact and mini tasks. This skill and `prompt-contracts` travel together; if you ever share this skill, ship that one with it.

On every create and every update:

1. **Invoke `prompt-contracts`** to author the contract for this task's work, in its canonical structure: GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE. Pre-fill it from the task, scope boundaries, and reference files so the user does not restate anything.
   - Standard and Deep tasks: full 5-part contract.
   - Compact and mini tasks: a minimal contract (GOAL + DEFINITION OF DONE + FAILURE) is acceptable unless the user asks for the full form.
2. **In-chat display is off by default.** Do not paste the Prompt Contract into chat unless the user opts in during creation or later asks to see it. Suppressing chat display never permits an omitted or weakened embedded contract -- the artifact still carries the complete contract verbatim, every time. When the user does opt in, paste the full Prompt Contract block as an explicit exception to the "do not paste the task into chat" rule, without pasting the rest of the task.
3. **Embed the exact same contract verbatim** into the task file under a `## Prompt Contract` section, placed after `## What Needs To Be Done` and before `## Task Checklist`. (For in-chat-only tasks there is no file to embed into; the contract simply appears inline with the rest of the task.)
4. The contract's DEFINITION OF DONE clause is this task's authoritative Definition of Done, and its FAILURE clause the authoritative rejection criteria; `finalize-task` verifies against them. This skill no longer writes a separate `## Definition of Done` section — the contract is the single home for it.

On any later update, re-derive or revise the contract to match the new scope and refresh the `## Prompt Contract` section in the file. Re-show the updated contract in chat only if the user has opted in or asks to see it.

**Availability guard.** Before authoring the contract, confirm the `prompt-contracts` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `prompt-contracts` skill is not loaded. It is required to author the mandatory Prompt Contract for this task. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, produce the 5-part contract inline from the known GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE format, embed and show it the same way, and note in your final report that the dedicated skill was unavailable.
- Never silently skip the Prompt Contract.

## Mandatory Checklist Contract

Every task created or updated with this skill MUST contain Markdown checklists. This is a hard requirement at every task depth and output mode: Compact, Standard, Deep, mini, durable-file, and in-chat-only tasks.

Use the completed Uzzy SR Plans 20 and 21 as the canonical checklist model, adapted to task scope:

```markdown
### Pending Phase: Phase A - [Name]

**Goal:** [Outcome for this phase.]

**Tasks:**

- [ ] [Concrete housekeeping or admin action.]

**Verification:**

- [ ] [Observable check that proves the action worked.]
```

Apply these rules on every create and update:

- Every independently actionable task step MUST use a standard Markdown checkbox.
- Every independently verifiable acceptance criterion MUST use a standard Markdown checkbox.
- Standard and Deep tasks that use phases MUST give every phase a `Goal`, `Tasks` checklist, `Verification` checklist, and status.
- Standard and Deep tasks without phases MUST contain a `## Task Checklist` and a checkbox-based `## Validation` section.
- Compact and mini tasks MUST contain both a `## Checklist` of actions and a checkbox-based `## Validation` section.
- When the Prompt Contract's DEFINITION OF DONE contains independently verifiable items, write those items as checkboxes, following the Plan 21 pattern. FAILURE items remain rejection-condition bullets, not completion checkboxes.
- Use `- [ ]` for all new, pending, or unverified work.
- Change an item to `- [x]` only when explicit user confirmation or recorded session evidence proves that exact item complete.
- During updates, tick every newly proven item and leave every unproven item unchecked. Never mass-check items merely because the user says "done" or because another item passed.
- Preserve completed checklist items as the task's audit trail. Do not delete them for cleanup. If later evidence invalidates a completed item, return it to `- [ ]` and add a dated explanation.
- Plain bullets under `Tasks`, `Task Checklist`, `Checklist`, `Verification`, `Validation`, or a checklist-style DEFINITION OF DONE do not satisfy this contract.
- Completion evidence should appear immediately after the applicable phase or checklist section when it materially explains why items changed to `[x]`.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/task-this`
- `use task-this`
- `create task`
- `update task`
- `task checklist`
- `housekeeping task`
- `admin task`
- clear equivalents asking for a pending or done workspace task file

If the user asks for an implementation plan, use the relevant implementation-plan workflow instead. If the user asks to finalize a plan, use the relevant plan-finalization workflow instead.

## Task Lifecycle

Task files use this lifecycle:

- `_pending.md` means the task is open or still needs action.
- `_done.md` means the task is completed.
- `_mini_task_pending.md` means the user explicitly asked for a mini task and the task is open or still needs action.
- `_mini_task_done.md` means a mini task is completed.

When creating a new task, the filename must end in `_pending.md`.

When the user explicitly asks for a "mini task", the filename must end in `_mini_task_pending.md` instead. Preserve the `mini_task` marker through lifecycle renames, so completion produces `_mini_task_done.md` and reopening returns to `_mini_task_pending.md`.

When the user says a task is complete or done, update completion statuses only when evidence or user confirmation supports it, then rename the file from `_pending.md` to `_done.md` if completion is confirmed.

When the user wants to update an existing `_done.md` task, reopen it gracefully:

1. Add a new phase, checklist section, or dated update section that explains why the task is active again.
2. Preserve the previous completed work and completion evidence.
3. Rename the task file from `_done.md` back to `_pending.md`.
4. **Move the file back from `Historical` to `Live`.** A done task lives in `Archive\Historical\Tasks\[Subject]\`; reopening moves it to `Archive\Live\Tasks\[Subject]\`, preserving the same `[Subject]` folder and the same `N.) ` number. A reopened (pending) task must live on the `Live` side so a "scan Live for active work" pass still finds it — never leave a reopened task stranded in `Historical`.
5. Update the status and lifecycle lines to show that the task was reopened.

Do not delete prior completed sections just because a task has been reopened.

## Required Review

Review only the sources needed to create or update the task accurately:

1. Governing workspace instructions, if present.
2. User-named reference files.
3. User-referenced task file, if any.
4. Existing task files when needed to decide create vs update.
5. Relevant folders or metadata only when needed to understand the housekeeping scope.

Do not perform a broad repository audit unless the task genuinely requires it.

## Create Vs Update Decision

Use update mode when:

- the user explicitly references an existing task
- the user says to update, revise, continue, reopen, or add to a task
- the user's request clearly matches exactly one existing `_pending.md` or `_done.md` task

Use create mode when:

- no existing matching task is found
- the task is clearly separate from existing task files
- the user explicitly asks for a new task
- the user provides a specific new filename ending in `_pending.md`

Ask before writing when:

- multiple plausible task files match
- the task could reasonably be folded into an existing task or created as its own task
- the target filename, directory, scope boundaries, or Definition of Done is unclear
- the user gives a vague request such as "make/update a task for this" without enough context to choose create vs update confidently

## Default Path And Naming

Default directory (the `[Subject]` folder is the broad category, e.g. `Skills/`, `Housekeeping/`, `Legacy/`; it is never numbered):

```text
<project root>\Archive\Live\Tasks\[Subject]\
```

Task files always live under `Archive/`, nested inside a `[Subject]` folder (in `Archive/Live/Tasks/[Subject]/`). If the workspace contract specifies a different task directory, use that contract path instead. Otherwise default to `<project root>\Archive\Live\Tasks\[Subject]\` — do not create a separate top-level `Tasks/` directory outside `Archive/`, and do not save tasks flat directly under `Tasks/` without a Subject folder.

Filename format:

```text
N.) <Topic>_pending.md
```

Mini task filename format, only when the user explicitly asks for a "mini task":

```text
N.) <Topic>_mini_task_pending.md
```

`N` is assigned **once at creation** as the next integer past the highest `N.) ` number found across **both** `Archive\Live\Tasks\[Subject]\` **and** `Archive\Historical\Tasks\[Subject]\` combined — the Subject's full Live + Historical namespace. Glob both folders, take the global max, add 1. If neither folder holds a numbered file, use `1`. This combined-namespace rule prevents collisions when the Live folder drains and would otherwise restart at `1` while Historical still holds that number.

The number is **immutable for the life of the file**: it survives the `_pending.md` ↔ `_done.md` rename and the Live ↔ Historical moves on finalize and reopen. Never renumber on finalization or reopening, and never reclaim gaps.

**Folders are never numbered — only files carry the `N.) ` prefix**, restarting at `1` per `[Subject]` folder across the combined namespace.

Generate the filename **Topic** as a short **Title Case phrase with spaces** describing the task's work — typically the `Main Task`, optionally led by the `Task Area / Component` (for example, `Global Skill Sync Sweep`). Match the workspace's other artifact filenames (`prompt-this`, `doc-this`, `session-summary`): Title Case, spaces, no underscores inside the Topic. Only the lifecycle suffix (`_pending`, `_mini_task_pending`) keeps its underscore form. Do not ask the user for the filename unless the derived Topic would be ambiguous or misleading.

## Required Inputs

Before writing a new task, make sure these are known or safely inferable:

1. Subject (the broad category folder, e.g. `Skills`, `Housekeeping`)
2. Task Area / Component
3. Main Task
4. What Needs To Be Done
5. Definition of Done
6. Output Task Directory
7. Scope Boundaries
8. Task Depth

Use this prompt shape when information is missing:

```text
We need to define this task before writing it.

How these fields determine the task path:
- Subject decides the broad category folder under `Archive/Live/Tasks`, usually `Archive/Live/Tasks/[Subject]` (the folder is never numbered).
- Main Task (optionally led by the Task Area / Component) becomes the filename **Topic** — a short Title Case phrase with spaces.
- Together they produce `N.) <Topic>_pending.md` under the Subject folder (`<project root>\Archive\Live\Tasks\[Subject]\` by default), where `N` is the next integer past the highest number across the Subject's combined `Live` + `Historical` folders.
- If the user explicitly asked for a mini task, use `N.) <Topic>_mini_task_pending.md` instead.

1. Subject:
2. Task Area / Component:
3. Main Task:
4. What Needs To Be Done:
5. Definition of Done:
6. Output Task Directory:
7. Scope Boundaries:
8. Task Depth:
```

Definition of Done means the series of constraints and technical specifications required for the agent or user to conclude that a task is complete.

For Scope Boundaries, tell the user:

```text
Scope boundaries mean what should be included, excluded, deferred, or treated as read-only. If you are not sure, say `delegate` and I will infer sensible boundaries from the workspace rules and the task.
```

For Task Depth, use:

- `Compact`: short checklist for a small housekeeping task, still including the mandatory full colored `Estimated Effort` table
- `Standard`: polished task with lifecycle note, context, Prompt Contract (its DEFINITION OF DONE clause is the task's Definition of Done), mandatory action and verification checklists, validation, and boundaries
- `Deep`: full phased task with mandatory task and verification checklists for multi-step workspace maintenance, sync, validation, or migration work

Default to `Standard` unless the task is clearly tiny or clearly complex.

If the user explicitly asks for a "mini task", default to `Compact` depth unless they also ask for Standard or Deep detail. "Mini" controls the filename suffix and expected brevity; it does not bypass the normal task lifecycle rules or the mandatory full colored `Estimated Effort` table.

## Task Template

For standard and deep tasks, use these sections when applicable:

```markdown
# [Task Area / Component] - [Main Task]

Status: PENDING ⌛ - created [YYYY-MM-DD].

Task lifecycle: PENDING on [YYYY-MM-DD]. [One sentence explaining what this task covers.]

## Agent Provenance

| Field                  | Value                  |
|------------------------|------------------------|
| Content owner          | Uzo                    |
| Original writing agent | <agent family>         |
| Original writing LLM   | <model>                |
| Created                | <YYYY-MM-DD>           |
| Artifact role          | <what this artifact is>|

## Context

**Delegation:** N/A

## Scope Boundaries

## What Needs To Be Done

## Prompt Contract

## Task Checklist

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

## Validation

## Estimated Effort

## Notes / Reopen History

## Feedback Section

<Always present, empty by default. Any agent appends `### Feedback N - YYYY-MM-DD - Agent - short descriptor`. Append-only; a correction is a new entry, never an edit. Never prune this section for being empty.>

## Agent Change Log

| Date and Time       | Agent     | Model   | Action  | Scope   |
|---------------------|-----------|---------|---------|---------|
| YYYY-MM-DD-HH:mm:ss | <agent>   | <model> | Created | <scope> |
```

The task's Definition of Done is not a standalone section — it lives in the `## Prompt Contract` section's DEFINITION OF DONE clause.

For compact tasks, allow:

- `## Context`
- `## Prompt Contract` (the mandatory minimal contract: GOAL + DEFINITION OF DONE + FAILURE)
- `## Checklist`
- `## Validation`
- `## Estimated Effort` using the mandatory full `Phase | Sessions | 🟣 | Complexity` table

## Mandatory Estimated Effort

Every durable task at every depth, including Compact tasks and `_mini_task_pending.md` tasks, must include this full estimated-effort table shape unless Unicode rendering is confirmed broken:

```markdown
| Phase | Sessions |    🟣    |                                            Complexity                                            |
|-------|----------|----------|--------------------------------------------------------------------------------------------------|
|   A   |    0.5   |    🟢    |                 Trivial - surgical setup, rename, or documentation-only work                     |
|   B   |     1    |    🟡    |                 Medium - multiple coordinated edits or ports with moderate verification          |
|   C   |    1.5   |    🔴    |                 Hard - integration risk or runtime-sensitive behavior                            |

**Total: ~3 sessions.** [One sentence explaining where most of the risk or effort sits.]
```

Keep the raw Markdown table vertically aligned in the editor: pad cells with spaces as needed so every `|` for each column stacks under the matching `|` above and below it.

The `🟣` column header is required for every durable task. It means "colored effort marker"; it labels the marker column and does not assign a difficulty by itself. Use these row markers consistently:

- `🟢` = Trivial or Easy
- `🟡` = Medium
- `🔴` = Hard

Include task phase letters, session-count estimates, colored markers, explanatory complexity text, and a total estimate line below the table. Do not use a simpler two-column `Phase | Effort` style for Compact, Standard, Deep, or mini tasks.

For reopened tasks, add or update:

```markdown
## Notes / Reopen History

- [YYYY-MM-DD] Reopened because [reason]. Previous completed work remains preserved below/above.
```

## Delegation Field

Every task carries a `**Delegation:**` line under `## Context`. It defaults to `N/A` and is a pointer, nothing more.

If this task's work was divided among multiple agents, the `delegate-this` skill fills it with the delegation record's path. `finalize-task` reads it at closure and prompts the user to close the delegation too. That is the field's entire purpose.

Do not populate this field yourself. Do not reason about delegation, routing, platforms, or assignment packets in this skill — that logic lives in `delegate-this`, and this skill has no dependency on it. A task with `**Delegation:** N/A`, or a task predating this field, is complete and correct.

## Child Numbering (Outside Delegation)

Tasks can be **children** of a parent task even outside any delegation — for example, when one large task is split into a parent and sub-tasks. This skill understands the lowercase child-numbering grammar enough to **allocate the next child suffix** and **obey a reserved prefix**; it does **not** absorb the delegation workflow.

Grammar (shared with `delegate-this`):

- independent / parent task: `N.)`
- independent mini task with no parent: `N.)`
- child task (mini or not): `Na.)`, `Nb.)` … `Nz.)`, then `Naa.)`, `Nab.)` …
- the parent's permanent `N` is inherited by every child **in the Task family**.

**Separate namespace anchor.** The Task family's master `N` comes from the Plan/Task Subject namespace only. It is independent of any Delegation record number or Summary family number — those are separate artifact-type namespaces with their own anchors, connected to the Task by explicit path pointers, not by a shared number. Do not scan the Delegation or Summary folders to choose a Task number, and do not expect the numbers to match.

How to assign a child prefix when parenthood applies:

1. **Infer parenthood** from explicit user direction ("this is a sub-task of …") or clear context. **Ask when parenthood is ambiguous** — do not guess.
2. **Scan the parent's existing lowercase children** across **both** `Archive\Live\Tasks\[Subject]\` and `Archive\Historical\Tasks\[Subject]\` (files matching `Na.)` … `Nz.)`, `Naa.)` … for the same parent `N`) to see which suffixes are taken.
3. **Allocate the next suffix** in alphabetical order, skipping any taken.
4. **Obey an orchestrator-reserved prefix exactly** when one is supplied (for example, when `delegate-this` reserved `1a.)` for this task). Never invent or renumber a reserved prefix.

The child prefix is **permanent**. It survives `_pending.md` ↔ `_done.md` renames and Live ↔ Historical moves; `finalize-task` preserves it through finalization and reopening. An independent mini task with no parent uses the plain `N.)` form, not a child suffix.

## Task Style Rules

Task files should be easy to scan and act on inside an editor.

For Standard and Deep tasks:

- include a top `Status:` line
- include a top `Task lifecycle:` line
- include the mandatory `## Prompt Contract` section; its DEFINITION OF DONE clause is the task's Definition of Done (no standalone `## Definition of Done` section)
- use checkboxes for concrete task steps
- use standard Markdown checkboxes: `- [ ]` for pending work and `- [x]` only for completed or user-confirmed work
- use `Pending Phase ⌛` headings for active phase sections when phases are needed
- separate current work from completed/reopened history
- include validation steps that prove the housekeeping task is actually complete
- include scope boundaries when the task touches workspace structure, global files, generated files, or restricted paths

For every task depth and output mode:

- use standard Markdown checkboxes: `- [ ]` for pending or unverified work and `- [x]` only for work proven complete
- require checkboxes for both concrete actions and verification/validation criteria
- preserve completed checkboxes as historical evidence rather than deleting them

For every durable task, including Compact and mini tasks:

- include `## Estimated Effort`
- require the full `Phase | Sessions | 🟣 | Complexity` table
- require the colored effort markers `🟣`, `🟢`, `🟡`, and `🔴` and use the appropriate marker in each effort row
- include a total sessions estimate line below the table
- keep the raw Markdown table pipes vertically aligned

Colored unicode markers (`🟣`, `🟢`, `🟡`, `🔴`) are required in `Estimated Effort` for every durable task. This requirement applies only to the `Estimated Effort` table, not every table in the task. If Unicode rendering is a confirmed concern, use the plain labels above, record that fallback in the task, and report the fallback to the user in chat.

Use status markers:

- `Pending ⌛`
- `In Progress`
- `Complete`
- `Blocked`
- `Reopened`
- `Optional / Pending`

Do not mark a task complete unless the user confirms completion or the session evidence clearly proves the Definition of Done has been satisfied.

## Output Rules

Task files belong in the workspace's task directory, which lives under `Archive/`, nested inside a `[Subject]` folder (`<project root>\Archive\Live\Tasks\[Subject]\` by default). If the workspace contract defines a different task directory, use that instead.

If the output directory is missing, create it only when file creation is allowed.

**Archive folder rule.** Tasks always live under `Archive/`, inside a `[Subject]` folder (in `Archive/Live/Tasks/[Subject]/`). If the `Archive/` folder does not yet exist in the workspace, create it yourself — along with the needed `Live/Tasks/[Subject]/` subfolders — when file creation is allowed. Never redirect the task into any other folder (such as `Documentation/` or a separate top-level `Tasks/` outside `Archive/`) as a fallback, and never save a task flat under `Tasks/` without a Subject folder. The task folder always nests inside `Archive/`.

After creating or updating a task, report the task path and summarize the change. Do not paste the entire task into chat unless the user asks.

Also report the `Estimated Effort` marker outcome in chat:

- If the `🟣` marker column and colored row markers were created successfully, say: `Estimated Effort table created with 🟣 effort markers. Good to go.`
- If Unicode rendering issues forced a plain-label fallback, say: `Unable to use 🟣 effort markers in the task due to rendering issues. I recorded the fallback in the task. Say the word and I'll try to redo that section.`

If the user asked for the task only in chat, do not create, update, rename, or finalize any file. Provide the in-chat task/checklist, include the full colored `Estimated Effort` table unless the user explicitly asks to omit it, and explicitly say no durable task file was changed.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to durable task artifacts and every later material task revision.

For every in-scope artifact:

- place an `## Agent Provenance` section immediately after the artifact's opening block -- its title, status, and lifecycle lines -- carrying `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role`, in that order;
- record `Original writing LLM` as the model that produced the artifact, kept distinct from the agent family that performed the write; use `Not recorded` when the model is genuinely unknown, and never infer it from the agent label or backfill it later;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`, `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` as the last section, or immediately above any section the artifact already reserves for the last position, rendered as a five-column `Date and Time | Agent | Model | Action | Scope` table with one row per material edit;
- stamp every change-log row `YYYY-MM-DD-HH:mm:ss` on a 24-hour clock, read from the machine clock and never estimated; leave historical date-only rows exactly as written rather than backfilling them, because a log carrying both shapes is correct and the boundary between them is itself information;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves to `Uzo`; do not confuse content ownership with the agent that performed the filesystem write. Do not inject provenance into product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill owns task content, Prompt Contract, checklists, estimates, Subject, permanent number, path, update/reopen behavior, and lifecycle. When co-invoked with `html-this` or `pdf-this`, run the full task workflow and save only the requested `.html` or `.pdf` durable artifact unless the user requests multiple formats. All Markdown-described structure remains semantically mandatory; only serialization changes.

Treat same-stem `.md`, `.html`, and `.pdf` variants as one task and one numbering entry. On update or reopen, preflight and update/move every sibling together. This section overrides `.md`-only examples only for the co-invoked run; `_pending`, `_mini_task_pending`, and done lifecycle semantics remain.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

This rule is **emitted into** every artifact this skill produces, adjacent to the DEFINITION OF DONE or Verification Checklist it governs — not buried in a trailing notes section. The executing agent must read it inside the artifact it was handed, without consulting any workspace contract.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

## Feedback Section

Every artifact this skill creates carries a `## Feedback Section`, **present and empty by default**, placed immediately above the `## Agent Change Log`.

The section exists so agents can talk to each other through the artifact instead of through a chat session neither of them shares. An orchestrator writes what it needs verified; a verifier writes what it found; the implementer writes back what it changed. Each reads what the others left, across platforms and across sessions.

Entries are append-only and numbered:

```markdown
## Feedback Section

### Feedback 1 - 2026-08-03 - Hermes Agent - Initial implementation

[what was done]

### Feedback 2 - 2026-08-03 - Bolu (Codex sub-agent) - Independent verification

[what was found, and what remains]
```

Rules:

- The parent heading is `## Feedback Section` and is always present, even with no entries.
- Each entry is `### Feedback N - date - agent - short descriptor`, numbered from 1 and never renumbered.
- Earlier entries are immutable. A correction is a **new** entry, never an edit to an old one.
- Entries may nest `####` sub-detail (an evidence ledger, a scenario table) inside a single entry.
- An empty Feedback Section is correct and must never be pruned for being empty.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

**Availability guard.** Confirm `markdown-table-aligner` is loaded before writing the final artifact. If it is unavailable, pause and tell the user that deterministic alignment cannot run; continue with the portable manual rule only if the user explicitly approves that fallback.

For an in-scope Markdown file or staged Markdown source:

1. Run the aligner's read-only `check`.
2. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. Do not reject or rework the table solely because a particular editor, emoji fallback font, or proportional renderer shows a residual pixel-level offset.
3. If exit `1` contains only safe padding findings, run `format` to a distinct nonexistent staged path, review the diff, adopt the staged result, and rerun `check`.
4. If exit `1` contains overflow, malformed, or ambiguous findings, make the editorial repair manually and rerun the helper; the script never chooses truncation text or overflow notes.
5. Exit `2` is an operational failure. Stop rather than falling back silently or treating raw character count as authoritative.
6. Preserve the complete portable Markdown Table Alignment rule below. The helper supplements it and never replaces it.

For HTML or PDF requested from Markdown, run the helper against the exact Markdown source packet before serialization. Chat-only tables continue to use the portable manual rule until block/stdin input is separately implemented.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;
- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm a newly produced artifact actually carries the Checklist Tick Discipline rule verbatim, since the section can survive in this skill while the template silently loses it;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;
- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After creating or updating a task:

- confirm the file exists
- confirm the file is nested inside a `[Subject]` folder under `Archive\Live\Tasks\` — never saved flat directly under `Tasks\`
- confirm the `N.) ` number is the max across the Subject's combined `Live` + `Historical` folders plus one, and that the `[Subject]` folder itself is unnumbered
- if reopening a done task, confirm it was moved from `Archive\Historical\Tasks\[Subject]\` back to `Archive\Live\Tasks\[Subject]\` with its `N.) ` number unchanged and prior completed evidence preserved
- confirm the filename ends in `_pending.md`, `_done.md`, `_mini_task_pending.md`, or `_mini_task_done.md` as appropriate
- confirm UTF-8 text was used
- confirm the top status and lifecycle lines exist for Standard and Deep tasks
- confirm a `## Prompt Contract` section exists with a DEFINITION OF DONE clause (the task's authoritative Definition of Done); confirm no standalone `## Definition of Done` section was written
- confirm every task at every depth and output mode contains Markdown action and verification/validation checklists
- for phased Standard and Deep tasks, confirm every phase has a Goal, Tasks checklist, Verification checklist, and status
- for non-phased Standard and Deep tasks, confirm `## Task Checklist` and `## Validation` contain checkboxes
- for Compact and mini tasks, confirm both `## Checklist` and `## Validation` contain checkboxes
- confirm every new or unverified item is `[ ]`, every `[x]` item has user confirmation or recorded evidence, and no checklist section substitutes plain bullets for required checkboxes
- confirm completed checklist items were preserved as history; if any item was reopened, confirm it was returned to `[ ]` with a dated explanation
- when DEFINITION OF DONE contains independently verifiable items, confirm they are checkboxes following the Uzzy SR Plan 21 pattern
- confirm a `**Delegation:**` line exists under `## Context`, reading `N/A` unless `delegate-this` populated it
- if the task is a **child** of a parent task, confirm its lowercase child prefix (`Na.)`, `Nb.)`, …) is the next free suffix for that parent across the combined Live + Historical Subject folders — or exactly matches an orchestrator-reserved prefix — and that parenthood was inferred from clear direction/context (not guessed when ambiguous)
- confirm the Prompt Contract is embedded verbatim in the artifact and, unless the `prompt-contracts` skill was unavailable, was authored through it; confirm it was pasted into chat only if the user opted in
- confirm validation steps are present
- for every durable task, including Compact and mini tasks, confirm the `Estimated Effort` table uses the full `Phase | Sessions | 🟣 | Complexity` shape, includes colored row markers, keeps raw Markdown pipes vertically aligned, and includes a total estimate line
- for every durable task, confirm the final chat response reports either successful `🟣` marker usage or the explicit Unicode fallback message
- report any missing source references or unresolved decisions

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
