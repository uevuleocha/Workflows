---
name: delegate-this
description: Orchestrate and route a substantial objective, plan, task, build, or backlog across multiple agents. Resolves an execution workspace, then creates the whole delegation artifact family (parent, delegation, mini artifacts, session-summary/return-report family) inside it using lowercase child numbering (N.), Na.), Nb.) ...). Mode A writes a durable cross-platform delegation record with one self-contained assignment packet per platform (Claude Code, Codex, zCode, Hermes, Antigravity); Mode B directly coordinates native in-platform subagents. Supports serial, parallel, and mixed execution waves, one-editor-per-file ownership, centrally reserved child prefixes, mandatory return reports with append-only feedback ledgers, per-packet checkpoint policy, provider-neutral Hermes routing, and cost and trust constraints. Use when the user invokes /delegate-this, delegate-this, delegate this, help me delegate this, split this between agents, or clear equivalents asking for this named delegation workflow.
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

```text A delegation always needs a parent plan and/or task to hang from. Do you already have one for this objective?

   - If yes, point me at it and I will attach it.
   - If no, I will create one with you before dispatching.
   ```

3. **If none exists**, create it now by invoking `plan-this` (for implementation work) and/or `task-this` (for housekeeping/admin work) with the objective's context pre-filled. Let the user verify it before dispatch.

Then establish **bidirectional linkage**:

- The delegation record names its parent plan/task path in its metadata.
- The parent plan/task names the delegation record path in its `Delegation` field.

**Availability guard for the parent skills.** Before authoring a parent, confirm `plan-this` / `task-this` are loaded.

- If NOT available, pause and tell the user:
  > The `plan-this` / `task-this` skill is not loaded. A delegation requires a parent plan or task. Please make it available, or tell me to continue and author the parent inline.
- If the user continues, author the parent inline in that skill's shape and note the substitution in the final report.
- Never silently dispatch a parentless delegation.

**Writing the backlink.** If the parent already carries a `Delegation` field (from a `delegate-this`-aware `plan-this` / `task-this`), fill it. If the parent predates that field, add the field yourself under the parent's `## Context` section, using the shape in `references/mode-a-delegation-template.md`. Prompt the user before editing a parent file they did not ask you to touch.

---

## The Execution Workspace

