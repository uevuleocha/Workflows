---
name: imp-upd-plan
description: Create or update active implementation plans with checklists, batched/phased outlines, verification steps, mandatory colored estimated-effort tables at every plan depth, and scope boundaries. Use when the user asks for an implementation plan, active plan update, phased checklist, batched outline, "make a plan", "update the plan", "update active plan", or similar planning work. This skill does not finalize plans.
---

# Imp Upd Plan

Create or update an active implementation plan. Plans are durable working artifacts for future implementation sessions, not short chat summaries.

This skill owns active plan creation and active plan updates only. Do not finalize, rename, or archive plans; leave finalization to the separate `finalize-plan` workflow.

If the user asks for a plan "in house", "in chat", "chat only", or clearly says they do not want a durable file, do not create or update a plan artifact. Provide the plan in chat only and make clear that no file was changed.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/imp-upd-plan`
- `use imp-upd-plan`
- `implementation plan`
- `update the plan`
- `update active plan`
- `make a plan`
- `phase this out`
- `checklist and batched outline`
- clear equivalents asking for a durable active implementation plan or active plan revision

If the user asks to finalize a plan, do not do it with this skill. Direct them to the `finalize-plan` workflow.

## Required Review

Review only the sources needed to create or update the plan accurately:

1. The project's canonical contract (e.g. `CLAUDE.md`)
2. User-named reference files
3. User-referenced active plan, if any
4. Existing plans under `<project root>\Archive\Plans\` when needed to decide create vs update
5. Relevant source files only when needed to understand scope, anchors, or feasibility

Do not perform a broad repository audit unless the plan request genuinely requires it.

## Create Vs Update Decision

When the user's intent is vague, ask clarifying questions before writing. Do not infer too aggressively from the presence of one matching active plan.

Use update mode when:

- the user explicitly references an existing active plan
- the user says to update, revise, continue, extend, or add to a plan
- the user provides task details that clearly match exactly one existing `_plan_active.md` **and** does not imply a new standalone plan
- the user explicitly references an existing finalized plan and asks to update, revise, continue, reopen, extend, or add to it

Use create mode when:

- no existing matching active plan is found
- the task is clearly separate from existing active plans
- the user explicitly asks for a new plan
- the user provides a specific new filename ending in `_plan_active.md`

Ask before writing when:

- multiple plausible active plans match
- exactly one active plan matches, but the user also says or implies `new plan`, `separate plan`, `for this`, `standalone`, or gives new plan metadata
- the task could reasonably be folded into an existing active plan or created as its own focused plan
- the target filename, directory, project/component, scope boundaries, or plan depth is unclear
- the user provides a vague request such as "make/update a plan for this" without enough context to choose create vs update confidently

When matching existing plans, inspect `<project root>\Archive\Plans\` for `_plan_active.md` and `_plan_finalized.md` files and compare project/component names, primary files, task phrases, and current plan titles.

## Plan Lifecycle

Plan files use this lifecycle:

- `_plan_active.md` means the plan is open or still needs action.
- `_plan_finalized.md` means the plan was completed and closed through the `finalize-plan` workflow.
- `_mini_plan_active.md` means the user explicitly asked for a mini plan and the plan is open or still needs action.
- `_mini_plan_finalized.md` means a mini plan was completed and closed through the `finalize-plan` workflow.

When creating a new durable plan, the filename must end in `_plan_active.md`.

When the user explicitly asks for a "mini plan", the filename must end in `_mini_plan_active.md` instead. Preserve the `mini_plan` marker through lifecycle renames, so finalization produces `_mini_plan_finalized.md` and reopening returns to `_mini_plan_active.md`.

When the user wants to update an existing `_plan_finalized.md` plan, reopen it gracefully:

1. Preserve the previous finalized work, completion evidence, and finalization notes.
2. Add a new phase, checklist section, or dated update section that explains why the plan is active again.
3. Rename the plan file from `_plan_finalized.md` back to `_plan_active.md`.
4. Update the status and lifecycle lines to show that the plan was reopened.
5. Leave finalization for a later explicit `finalize-plan` pass after the user verifies the reopened work.

Do not delete prior completed sections just because a finalized plan has been reopened.

## Create Mode

Default directory:

```text
<project root>\Archive\Plans\[Project]\
```

Filename format:

```text
N.) {primary_file_or_component}_{main_task}_plan_active.md
```

Mini plan filename format, only when the user explicitly asks for a "mini plan":

```text
N.) {primary_file_or_component}_{main_task}_mini_plan_active.md
```

`N` is the next available integer in the target plan directory, starting from `1`. If the directory is empty, use `1`. If existing plan files already use the `N.) ` prefix, increment past the highest existing number. The numeric prefix survives `_plan_active.md` -> `_plan_finalized.md` and `_plan_finalized.md` -> `_plan_active.md` lifecycle renames. Do not renumber existing plans during finalization or reopening.

Generate the body of the filename from `Primary File or Main Component` and `Main Task`. Use lowercase letters, digits, and underscores for the body. Do not ask the user for the filename unless the derived name would be ambiguous or misleading.

## Update Mode

When updating an active plan:

- preserve the existing plan's style and structure
- add new decisions, phases, verification items, effort estimates, or out-of-scope notes where they belong
- update statuses only when the user or session evidence supports the status
- keep unrelated sections intact
- do not restyle the whole plan just for consistency
- do not rename `_plan_active.md` to `_plan_finalized.md`

If an update conflicts with the existing plan, record the new user decision clearly in `Locked Decisions` or the relevant phase rather than silently deleting the old context.

## Required Inputs

Before writing a new plan, make sure these are known or safely inferable:

1. Project / Component
2. Main Task
3. Primary File or Main Component
4. Reference Files, optional
5. Output Plan Directory
6. Scope Boundaries
7. Plan Depth

Use this prompt shape when information is missing:

```text
We need to define this implementation plan.

