---
name: wiki-sync
description: Maintain an existing schema-driven workspace wiki by safely detecting and ingesting new or changed declared sources, updating cross-linked pages, index, and log, or helping add source roots. Use when the user invokes /wiki-sync, says use wiki-sync, sync the wiki, update the wiki, ingest these sources, or update the sources for the wiki.
---

# Wiki Sync

Synchronize the existing wiki in the current workspace according to that
workspace's `wiki/wiki-schema.md`.

The schema—not this skill—defines the source roots, taxonomy, folders, naming,
page formats, citations, index, log, and federation behavior.

## Project Contract

Read and obey the current workspace's canonical contract before doing anything.
Its safety, naming, encoding, approval, and direct-edit rules remain in force.

## Invocation

Treat these as direct invocation:

- `/wiki-sync`
- `use wiki-sync`
- `sync the wiki`
- `update the wiki`
- `ingest these sources`
- `update the sources for the wiki`

If `wiki/wiki-schema.md` does not exist, stop and offer `wiki-this`. Do not invent
a schema during a maintenance run.

## Non-Negotiable Boundaries

- Scope is the current workspace root and its own wiki only.
- Every declared source root is strictly read-only: never edit, move, rename, or
  delete a source.
- Never descend into a nested workspace, including one found beneath a declared
  source root.
- Never hardcode page types, category folders, or hub-only paths. Read them from
  the active schema on every run.
- Write only to paths the schema designates as wiki outputs. A source-root change
  may edit the schema only after user approval.
- Do not silently delete wiki pages. Report stale or orphaned pages for review
  unless the schema explicitly provides an approved retirement procedure.

## Required Inputs

Normally infer these from the invocation and workspace:

1. Current workspace root.
2. `wiki/wiki-schema.md`.
3. Declared source roots and exclusion rules.
4. Existing `index.md`, `log.md`, and wiki pages.
5. Requested scope: all detected changes, named sources, or source-root update.
6. User-approved history-aware treatment choices for detected groups, if any.

Ask only when the requested ingest order, schema meaning, source-root change, or
federation action is ambiguous. Batching is never inferred as approved.

## Sync Workflow

### 1. Scope and load

- Resolve the workspace in which the skill was invoked; do not silently select a
  parent, sibling, or child workspace.
- Read the canonical workspace contract, then read `wiki/wiki-schema.md` fully.
- Read the schema-declared index, log, taxonomy, formats, and federation rules.
- Resolve source roots relative to the current workspace unless the schema
  explicitly and validly declares another form.
- Fail safely if a declared root is missing or escapes allowed scope.

### 2. Establish read-only evidence

Before wiki writes, capture a practical source-state baseline using available
read-only metadata or version-control status. Choose evidence proportional to
the run: file inventory plus timestamps/sizes for ordinary runs; hashes or a
clean version-control diff for higher-risk verification.

This evidence is a guardrail, not permission to alter or normalize sources.

### 3. Enumerate without crossing workspaces

- Walk every declared source root recursively at any depth.
- Prune excluded paths and nested workspaces according to the host marker rule.
- At minimum, treat descendant directories containing canonical agent-contract
  markers as separate workspaces unless the active schema says otherwise.
- Do not ingest the wiki's own generated output as a source unless the schema
  deliberately declares that behavior.

### 4. Detect new or changed sources

Use the evidence the schema makes available: source provenance in page metadata,
existing page content, index entries, log history, filesystem metadata, hashes,
or version-control history. Do not pretend that timestamps or log prose alone
prove content equality.

- New: no existing wiki provenance maps to the source.
- Changed: reliable evidence shows source content changed after its last ingest,
  or comparison reveals material not represented by the current wiki pages.
- Uncertain: evidence is insufficient. Put the source in a review set or ask the
  user whether to resynthesize it; never silently label it unchanged.

Build an ingest manifest covering every in-scope new, changed, and uncertain
source. Never silently truncate the manifest. Source files remain untouched
regardless of the detection outcome.

### 5. Confirm ingest order and batching

Before synthesis, show the manifest summary and the intended ingest order.

- For a large manifest or substantial rewrite, the agent may propose batches
  when that is likely to improve synthesis quality.
- Batching requires explicit user confirmation of the batch plan before the
  first batch starts. Do not silently batch.
- If the user requests a specific order, preserve it.
- If the user requests one-shot ingestion, "everything at once," or equivalent,
  run one complete pass in that requested order. Do not replace it with batches.
- Never use batching or one-shot execution to omit sources. Coverage must match
  the confirmed manifest.
- Each confirmed batch is a separate pass: establish its own read-only source
  baseline, synthesize its complete assigned manifest slice, update navigation
  and log as the schema requires, then verify source immutability before the next
  batch begins.

