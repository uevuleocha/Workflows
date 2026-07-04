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

When invoked by `imp-upd-plan` or `imp-upd-task`, the calling skill embeds the contract into that plan/task artifact under a `## Prompt Contract` section. `prompt-contracts` itself still writes no standalone contract file — on its own it delivers the contract in chat.

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

- Include required evidence: "unit tests pass", "validator reports Skill is valid", "manual review confirms no stale contract-shape wording"
- Include scope completion: "local master skill updated", "metadata updated", "global sync deferred"
- Keep it concrete enough to verify: "all configured roles covered" not "quality is good"
- Do not duplicate FAILURE; DoD says what must be true, FAILURE says what must not happen

#### Writing good FAILURE clauses

This is the most important section. Think about how the task could "technically work" but actually be wrong:

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

| Parameter | Default | Description |
|-----------|---------|-------------|
| verify | true | Run self-verification before delivering |
| strict | true | Fail the task if any DoD criterion is unmet or any FAILURE condition is triggered |
| template | standard | Contract template (standard, minimal, detailed) |

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
- validate completeness, consistency, testability, and scope
- run the DEFINITION OF DONE and FAILURE-condition self-verification before delivering
- report contract status (ALL PASS or explicit failures) at the end

Do not:

- bypass any direct-edit, approval, or manual-copy rules the host project enforces
- skip the DEFINITION OF DONE or FAILURE self-verification when `verify` is true
- silently relax a CONSTRAINT or downgrade a FAILURE condition to make the task pass
- force a contract onto trivial tasks where it would be more text than the code

## Validation

After creating or updating this skill itself:

- confirm the skill folder contains `SKILL.md` and, where the host expects it, `agents\openai.yaml`
- confirm the 5-section contract template (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE) appears intact
- confirm the Execution, Self-Verification, and Boundaries sections exist
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
