---
name: ltney
description: Enter LTNEY mode, meaning LETS TALK NO EXECUTIONS YET. Use when the user explicitly invokes /ltney, $ltney, LTNEY, LETS TALK NO EXECUTIONS YET, or asks to answer questions and stand by without mutating commands, creating files, editing files, generating product-code snippets, running validation/build/test workflows, or making workspace changes. Reading and inspecting files is never blocked unless the user explicitly says so, including transitive reads of files referenced inside other user-provided files. When combined with another explicitly invoked skill, perform that skill under LTNEY's diligent/no-execution discipline unless green-light supersedes LTNEY for a named task.
---

# LTNEY

Enter LTNEY mode: `LETS TALK NO EXECUTIONS YET`.

This skill is for discussion, architecture thinking, careful answers, feasibility checks, risk review, and standing by. It is not an implementation workflow and does not authorize mutating command execution, file changes, durable artifact creation, product-code generation, validation runs, build/test runs, or operational workflows by itself.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

For product source files, preserve the manual-copy workflow defined in the project contract. LTNEY does not authorize direct product-code edits, generated product-code blocks, implementation snippets, workspace writes, mutating commands, validation runs, or build/test runs.

Default output is chat only: answer the user's questions, reason carefully, clarify assumptions, and stand by for next instructions.

## UTF-8 Rule

Always use UTF-8 for every skill, workflow, markdown file, YAML file, plan, summary, and helper script created or edited through an execution workflow that supersedes LTNEY.

When writing or reading text from scripts, specify UTF-8 explicitly, for example `encoding="utf-8"` in Python. Do not rely on Windows default encoding.

When validating folder-style skills, always run Python in UTF-8 mode with `-X utf8`.

## Invocation

Treat these as direct invocation and enter LTNEY mode:

- `/ltney`
- `$ltney`
- `LTNEY`
- `LETS TALK NO EXECUTIONS YET`
- clear equivalents where the user asks the agent to answer, discuss, and stand by without mutating commands, writing files, generating code, running validation/build/test workflows, or making changes

If LTNEY is invoked by itself, it means discussion only: answer, reason carefully, gather read-only context when useful, and stand by without creating artifacts, generating product code, editing files, running mutating commands, or performing validation/build/test workflows.

If LTNEY is invoked together with another explicit skill, LTNEY does not globally block that skill. Perform the other skill under LTNEY discipline unless that skill is an execution workflow explicitly authorized by the user:

- no mutating command execution unless the other named skill requires it and is explicitly approved
- no file creation or file edits unless the other named skill requires it and is explicitly approved
- no product-code generation
- no direct product-code edits
- read-only inspection is always allowed — reading and inspecting files is never blocked by LTNEY unless the user explicitly says so, including transitive reads of files referenced inside other user-provided files
- be diligent, meticulous, and surgical
- ask clarifying questions when the user's intent is vague
- preserve all project-contract and product-code safety boundaries

## Reading And Inspection Are Never Blocked

**LTNEY never blocks reading or inspecting files, unless the user explicitly says so.**

This is absolute and unconditional by default. Reading, viewing, listing, searching, and comparing files is not an execution in the LTNEY sense — it is context gathering, and context gathering always proceeds under LTNEY. An agent in LTNEY mode must not treat read or inspection work as something it needs permission for, or something it should stop short of, or something it should defer to a later turn. Read and inspect freely; stand by only on the execution side.

The only thing that can narrow this rule is an explicit user instruction in the current conversation — for example "don't read any other files," "just answer from what's in front of you," or "stay in chat only." Absent such an explicit instruction, the default is: reading and inspection are always allowed.

### Transitive reads (files referenced inside other files)

The read-never-blocks rule extends to files that the user did not name directly but that are referenced inside a file the user provided or named.

A prompt file, plan, task, report, summary, or any other user-provided file may itself instruct the agent to read further files. Under LTNEY, the agent follows those read references and reads every referenced file as part of working the provided file — without needing a second prompt or explicit per-file permission. This is still read-only inspection, not execution.

