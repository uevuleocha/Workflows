---
name: delegate-this
description: Orchestrate and route a substantial objective, plan, task, build, or backlog across multiple agents. Mode A creates a durable, immutable cross-platform delegation record with one self-contained assignment packet per platform (Claude Code, Codex, zCode, Hermes, Antigravity) for the user to carry; Mode B directly coordinates native in-platform subagents. Supports serial, parallel, and mixed execution waves, one-editor-per-file ownership, reviewer/resolver loops, cost and trust constraints, and main/mini plan and task linkage. Use when the user invokes /delegate-this, delegate-this, delegate this, help me delegate this, split this between agents, delegate this across platforms, delegate this to subagents, or clear equivalents asking for this named delegation workflow.
---

# Delegate This

Divide a substantial objective among multiple agents, dispatch clear assignments, track returns, and integrate the result without losing the parent objective.

This is a general-purpose orchestration and workload-routing skill. It is not merely a command to spawn several agents, and it is not tied to any one workspace or backlog.

You may begin from any of these states:

- **A raw objective** — the user wants to build, fix, research, migrate, or design something substantial.
- **An evolved discussion** — brainstorming or planning has reached a delegatable direction.
- **An existing main plan or main task** — the authoritative objective is already durable.
- **A backlog** — prompts, bugs, roadmap items, test failures, docs, or feature requests must first be reconciled, then routed.

One orchestrator understands the whole objective, divides ownership safely, identifies dependencies, decides serial/parallel/mixed execution, dispatches, tracks returns, and integrates.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, approval gates, and product-code workflow defined there apply unchanged. Delegation never grants a receiving agent authority the host contract withholds.

## UTF-8 Rule

Write every delegation record, packet, plan, and task in UTF-8. Never rely on the Windows default encoding.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/delegate-this`
- `delegate-this`
- `use delegate-this`
- `use the delegate-this skill`
- `delegate this`
- `help me delegate this`
- `split this between agents`
- `delegate this across platforms`
- `delegate this to subagents`
- clear equivalents asking for this named reusable delegation workflow

If the user only wants to think out loud about splitting work, do not create files. Use `brainstorm`, then return here when a delegatable direction exists.

---

## The Compulsory Parent Rule (Mode A only)

**A Mode A delegation must always have a parent plan and/or task. A plan or task need not have a delegation.**

This asymmetry is mandatory and enforced here, never in the plan/task skills. It is what makes a dispatched record discoverable at finalization time instead of silently orphaned.

**Mode B does not require a parent.** Mode B creates no durable delegation record, so there is nothing to orphan. If a suitable parent already exists, reuse it and link any durable mini artifacts to it. If none exists, that does not block Mode B. You may still create a plan or task when the work independently merits durable tracking — but that is a **tracking decision, not a delegation prerequisite.** Never manufacture a parent just to satisfy this rule in Mode B.

Before creating any delegation record or dispatching any Mode A packet, resolve the parent:

1. **If a parent plan/task clearly exists** in the current context — the user named it, or the session has been working from it — attach it. Do not ask.
2. **If it is unclear whether one exists**, ask:

   ```text
   A delegation always needs a parent plan and/or task to hang from.
   Do you already have one for this objective?

   - If yes, point me at it and I will attach it.
   - If no, I will create one with you before dispatching.
   ```

3. **If none exists**, create it now by invoking `imp-upd-plan` (for implementation work) and/or `imp-upd-task` (for housekeeping/admin work) with the objective's context pre-filled. Let the user verify it before dispatch.

Then establish **bidirectional linkage**:

- The delegation record names its parent plan/task path in its metadata.
- The parent plan/task names the delegation record path in its `Delegation` field.

**Availability guard for the parent skills.** Before authoring a parent, confirm `imp-upd-plan` / `imp-upd-task` are loaded.

- If NOT available, pause and tell the user:
  > The `imp-upd-plan` / `imp-upd-task` skill is not loaded. A delegation requires a parent plan or task. Please make it available, or tell me to continue and author the parent inline.
- If the user continues, author the parent inline in that skill's shape and note the substitution in the final report.
- Never silently dispatch a parentless delegation.

**Writing the backlink.** If the parent already carries a `Delegation` field (from a `delegate-this`-aware `imp-upd-plan` / `imp-upd-task`), fill it. If the parent predates that field, add the field yourself under the parent's `## Context` section, using the shape in `references/mode-a-delegation-template.md`. Prompt the user before editing a parent file they did not ask you to touch.

---

## Modes

Pick the mode from context. If genuinely ambiguous, ask one short question.

