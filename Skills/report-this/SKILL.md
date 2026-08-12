---
name: report-this
description: "Create, update, reopen, or stage durable reports in two modes, including evidence-first issue reports and source-backed analytical reports. Saves pending reports with permanent numbering and a dismissible lifecycle footer, and can produce send-ready, stripped copies for external delivery. Use when the user invokes /report-this, asks to report a bug, asks for a durable report on a subject, or asks for send-ready, clean, or stripped copies of existing reports."
---

# Report This

Create, update, or reopen a durable report. Mode A is a platform or issue report; Mode B is an analytical or professional report. Both use one lifecycle: `pending` in Live, then `reported` in Historical through `finalize-report`.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/report-this` or `use report-this`
- `report this bug to <platform>` or an equivalent durable issue-report request
- `write a report on <subject>` or an equivalent durable analytical-report request
- `make a report`, `save this as a report`, or `report file`
- `stage this report for sending`, `make a send-ready copy`, or an equivalent request to send, submit, file, deliver, share, or otherwise externally publish existing reports

If the user wants only an in-chat answer, create no file. Route plans to `plan-this`, tasks to `task-this`, prompts to `prompt-this`, documentation to `doc-this`, and report closure to `finalize-report`.

## Two Report Modes

Infer confidently and ask one question only when genuinely ambiguous:

- **Mode A — Platform / Issue:** a malfunction, defect, incident, vendor, or team target. Use the evidence-first issue template.
- **Mode B — Analytical / Professional:** an article, paper, video, event, dataset, decision, or topic. Use the thesis-and-analysis template.

Mode affects the body only. Never encode a mode tag in the report or use it to choose a lifecycle state.

## Required Inputs

Infer before asking:

1. Mode.
2. Subject — a broad, reusable folder category.
3. Topic/title — the specific report filename body.
4. Audience and source/evidence material.
5. Whether this is create, update, or reopen.

Ask only for inputs that cannot be inferred safely. Settle Subject and Topic collaboratively; avoid one Subject folder per file.

## Create, Update, Or Reopen

- **Create:** no matching report exists or the user requests a distinct report.
- **Update:** the user references a pending report or asks to revise it.
- **Reopen:** the user references a reported file and asks to revise, extend, or reopen it. Move it from Historical to the matching Live Subject folder, rename `_reported.md` to `_pending.md`, preserve its number, update the footer to `PENDING ⌛`, and retain its original created date. Record that it was reopened.
- Ask when multiple plausible reports match. Never overwrite a collision.

`report-this` is the only workflow that reopens a report. It never finalizes one.

## Send-Ready Staging

Staging is an explicitly requested operation alongside create, update, and reopen. Trigger it when the user asks to send, submit, file, deliver, share, or otherwise externally publish one or more existing reports, or asks for send-ready, clean, or stripped copies of them. Staging never creates, renumbers, or modifies a durable report; it only reads originals and writes copies.

Accept one report, several reports, or every report in a Subject folder. When the request is ambiguous about which reports are in scope, ask once rather than guessing: staging the wrong report is cheap to undo, but staging a report the user did not intend to send invites them to send it.

Write staged copies to a folder inside the target workspace's temporary directory, named from the Subject folder the durable reports actually live in:

```text
<workspace root>\tmp\<Subject>-reports-send-ready\
```

The Subject segment is the durable report's own Subject folder name, lowercased and hyphenated where it contains spaces. Reports under Subject `Hermes` stage to `tmp\hermes-reports-send-ready\`. Reports under Subject `Troubleshooting a Bug` stage to `tmp\troubleshooting-a-bug-reports-send-ready\`. Reports under Subject `Codex` stage to `tmp\codex-reports-send-ready\`. Create the folder when it does not exist; reuse it when it does. One staging folder per Subject, never one per report.

Name each staged copy after its source, preserving the permanent `N.)` prefix and the Topic exactly, and dropping only the `_pending` lifecycle suffix:

```text
source:  Archive\Live\Reports\Hermes\3.) Some Topic_pending.md
staged:  tmp\hermes-reports-send-ready\3.) Some Topic.md
```

Strip from every staged copy all workspace-only material, so what remains is exactly what a maintainer or recipient should receive:

- the dismissible footer block, including its HTML comment banner and the divider that introduces it;
- the `## Agent Provenance` section and its table;
- the `## Agent Change Log` section and its table;
- any other internal workflow metadata, lifecycle marker, or agent-coordination block that would be meaningless or inappropriate outside the workspace.

