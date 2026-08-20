---
name: prompt-contracts
description: Define a 5-part engineering spec (GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE) before implementation so "done" has zero ambiguity. Use when the user explicitly invokes /prompt-contracts, use prompt-contracts, use the prompt-contracts skill, write a contract, define success criteria, define failure conditions, spec this out, what does done look like, or clear equivalents naming this skill.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, AskUserQuestion
---

# Prompt Contracts

Define a 5-part contract before implementation: **GOAL** (target outcome, measurable where meaningful), **CONSTRAINTS** (hard limits), **FORMAT** (exact output shape), **DEFINITION OF DONE** (positive completion checklist), and **FAILURE** (explicit conditions that mean "not done"). The agent treats this as an engineering spec with zero ambiguity about what "done" means.

**Why this works:** Agents hallucinate and over-engineer when success is undefined, and silently cut corners when failure is undefined. A prompt contract front-loads the reasoning about scope, completion evidence, and edge cases. The DEFINITION OF DONE clause tells the agent when it can stop; the FAILURE clause prevents the agent from taking shortcuts it would otherwise rationalize as acceptable.

## Project Contract

This skill operates under whatever canonical contract the host project defines (e.g. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or none). Any safety rules, path scope, or code-delivery workflow defined there apply unchanged.

A Prompt Contract authored under this skill is a **planning artifact**. It scopes what the work must achieve; it does not by itself grant authority to bypass any direct-edit, manual-copy, or approval rules the host project enforces.

When invoked by `plan-this` or `task-this`, the calling skill embeds the contract into that plan/task artifact under a `## Prompt Contract` section. `prompt-contracts` itself still writes no standalone contract file — on its own it delivers the contract in chat.

### Embedded Caller Mode

An owning durable-artifact skill may define a stricter caller policy. `north-star` uses embedded caller mode: derive, validate, and embed the complete contract without asking for separate Prompt Contract approval. The user's sufficiently detailed North Star invocation supplies the authority to begin the first Full or Batch pursuit. The contract is not repeated in chat by default; show it only when the user explicitly opts in during creation or asks to see it later. Material scope changes update the embedded contract, while evidence-only progress does not rewrite it.

This exception belongs to the calling workflow. It does not change the direct invocation behavior below and does not silently alter `plan-this`, `task-this`, `prompt-this`, or other callers.

## Invocation

Treat these as direct invocation and begin the prompt-contracts workflow:

- `/prompt-contracts`
- `use prompt-contracts`
- `use the prompt-contracts skill`
- "write a contract", "define success criteria", "define failure conditions", "spec this out", "what does done look like"
- clear equivalents where the user explicitly names this skill

If the user only wants a quick answer or a trivial change, skip the contract and answer directly. Flag that a contract would be overkill rather than forcing one through.

## Execution

### 1. Receive the task

Read the user's request. Determine whether they have already provided a contract or need help writing one.

- **If the user provides a contract:** Parse it into the 5 sections and proceed to validation (step 3).
- **If the user provides a plain task:** Help them convert it into a contract (step 2).

### 2. Generate the contract

If the user gave a plain task description, convert it into a structured contract. Use what you know from the codebase, the task description, and reasonable defaults.

Present the draft contract to the user for approval before proceeding.

#### Contract template

```markdown
## Contract

GOAL: [What does success look like? Prefer a measurable metric when meaningful.]

CONSTRAINTS:
- [Hard limit 1 — technology, scope, or resource constraint]
- [Hard limit 2]
- [Hard limit 3]

FORMAT:
- [Exact output shape — files, structure, what's included]
- [File naming and organization]
- [What to include — types, tests, docs]

DEFINITION OF DONE:
- [Positive completion criterion 1]
- [Positive completion criterion 2]
- [Evidence or validation required before the task can be considered complete]

FAILURE (any of these = not done):
- [Specific failure condition 1]
- [Specific failure condition 2]
- [Edge case that must be handled]
- [Quality bar that must be met]
```

#### Writing good GOAL statements

- Prefer a number when it is meaningful: "handles 50K req/sec" not "handles high traffic"
- Use behavioral criteria when a number would be artificial: "user can filter by date, status, and assignee" is better than inventing a fake metric
- Be specific: "returns results in <200ms p95" not "is fast"
- Define the user-visible outcome: "user can filter by date, status, and assignee" not "add filtering"

#### Writing good CONSTRAINTS

- Only hard limits — things that are NOT negotiable
- Technology constraints: "no external dependencies", "must use existing ORM"
- Scope constraints: "under 200 lines", "single file", "no new database tables"
- Compatibility: "must work with Node 18+", "backwards compatible with v2 API"

#### Writing good FORMAT

- Exact file structure: "single file: `rate_limiter.py`" not "a Python file"
- What to include: "type hints on all public methods", "5+ pytest tests"
- What to exclude: "no comments explaining obvious code", "no README"

#### Writing good DEFINITION OF DONE clauses

This is the positive completion checklist. It defines what must be true before the agent can stop looping and deliver.

