---
name: imp-upd-task
description: Create or update pending workspace housekeeping and admin task files with checklists, Definition of Done, scope boundaries, validation steps, mandatory colored estimated-effort tables at every task depth, and pending/done lifecycle handling. Use when the user asks for /imp-upd-task, create task, update task, task checklist, housekeeping task, admin task, or clear equivalents.
---

# Imp Upd Task

Create or update a workspace task file for general housekeeping and admin work. A task here is non-product backbone work that keeps files, folders, skills, plans, summaries, documentation, workflows, or workspace structure organized and in sync.

This skill is a lighter sibling to implementation-plan workflows. Use it for operational tasks and maintenance checklists, not for durable implementation plans that require phased product or architecture work.

If the user asks for a task "in house", "in chat", "chat only", or clearly says they do not want a durable file, do not create or update a task artifact. Provide the task/checklist in chat only and make clear that no file was changed.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/imp-upd-task`
- `use imp-upd-task`
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
4. Update the status and lifecycle lines to show that the task was reopened.

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

Default directory:

```text
Tasks/
```

If the workspace contract specifies a different task directory, use that contract path instead. If no task directory exists and the workspace contract is silent, ask before creating a new top-level task directory.

Filename format:

```text
N.) {area_or_component}_{main_task}_pending.md
```

Mini task filename format, only when the user explicitly asks for a "mini task":

```text
N.) {area_or_component}_{main_task}_mini_task_pending.md
```

`N` is the next available integer in the task directory, starting from `1`. If the task directory is empty, use `1`. If existing task files already use the `N.) ` prefix, increment past the highest existing number. The numeric prefix survives the `_pending.md` → `_done.md` rename — do not renumber on finalization.

Generate the body of the filename from the task area/component and main task. Use lowercase letters, digits, and underscores for the body. Do not ask the user for the filename unless the derived name would be ambiguous or misleading.

## Required Inputs

Before writing a new task, make sure these are known or safely inferable:

1. Task Area / Component
2. Main Task
3. What Needs To Be Done
4. Definition of Done
5. Output Task Directory
6. Scope Boundaries
7. Task Depth

Use this prompt shape when information is missing:

```text
We need to define this task before writing it.

How these fields determine the task path:
- Task Area / Component becomes the leading part of the filename.
- Main Task becomes the rest of the filename body.
- Together they produce `N.) {area_or_component}_{main_task}_pending.md` directly under the workspace's task directory, where `N` is the next available integer (start at `1`).
- If the user explicitly asked for a mini task, use `N.) {area_or_component}_{main_task}_mini_task_pending.md` instead.

1. Task Area / Component:
2. Main Task:
3. What Needs To Be Done:
4. Definition of Done:
5. Output Task Directory:
6. Scope Boundaries:
7. Task Depth:
```

Definition of Done means the series of constraints and technical specifications required for the agent or user to conclude that a task is complete.

For Scope Boundaries, tell the user:

```text
Scope boundaries mean what should be included, excluded, deferred, or treated as read-only. If you are not sure, say `delegate` and I will infer sensible boundaries from the workspace rules and the task.
```

For Task Depth, use:

- `Compact`: short checklist for a small housekeeping task, still including the mandatory full colored `Estimated Effort` table
- `Standard`: polished task with lifecycle note, context, checklist, Definition of Done, validation, and boundaries
- `Deep`: full phased task for multi-step workspace maintenance, sync, validation, or migration work

Default to `Standard` unless the task is clearly tiny or clearly complex.

If the user explicitly asks for a "mini task", default to `Compact` depth unless they also ask for Standard or Deep detail. "Mini" controls the filename suffix and expected brevity; it does not bypass the normal task lifecycle rules or the mandatory full colored `Estimated Effort` table.

## Task Template

For standard and deep tasks, use these sections when applicable:

```markdown
# [Task Area / Component] - [Main Task]

Status: PENDING ⌛ - created [YYYY-MM-DD].

Task lifecycle: PENDING on [YYYY-MM-DD]. [One sentence explaining what this task covers.]

## Context

## Scope Boundaries

## What Needs To Be Done

## Definition of Done

## Task Checklist

## Validation

## Estimated Effort

## Notes / Reopen History
```

For compact tasks, allow:

- `## Context`
- `## Checklist`
- `## Definition of Done`
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

## Task Style Rules

Task files should be easy to scan and act on inside an editor.

For Standard and Deep tasks:

- include a top `Status:` line
- include a top `Task lifecycle:` line
- include a clear `Definition of Done` section
- use checkboxes for concrete task steps
- use standard Markdown checkboxes: `- [ ]` for pending work and `- [x]` only for completed or user-confirmed work
- use `Pending Phase ⌛` headings for active phase sections when phases are needed
- separate current work from completed/reopened history
- include validation steps that prove the housekeeping task is actually complete
- include scope boundaries when the task touches workspace structure, global files, generated files, or restricted paths

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

Task files belong in the workspace's task directory. If the workspace contract does not define one, prefer `Tasks/` only after confirming that directory with the user or detecting it already exists.

If the output directory is missing, create it only when file creation is allowed.

After creating or updating a task, report the task path and summarize the change. Do not paste the entire task into chat unless the user asks.

Also report the `Estimated Effort` marker outcome in chat:

- If the `🟣` marker column and colored row markers were created successfully, say: `Estimated Effort table created with 🟣 effort markers. Good to go.`
- If Unicode rendering issues forced a plain-label fallback, say: `Unable to use 🟣 effort markers in the task due to rendering issues. I recorded the fallback in the task. Say the word and I'll try to redo that section.`

If the user asked for the task only in chat, do not create, update, rename, or finalize any file. Provide the in-chat task/checklist, include the full colored `Estimated Effort` table unless the user explicitly asks to omit it, and explicitly say no durable task file was changed.

## Validation

After creating or updating a task:

- confirm the file exists
- confirm the filename ends in `_pending.md`, `_done.md`, `_mini_task_pending.md`, or `_mini_task_done.md` as appropriate
- confirm UTF-8 text was used
- confirm the top status and lifecycle lines exist for Standard and Deep tasks
- confirm a `Definition of Done` section exists
- confirm validation steps are present
- for every durable task, including Compact and mini tasks, confirm the `Estimated Effort` table uses the full `Phase | Sessions | 🟣 | Complexity` shape, includes colored row markers, keeps raw Markdown pipes vertically aligned, and includes a total estimate line
- for every durable task, confirm the final chat response reports either successful `🟣` marker usage or the explicit Unicode fallback message
- report any missing source references or unresolved decisions

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
