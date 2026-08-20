---
name: buzz-agent-setup
description: Generate the complete hand-entered configuration for a Buzz managed agent - dialog fields, agent instructions that always open with the mandatory model-identity line, a curated under-2KB core memory built through a written admission test, and optional cold memory slugs - as copyable output only. Use when the user invokes /buzz-agent-setup, use buzz-agent-setup, asks to set up a new Buzz agent, configure a Buzz managed agent, add a new lab to Buzz, or prepare agent instructions and core memory for Buzz. Never calls the Buzz CLI, never writes files, never touches secrets.
---

# Buzz Agent Setup

## What This Skill Does, And Why

Buzz Desktop manages agents through a GUI dialog. `managed-agents.json` is written by the Desktop app; agents never write it. There is no CLI, no config file an agent may edit, and no computer-use path in this setup. This skill is therefore a **configuration generator, not an installer**: given a description of what an agent is for, it produces every value the user must paste by hand - the dialog fields, the agent instructions, the `core` memory, and any cold memory slugs.

It writes nothing to Buzz, runs no Buzz CLI command, requires no running Buzz instance, and never touches a secret.

Three problems it exists to solve:

1. **Adding a new lab is tribal knowledge.** The working pattern - the in-process runner, an OpenAI-compatible provider, and a base-URL override set under Advanced - belongs in a skill, not in one session summary.
2. **`core` memory compounds.** It is injected on every turn forever, so appending to it carelessly is the one configuration mistake with unbounded cost. It needs curation, not accumulation.
3. **In-process-runner agents cannot see their own model.** They guess, and guess confidently wrong. The only fix is stating the model in their instructions.

This skill operates under the project's canonical contract (`CLAUDE.md` / `AGENTS.md`). It creates no files and no durable artifacts; its entire output is chat text the user pastes into the Buzz dialog.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/buzz-agent-setup`
- `use buzz-agent-setup`
- `use the buzz-agent-setup skill`
- `set up a new Buzz agent`
- `configure a Buzz managed agent`
- `add a new lab to Buzz`
- `prepare agent instructions and core memory for Buzz`
- clear equivalents asking for a Buzz managed-agent configuration to be produced

## Required Inputs

Ask only for what is genuinely missing. Never infer a value that belongs to the user.

1. **Agent name.**
2. **What the agent is for** - the role. Optional; a run with no role is valid.
3. **The harness the user selected** in the Buzz dialog, and, if it is not obvious, which **class** it is (see Harness Classes).
4. **The exact model string** and its display name, as the provider documents them.
5. **For the in-process runner:** the provider, and the base URL - the user confirms which endpoint matches the key they hold.
6. **Context limit:** the model's real window. Ask the user; never assert it from memory.
7. Optional preferences: parallelism, thinking/effort, instance name pool, and any candidate `core` rules the user wants weighed.

## Harness Classes - Branch On Class, Never On Names

Buzz ships a set of harnesses and also accepts user-registered custom harnesses, so any list of names in this skill would be wrong within weeks. Never enumerate harnesses. The user selects the harness in the Buzz dialog and tells this skill which one; the skill's only job is to determine **which class it is**. A harness this skill has never heard of is handled correctly by asking the user which class it is.

| Class                | What it is            | Behaviour that follows     |
| -------------------- | --------------------- | -------------------------- |
| In-process runner    | Buzz's own LLM runner | -> see note [in-process]   |
| External-CLI harness | Any ACP-driven CLI    | -> see note [external-cli] |

Note [in-process]: Buzz owns the tuning fields, the agent needs a provider and a base-URL override, and model identity is never passed into the session.

Note [external-cli]: The CLI owns its own context management, rounds, and effort, so the Buzz tuning fields do not apply to it. This covers shipped harnesses and user-registered custom ones.

Only the class matters. If the harness is the in-process runner, the provider and base-URL path applies; otherwise the CLI-managed path applies.

## The Four Output Blocks

Given a description of what an agent is for, produce the configuration in exactly these four blocks, in order.

### Block 1 - Dialog Fields

| Field              | Guidance this skill applies                        |
| ------------------ | -------------------------------------------------- |
| Agent name         | From the user                                      |
| Agent harness      | Whatever the user selected; only its class matters |
| Model              | -> see note [model]                                |
| Env vars           | -> see note [env-vars]                             |
| Context limit      | -> see note [context-limit]                        |
| Max output tokens  | Inherit unless the user has a reason               |
| Max rounds         | Inherit                                            |
| Thinking / Effort  | Inherit unless the user specifies                  |
| Parallelism        | Recommend 2-3, not the default 10                  |
| Instance name pool | Optional                                           |

Note [model]: Exact provider model string, as the provider documents it - never from memory.

Note [env-vars]: Base-URL override when the in-process runner is used.

Note [context-limit]: The model's real window - ask the user; never assert it from memory.

For any **external-CLI harness**, say plainly that context limit, max rounds, max output, and effort **do not exist** in the Buzz dialog for that class and are managed by the CLI's own configuration - rather than emitting values that cannot be entered.

### Block 2 - Agent Instructions

Must always open with the model-identity line, because the agent cannot derive it:

```text
You are running <Model Display Name> (`<exact-model-string>`).
```

Then the agent's role. Where the user has not defined a role, say so and emit only the identity line rather than inventing a persona.

**Every time this block is emitted, warn that the model string is hardcoded and must be updated by hand if the model changes**, because a stale hardcoded model is worse than none - the agent will report it confidently.

### Block 3 - `core` Memory