In plain language, a **good result** is one where every Definition of Done item is met and no Failure condition occurred. This is a terminology bridge only; `DEFINITION OF DONE` remains the canonical header and logic.

- Include required evidence: "unit tests pass", "validator reports Skill is valid", "manual review confirms no stale contract-shape wording"
- Include scope completion: "local master skill updated", "metadata updated", "sync authorization and status recorded"
- Keep it concrete enough to verify: "all configured roles covered" not "quality is good"
- Do not duplicate FAILURE; DoD says what must be true, FAILURE says what must not happen

#### Writing good FAILURE clauses

This is the most important section. Think about how the task could "technically work" but actually be wrong:

In plain language, a **bad result** exists when at least one Failure condition occurred. **Things to avoid** are the concrete Failure conditions listed here. These phrases do not add new contract sections or change the rule that any active Failure means not done.

- Missing edge case: "no test for empty input"
- Performance miss: "latency exceeds 1ms on synthetic load"
- Silent failure: "swallows errors without logging"
- Incomplete: "doesn't handle the concurrent access case"
- Over-engineered: "adds abstraction layers not required by GOAL"

### 3. Validate the contract

Before implementing, check that the contract is:

- **Complete** — all 5 sections filled out
- **Consistent** — CONSTRAINTS don't contradict GOAL
- **Outcome-driven** — DEFINITION OF DONE directly proves the GOAL was reached
- **Testable** — every DoD criterion and FAILURE condition can be verified or explicitly marked for manual verification
- **Scoped** — GOAL is achievable within the CONSTRAINTS

If anything is ambiguous, ask the user to clarify before proceeding.

### 4. Implement against the contract

Build the solution. Treat each section as a hard requirement:

- **GOAL**: The thing you're optimizing for
- **CONSTRAINTS**: Boundaries you cannot cross
- **FORMAT**: Exact shape of your output
- **DEFINITION OF DONE**: Positive criteria that must be satisfied before you stop
- **FAILURE**: Negative conditions you must actively prevent

As you implement, mentally check both the DEFINITION OF DONE and every FAILURE condition. If you catch yourself about to violate one, stop and fix it before moving on.

### 5. Self-verify against DEFINITION OF DONE and FAILURE conditions

Before delivering, run through every DoD and FAILURE condition as a checklist:

```markdown
## Contract Verification

- [ ] DEFINITION OF DONE 1: {criterion} → VERIFIED: {how you confirmed it passes}
- [ ] DEFINITION OF DONE 2: {criterion} → VERIFIED: {how you confirmed it passes}
- [ ] FAILURE 1: {condition} → VERIFIED: {how you confirmed it passes}
- [ ] FAILURE 2: {condition} → VERIFIED: {how you confirmed it passes}
- [ ] FAILURE 3: {condition} → VERIFIED: {how you confirmed it passes}
- [ ] GOAL met: {evidence, including metric if applicable}
- [ ] All CONSTRAINTS respected: {confirmation}
- [ ] FORMAT matches spec: {confirmation}
```

If any DoD criterion is unmet or any FAILURE condition is violated, fix it before delivering. The contract says "any of these = not done" — respect that literally.

### 6. Deliver with contract status

Present the output alongside the contract verification:

```
Contract status: ALL PASS

GOAL: ✓ {outcome achieved — show evidence}
CONSTRAINTS: ✓ {all respected}
FORMAT: ✓ {matches spec}
DEFINITION OF DONE: ✓ {all completion criteria verified}
FAILURE conditions: ✓ {all verified — none triggered}
```

If any condition failed and couldn't be resolved, be explicit:

```
Contract status: 1 FAILURE

GOAL: ✓
CONSTRAINTS: ✓
FORMAT: ✓
DEFINITION OF DONE: 1 of 5 unmet
FAILURE conditions: 1 of 4 failed
  - FAILED: "latency <1ms on 50K requests" — achieved 1.3ms
  - Reason: {why it failed}
  - Options: {what could fix it — different algorithm, relaxed constraint, etc.}
```

## Example contracts

### API endpoint

```
GOAL: GET /users endpoint returning paginated results, handling 10K concurrent connections.

CONSTRAINTS:
- Express.js, existing Prisma ORM
- No new dependencies
- Under 80 lines (route + controller)

FORMAT:
- Route in routes/users.ts
- Controller in controllers/users.ts
- 5 tests in __tests__/users.test.ts
- OpenAPI JSDoc on the route

DEFINITION OF DONE:
- Endpoint returns paginated user lists with limit/offset query parameters
- Valid query params return 200 with expected response shape
- Invalid query params return 400 with a clear validation error
- Tests pass for success, empty results, and invalid page number

FAILURE:
- No pagination (limit/offset at minimum)
- No input validation on query params
- Returns 500 on invalid input instead of 400
- No test for empty results
- No test for invalid page number
```

### React component