Do not alter the report's substance. Titles, metadata tables intended for the recipient, evidence tables, reproduction steps, expected behavior, workarounds, suggested fixes, outcome, and notes all stay verbatim. Do not reflow prose, renumber sections, or re-style tables. Trim trailing blank lines and orphaned dividers left behind by the removals so the staged file ends cleanly on real content.

Verify each staged copy before reporting success: confirm the destination exists, confirm zero residual references to any stripped block, and confirm the file does not end on a dangling divider or comment fragment. Report the staging folder path, every staged filename, and what was stripped.

Because the staging folder lives in the workspace temporary directory, apply the workspace's temporary-file rule: tell the user the files were created there, and note that `finalize-report` will remove them when the reports are finalized.

Staged copies are derived artifacts. They carry no lifecycle of their own, are never numbered independently, are never archived, and are safe to delete at any time. Re-staging an already-staged report overwrites its copy rather than creating a second one.

Ownership stays clean: `report-this` owns staging (which reports, the folder name, the strip list, and verification). `finalize-report` owns cleanup (deleting copies attributable to reports it just finalized, and removing the folder when it empties). Neither skill takes on the other's job, and staging never becomes a side effect of finalization or vice versa.

## Location And Permanent Numbering

```text
Pending:  <root>\Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
Reported: <root>\Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

Folders are never numbered. Files alone carry `N.)`. For a new report, compute `N = max(all N.) in Live/Reports/<Subject> plus all N.) in Historical/Reports/<Subject>) + 1`, starting at `1`. Assign the number once for life; never renumber, reclaim gaps, or calculate from only one side.

Create the required unnumbered Subject folder when allowed. Stop on a filename or number collision.

## Mode A Body

Use `references/mode-a-template.md`. Required sections are Report Metadata, Title, Environment, Summary, Root Cause with evidence, Steps to Reproduce, Expected Behavior, Workaround, Suggested Fixes, Outcome, and Notes.

Facts, observations, hypotheses, and recommendations must remain distinguishable. Never invent reproduction steps, versions, logs, root causes, or outcomes. Mark unknown fields clearly.

## Mode B Body

Use `references/mode-b-template.md`. Required core sections are Report Metadata, Executive Summary, Overview of the Source, Key Points / Findings, Analysis / Discussion, Conclusion, and References / Sources. Background / Context and Recommendations / Takeaways may be omitted only in a compact report when they add no material value.

Keep source-faithful summary separate from author analysis or inference. If a source cannot be fully accessed, say so and do not fabricate its contents. For a blocked source, look for an authoritative canonical or cross-posted version before asking for user-provided text or screenshots.

## Contract And Effort Controls

A Prompt Contract is optional by default. Use `prompt-contracts` when the user asks for explicit acceptance criteria or when a complex Mode B assignment needs a testable thesis, source, analysis, citation, or delivery gate. Keep any contract in a clearly labeled workspace-only section above the footer.

An Estimated Effort table is optional. Include one only when the report itself commissions or evaluates multi-phase follow-up work.

## Dismissible Footer

Every report ends with the exact footer from `references/dismissible-footer.md`. The official report begins at line 1 with its title or report content; never put workflow status or mode metadata at the top. The footer carries only lifecycle and dates, includes no mode tag, and instructs the user to delete everything below the final divider before external delivery.

Footer cardinality is strict: every report contains exactly one canonical dismissible footer. Creation appends the footer once. Update and reopen locate the existing footer and replace or normalize that block in place; they never append another footer. If update/reopen finds no footer or more than one footer, stop and repair the report to exactly one canonical footer before continuing.

## Workflow

1. Read the relevant source/evidence and determine create, update, or reopen.
2. Infer Mode, Subject, Topic, audience, and required body depth.
3. Resolve ambiguity before writing; do not guess evidence or source content.
4. For create, calculate the combined Live plus Historical number.
5. For reopen, collision-check the Live destination before moving and renaming.
6. For creation, draft the body and append the exact pending footer once. For update/reopen, replace or normalize the one existing footer in place. Never append a footer during update/reopen. Preserve unrelated user-authored content.
7. Write UTF-8 and verify the path, filename, required sections, source honesty, and footer.
8. Report the path, Mode used, Subject, number, and any access limitations.
9. For a staging request, follow the Send-Ready Staging section instead; staging never enters the create/update/reopen workflow.

## Boundaries

Do not finalize reports, send them externally, claim an issue was reproduced without evidence, fabricate inaccessible sources, store a mode tag, create a top lifecycle header, or overwrite a destination. `finalize-report` exclusively owns the pending-to-reported transition. Staging produces send-ready copies only; it never transmits a report externally and never modifies, moves, or renumbers a durable report.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to durable reports and every later reopen, evidence, or content update.

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

This skill owns report mode, evidence, sections, source honesty, dismissible footer, Subject, permanent number, path, update/reopen behavior, and lifecycle. When co-invoked with `html-this` or `pdf-this`, run the full report workflow and save only the requested `.html` or `.pdf` artifact unless the user requests multiple formats. The format skill may improve presentation but must preserve the report's facts, evidence boundaries, and lifecycle footer meaning.

Treat same-stem `.md`, `.html`, and `.pdf` variants as one report and one numbering entry. Update or reopen the complete sibling set together. This section overrides `.md`-only examples only for the co-invoked run; `_pending`/`_reported` rules remain.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

**Availability guard.** Confirm `markdown-table-aligner` is loaded before writing the final artifact. If it is unavailable, pause and tell the user that deterministic alignment cannot run; continue with the portable manual rule only if the user explicitly approves that fallback.

For an in-scope Markdown file or staged Markdown source:

1. Run the aligner's read-only `check`.
2. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. Do not reject or rework the table solely because a particular editor, emoji fallback font, or proportional renderer shows a residual pixel-level offset.
3. If exit `1` contains only safe padding findings, run `format` to a distinct nonexistent staged path, review the diff, adopt the staged result, and rerun `check`.
4. If exit `1` contains overflow, malformed, or ambiguous findings, make the editorial repair manually and rerun the helper; the script never chooses truncation text or overflow notes.
5. Exit `2` is an operational failure. Stop rather than falling back silently or treating raw character count as authoritative.
6. Preserve the complete portable Markdown Table Alignment rule below. The helper supplements it and never replaces it.

For HTML or PDF requested from Markdown, run the helper against the exact Markdown source packet before serialization. Chat-only tables continue to use the portable manual rule until block/stdin input is separately implemented.

## Markdown Table Alignment

Every Markdown table this skill writes or causes to be written must be visually pipe-aligned. Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view.

Rendered visual alignment is authoritative; raw `|` indices are diagnostic only, because Unicode display width (emoji, arrows, wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. When a table exceeds approximately 120 characters in total width, narrow the columns and move detail to notes so it renders on one line without word-wrapping.

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

After create/update/reopen, confirm:

- the expected Live path exists and the Historical source is absent after reopen
- Subject is unnumbered and `N.)` is permanent and collision-free
- filename ends in `_pending.md`
- the selected mode's required sections exist
- summary and analysis are distinct in Mode B
- unknown or inaccessible evidence is labeled honestly
- the exact dismissible pending footer is last
- exactly one canonical dismissible footer exists
- UTF-8 was preserved

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep stdout and stderr separate, reading pass/fail from the process exit code. Confirm the `## Markdown Table Alignment` section in this skill remains present in full, and confirm the staging operation, strip list, folder rule, and verification requirements remain in force.