For an ordinary small manifest, confirm the manifest/order as part of the normal
sync checkpoint; do not manufacture unnecessary batches.

### 6. Detect and confirm history-aware treatment

Inspect the manifest for any folder or coherent source group that is mostly a
point-in-time historical record rather than durable reference knowledge.
Session summaries, changelogs, migration logs, and backups are examples only;
never hardcode detection to one folder name or artifact family.

When such a group is detected:

1. Name the exact group and explain briefly why it appears mostly historical.
2. Ask the user to choose for that group:
   - normal ingestion with a full schema-defined source page per item; or
   - **mine-and-fold + light history** treatment.
3. Use mine-and-fold + light history only after explicit user agreement. If the
   user declines or does not agree, ingest that group normally.
4. Record the choice per group; different groups may use different treatments.

For an approved mine-and-fold + light history group:

- Mine durable lessons, decisions, outcomes, what worked, and what failed, then
  fold them into the relevant knowledge pages declared by the active schema.
- Create one light provenance page per historical item, carrying the schema's
  required metadata plus title, date, key decisions, what worked/failed, and
  links to affected knowledge pages or their schema-equivalent fields.
- File those light pages under a dedicated history type/topic/folder declared by
  the active schema so they remain discoverable without dominating navigation.
- If the schema does not declare a suitable history location or page format,
  show the exact schema amendment and wait for approval before using the
  treatment. Never hardcode a folder or taxonomy into the skill.
- Preserve coverage and provenance for every item. The treatment changes depth
  and filing, not whether an item is represented.

This decision is separate from batching: a confirmed batch may contain normal
and history-aware groups, but each group's user-approved treatment remains
binding.

### 7. Synthesize according to the schema

For each approved new or changed source:

1. Read the source.
2. Create or update its provenance representation as the schema requires.
3. Create or update the page types and categories declared by this schema.
4. Reuse the existing page for the same real thing; do not create duplicates.
5. Add the schema-required cross-links and citations in both relevant directions.
6. Mark inference and preserve conflicting claims according to the schema.
7. Preserve still-valid material from earlier sources when updating shared pages.

Never assume names such as source, entity, concept, or topic. Those are valid
only when the active workspace schema declares them.

### 8. Update navigation and log

- Rebuild or update the schema-declared index so every current wiki page appears
  once with the required summary and grouping.
- Append exactly one sync entry in the schema's log format, summarizing processed,
  skipped, uncertain, and affected pages.
- Preserve append-only log history.

### 9. Apply federation rules

Read federation behavior from the schema.

- A child workspace sync touches only that workspace's wiki.
- A hub may refresh inbound links from child wikis when its schema requires it.
- Refresh links by reading child wiki navigation/schema only; never ingest child
  source roots or duplicate child knowledge into the hub.
- Do not create hub-to-child outbound links unless the schema and user approval
  allow them.

### 10. Verify source immutability and report

- Re-capture the source-state evidence used before the run.
- Confirm no source was edited, moved, renamed, or deleted.
- Review the wiki diff for schema compliance, valid citations, duplicate pages,
  index completeness, and one appended log entry.
- Report processed sources, uncertain sources, created/updated pages, federation
  changes, and source-immutability evidence.

If any source changed, stop, report a hard failure, and do not conceal it by
modifying the source again.

## Updating Source Roots

When the user says "update the sources for the wiki":

1. Clarify whether they mean add/remove a declared source root or ingest new
   files already under a declared root.
2. Inspect the proposed root read-only and check scope/nested-workspace risks.
3. Show the exact schema change and consequences.
4. Wait for approval before editing the source-root declaration.
5. Never move files into or out of a source root.
6. Run the normal sync workflow after the schema change if approved.

Removing a root does not authorize deleting its wiki pages; produce a review
list unless the schema defines an approved retirement procedure.

## Failure Conditions

Stop and report instead of claiming success if:

- a source changed, moved, renamed, or was deleted;
- the schema is missing, malformed, contradictory, or cannot resolve its roots;
- the run would cross into a nested workspace;
- a page taxonomy or folder was assumed rather than read from the schema;
- citations cannot be resolved to declared provenance;
- duplicate pages are knowingly introduced;
- a child source would be ingested into a hub wiki;
- ingestion was batched without confirmation, truncated, or reordered against
  the user's instruction;
- a historical group was compressed, mined, or given light pages without being
  detected, named, and explicitly approved by the user;
- history-aware behavior was hardcoded to a folder name, artifact family, page
  taxonomy, or output folder rather than driven by context and the schema.

## Validation

Report the resolved workspace, schema used, source roots, detection method,
processed/uncertain sources, wiki outputs, federation actions, and before/after
source-state result. State the confirmed ingest order, whether execution was
one-shot or batched, every detected historical group and its user-selected
treatment, and the per-pass immutability result. State plainly whether the sync
passed or failed.