```
GOAL: Reusable DataTable component supporting sort, filter, and pagination for up to 10K rows without lag.

CONSTRAINTS:
- React 18+, TypeScript, no external table libraries
- Must accept generic row type via generics
- Virtualized rendering for 1K+ rows

FORMAT:
- components/DataTable/DataTable.tsx (component)
- components/DataTable/DataTable.types.ts (types)
- components/DataTable/DataTable.test.tsx (tests)
- Storybook story showing 3 variants

DEFINITION OF DONE:
- Component supports sorting, filtering, pagination, empty state, and generic row inference
- Storybook shows default, empty, and large-data variants
- Tests cover sorting, filtering, pagination, empty state, and mixed-type sort behavior
- Performance check confirms 5K rows can scroll without visible lag

FAILURE:
- Scrolling lags on 5K rows
- Sort doesn't handle mixed types (strings vs numbers)
- Filter doesn't debounce (fires on every keystroke)
- No empty state
- Generic type not inferred from data prop
```

## When to use

- Infrastructure code (rate limiters, caches, queues)
- API endpoints and services
- Anything that will be hard to fix later
- Tasks where quality matters more than speed
- When you want to prevent "it technically works but..." outcomes

## When NOT to use

- Quick prototypes ("just get something working")
- Exploratory tasks where requirements are still forming
- Trivial changes where a contract would be more text than the code itself

## Configuration

These settings are behavioral defaults for agents using the skill. They are not guaranteed executable parameters unless the host tool, runtime, or calling workflow explicitly implements them.

| Parameter | Default  | Description                                                      |
| --------- | -------- | ---------------------------------------------------------------- |
| verify    | true     | Run self-verification before delivering                          |
| strict    | true     | Fail if any DoD item is unmet or any FAILURE condition is active |
| template  | standard | Contract template (standard, minimal, detailed)                  |

## Edge cases

- **User provides incomplete contract**: Fill in missing sections with reasonable defaults and confirm with the user.
- **FAILURE conditions conflict with GOAL**: Flag the contradiction. Ask which takes priority.
- **DEFINITION OF DONE conflicts with FAILURE**: Flag the contradiction. Ask whether the positive completion criterion or negative rejection rule should be changed.
- **Can't verify a FAILURE condition**: Note it as "UNVERIFIABLE" and explain why. Suggest how the user can verify manually.
- **Can't verify a DoD criterion**: Note it as "UNVERIFIABLE" and explain why. Suggest how the user can verify manually.
- **Contract is overkill for the task**: If the task is trivial, say so. Suggest skipping the contract or using a minimal version (GOAL + DEFINITION OF DONE + FAILURE only).

## Boundaries

Do:

- parse user-provided contracts into the 5 canonical sections
- draft contracts from plain task descriptions and present for approval
- honor an owning skill's explicit embedded-caller policy, including North Star's approval-free authoring and opt-in-only chat display
- validate completeness, consistency, testability, and scope
- run the DEFINITION OF DONE and FAILURE-condition self-verification before delivering
- report contract status (ALL PASS or explicit failures) at the end

Do not:

- bypass any direct-edit, approval, or manual-copy rules the host project enforces
- skip the DEFINITION OF DONE or FAILURE self-verification when `verify` is true
- silently relax a CONSTRAINT or downgrade a FAILURE condition to make the task pass
- force a contract onto trivial tasks where it would be more text than the code

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

This rule is **emitted into** every artifact this skill produces, adjacent to the DEFINITION OF DONE or Verification Checklist it governs — not buried in a trailing notes section. The executing agent must read it inside the artifact it was handed, without consulting any workspace contract.

## In-Pass And Deferred Real-World Verification

**In-Pass And Deferred Real-World Verification.** Classify every verification item before saving or finalizing an artifact:

- **In-Pass Verification:** evidence the executing agent can produce safely in the current pass, including deterministic tests, fixtures, simulations, and mock scenarios. These items remain blocking completion criteria and follow Checklist Tick Discipline.
- **Deferred Real-World Verification:** evidence that genuinely requires later live use, elapsed time, user adoption, or an external event. Put only these items in a separate `## Deferred Real-World Verification` checklist. They are non-blocking for finalization and may remain unticked after all in-pass completion criteria are met. State the future trigger and evidence required for each item.

Never defer an item the current agent can safely verify now merely to claim completion. Omit the deferred section when no genuine deferred item exists.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## In-Pass And Deferred Real-World Verification` section is present; immediately verifiable items remain blocking and any genuine later-use items are isolated under a non-blocking `## Deferred Real-World Verification` checklist with their trigger and required evidence;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm a newly produced artifact actually carries the Checklist Tick Discipline rule verbatim, since the section can survive in this skill while the template silently loses it;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;

After creating or updating this skill itself:

- confirm the skill folder contains `SKILL.md` and, where the host expects it, `agents\openai.yaml`
- confirm the 5-section contract template (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE) appears intact
- confirm the Execution, Self-Verification, and Boundaries sections exist
- confirm the good-result and bad-result language maps only to DEFINITION OF DONE and FAILURE, without adding headers
- confirm North Star embedded caller mode is approval-free and chat display remains opt-in
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
