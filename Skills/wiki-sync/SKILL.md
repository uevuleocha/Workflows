---
name: wiki-sync
description: Maintain an existing schema-driven workspace wiki by safely detecting and ingesting new or changed declared sources, updating cross-linked pages, index, and log, or helping add source roots. Use when the user invokes /wiki-sync, says use wiki-sync, sync the wiki, update the wiki, ingest these sources, or update the sources for the wiki.
---

# Wiki Sync

Synchronize the existing wiki in the current workspace according to that workspace's `wiki/wiki-schema.md`.

The schema—not this skill—defines the source roots, taxonomy, folders, naming, page formats, citations, index, log, and federation behavior.

## Project Contract

Read and obey the current workspace's canonical contract before doing anything. Its safety, naming, encoding, approval, and direct-edit rules remain in force.

## Invocation

Treat these as direct invocation:

- `/wiki-sync`
- `use wiki-sync`
- `sync the wiki`
- `update the wiki`
- `ingest these sources`
- `update the sources for the wiki`

If `wiki/wiki-schema.md` does not exist, stop and offer `wiki-this`. Do not invent a schema during a maintenance run.

## Non-Negotiable Boundaries

- Scope is the current workspace root and its own wiki only.
- Every declared source root is strictly read-only: never edit, move, rename, or delete a source.
- Never descend into a nested workspace, including one found beneath a declared source root.
- Never hardcode page types, category folders, or hub-only paths. Read them from the active schema on every run.
- Write only to paths the schema designates as wiki outputs. A source-root change may edit the schema only after user approval.
- Do not silently delete wiki pages. Report stale or orphaned pages for review unless the schema explicitly provides an approved retirement procedure.

## Required Inputs

Normally infer these from the invocation and workspace:

1. Current workspace root.
2. `wiki/wiki-schema.md`.
3. Declared source roots and exclusion rules.
4. Existing `index.md`, `log.md`, and wiki pages.
5. Requested scope: all detected changes, named sources, or source-root update.
6. Any user permission already granted for a full-source-page exception on a detected historical group. Absent such permission, the mandatory mine-and-fold + light history default applies and is not an input to gather.

Ask only when the requested ingest order, schema meaning, source-root change, or federation action is ambiguous. Batching is never inferred as approved.

## Sync Workflow

### 1. Scope and load

- Resolve the workspace in which the skill was invoked; do not silently select a parent, sibling, or child workspace.
- Read the canonical workspace contract, then read `wiki/wiki-schema.md` fully.
- Read the schema-declared index, log, taxonomy, formats, and federation rules.
- Resolve source roots relative to the current workspace unless the schema explicitly and validly declares another form.
- Fail safely if a declared root is missing or escapes allowed scope.

### 2. Establish read-only evidence

Before wiki writes, capture a practical source-state baseline using available read-only metadata or version-control status. Choose evidence proportional to the run: file inventory plus timestamps/sizes for ordinary runs; hashes or a clean version-control diff for higher-risk verification.

This evidence is a guardrail, not permission to alter or normalize sources.

### 3. Enumerate without crossing workspaces

- Walk every declared source root recursively at any depth.
- Prune excluded paths and nested workspaces according to the host marker rule.
- At minimum, treat descendant directories containing canonical agent-contract markers as separate workspaces unless the active schema says otherwise.
- Do not ingest the wiki's own generated output as a source unless the schema deliberately declares that behavior.

### 4. Detect new or changed sources

Use the evidence the schema makes available: source provenance in page metadata, existing page content, index entries, log history, filesystem metadata, hashes, or version-control history. Do not pretend that timestamps or log prose alone prove content equality.

- New: no existing wiki provenance maps to the source.
- Changed: reliable evidence shows source content changed after its last ingest, or comparison reveals material not represented by the current wiki pages.
- Uncertain: evidence is insufficient. Put the source in a review set or ask the user whether to resynthesize it; never silently label it unchanged.

Build an ingest manifest covering every in-scope new, changed, and uncertain source. Never silently truncate the manifest. Source files remain untouched regardless of the detection outcome.

### 5. Confirm ingest order and batching

Before synthesis, show the manifest summary and the intended ingest order.

- For a large manifest or substantial rewrite, the agent may propose batches when that is likely to improve synthesis quality.
- Batching requires explicit user confirmation of the batch plan before the first batch starts. Do not silently batch.
- If the user requests a specific order, preserve it.
- If the user requests one-shot ingestion, "everything at once," or equivalent, run one complete pass in that requested order. Do not replace it with batches.
- Never use batching or one-shot execution to omit sources. Coverage must match the confirmed manifest.
- Each confirmed batch is a separate pass: establish its own read-only source baseline, synthesize its complete assigned manifest slice, update navigation and log as the schema requires, then verify source immutability before the next batch begins.

For an ordinary small manifest, confirm the manifest/order as part of the normal sync checkpoint; do not manufacture unnecessary batches.

### 6. Apply history-aware treatment

Inspect the manifest for any folder or coherent source group that is mostly a point-in-time historical record rather than durable reference knowledge. Session summaries, changelogs, migration logs, and backups are examples only; never hardcode detection to one folder name or artifact family. Detection stays context-driven and schema-driven; only the treatment applied after detection is fixed.

**Mandatory default.** For every detected historical group, **mine-and-fold + light history is the compulsory, explicit default treatment.** Apply it directly. Do not pause, do not ask the user to choose, and do not treat full source pages as the fallback. This default is not advisory and an agent may not substitute its own preference for it.