**Resolve the execution workspace before Mode A creates any parent, delegation, mini artifact, or return report.** The execution workspace is the root whose `Archive\` tree will hold the entire delegation family — the parent plan/task, the delegation record, the mini artifacts, and the session-summary / return-report family. Pin it once at the start of the run; every artifact path in the delegation record is resolved relative to it.

Do not resolve a parent, then a delegation, then a return report each against a different workspace. Decide the workspace first, then create the **whole family** (parent, delegation, minis, return reports) inside it. This is what keeps a dispatched delegation's family together instead of spread across roots.

The execution workspace is normally obvious — it is the active workspace root. If it is not (for example, the objective spans two roots), stop and ask which one owns the delegation family before creating anything.

---

## Artifact Family and Lowercase Child Numbering

A Mode A dispatch produces a **family of artifacts** that must stay coordinated. All of them live under the execution workspace's `Archive\` tree, and every file that belongs to a family carries a **lowercase child prefix**. The families are **linked by explicit pointers, not by a shared number.**

The dispatched family has up to three **artifact-type namespaces**, each with its own numeric anchor:

- **Plan/Task family** — the parent plan and/or task, plus its mini plans/tasks.
- **Delegation record** — one record, in its own Delegation Subject namespace.
- **Summary family** — the orchestrator/master summary plus one delegated return report per returning assignment.

### Separate, linked family anchors

**Do not use one shared numeric anchor across different artifact-type namespaces.** Each family gets its master number from its **own** Subject namespace; children inherit that family's master number. Explicit paths and pointers connect the families; their numeric anchors need not match.

| Family            | Master number source                 | Children inherit         |
| ----------------- | ------------------------------------ | ------------------------ |
| Plan/Task         | Its own Plan/Task Subject namespace  | The Plan/Task master `N` |
| Delegation record | Its own Delegation Subject namespace | n/a (one record)         |
| Summary           | Its own Summary Subject namespace    | The Summary master `N`   |

Each anchor is calculated as one greater than the highest top-level `N.)` across that namespace's **own combined Live and Historical** Subject folder. Scanning only one folder (or one artifact-type namespace) for another family's number is how collisions happen — each family scans its own namespace only.

Canonical example:

- Plan family: `1.)` (master, from the Plan Subject namespace); children `1a.)` through `1e.)`.
- Delegation record: `1.)` in its separate Delegation Subject namespace.
- Summary family: `9.)` (master, from the Summary Subject namespace); reports `9a.)` through `9e.)`.

The Plan master (`1.`), the Delegation master (`1.`), and the Summary master (`9.`) are **coincidentally equal in two cases and different in the third — and that is correct.** They are independent anchors. The delegation record, the parent plan, and the master summary name each other by path.

### Child-numbering grammar

| Kind of artifact                             | Prefix shape     | Example |
| -------------------------------------------- | ---------------- | ------- |
| Master / independent artifact in a namespace | `N.)`            | `1.)`   |
| Independent mini artifact with **no** parent | `N.)`            | `1.)`   |
| Child mini artifact / child return report    | `Na.)`, `Nb.)`   | `1a.)`  |
| Second-level child (children of a child)     | `Naa.)`, `Nab.)` | `1aa.)` |

Rules:

- A family's master `N` is **inherited by that family's own children only.** A Plan master `1.)` produces Plan children `1a.)`, `1b.)`, …, then `1aa.)`, `1ab.)`, … after `1z.)`. A Summary master `9.)` produces Summary children `9a.)`, `9b.)`, …. The numbers do not cross families.
- Child suffixes use lowercase letters only, and allocate strictly in alphabetical order: `a`, `b`, …, `z`, then `aa`, `ab`, … .
- The suffix is part of the artifact's **permanent identity**. It survives lifecycle renames, Live ↔ Historical moves, finalization, and reopening. `finalize-plan` / `finalize-task` / `finalize-delegation` **must preserve the complete lowercase child prefix** — never strip the suffix, never renumber it.
- An independent mini artifact with no parent takes the plain `N.)` form, not a child suffix.
- This grammar is owned by `delegate-this`. `plan-this`, `task-this`, and `session-summary` understand it well enough to **allocate the next child suffix** within their own family and **obey a reserved prefix**; they do not absorb the delegation workflow.

### Central prefix reservation

**The orchestrator reserves every child prefix before dispatch.** This is the single source of truth for each family — there is no "create a mini plan later" without reserving its prefix now.

Before writing the delegation record, the orchestrator:

1. resolves the Plan/Task family master `N` (one greater than the highest top-level `N.)` across that Plan/Task Subject's combined Live + Historical namespace), then scans that master's existing lowercase children (`Na.)` … `Nz.)`, `Naa.)` …) across the same combined namespace to reserve the next suffix for each mini plan/task;
2. resolves the Delegation record's own `N` (one greater than the highest across the Delegation Subject's combined Live + Historical namespace) — independently of the Plan/Task number;
3. resolves the Summary family master `N` (one greater than the highest across the Summary Subject's combined Live + Historical namespace), then reserves the next Summary child suffix for each return report;
4. writes each **exact reserved prefix** into the right place — mini-plan prefixes into the **assignment overview**, the **mini-artifact table**, and each **packet**; return-report prefixes into the **session-summary / return-report family table** and each **packet**;
5. records the explicit path pointers that connect the families (the parent plan names the delegation record; the delegation record names the parent and the master summary).

Never write "create a mini plan later" without a reserved prefix. If a mini artifact or return report is genuinely contingent, still reserve its prefix and mark it `(reserved, created after recon)`.

### Session-summary / return-report family

Reserve the session-summary family before dispatch, using the **Summary** master `N` from the Summary Subject namespace:

- **orchestrator / master summary:** `N.)` — the master summary of the whole delegation (e.g. `9.)`).
- **delegated return reports:** `Na.)`, `Nb.)`, … — one per returning assignment (e.g. `9a.)`, `9b.)`, …).

A delegated return report's filename **ends in `Report.md`** (for example, `9a.) claude_packet1_wave1_Report.md`). It is created when the assignment returns, under the execution workspace's `Archive\Historical\Summaries\<Subject>\`. The master summary and every return report share the **Summary family's** master `N`, not the Plan or Delegation number. See **Delegated Return Reports** below.

---

## Modes

Pick the mode from context. If genuinely ambiguous, ask one short question.

### Mode A — Cross-Platform Delegation

Delegate to user-authorized **external** coding-agent platforms. You normally **cannot message those platforms directly**. You create one durable delegation record holding shared context plus a self-contained assignment packet per platform. The user carries that same file to every assigned platform.

Never claim you contacted another platform unless the runtime genuinely provides that capability.

Mode A workflow:

1. Confirm the objective and resolve the **execution workspace** (above) — before any parent or delegation is created.
2. Resolve the **compulsory parent** (above), creating it in the execution workspace if none exists.
3. Confirm which supported platforms are **available and authorized for this run**. Never assume all five.
4. Confirm forbidden platforms/providers and whether any paid API use is permitted. Default: no.
5. Reconcile the work, dependencies, risk, and file ownership.
6. Decide serial, parallel, or mixed execution waves.
7. **Reserve the whole family** in the execution workspace, using **separate linked anchors**: the Plan/Task family master `N` plus each child mini prefix (`Na.)`, `Nb.)`, …); the Delegation record's own `N`; and the Summary family master `N` plus each return-report prefix. Put each exact reserved prefix in the overview, the mini-artifact table, the session-summary/return-report table, and each packet.
8. Create mini plans/tasks (now or after recon) using their **reserved child prefixes**.
9. Create the delegation record and show the **assignment overview** in chat.
10. Explain launch order, return/handoff instructions, and the **Checkpoint Policy** for every packet.
11. Reconcile returned work, collect the mandatory **return reports**, and update the family before declaring the parent objective complete.

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

Invoke `plan-this` / `task-this` normally, with the necessary context. **Those skills do not need to know the delegation workflow.** They carry only a thin `Delegation` pointer field. All delegation intelligence and parent–child linkage lives here.

Each mini artifact should identify its parent, isolated scope, dependencies, owned surfaces, deliverables, Definition of Done, verification, and handoff destination. The parent should link to the mini artifacts and reflect their results without losing its original structure. Mini artifacts carry their **reserved child prefix** (`Na.)`, `Nb.)`, …) for the life of the file.

---

## Delegated Return Reports

A return report is **mandatory at packet/wave completion** for every dispatched assignment. It is how a returning agent hands back its deliverable, evidence, and status so the orchestrator can integrate.

A return report is a **session-summary family member**:

- It uses **session-summary structure** (the 🎭 ACTS narrative, metadata header, Definition of Done ACT, final-state block) — `session-summary` owns that shape; `delegate-this` only reserves the prefix and mandates the report.
- It adds one delegation-specific section: an **append-only `## Delegation Ledger`**, placed after the session-summary body.
- Its filename **ends in `Report.md`** and carries the reserved child prefix (`Na.)`, `Nb.)`, …) under `<execution workspace>\Archive\Historical\Summaries\<Subject>\`.

### Delegation Ledger rules

The `## Delegation Ledger` section is append-only:

- **Existing report content is immutable.** Never rewrite a returned deliverable, ACT, or earlier line of the report.
- **Earlier feedback entries are immutable.** Once written, a feedback line is never edited or deleted — corrections are added as new lines.
- **Feedback is appendable only while the delegation is active.** The orchestrator (and, when relevant, the returning worker) may append feedback lines while the delegation is `_dispatched`.
- **The entire report freezes when `finalize-delegation` closes the delegation.** After the record becomes `_completed`, no further feedback may be appended — the report is a closed historical artifact.

A feedback line is short and dated, e.g.:

```markdown
## Delegation Ledger

- [2026-07-11] Orchestrator: deliverable matched DoD; one nit — rename helper
  to match the parent's vocabulary.
- [2026-07-11] Worker: helper renamed; re-validated, clean.
```

### Thin dependency

`session-summary` understands the **report/feedback shape** (it is the owner of the summary body and the `Report.md` family rule), but it does **not** absorb the delegation workflow — no packet schema, no routing, no lifecycle moves. The report's lifecycle is driven entirely by `delegate-this` (create on return) and `finalize-delegation` (freeze on close).

---

## Checkpoint Policy (every packet)

**Every packet must carry an explicit Checkpoint Policy.** It tells the receiving agent, in advance, exactly where execution stops within that packet.