### Mode A — Cross-Platform Delegation

Delegate to user-authorized **external** coding-agent platforms. You normally **cannot message those platforms directly**. You create one durable delegation record holding shared context plus a self-contained assignment packet per platform. The user carries that same file to every assigned platform.

Never claim you contacted another platform unless the runtime genuinely provides that capability.

Mode A workflow:

1. Confirm the objective and resolve the **compulsory parent** (above).
2. Confirm which supported platforms are **available and authorized for this run**. Never assume all five.
3. Confirm forbidden platforms/providers and whether any paid API use is permitted. Default: no.
4. Reconcile the work, dependencies, risk, and file ownership.
5. Decide serial, parallel, or mixed execution waves.
6. Create mini plans/tasks where useful, or explicitly instruct a receiving agent to investigate first and then create its own mini artifact.
7. Create the delegation record and show the **assignment overview** in chat.
8. Explain launch order and return/handoff instructions.
9. Reconcile returned work before declaring the parent objective complete.

### Mode B — Within-Platform Delegation

Use native subagents or agent teams on the active platform. Mode B does **not** create a delegation record merely for dispatch, because you can feed instructions to your subagents directly. **Mode B is also parent-optional** — see `The Compulsory Parent Rule (Mode A only)`. Create a plan or task only when the work independently merits durable tracking.

Mode B workflow:

1. Detect the native delegation capabilities that **actually exist** on this host.
2. Support serial, parallel, and mixed subagent execution.
3. Create or reference mini plans/tasks when the delegated work merits durable tracking.
4. Assign non-overlapping ownership; respect one-editor-per-file.
5. Use reviewer/resolver loops when risk or complexity justifies them.
6. Keep one orchestrator/integrator responsible for the complete outcome.
7. Report the assignment/model overview in chat after dispatch.
8. State plainly when the host cannot programmatically select or expose a requested subagent model.

**Subagents are an execution mechanism, not a synonym for parallelism.** A Mode B orchestrator may spawn Agent A, wait for its prerequisite, then spawn Agent B.

---

## Delegation Record — Location and Lifecycle

A delegation is a **lifecycle artifact**, sibling to plans and tasks. Its *content* is immutable after dispatch; its *state* is not.

```text
Dispatched:  <Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md
Completed:   <Workspace>\Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md
```

Rules:

- Mode A creates the record at the **Live** path with the `_dispatched` suffix. A dispatched delegation is an open obligation.
- `finalize-delegation` — and only that skill — renames `_dispatched` → `_completed` and moves the file to **Historical**.
- **Subject folders are never numbered.**
- **`N` is lifecycle-agnostic and permanent.** Calculate it as one greater than the highest numeric prefix found across **both** the Live and Historical Delegations folders for that Subject. Checking only the Live folder will silently reuse a number already taken by a completed record that has moved to Historical.
- Assign `N` once. Never reclaim gaps, never renumber during finalization, never change it on a future reopen.
- The record is **not the active execution tracker**. Parent and mini plans/tasks track execution and stay Live while unfinished.
- After dispatch, do not routinely rewrite the record. Actual model choices and results belong in handoffs, session summaries, or the parent artifact.
- Session summaries used for handoffs are Historical records.
- `<Workspace>` is the active workspace root. If it has no `Archive/` folder, create `Archive\Live\Delegations\` when file creation is allowed. Never redirect the record elsewhere. Never hardcode a specific user's workspace path.

The record contains:

1. Metadata and objective.
2. Parent plan/task paths (mandatory) and mini artifact paths.
3. Shared context and global constraints.
4. Dependency and execution-wave explanation.
5. Assignment overview.
6. One assignment packet per platform/agent.
7. Launch instructions for the user.
8. Return and integration instructions.
9. Global stop conditions.

Use `references/mode-a-delegation-template.md`.

Every receiving agent may read the entire record for context but must primarily execute **only the packet addressed to its platform and assigned role**.

### Finalization

When every assignment has returned and the parent objective is integrated, the delegation is finished. Do **not** finalize it here.

- Direct the user to `finalize-delegation`. **Only that skill may change a delegation's lifecycle state, suffix, or Live/Historical location.**
- **There is no manual move/rename fallback.** If `finalize-delegation` is not loaded, stop. Leave the record `_dispatched` exactly where it is, name the missing skill, and point the user at its install route:
  > This delegation is ready to close, but the required `finalize-delegation` skill is not loaded. I am leaving the record `_dispatched` rather than moving it by hand — a manual move skips the return-and-integration verification and the parent-pointer repair, which is how records get silently orphaned. Install `finalize-delegation` from the local master (see its `README.md`) or re-run `global-sync`, then run it.
- Never instruct the user to move or rename the record themselves, and never do it yourself.
- When the parent plan/task is finalized, `finalize-plan` / `finalize-task` will see the `Delegation` pointer and prompt the user to run `finalize-delegation`. Never mutate the delegation record from a plan/task finalization pass.

---

## Main Plans, Main Tasks, and Mini Artifacts

The parent plan or task remains **authoritative**. Delegation must not replace, fragment, or silently rewrite it.

Any durable plan or task born specifically from delegation is a **mini plan** or **mini task**. This holds whether the orchestrator creates it before dispatch, the receiving agent creates it after investigation, or the branch is serial, parallel, or mixed.

Invoke `imp-upd-plan` / `imp-upd-task` normally, with the necessary context. **Those skills do not need to know the delegation workflow.** They carry only a thin `Delegation` pointer field. All delegation intelligence and parent–child linkage lives here.

Each mini artifact should identify its parent, isolated scope, dependencies, owned surfaces, deliverables, Definition of Done, verification, and handoff destination. The parent should link to the mini artifacts and reflect their results without losing its original structure.

---

## Assignment Packets

Each Mode A packet — and the equivalent Mode B subagent instruction — must include every field below. Use `references/assignment-packet-template.md`.

1. Platform/agent identity
2. Assigned role
3. Execution wave and prerequisites
4. Recommended model, when you have a defensible recommendation
5. Parent plan/task path
6. Mini plan/task path, or instructions to create one after investigation
7. Required reference paths
8. Goal
9. Exact scope
10. Explicit exclusions
11. Owned files/directories, or read-only surfaces
12. Dependencies and expected inputs
13. Deliverables
14. Constraints and safety rules
15. Definition of Done
16. Verification requirements
17. Handoff format and destination
18. Stop-and-return conditions
19. Cost/trust rationale

**Every field is mandatory.** When a field is genuinely inapplicable, retain the line and write `N/A` plus a short reason — never delete it. The Cost/trust rationale field is **never omitted**; when the route needs no defence, write `N/A — routing self-evident`.

A packet must be **self-contained enough that a fresh agent can act** without the user reconstructing your reasoning.

---

## Assignment Overview

Mode A shows the overview in chat **and** in the delegation record. Mode B shows it in chat after dispatch.

Fields: Execution wave · Platform · Agent role · Assignment · Recommended model · Actual model · Parent artifact · Mini artifact · Dependency · Status.

- **Mode A** — `Actual model` may initially read `User to select`.
- **Mode B** — report the actual model when the host exposes it; otherwise `Not exposed by platform`.
- **Never guess a model.**

When rendering as a Markdown table, obey the workspace contract's strict pipe-alignment and 80-character cell cap.

---

## Supported Platforms and Run-Time Authorization

The maintained platform identities are:

1. Claude Code
2. Codex
3. zCode
4. Hermes
5. Antigravity

This list is stable enough to maintain here and may be deliberately updated if the user adds or removes a coding-agent platform. **It is not a list of platforms automatically available for every run.**

Mode A must **ask which platforms are currently available** when the user did not specify. Subscription expiration, usage limits, outages, preference, task sensitivity, or cost may exclude any platform.

Decision order:

1. Understand the work.
2. Confirm the authorized platform set.
3. Confirm provider/model restrictions and paid-use permission.
4. Score and route work **only among the authorized platforms**.

Your preference profile cannot expand the user's authorization.

Routing factors, standing policies, and model-recommendation rules live in `references/routing-and-cost-policy.md`. Read it before routing.

---

## Delegation Hierarchy

Use only the layers the workload warrants:

- **Orchestrator** — understands the full objective, decomposes, assigns ownership, tracks dependencies, coordinates returns, integrates.
- **Workstream lead** — owns one substantial domain/file family when that branch is itself complex.
- **Worker** — completes one bounded research or implementation assignment.
- **Reviewer** — independently checks results, normally without editing.
- **Resolver/integrator** — applies confirmed corrections, joins workstreams.

Small work: orchestrator → workers → integrator. Large work may use all five. **Do not add hierarchy merely for appearance.**

---

## Serial, Parallel, and Mixed Execution

**Parallel** is safe only when workstreams have no unmet dependency and no overlapping write ownership.

**Serial** is required when Agent B needs Agent A's output, a user checkpoint, a build artifact, a schema decision, or an integration state.

**Mixed is first-class.** Example:

1. Research agent maps the system.
2. Two implementation agents work on separate owned surfaces in parallel.
3. Reviewer checks the combined result.
4. Resolver/integrator applies confirmed findings.

Mode A explains launch order to the user. Mode B activates subagents at the correct time rather than spawning everything immediately.

---

## Ownership, Review, and Integration Safety

**One editor per file is mandatory.** Identify overlapping surfaces before dispatch and either assign a single writer or serialize the edits.

Reviewers should normally be read-only. Confirmed findings go to a resolver or the orchestrator.

Before completion, compare returned work against the parent objective, every mini artifact, the shared constraints, and the Definition of Done.

If agents return **conflicting solutions, do not silently pick one.** Explain the conflict, compare evidence and tradeoffs, and resolve it through the user or an explicit integrator decision.

**Dispatch is not completion.** Never mark the parent objective complete merely because assignments were sent.

---

## Backlog Reconciliation

When the input is a collection rather than a single objective, reconcile before routing:

1. Inventory items.
2. Determine which are **Done** or **Not done** using current evidence.
3. For Not done work, note whether it is **Partly done** or **Completely not done**.
4. Detect overlap, supersession, dependencies, and shared ownership.
5. Bundle overlapping unfinished items so the **newer direction is authoritative** and older requirements remain a completeness checklist.
6. Route only the remaining work.

A prompt backlog is an explicitly supported example. Do not hardcode any workspace's paths or prompt list. The same logic applies to bugs, roadmaps, test failures, migration work, documentation backlogs, and feature requests.

---

## Required Intake

Before dispatch, resolve:

1. Objective, and the **compulsory parent** plan/task.
2. Mode A or Mode B.
3. Authorized platforms (Mode A), or native delegation capability (Mode B).
4. Forbidden platforms/providers/models.
5. Paid API authorization. **Default is no.**
6. Desired or required execution pattern, if the user specified one.
7. Required durable mini plans/tasks.
8. File/repository ownership boundaries.
9. User checkpoints and integration authority.
10. Expected final deliverable and Definition of Done.

**Infer safe answers from existing context.** Do not make the user repeat information already in a parent artifact or the current session. Pause only for inputs that materially change routing or authorization — the platform set, paid-use permission, and the parent artifact are always worth pausing for.

---

## Boundaries

Do:

- resolve and bind a parent plan/task before every **Mode A** delegation
- ask which platforms are authorized for this run
- write the Mode A record to `Archive\Live\Delegations\<Subject>\` with `_dispatched`
- calculate `N` across **both** the Live and Historical Subject folders, and assign it once
- produce packets carrying every required field, `N/A` + reason where inapplicable
- distinguish recommended, user-selected, and programmatically confirmed models
- assign exactly one writer per file
- explain launch order and stop conditions
- reconcile returns against the parent Definition of Done before claiming completion

Do not:

- create a **Mode A** delegation with no parent plan/task
- require a parent, or create a delegation record, for Mode B
- move or rename a delegation record yourself, or tell the user to, when `finalize-delegation` is unavailable — stop instead
- reuse an `N` already taken by a completed record in the Historical Subject folder
- omit the Cost/trust rationale field from a packet
- copy this workflow into `imp-upd-plan`, `imp-upd-task`, `finalize-plan`, or `finalize-task`
- assume delegation means parallel execution
- assume every supported platform is available
- hardcode a fast-changing model catalog, or any user's absolute workspace paths
- authorize paid API usage by inference
- give Antigravity high-risk work under the default profile
- let multiple agents edit the same file concurrently
- claim cross-platform communication you did not perform
- mark the parent objective complete because assignments were dispatched
- finalize the delegation record yourself — that is `finalize-delegation`

---

## Validation

After a delegation run, confirm and report:

- for Mode A, the parent plan/task path, and that its `Delegation` field names the record
- for Mode B, that no parent was manufactured and no delegation record was created
- the delegation record path, that it ends in `_dispatched.md`, sits under `Archive\Live\Delegations\<Subject>\`, and carries an `N.) ` prefix one greater than the highest across **both** the Live and Historical Subject folders
- the Subject folder is unnumbered
- every packet carries all 19 required fields, with `N/A` + reason where inapplicable and a Cost/trust rationale always present
- the authorized platform set, and that no unauthorized platform received work
- paid API use was either not used or explicitly approved
- no two agents own the same file for writing
- the assignment overview was shown in chat with pipe-aligned cells ≤80 chars
- for Mode B, whether the host exposed actual models, or `Not exposed by platform`
- that dispatch was not reported as completion

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
