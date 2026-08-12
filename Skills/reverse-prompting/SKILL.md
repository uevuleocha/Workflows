---
name: reverse-prompting
description: Force the agent to ask clarifying questions before starting work. The agent surfaces its own assumptions, the user disambiguates, and only then does it proceed. Use when the user explicitly invokes /reverse-prompting, use reverse-prompting, use the reverse-prompting skill, "ask me questions first", "what questions do you have", "clarify before starting", "surface assumptions", "don't start until you ask me", "ask before building", or clear equivalents naming this skill.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, AskUserQuestion
---

# Reverse Prompting

Before touching anything, ask the user exactly 5 clarifying questions that would most change your approach. Do not proceed until they answer. Surface your own assumptions, let the user disambiguate, then build with high-quality context.

**Why this works:** The most expensive agent failures are silent assumption failures — confidently building the wrong thing because you assumed REST when they meant GraphQL, or assumed a new file when they wanted to extend an existing one. Reverse prompting makes those assumptions visible and fixable before they're expensive. The 5-question constraint forces you to prioritize which unknowns matter most.

## Project Contract

This skill operates under whatever canonical contract the host project defines (e.g. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or none). Any safety rules, path scope, or code-delivery workflow defined there apply unchanged.

Reverse Prompting is a **pre-implementation intake**. The questions it surfaces inform the work; they do not by themselves grant authority to bypass any direct-edit, manual-copy, or approval rules the host project enforces.

## Invocation

Treat these as direct invocation and begin the reverse-prompting workflow:

- `/reverse-prompting`
- `use reverse-prompting`
- `use the reverse-prompting skill`
- "ask me questions first", "what questions do you have", "clarify before starting"
- "surface assumptions", "don't start until you ask me", "ask before building"
- clear equivalents where the user explicitly names this skill

If the task is trivial, or the user has already provided an extremely detailed spec, or speed clearly matters more than perfection, skip the reverse-prompting workflow and answer directly. Flag that the questions would be overkill rather than forcing them through.

## Execution

### 1. Receive the task

Read the user's task description. Do NOT start implementing. Instead, analyze what you'd need to know to do this well.

### 2. Check for project context (optional)

If the host project has relevant context that may pre-answer questions, read it first:

- Any canonical contract file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`)
- Any project decisions / experience / ADR docs (path varies by project — e.g. `active/experience/`, `docs/decisions/`, `DECISIONS.md`)
- Existing code for patterns that answer some questions implicitly

This narrows your questions to things NOT already answered by the codebase or its docs.

### 3. Generate your 5 questions

Think about what assumptions you'd silently make if you just started coding. Turn those assumptions into questions. Prioritize by impact — ask the questions where a different answer would most change your implementation.

Categories to consider:

- **Scope** — what's in vs out? ("Should this handle X or is that a separate task?")
- **Tech choices** — which tools/patterns? ("REST or GraphQL? New service or extend existing?")
- **Edge cases** — what happens when things break? ("What should happen if the API is down?")
- **Performance** — what scale? ("Are we talking 100 users or 100K?")
- **Integration** — what touches this? ("Does this need to work with the existing auth system?")
- **UX** — what does the user see? ("Should errors show a toast or inline message?")
- **Existing patterns** — follow or diverge? ("The codebase uses X pattern — should I match it or is this a chance to improve?")

#### Question format

Use `AskUserQuestion` where appropriate, or present questions directly in chat. For each question:

1. State the assumption you'd make if not asked
2. Ask the question
3. Explain why the answer matters

Example:

```
Q1 (highest impact): Should this be a REST API or GraphQL?
My default assumption: REST, since the existing codebase uses Express.
Why it matters: GraphQL would require adding apollo-server and restructuring the resolver layer — completely different implementation path.
```

### 4. Wait for answers

Do not proceed until the user answers all 5 questions. If they skip a question, use your default assumption and note it explicitly so the user can correct it later.

### 5. Record answers (optional but recommended)

If the host project uses an experience / decisions doc, append the Q&A to the relevant file:

```markdown
## {Task Name} — Decisions ({date})

Q: {question}
A: {user's answer}
Rationale: {why this matters for future tasks}
```

This way, future tasks in the same domain don't need to re-ask answered questions.

### 6. Proceed with implementation

Now you have disambiguated context. Proceed with the task, referencing the user's answers as your requirements. If you find yourself making a new assumption mid-implementation, pause and ask — don't silently decide.

## Advanced: Accumulated Experience

For repeat task domains (e.g., "build another API endpoint", "add another page"), use an experience / decisions doc to avoid re-asking the same questions:

```
Before you begin:
1. Read {project experience/decisions doc} for decisions from past builds
2. Ask me 5 questions that AREN'T already answered by that doc
3. After I answer, append my answers to the doc for next time
4. Then proceed with implementation
```

This creates a flywheel: each task adds context, so future tasks need fewer questions and produce better output immediately.

## When to use

- Any task where you'd normally spend 10+ minutes writing a detailed spec
- Complex features with multiple valid approaches
- Tasks touching unfamiliar parts of the codebase
- Anything where getting it wrong means significant rework

## When NOT to use

- Trivial tasks ("fix this typo", "add a log line")
- Tasks with extremely detailed specs already provided
- Urgent hotfixes where speed matters more than perfection
- Follow-up tasks where the questions were already answered in a prior round

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| question_count | 5 | Number of questions to ask (3–7 range) |
| experience_doc | none | Path to an experience / decisions doc for accumulated learning |
| priority_order | impact | Sort questions by implementation impact |

## Edge cases

- **User says "just do it"**: Respect it. List your assumptions inline and proceed.
- **All questions are already answered by context**: Skip to implementation. Note that you reviewed context and found no ambiguities.
- **User answers are contradictory**: Flag the contradiction. Ask one follow-up to resolve it.
- **Task changes after questions**: Re-assess whether your answers still apply. Ask 1–2 new questions if the scope shifted significantly.

## Boundaries

Do:

- read available project context before generating questions
- ask exactly the configured number of questions (default 5), prioritized by impact
- state your default assumption for each question so the user can correct it cheaply
- wait for answers before implementing
- optionally append Q&A to a project experience / decisions doc when one exists

Do not:

- start implementing before the user has answered (or explicitly said "just do it")
- bypass any direct-edit, approval, or manual-copy rules the host project enforces
- silently expand or compress the question count outside the 3–7 range without telling the user
- re-ask questions that the project context already answers

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

After creating or updating this skill itself:

- confirm the skill folder contains `SKILL.md` and, where the host expects it, `agents\openai.yaml`
- confirm the 6-step Execution flow and the 5-question default appear intact
- confirm the Invocation, Project Contract, Edge Cases, and Boundaries sections exist
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