How these fields determine the plan path:
- Project / Component decides the folder under `Archive/Plans`, usually `Archive/Plans/[Project]`.
- Primary File or Main Component becomes the filename prefix.
- Main Task becomes the filename body.
- Together they produce `N.) {primary_file_or_component}_{main_task}_plan_active.md`, where `N` is the next available integer in the target plan directory.
- If the user explicitly asked for a mini plan, use `N.) {primary_file_or_component}_{main_task}_mini_plan_active.md` instead.

1. Project / Component:
2. Main Task:
3. Primary File or Main Component:
4. Reference Files (optional):
5. Output Plan Directory:
6. Scope Boundaries:
7. Plan Depth:
```

Reference files are optional. If the user gives none, inspect likely project files only as needed.

For Scope Boundaries, tell the user:

```text
Scope boundaries mean what should be included, excluded, deferred, or treated as read-only. If you are not sure, say `delegate` and I will infer sensible boundaries from the repo, the project's canonical contract, and the task.
```

For Plan Depth, use:

- `Compact`: short checklist for a small change, still including the mandatory full colored `Estimated Effort` table
- `Standard`: polished phased plan with status/lifecycle note, context, locked decisions when useful, critical files, proposed shape when relevant, phase-by-phase verification, colored effort markers, and out-of-scope items
- `Deep`: full phased plan with strong layout, locked decisions, critical files, proposed implementation or skill shape, phase-by-phase verification, effort estimates, colored difficulty markers, and explicit boundaries

Default to `Standard` unless the task is clearly tiny or clearly complex.

If the user explicitly asks for a "mini plan", default to `Compact` depth unless they also ask for Standard or Deep detail. "Mini" controls the filename suffix and expected brevity; it does not bypass the normal durable-plan lifecycle rules or the mandatory full colored `Estimated Effort` table.

## Plan Template

For standard and deep plans, use these sections when applicable:

```markdown
# [Project/Component] - [Main Task]

Status: ACTIVE / PENDING - created [YYYY-MM-DD].

Plan lifecycle: ACTIVE on [YYYY-MM-DD]. [One sentence explaining what this plan covers.]

## Context

## Locked Decisions

## Critical Files

## Proposed [Skill / Implementation / Workflow] Shape

## Phased Implementation Plan

## Verification Per Phase

## Estimated Effort

For every durable plan at every depth, including Compact plans and `_mini_plan_active.md` plans, the `Estimated Effort` section must use this full estimated-effort table shape unless Unicode rendering is confirmed broken:

```markdown
| Phase | Sessions |    🟣    |                                            Complexity                                            |
|-------|----------|----------|--------------------------------------------------------------------------------------------------|
|   A   |    0.5   |    🟢    |                 Trivial - surgical setup, rename, or documentation-only work                     |
|   B   |     1    |    🟡    |                 Medium - multiple coordinated edits or ports with moderate verification          |
|   C   |    1.5   |    🔴    |                 Hard - integration risk or runtime-sensitive behavior                            |

**Total: ~3 sessions.** [One sentence explaining where most of the risk or effort sits.]
```

Keep the raw Markdown table vertically aligned in the editor: pad cells with spaces as needed so every `|` for each column stacks under the matching `|` above and below it.

The `🟣` column header is required for every durable plan. It means "colored effort marker"; it labels the marker column and does not assign a difficulty by itself. Use these row markers consistently:

- `🟢` = Trivial or Easy
- `🟡` = Medium
- `🔴` = Hard

Use the richer table style from `9.) uzzy_sr_drawing_engine_plan_finalized.md` as the preferred example: include phase letters, session-count estimates, colored markers, explanatory complexity text, and a total estimate line below the table. Do not use a simpler two-column `Phase | Effort` style for Compact, Standard, Deep, or mini plans.