Concrete example: the user hands the agent a prompt file (authored by another agent or platform) and says "work this prompt file under LTNEY." That prompt file says "read files A, B, and C." The agent reads the prompt file, then reads A, B, and C — all under LTNEY, all in the same turn, no second prompt required. The agent performs every read the prompt file asks for; it simply does not perform the executions the prompt file asks for until LTNEY is superseded for those executions.

This prevents the failure mode where an over-literal agent reads only the directly-named file and stops, forcing the user to spend a second turn explicitly telling it to read the referenced files.

### What read-only inspection includes

Allowed read-only inspection includes:

- reading files the user names, directly or indirectly
- reading files referenced inside other user-provided files (transitive reads)
- listing directories to understand available files
- searching text with read-only tools such as `rg`
- comparing already-existing files or task records
- inspecting configuration, skill, plan, task, summary, or documentation files
- summarizing what was found without editing anything

These actions are context gathering, not execution. Do not ask the user to leave LTNEY just to read or inspect files they asked about, or files those files reference.

### LTNEY still blocks executions

LTNEY still blocks actions that change state or run operational workflows, including file writes, moves, deletes, patches, validators, tests, builds, scripts that execute project logic, global sync, or durable artifact creation unless a scoped execution workflow such as `green-light` supersedes LTNEY for the named task. The execution side of working a prompt file — writing, editing, running, syncing — remains blocked until LTNEY is superseded for those actions.

### Ambiguous action phrases are not a green-light

"Let's get to work," "get to work," "go ahead," "continue," "proceed," and "please XYZ = <path>!!" are **not** a greenlight while LTNEY is active. Under LTNEY they mean: proceed with reading, research, and context-gathering — no writes, no mutations, no executions. Only an explicit `green-light` invocation lifts the block, and only for the named task. Never infer a greenlight from urgency, enthusiasm, or an action verb; when unsure, stay in LTNEY and confirm.

The user has stated the rule directly:

> "When I want the green light, I'll give you the green light."
>
> "If the LTNEY skill is active, and I say let's get to work, that just means get to work on doing the research and everything or whatever you need to do, but no actual executions yet."

This also governs `inspect` Mode C, whose trigger list includes "Inspect this, then get to work on what it describes." Under LTNEY, that phrase authorizes the reading half only; the described work waits for an explicit green-light.

## LTNEY And Green-Light

`green-light` is the scoped execution override for LTNEY.

If LTNEY and `green-light` point to the same named task, `green-light` supersedes LTNEY for that task only. Proceed under the normal green-light scope and the project's safety rules; do not ask for a second approval when the task is clear.

If LTNEY and `green-light` point to different named tasks, both can coexist: execute only the greenlit task within normal green-light scope, and keep LTNEY active for the separate discussion-only task.

If a greenlight is invoked but the target task is unclear, ask which task the greenlight applies to before executing.

After a greenlit task completes, LTNEY remains active for the rest of the conversation unless the user explicitly exits LTNEY or all modes.

## LTNEY Mode Contract

Invoking this skill means the session is in LTNEY mode.

While in LTNEY mode:

- every assistant response must end with the mode footer described below
- LTNEY mode remains active until the user explicitly exits, ends, stops, clears, or terminates LTNEY mode. A later invocation of another mode does not end LTNEY mode; the modes layer together.
- if the user says "exit all modes", "end all modes", "stop all modes", "clear all modes", or "terminate all modes", all active modes including LTNEY are ended

Mode footer: if LTNEY is the only active mode, end with `Mode = LTNEY`. If multiple modes are active, end with `Modes = LTNEY + Mode B + ... + Mode Z` using every active mode exactly once. Order does not matter, but keep it consistent when practical.

## LTNEY Behavioral Contract

While in LTNEY mode, the agent should:

- answer every question the user asked
- discuss architecture, tradeoffs, feasibility, risks, and options
- clarify unclear assumptions before proposing execution
- separate confirmed facts from assumptions
- avoid drifting into implementation
- use read-only inspection when needed to answer accurately
- avoid mutating command execution and file-writing workflows unless a scoped execution skill supersedes LTNEY for a named task
- stop after the discussion answer and wait for the next instruction

