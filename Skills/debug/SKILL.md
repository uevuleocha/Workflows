---
name: debug
description: Enter command-triggered Debug mode to help the user pinpoint and squash issues or bugs (#UzzysBugsBeGone) with structured intake, bug-list confirmation, evidence-first investigation, ask-before-edit safety, product-code surgical blocks, and focused verification. Use only when the user explicitly invokes /debug, use debug, use the debug skill, or a clear equivalent naming this skill.
---

# Debug

Help the user pinpoint and squash issues or bugs. `#UzzysBugsBeGone`

This skill enters Debug mode. It is for structured diagnosis, root-cause analysis, carefully scoped investigation, proposed fixes, and verification. It is not a broad auto-trigger for every error-like message.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

For non-product workspace files, diagnose first and ask before editing unless the user explicitly says to edit or fix that file.

## Invocation

Treat these as direct invocation and enter Debug mode:

- `/debug`
- `use debug`
- `use the debug skill`
- clear equivalents where the user explicitly names the debug skill

Do not auto-trigger this skill from broad phrases like `debug this`, `diagnose this`, `why is this failing`, or `fix this failure` unless the user explicitly names or invokes the `debug` skill.

If the user only wants a quick explanation of an error message outside Debug mode, answer directly without entering Debug mode or creating artifacts.

## Debug Mode Contract

Invoking this skill means the session is in Debug mode.

While in Debug mode:

- every assistant response must end with the mode footer described below
- Debug mode remains active until the user explicitly exits, ends, stops, clears, or terminates Debug mode. A later invocation of another mode does not end Debug mode; the modes layer together.
- if the user says "exit all modes", "end all modes", "stop all modes", "clear all modes", or "terminate all modes", all active modes including Debug are ended
- do not silently create plans, summaries, workflows, or memory updates
- if debugging reveals multi-phase work, suggest using `$plan-this` rather than creating a plan inside this skill
- if the user asks for a summary, plan, finalization, or workflow update, use the appropriate skill or workflow normally

Mode footer: if Debug is the only active mode, end with `Mode = Debugging`. If multiple modes are active, end with `Modes = Debugging + Mode B + ... + Mode Z` using every active mode exactly once. Order does not matter, but keep it consistent when practical.

## Debug Intake

Before deep-diving, ask for or confirm the debug intake. If the user already supplied enough detail, summarize what is known and ask only for missing or uncertain items.

Use this prompt shape when intake is needed:

```text
We are in Debug mode. Before I deep-dive, let me capture the bug list and investigation scope.

1. Files to reference or compare:
2. Similar tool/feature that may already implement this correctly:
3. Issues you are noticing:
4. Your thoughts or ideas for each issue:
5. Proposed fixes or debugging paths you want considered:
6. What you want me to delegate to myself for deeper file investigation:
7. Should I diagnose only, provide code blocks, or ask before any edit/fix?
```

After intake, summarize the bug list back to the user before branching into investigation. Include:

- the suspected issue list
- files or tools to inspect
- similar implementations to compare against
- user-proposed debug paths
- what the agent will investigate first
- what is explicitly out of scope

If the user asks the agent to proceed after the summary, investigate in the smallest useful slice.

## Required Review

Review only the sources needed to debug the issue accurately:

1. The project's canonical contract (e.g. `CLAUDE.md`)
2. user-named files, logs, plans, summaries, workflows, tools, or commands
3. similar tools or features named by the user or clearly relevant to the issue
4. relevant active plan if the debug issue belongs to planned work
5. existing tools under `tools/` before creating a new diagnostic script
6. relevant source files only when needed to locate the failure

Do not perform a broad repo audit unless the failure is cross-cutting or the user asks for it.

## Debug Workflow

Use this order unless the issue clearly requires a smaller path:

1. **Capture the failure**
   - Preserve the exact command, error text, stack trace, bad output, screenshot detail, or user-observed behavior.
   - Distinguish confirmed facts from assumptions.

2. **Establish the boundary**
   - Identify whether the target is a skill, workflow, tool, plan, summary, bot, indicator, JSON bridge/database, or environment issue.
   - Reconfirm any read-only or no-edit boundaries defined by the project's canonical contract.

3. **Compare known-good patterns**
   - Check whether a similar tool or feature already implements the behavior correctly.
   - Use existing architecture and local patterns before proposing new structures.

4. **Reproduce or inspect**
   - Run the smallest relevant command or deterministic check when available.
   - Prefer existing scripts in `tools/` or skill-specific scripts before writing new helpers.
   - If reproduction is impossible, explain what evidence is missing and use static inspection.

5. **Find the root cause**
   - Trace from symptom to cause, citing exact files, methods, fields, plan items, command output, or config entries.
   - Avoid speculative fixes until the failure path is coherent.

6. **Choose the fix path**
   - For non-product workspace files, ask before editing unless the user explicitly said to edit or fix.
   - For product source files, provide surgical code blocks and exact placement instructions unless direct edits were explicitly authorized.
   - If the fix is larger than a narrow patch, suggest `$plan-this` before continuing.

7. **Verify**
   - Rerun the failing command, validator, parser, compile-adjacent check, or focused smoke test when possible.
   - If verification cannot run, state exactly why and what the user should run next.

8. **Report**
   - Lead with the root cause and outcome.
   - Include files inspected, files changed if any, commands run, verification result, remaining risks, and next action.
   - End with the mode footer while Debug mode remains active.

## Edit Permission Rules

Use diagnosis-first behavior.

For non-product files such as skills, markdown plans, summaries, workflows, YAML, Python tools, or helper scripts:

- do not edit just because the fix is obvious
- ask before editing unless the user explicitly says to edit, fix, apply changes, make the edit, or equivalent
- when asking, state the exact file and intended change

For product source files:

- default to diagnosis, code blocks, and exact placement instructions in chat
- do not directly edit unless the user explicitly authorizes direct product-code edits
- preserve the manual-copy workflow defined in the project's canonical contract

## Diagnostic Printout Guardrail

If a debug path requires adding many diagnostic printouts, log calls, chart comments, or trace calls, require a dedicated switch such as:

```text
Enable X Debug
```

Use a topic-specific name that fits the codebase style, for example:

- `EnableZoneDebug`
- `EnableJsonDebug`
- `EnableTimingDebug`
- `EnableBridgeDebug`

For product source files, deliver the switch and diagnostic print/log blocks in chat unless direct edits are explicitly authorized.

## Root-Cause Discipline

Do:

- read the full trace or full relevant output before patching
- check for stale assumptions from prior summaries or plans
- keep hypotheses testable and revise them when evidence contradicts them
- compare against similar implementations when useful
- prefer minimal fixes that match the existing architecture
- preserve user changes and unrelated work
- suggest updating a relevant active plan only when the debug session changes its status or scope

Do not:

- edit product source files directly without explicit authorization
- edit non-product files without asking unless the user explicitly said to edit or fix
- hide uncertainty behind confident language
- claim a fix is verified if the relevant check did not run
- create a new tool when an existing one can answer the question
- delete, reset, or overwrite files to get unstuck without explicit approval

## Output Modes

Use the output mode implied by the user:

- **Diagnosis only:** explain root cause, evidence, and proposed fix without editing files.
- **Surgical code blocks:** provide exact replacement/addition blocks and placement instructions.
- **Ask-before-edit:** propose the file edit and wait for approval.
- **Direct fix:** only when the user explicitly said to edit/fix the relevant non-product file or explicitly authorized product-code edits.
- **Plan update:** suggest `$plan-this` when debugging reveals multi-phase work or changes an active plan.
- **Final report:** summarize the failure, cause, fix, verification, and any remaining action.

If the requested output mode conflicts with the project's canonical contract or safety rules, follow the stricter rule and explain the constraint.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to durable Debug captures, evidence records, and subsequent diagnostic updates.

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

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After a debug fix:

- confirm every edited file is within the allowed path for that task per the project's canonical contract
- run the narrowest relevant verification available
- report commands/checks and their results
- report any checks that could not be run

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