A Checkpoint Policy states three things explicitly:

1. **Where execution stops.** Default: **complete the packet continuously**; intermediate milestones are **not** user checkpoints unless explicitly labelled `USER CHECKPOINT`.
2. **Whether sync is allowed.** For single-repository skill work, the default is **centralized synchronization** (see below): workers do **not** sync; the orchestrator does one final global-sync + parity pass after review.
3. **What deliverables must be returned first.** The packet's return report and any named deliverables come back before the worker stops or pauses.

Label a midpoint checkpoint explicitly as `USER CHECKPOINT` only when the user genuinely must act mid-packet (e.g. an approval gate). Otherwise the worker runs the packet to completion and returns once.

The Checkpoint Policy is a required field in the packet template and appears in the delegation record alongside each packet.

---

## Centralized Synchronization (multi-agent skill work)

For **multi-agent skill work inside one Workflows repository**, the default synchronization model is **centralized**:

- **Workers edit and validate local masters only.** Each worker edits its owned `Skills/<name>/` files, runs validation locally, and returns its deliverables (diffs, reports, validation output).
- **Workers never pause merely to ask about sync.** Sync is the orchestrator's concern, not the worker's gate.
- **The orchestrator performs one final global-sync and parity pass** after all reviews and corrections are in — propagating the reviewed local masters to the global install locations (Codex, Claude, Antigravity, Hermes, zCode) and verifying parity.
- **Explicit user override wins.** If the user says a worker may sync its own surface, or asks for a different sync model, obey that for the run.

This default keeps one-editor-per-file clean and avoids races where several workers each push to the same global install concurrently. It does not change how non-skill delegations sync; it is the default specifically for skill work in this repository.

---

## Provider-Neutral Hermes Routing

Hermes routing is **provider-neutral**. Do not permanently bind Hermes to a specific provider or model, and never downgrade it based on GLM, OpenAI, Codex, or zCode.

Before routing any assignment to Hermes:

1. **Ask which provider/model Hermes currently uses** and **which subscription/quota pool it shares.** Hermes's provider surface changes over time; treat it as dynamic, not fixed.
2. **Route by capability, trust, and tools** — same routing factors as every other platform. Provider identity is an input to routing, not a label.
3. **Schedule according to current quota capacity.** If the configured provider is near its quota ceiling, serialize, defer, or reroute rather than overload it.
4. **Never permanently bind or downgrade Hermes** based on GLM, OpenAI, Codex, or zCode. A run-time pairing is a run-time decision, recorded in the delegation record, not a standing downgrade.
5. **Pay-as-you-go providers always require explicit approval** — for this run, not inferred from a previous one.

The routing factors and cost gate in `references/routing-and-cost-policy.md` apply unchanged; this section governs **Hermes specifically** because its provider/model surface is dynamic where the other platforms' are relatively fixed.

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
20. Checkpoint Policy (where execution stops, whether sync is allowed, what must be returned first)
21. Return report (reserved prefix and path; mandatory at packet/wave completion)