Target **under 2 KB** (the hard cap is 65,535 bytes; stay far under it). Apply the admission test (see The `core` Admission Test) to every candidate line, and say for each accepted or rejected line which way it went and why.

Two rules are standard and belong in every agent's `core` unless the user declines:

1. **Handoff announcement and supersession.** If the context begins with `[Context Handoff]`, the entire reply that turn is: state that a handoff occurred, summarise what the agent believes it was doing, and request a summary. Do no other work. A summary the user then supplies is authoritative and supersedes the `[Context Handoff]` content wherever they conflict.
2. **Read the channel description first**, and treat the workspace it names as the working context.

### Block 4 - Cold Memory Slugs

Proposed `mem/<slug>` contents, each with a one-line statement of when it should be read. Slugs are optional; emit none rather than inventing them.

## Reference Configuration Table (Shape Only)

| Block   | Contents                             |
| ------- | ------------------------------------ |
| Block 1 | Dialog fields for the Buzz agent GUI |
| Block 2 | -> see note [block-2]                |
| Block 3 | Curated `core` memory, under 2 KB    |
| Block 4 | Optional cold `mem/<slug>` proposals |

Note [block-2]: Agent instructions, opening with the model-identity line.

## The New-Lab Recipe

A short procedure for adding any lab that exposes an OpenAI-compatible endpoint:

1. Select the in-process runner as the harness.
2. Select the OpenAI-compatible provider.
3. Set `OPENAI_COMPAT_BASE_URL` under Advanced.
4. Set the model string the provider documents.
5. Set Context limit to that model's real window as confirmed by the user.

Two durable warnings belong with it, both structural rather than lab-specific:

1. **The Base URL has no dialog field.** It exists only as an environment variable under Advanced. This is the single most easily missed step, and its failure mode is a misleading one - the request goes to the default OpenAI endpoint and returns an authentication error naming OpenAI, which reads as a bad key rather than a wrong destination.
2. **Some providers expose more than one base URL** for different plan or key types. Have the user confirm which endpoint matches the key they hold, rather than assuming a provider has exactly one.

## The `core` Admission Test

Target under 2 KB; hard cap 65,535 bytes - stay far under it. Apply this written test to every candidate line:

> Does this need to be true on *every* turn, regardless of what is being done? If it only matters sometimes, it belongs in a cold slug. If it is already carried by the nest `AGENTS.md`, the channel description, or a workspace's own `AGENTS.md`, it belongs in none of them twice.

The failure mode to design against is `core` becoming a junk drawer. It is the only field with unbounded compounding cost, and the natural instinct on every future run will be to append one more useful line. The admission test exists to make that instinct answerable rather than a matter of taste - a line either has to be true every turn or it does not, and if something else already carries it, `core` must not.

## Worked Example - Illustrative Only

The skill may carry **one** worked example so its output shape is unambiguous. It must be explicitly labelled as an illustration of the *shape*, not a catalogue to read values out of, and it must not attempt to enumerate the user's current agents. Any example must use placeholder-flavoured values (`<lab>`, `<model-string>`, `https://api.<lab>.example/v1`) rather than real current model strings, so nothing in the skill goes stale when a model is renamed or retired.

Shape of the worked example:

```text
Block 1 - Dialog fields
  Agent name: <name> | Harness: in-process runner (class only)
  Model: <model-string> | Env vars: OPENAI_COMPAT_BASE_URL=https://api.<lab>.example/v1
  Context limit: <the user-confirmed real window> | Parallelism: 2-3

Block 2 - Agent instructions
  You are running <Model Display Name> (`<model-string>`).
  <Role, if the user defined one. If not: state the role is undefined and stop here.>
  [Warning: the model string above is hardcoded - update it by hand if the model changes.]

Block 3 - core memory (target under 2 KB)
  1. Handoff announcement and supersession rule.
  2. Read the channel description first; treat its workspace as context.
  <Further lines only if they pass the admission test.>

Block 4 - Cold memory slugs
  mem/<slug> - read when: <one line>. Optional; emit none rather than inventing them.
```

The skill must never contain: a list of labs, a list of model strings, a list of context-window sizes, a list of provider endpoints, or a list of harness names. All of those change on a timescale of weeks. Every one of them is an input the user supplies at run time.

## Boundaries

Do:

- produce all four blocks as copyable chat output
- branch on harness class, and ask the user which class an unknown harness is
- ask for context windows; never assert them from memory
- apply the admission test visibly to every candidate `core` line
- recommend parallelism 2-3 over the default 10

Do not:

- call the Buzz CLI, use computer use, touch the network, or write to any Buzz path - output only
- emit, request, or echo a secret value - name the variable; the user supplies the secret
- enumerate labs, models, endpoints, context windows, or harness names
- invent a role, a memory slug, a model string, or a context-window size the user did not supply
- emit Context limit, Max rounds, Max output, or Effort values for an external-CLI harness agent as if they were enterable
- duplicate `buzz-channel-description`'s job - channel descriptions are that skill's output

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

When creating or updating this skill itself:

- validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`), and decide pass/fail from the exit code alone
- confirm the `## Markdown Table Alignment` section and its validation check remain present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells

Each run of this skill, confirm:

- all four blocks were emitted in order, Block 2 opened with the model-identity line and carried the stale-value warning
- harness handling branched on class; an unknown harness was resolved by asking; an external-CLI harness produced a plain statement that the tuning fields do not exist rather than enterable values
- context windows came from the user, never from memory
- the admission test was applied visibly to every `core` candidate line
- no secret was emitted, requested inline, or echoed; no Buzz CLI command, network call, or write to any Buzz path occurred
- no lab, model string, endpoint, context window, or harness was enumerated