## Open Items Explicitly Out Of Scope
```

For compact plans, allow:

- `## Context`
- `## Checklist`
- `## Verification`
- `## Estimated Effort` using the mandatory full `Phase | Sessions | 🟣 | Complexity` table
- `## Assumptions`

For complex ecosystem work, prefer the polished style used by existing finalized plans in `<project root>\Archive\Plans\`. For large product-code architecture work, also use the full style of existing deep plans when that better fits the project.

## Plan Style Rules

Plans should have good UI. Make the file easy to scan and review inside an editor.

For Standard and Deep plans:

- include a top `Status:` line
- include a top `Plan lifecycle:` line
- use markdown tables for `Locked Decisions`, `Critical Files`, `Verification Per Phase`, and `Estimated Effort`
- include a `Proposed Skill Shape`, `Proposed Implementation Shape`, or equivalent section when the plan is creating a skill, workflow, tool, or architecture
- use clear phase separators with `---` between major phase blocks when the plan is long
- keep phase titles consistent: `### Phase A - [Name] - [Status]`
- include colored status/difficulty markers where they help scanning
- preserve a clean, polished layout comparable to existing finalized plans

For every durable plan, including Compact and mini plans:

- include `## Estimated Effort`
- require the full `Phase | Sessions | 🟣 | Complexity` table
- require the colored effort markers `🟣`, `🟢`, `🟡`, and `🔴` and use the appropriate marker in each effort row
- include a total sessions estimate line below the table
- keep the raw Markdown table pipes vertically aligned

Use phased batches such as `Phase A`, `Phase B`, etc.

Each phase should include:

- goal
- concrete tasks
- verification
- status when known

Use status markers:

- `Complete`
- `Pending`
- `Implemented / Debug Pending`
- `Optional / Pending`

Use difficulty markers:

- `Trivial`
- `Easy`
- `Medium`
- `Hard`

Colored unicode markers (`🟣`, `🟢`, `🟡`, `🔴`) are required in `Estimated Effort` for every durable plan, including Compact and mini plans. This requirement applies only to the `Estimated Effort` table, not every table in the plan. If Unicode rendering is a confirmed concern, use the plain labels above, record that fallback in the plan, and report the fallback to the user in chat.

Include `Locked Decisions` when user clarifications materially shape the plan.

Include `Open Items Explicitly Out Of Scope` when boundaries prevent accidental overreach.

Mention critical files with their role and whether they are editable. For product code, mark direct edits as disallowed unless the user explicitly authorizes them.

## No Finalization

Do not finalize plans in this skill.

Do not:

- rename `_plan_active.md` to `_plan_finalized.md`
- mark every item complete because the user said "final"
- archive or delete plan files
- treat session-summary plan status updates as finalization

If the user asks for finalization, direct them to the `finalize-plan` skill.

## Output Rules

Plans belong under `<project root>\Archive\Plans\`.

If the output directory is missing, create it only when file creation is allowed.

After creating or updating a plan, report the plan path and summarize the change. Do not paste the entire plan into chat unless the user asks.

After creating or updating any durable plan, report the `Estimated Effort` marker outcome in chat:

- If the `🟣` marker column and colored row markers were created successfully, say: `Estimated Effort table created with 🟣 effort markers. Good to go.`
- If Unicode rendering issues forced a plain-label fallback, say: `Unable to use 🟣 effort markers in the plan due to rendering issues. I recorded the fallback in the plan. Say the word and I'll try to redo that section.`

If the user asked for the plan only in chat, do not create, update, rename, or finalize any file. Provide the in-chat plan, include the full colored `Estimated Effort` table unless the user explicitly asks to omit it, and explicitly say no durable plan file was changed.

## Validation

After creating or updating a plan:

- confirm the file exists
- confirm the filename starts with the correct `N.) ` numeric prefix when a durable plan file was created
- confirm the filename ends in `_plan_active.md`, or `_mini_plan_active.md` when the user explicitly requested a mini plan
- if reopening a finalized plan, confirm the file was renamed from `_plan_finalized.md` back to `_plan_active.md`, or from `_mini_plan_finalized.md` back to `_mini_plan_active.md`, and that prior finalized evidence was preserved
- skim the major headings for the chosen plan depth
- for Standard and Deep plans, confirm the top status/lifecycle lines exist
- for every durable plan, including Compact and mini plans, confirm the `Estimated Effort` table uses the full `Phase | Sessions | 🟣 | Complexity` shape, includes colored row markers, keeps raw Markdown pipes vertically aligned, and includes a total estimate line
- for every durable plan, confirm the final chat response reports either successful `🟣` marker usage or the explicit Unicode fallback message
- for Standard and Deep plans, confirm the layout is comparable to existing finalized plans
- report any missing source references or unresolved decisions

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