**Every field is mandatory.** When a field is genuinely inapplicable, retain the line and write `N/A` plus a short reason — never delete it. The Cost/trust rationale field is **never omitted**; when the route needs no defence, write `N/A — routing self-evident`.

A packet must be **self-contained enough that a fresh agent can act** without the user reconstructing your reasoning.

---

## Assignment Overview

Mode A shows the overview in chat **and** in the delegation record. Mode B shows it in chat after dispatch.

Fields: Execution wave · Platform · Agent role · Assignment · Recommended model · Actual model · Parent artifact · Mini artifact · Reserved prefix · Return report · Dependency · Status.

- **Mode A** — `Actual model` may initially read `User to select`.
- **Mode B** — report the actual model when the host exposes it; otherwise `Not exposed by platform`.
- **Reserved prefix** — the exact lowercase child prefix the orchestrator reserved for this assignment's **mini artifact** in the Plan/Task family (e.g. `1a.)`), or `N/A` when the assignment creates no mini artifact. (The matching **return-report** prefix comes from the Summary family and is shown in the Return report column.)
- **Return report** — the reserved path ending in `Report.md`, carrying the Summary-family child prefix (e.g. `9a.)`), or `(reserved, created on return)`.
- **Never guess a model, and never leave a child prefix blank when one was reserved.**

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
2. The **execution workspace** whose `Archive\` tree holds the whole family.
3. Mode A or Mode B.
4. Authorized platforms (Mode A), or native delegation capability (Mode B).
5. Forbidden platforms/providers/models.
6. Paid API authorization. **Default is no.**
7. **Hermes provider/model and quota pool** if Hermes is in the authorized set.
8. Desired or required execution pattern, if the user specified one.
9. Required durable mini plans/tasks, each with a **reserved child prefix**.
10. The **session-summary / return-report family** (master `N.)`, reports `Na.)`, `Nb.)`, …).
11. File/repository ownership boundaries.
12. User checkpoints and integration authority.
13. **Synchronization model** for skill work (default: centralized sync; allow override).
14. Expected final deliverable and Definition of Done.

**Infer safe answers from existing context.** Do not make the user repeat information already in a parent artifact or the current session. Pause only for inputs that materially change routing or authorization — the execution workspace, the platform set, paid-use permission, the Hermes provider/quota, and the parent artifact are always worth pausing for.

---

## Boundaries

Do:

- resolve the **execution workspace** before creating any parent, delegation, mini artifact, or return report
- resolve and bind a parent plan/task before every **Mode A** delegation
- reserve the whole family before dispatch using **separate linked anchors** — Plan/Task family `N` + child prefixes, Delegation `N`, Summary family `N` + return-report prefixes — and write each exact reserved prefix into the overview, mini-artifact table, return-report table, and each packet
- calculate each family's `N` across **its own** combined Live and Historical Subject namespace; never share one number across artifact-type namespaces
- ask which platforms are authorized for this run
- write the Mode A record to `Archive\Live\Delegations\<Subject>\` with `_dispatched`
- calculate `N` across **both** the Live and Historical Subject folders, and assign it once
- produce packets carrying every required field, `N/A` + reason where inapplicable
- include an explicit **Checkpoint Policy** in every packet
- mandate a **return report** (ending in `Report.md`) at packet/wave completion
- for skill work, default to **centralized synchronization**; let the user override
- route Hermes in a **provider-neutral** way (ask provider/model + quota, route by capability/trust/tools, schedule by quota)
- distinguish recommended, user-selected, and programmatically confirmed models
- assign exactly one writer per file
- explain launch order and stop conditions
- reconcile returns against the parent Definition of Done before claiming completion

Do not:

- create a **Mode A** delegation with no parent plan/task
- require a parent, or create a delegation record, for Mode B
- create any family member before resolving the execution workspace
- use one shared numeric anchor across the Plan/Task, Delegation, and Summary namespaces — each family has its own anchor
- leave a child prefix blank or vague ("create a mini plan later") instead of reserving it
- move or rename a delegation record yourself, or tell the user to, when `finalize-delegation` is unavailable — stop instead
- reuse an `N` or a child suffix already taken by a completed record in the Historical Subject folder
- omit the Cost/trust rationale field from a packet
- omit the Checkpoint Policy from a packet
- permanently bind or downgrade Hermes based on GLM, OpenAI, Codex, or zCode
- authorize paid API usage by inference, or treat a prior run's approval as standing
- copy this workflow into `plan-this`, `task-this`, `finalize-plan`, or `finalize-task`
- assume delegation means parallel execution
- assume every supported platform is available
- hardcode a fast-changing model catalog, or any user's absolute workspace paths
- give Antigravity high-risk work under the default profile
- let multiple agents edit the same file concurrently
- claim cross-platform communication you did not perform
- mark the parent objective complete because assignments were dispatched
- finalize the delegation record yourself — that is `finalize-delegation`

---

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to delegation records, integration updates, and completion evidence.

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

This skill owns delegation routing, numbering, assignment packets, parent/child relationships, return-report content, and lifecycle. When co-invoked with `html-this` or `pdf-this`, preserve that ownership and serialize the requested human-readable delegation records, mini artifacts, handoffs, summaries, and return reports only in the requested format. Pass the format request through to every called artifact-producing skill.

Machine-consumed state remains native. Same-stem `.md`, `.html`, and `.pdf` variants are one logical artifact and one reserved prefix. On update, return, or reopen, preflight and update the complete sibling set. This section overrides extension-only examples during a co-invoked run; all family numbering, feedback, freeze, and completion rules remain mandatory.

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

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

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

After a delegation run, confirm and report:

- the **execution workspace** was resolved before any parent/delegation/mini/report was created, and the whole family lives under its `Archive\` tree
- for Mode A, the parent plan/task path, and that its `Delegation` field names the record
- for Mode B, that no parent was manufactured and no delegation record was created
- the delegation record path, that it ends in `_dispatched.md`, sits under `Archive\Live\Delegations\<Subject>\`, and carries an `N.) ` prefix one greater than the highest across **both** the Live and Historical Subject folders
- the Subject folder is unnumbered
- **every child prefix was reserved before dispatch** and the exact reserved prefix appears in the assignment overview, the mini-artifact table, the return-report table, and each packet — no blank or vague "create later" placeholders
- the families use **separate linked anchors**: Plan/Task master `N` (e.g. `1.)`), Delegation master `N` (e.g. `1.)`), and Summary master `N` (e.g. `9.)`) are each calculated from their own combined Live + Historical namespace; the families are connected by explicit path pointers, not a shared number
- the **session-summary / return-report family** is reserved from the Summary master `N`: master `N.)` (e.g. `9.)`), reports `Na.)`, `Nb.)`, … (e.g. `9a.)`, `9b.)`, …); report filenames end in `Report.md`
- every packet carries all 21 required fields, with `N/A` + reason where inapplicable, a Cost/trust rationale always present, and a Checkpoint Policy always present
- every packet's Checkpoint Policy states where execution stops, whether sync is allowed, and what must be returned first
- the authorized platform set, and that no unauthorized platform received work
- Hermes routing was provider-neutral: provider/model + quota pool were asked, routing was by capability/trust/tools, scheduling by quota, and Hermes was not permanently bound or downgraded
- paid API use was either not used or explicitly approved
- for skill work, the centralized-sync default was used unless the user overrode it
- no two agents own the same file for writing
- the assignment overview was shown in chat with pipe-aligned cells ≤80 chars
- for Mode B, whether the host exposed actual models, or `Not exposed by platform`
- that dispatch was not reported as completion

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