**The one exception — full source page, by permission only.** An agent may use normal ingestion with a full schema-defined source page for a historical group or item **only** when it has a specific, articulable, genuinely strong reason that the default would lose something the wiki needs. In that case it must:

1. Stop before writing that group.
2. Name the exact group or item and state the specific reason a full source page is better for it.
3. Wait for the user's explicit permission.
4. Proceed with full source pages only if permission is granted. **If the user declines, or gives no clear agreement, apply the mandatory mine-and-fold + light history default immediately and continue the run without asking a follow-up question.**

Reserve this escalation for genuine cases. Do not stop on every historical group, do not stop out of caution, and do not use the exception to reintroduce ask-every-time behavior. A run that raises no exception is the normal, correct run.

Record the treatment applied per group; a granted exception may make different groups use different treatments.

For a mine-and-fold + light history group:

- Mine durable lessons, decisions, outcomes, what worked, and what failed, then fold them into the relevant knowledge pages declared by the active schema.
- Create one light provenance page per historical item, carrying the schema's required metadata plus title, date, key decisions, what worked/failed, and links to affected knowledge pages or their schema-equivalent fields.
- File those light pages under a dedicated history type/topic/folder declared by the active schema so they remain discoverable without dominating navigation.
- If the schema does not declare a suitable history location or page format, show the exact schema amendment and wait for approval before using the treatment. This gate stays blocking even though the treatment itself is the mandatory default; a mandatory treatment never authorizes inventing a folder or taxonomy. Never hardcode a folder or taxonomy into the skill.
- Preserve coverage and provenance for every item. The treatment changes depth and filing, not whether an item is represented.

This is separate from batching: a confirmed batch may contain ordinary and historical groups, but each historical group's treatment - the default, or a permitted exception - remains binding.

### 7. Synthesize according to the schema

For each approved new or changed source:

1. Read the source.
2. Create or update its provenance representation as the schema requires.
3. Create or update the page types and categories declared by this schema.
4. Reuse the existing page for the same real thing; do not create duplicates.
5. Add the schema-required cross-links and citations in both relevant directions.
6. Mark inference and preserve conflicting claims according to the schema.
7. Preserve still-valid material from earlier sources when updating shared pages.

Never assume names such as source, entity, concept, or topic. Those are valid only when the active workspace schema declares them.

### 8. Update navigation and log

- Rebuild or update the schema-declared index so every current wiki page appears once with the required summary and grouping.
- Append exactly one sync entry in the schema's log format, summarizing processed, skipped, uncertain, and affected pages.
- Preserve append-only log history.

### 9. Apply federation rules

Read federation behavior from the schema.

- A child workspace sync touches only that workspace's wiki.
- A hub may refresh inbound links from child wikis when its schema requires it.
- Refresh links by reading child wiki navigation/schema only; never ingest child source roots or duplicate child knowledge into the hub.
- Do not create hub-to-child outbound links unless the schema and user approval allow them.

### 10. Verify source immutability and report

- Re-capture the source-state evidence used before the run.
- Confirm no source was edited, moved, renamed, or deleted.
- Review the wiki diff for schema compliance, valid citations, duplicate pages, index completeness, and one appended log entry.
- Report processed sources, uncertain sources, created/updated pages, federation changes, and source-immutability evidence.

If any source changed, stop, report a hard failure, and do not conceal it by modifying the source again.

## Updating Source Roots

When the user says "update the sources for the wiki":

1. Clarify whether they mean add/remove a declared source root or ingest new files already under a declared root.
2. Inspect the proposed root read-only and check scope/nested-workspace risks.
3. Show the exact schema change and consequences.
4. Wait for approval before editing the source-root declaration.
5. Never move files into or out of a source root.
6. Run the normal sync workflow after the schema change if approved.

Removing a root does not authorize deleting its wiki pages; produce a review list unless the schema defines an approved retirement procedure.

## Failure Conditions

Stop and report instead of claiming success if:

- a source changed, moved, renamed, or was deleted;
- the schema is missing, malformed, contradictory, or cannot resolve its roots;
- the run would cross into a nested workspace;
- a page taxonomy or folder was assumed rather than read from the schema;
- citations cannot be resolved to declared provenance;
- duplicate pages are knowingly introduced;
- a child source would be ingested into a hub wiki;
- ingestion was batched without confirmation, truncated, or reordered against the user's instruction;
- a detected historical group was given full schema-defined source pages without the agent stopping, naming the group, stating a specific strong reason, and receiving explicit user permission;
- a detected historical group was given anything other than mine-and-fold + light history while no such permission was in force;
- the user was asked to choose a treatment for a historical group, or the run paused on one, without a specific strong reason for a full source page being raised;
- mine-and-fold + light history was applied while the active schema declared no suitable history location or page format and no schema amendment was approved;
- coverage or provenance was dropped for any historical item, rather than only its depth and filing being reduced;
- history-aware behavior was hardcoded to a folder name, artifact family, page taxonomy, or output folder rather than driven by context and the schema.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to human-facing wiki pages whose schema permits provenance; preserve original creators and append each material agent update.

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

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

Report the resolved workspace, schema used, source roots, detection method, processed/uncertain sources, wiki outputs, federation actions, and before/after source-state result. State the confirmed ingest order, whether execution was one-shot or batched, every detected historical group with the treatment applied to it, and the per-pass immutability result. Name any group where the mandatory mine-and-fold + light history default was displaced by a permitted full-source-page exception, along with the reason given and the user's explicit permission, so a misjudged detection stays auditable after the run. State plainly whether the sync passed or failed.