LTNEY mode alone does not create durable artifacts. It can discuss what a plan or task might contain, but it must not create or update a file by itself.

When LTNEY is explicitly combined with an artifact-owning skill such as `plan-this` or `task-this`, that skill may create or update its own artifact only when the user clearly asked for that workflow. In that case, LTNEY controls the style and safety posture, not whether the other named skill is allowed to run.

## Allowed Output

Allowed LTNEY output includes:

- direct answers to the user's questions
- read-only file inspection, directory listing, text search, and file comparison when needed to answer the user's request
- architecture discussion
- feasibility checks
- pros and cons
- risk analysis
- implementation strategy discussion without code
- questions that clarify scope or intent
- high-level next-step options
- references to which skill should be used later, such as `green-light`, `plan-this`, `task-this`, `debug`, `inspect`, or `session-summary`

## Forbidden Output

Do not produce or perform any of the following while LTNEY is active unless another explicitly invoked and scoped execution skill supersedes LTNEY for the named task:

- code blocks
- method blocks
- replacement snippets
- line-by-line code changes
- patch blocks
- full files
- direct file edits
- `apply_patch` edits
- shell commands that modify files
- validation commands or test runs
- build runs or operational scripts
- durable implementation plan creation or update
- durable task creation or update
- skill creation, skill update, skill sync, or global workflow sync
- session summary files
- workflow updates
- product source-file edits or generated product-code snippets

If the user wants to move from LTNEY-only discussion into execution, they should explicitly invoke the appropriate workflow, such as `green-light`, `plan-this`, `task-this`, `debug`, `inspect`, or a skill-creation workflow.

## Diligence Rule

Be Diligent, Meticulous, and Surgical.

In LTNEY mode this means:

- answer the actual questions in the prompt before offering next steps
- avoid sloppy assumptions
- do not over-scope the response into unrelated implementation work
- flag uncertainty clearly
- keep recommendations tightly tied to the user's stated goal
- preserve project-contract safety boundaries while reading and inspecting freely — reading and inspection are never blocked by LTNEY unless the user explicitly says so, including transitive reads

## Relationship To Other Skills

Use LTNEY when the user wants discussion only, or when the user wants another named skill performed with no-execution, highly diligent LTNEY discipline.

Use `green-light` when the user explicitly approves moving from discussion into execution. `green-light` supersedes LTNEY only for the named greenlit task and does not end LTNEY mode globally.

Use `plan-this` when the user wants a durable active implementation plan written under `<project root>\Archive\Live\Plans\`. LTNEY does not block `plan-this` when both are explicitly invoked; it requires the agent to stay diligent and avoid unrelated execution.

Use `task-this` when the user wants a durable housekeeping task written under `<project root>\Archive\Live\Tasks\`. LTNEY does not block `task-this` when both are explicitly invoked; it requires the agent to keep the task scoped and avoid unrelated execution.

Use `debug` later when the user wants structured bug diagnosis or root-cause investigation.

Use `inspect` later when the user wants a recently applied code batch checked and synced into current-session context.

Use `session-summary` later when the user wants a saved session summary file.

Do not silently switch from LTNEY into another skill's execution or file-writing behavior in the same turn unless that other skill is explicitly invoked by the user or green-light supersedes LTNEY for a named task.

## Standby Behavior

After answering, stand by for next instructions. The required mode footer from the LTNEY Mode Contract section must always appear at the end of every response while LTNEY mode is active.

When helpful, add "Standing by for next instructions." before the mode footer for additional clarity, but the mode footer itself is never optional.

## Validation

After creating or updating this skill:

- confirm every edited file is inside the allowed path for that task per the project's canonical contract
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
- smoke-check for `LETS TALK NO EXECUTIONS YET`, `DO NOT EXECUTE YET`, `Reading And Inspection Are Never Blocked`, `LTNEY never blocks reading or inspecting files, unless the user explicitly says so`, `transitive reads`, `stand by`, `Diligent, Meticulous, and Surgical`, `no mutating command execution`, `LTNEY does not globally block other explicitly invoked skills`, `Ambiguous action phrases are not a green-light`, and `green-light` scoped supersession handling.
