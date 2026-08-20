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
- Never discover, infer, broaden, or add a source root. Use only roots explicitly declared in both the active schema and its coverage contract. If they are missing or disagree, stop.

## Required Inputs

Normally infer these from the invocation and workspace:

1. Current workspace root.
2. `wiki/wiki-schema.md`.
3. Declared source roots and exclusion rules.
4. Existing `index.md`, `log.md`, and wiki pages.
5. Requested scope mode: `workspace-full`, `root-full`, `named-source`, or source-root update.
6. The machine-readable coverage contract declared or referenced by the active schema. It supplies source roots, exclusions, nested-workspace markers, identity granularity, wiki provenance extraction, path comparison, and allowed skip reasons.
7. The schema-declared structural unresolved-verification page and adjacent disposition marker, when present.

Routine synchronization is autonomous. Ask only when proceeding would require guessing a source root, crossing a workspace, exposing sensitive material, destructively replacing established policy, or choosing between materially contradictory schema meanings. Complete safe work first and report non-blocking concerns or recommendations afterward.

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

### 3. Select an explicit scope mode

Every ingest run declares exactly one coverage scope before enumeration:

- `workspace-full`: every eligible identity under every declared source root. Only this scope can support a claim that the entire workspace wiki is synchronized.
- `root-full`: every eligible identity under one schema-declared root. It may claim only that named root is synchronized.
- `named-source`: one or more explicit schema-derived source identities. It may claim only that named scope is synchronized and must never imply workspace-wide or root-wide coverage.

Use `workspace-full` when the user invokes `wiki-sync`, says "sync," or otherwise requests an ordinary update without naming a narrower scope. Use `root-full` or `named-source` only when the user explicitly identifies that narrower scope. Never infer additional source roots while selecting scope.

The active schema must declare or reference a machine-readable version-1 coverage contract following `references/coverage-reconciliation-contract.md`.

**Autonomous compatibility bridge.** If the contract is missing but the schema already declares an explicit, unambiguous source-root list and enough identity/include/exclude/provenance meaning to mirror it exactly, create `wiki/coverage-contract.json`, add the schema reference, validate it, and continue the same run. This is a mechanical representation of already-declared policy, not permission to infer or change sources. For non-source mechanics the version-1 reference supplies deterministic defaults when the schema is silent: exact-case path comparison, canonical nested-workspace markers, and the reference's allowed skip reasons. Report those defaults afterward. If any source root, identity boundary, include/exclude scope, wiki path, or provenance field would need to be guessed, stop and report the exact ambiguity. Never claim deterministic coverage until the generated contract passes the helper.

### 4. Enumerate without crossing workspaces

- Walk every declared source root recursively at any depth.
- Prune excluded paths and nested workspaces according to the host marker rule.
- At minimum, treat descendant directories containing canonical agent-contract markers as separate workspaces unless the active schema says otherwise.
- Do not ingest the wiki's own generated output as a source unless the schema deliberately declares that behavior.
- Run `scripts/reconcile_wiki_sources.py inventory` against the resolved workspace and schema-declared contract. Treat exit `2` as an operational failure. Preserve the JSON inventory as the authoritative eligible-identity set for this checkpoint.

### 5. Classify every selected identity

Use the evidence the schema makes available: source provenance in page metadata, existing page content, index entries, log history, filesystem metadata, hashes, or version-control history. Do not pretend that timestamps or log prose alone prove content equality.

- `represented-unchanged`: current wiki provenance maps to the identity and reliable evidence supports no material source change.
- `new`: no current or previous wiki provenance maps to the identity.
- `changed`: current provenance maps to the identity, or a moved/renamed identity explicitly names its stale `previous_paths`, and reliable evidence shows material change or path/lifecycle drift.
- `uncertain`: evidence is insufficient. Put the identity in the mandatory resynthesis set and report it afterward; never silently label it unchanged and never interrupt a safe run merely to ask whether it should be reread.
- `skipped`: the identity is deliberately omitted for a reason code explicitly allowed by the active coverage contract. Free-form or invented skip reasons are invalid.

Build a version-1 JSON manifest containing every identity selected by the scope, including represented-and-unchanged identities. Each identity appears exactly once. For moved or renamed sources, use `previous_paths` to reconcile stale provenance; a path mapping does not prove content equality, so preserve any content uncertainty separately.

Do not pretend that timestamps, log prose, or a prior "full sync" status alone prove unchanged content. Use hashes, version-control comparison, or direct semantic comparison when available. If reliable evidence is unavailable, classify the identity as `uncertain`.

### 6. Coverage Reconciliation Gate

After classification and before synthesis, run `scripts/reconcile_wiki_sources.py check` with the exact scope, `--phase before`, and `--claim none`. The helper is read-only and must remain generic; all workspace-specific meaning comes from the active coverage contract.

The gate must prove:

1. every selected eligible identity is classified exactly once;
2. every `represented-unchanged` identity has current provenance;
3. every `new` identity lacks current and previous provenance;
4. every `changed` identity has current provenance or explicitly reconciled previous provenance;
5. every skipped identity uses a schema-supported reason;
6. stale provenance is either reconciled through `previous_paths` or reported as unexplained; and
7. the requested status claim, when later made, matches the declared scope.

Exit `1` means coverage or claim findings exist; fix the manifest or disclose and resolve the finding before synthesis. Exit `2` means validity is unknown because the contract, manifest, path, encoding, or runtime operation failed; stop. Never shrink the manifest to make the gate pass.

An uncertainty or schema-supported skip is disclosed and processed conservatively in the same run. It prevents a synchronized status claim for that scope until resolved, but it does not by itself require a user checkpoint. Reserve `workspace-synced`, `root-synced`, and `scoped-synced` for their matching scopes with complete reconciliation and zero uncertain or skipped identities.

### 7. Select autonomous ingest order and batching

Select a deterministic ingest order and continue without a routine pre-write checkpoint. Preserve any user-specified order. Otherwise order by coverage-contract root order, then stable workspace-relative identity path. Keep the complete manifest inspectable in run evidence and report classification counts, every new/changed/uncertain/skipped identity, reconciled stale paths, execution order, and permitted claim after completion.

- For a large manifest or substantial rewrite, the agent may use internal batches when that is likely to improve synthesis quality.
- Internal batching must remain one uninterrupted invocation and must not request routine confirmation.
- If the user requests a specific order, preserve it.
- If the user requests one-shot ingestion, "everything at once," or equivalent, run one complete pass in that requested order. Do not replace it with batches.
- Never use batching or one-shot execution to omit sources. Coverage must match the complete manifest.
- Each internal batch is a separate verification slice: establish its own read-only source baseline, synthesize its complete assignment, update navigation and log as the schema requires, then verify source immutability before continuing automatically.

For an ordinary small manifest, use one pass and continue directly.

### 8. Apply history-aware treatment

Inspect the manifest for any folder or coherent source group that is mostly a point-in-time historical record rather than durable reference knowledge. Session summaries, changelogs, migration logs, and backups are examples only; never hardcode detection to one folder name or artifact family. Detection stays context-driven and schema-driven; only the treatment applied after detection is fixed.

**Mandatory default.** For every detected historical group, **mine-and-fold + light history is the compulsory, explicit default treatment.** Apply it directly. Do not pause, do not ask the user to choose, and do not treat full source pages as the fallback. This default is not advisory and an agent may not substitute its own preference for it.

**Full-page recommendation after completion.** A sync never pauses to request a historical full-page exception. Even when the agent has a strong reason that a full page may be better, it first applies the mandatory light treatment, completes the run, and reports the exact item and reason afterward. Only a later explicit user instruction may convert that already-represented item to a full schema-defined page. The recommendation is advice, not pending sync work.

Record the light treatment applied per group and every post-run full-page recommendation.

For a mine-and-fold + light history group:

- Mine durable lessons, decisions, outcomes, what worked, and what failed, then fold them into the relevant knowledge pages declared by the active schema.
- Create one light provenance page per historical item, carrying the schema's required metadata plus title, date, key decisions, what worked/failed, and links to affected knowledge pages or their schema-equivalent fields.
- File those light pages under a dedicated history type/topic/folder declared by the active schema so they remain discoverable without dominating navigation.
- If the schema lacks a history location or page format and its existing taxonomy admits one unambiguous compatible location, add that minimal wiki-output declaration and continue. If competing locations would materially change the taxonomy, stop rather than guess. Never hardcode a workspace-specific folder into the skill.
- Preserve coverage and provenance for every item. The treatment changes depth and filing, not whether an item is represented.

This is separate from batching: every batch applies the same automatic light treatment.

### 9. Maintain forward-only unresolved verification

Use the structural page declared by the schema, normally `wiki/unresolved-verification.md`. If an existing schema lacks the declaration, add this compatible structural wiki-output declaration and create an empty page in the same run; this does not authorize source changes or legacy backfill.

For each `new` or `changed` source actually read during this run:

1. Determine whether it is a finalized durable artifact from its own status/lifecycle evidence and whether it carries a DEFINITION OF DONE, Verification Checklist, or equivalent verification checkboxes.
2. Collect every unticked item (`- [ ]`) regardless of an ordinary explanation.
3. Exclude only an item carrying the standardized adjacent disposition line `Verification disposition: intentionally left unchecked -- <reason>.` directly beneath or beside that exact checkbox.
4. Replace that source's prior unresolved-page entries with its current unresolved set. A checked or dispositioned item therefore disappears on the next sync after the source changes.
5. Record each remaining item with only its source artifact path, owning section, and checkbox text. The page is a discovery view; never put authoritative checkboxes on it and never edit the source while wearing the wiki-maintainer role.

Preserve existing unresolved-page entries for `represented-unchanged` sources without reopening those sources solely for this feature. Do not scan or backfill any source already represented and unchanged when the feature is introduced. Sources first ingested after introduction, including every source in a new wiki's initial ingestion, are eligible because that ingestion is forward work.

If no entries exist, retain the page with a short statement that no unresolved verification items have been recorded from forward ingestions.

### 10. Synthesize according to the schema

For each new, changed, or conservatively resynthesized uncertain source:

1. Read the source.
2. Create or update its provenance representation as the schema requires.
3. Create or update the page types and categories declared by this schema.
4. Reuse the existing page for the same real thing; do not create duplicates.
5. Add the schema-required cross-links and citations in both relevant directions.
6. Mark inference and preserve conflicting claims according to the schema.
7. Preserve still-valid material from earlier sources when updating shared pages.

Never assume names such as source, entity, concept, or topic. Those are valid only when the active workspace schema declares them.

### 11. Update navigation and log

- Rebuild or update the schema-declared index so every current wiki page appears once with the required summary and grouping.
- Append exactly one sync entry in the schema's log format, summarizing processed, skipped, uncertain, and affected pages.
- Preserve append-only log history.

### 12. Apply federation rules

Read federation behavior from the schema.

- A child workspace sync touches only that workspace's wiki.
- A hub may refresh inbound links from child wikis when its schema requires it.
- Refresh links by reading child wiki navigation/schema only; never ingest child source roots or duplicate child knowledge into the hub.
- Do not create hub-to-child outbound links unless the schema and user approval allow them.

### 13. Reconcile again, verify source immutability, and report

- Re-capture the source-state evidence used before the run.
- Confirm no source was edited, moved, renamed, or deleted.
- Re-run the helper with `--phase after` against a fresh inventory and the completed manifest. This catches an identity added, moved, renamed, or deleted after the first gate, requires new and changed identities to have current provenance, and requires every stale path to be repaired.
- Run the matching status claim: `workspace-synced` for `workspace-full`, `root-synced` for `root-full`, or `scoped-synced` for `named-source`. Do not publish a broader status than the helper permits.
- Review the wiki diff for schema compliance, valid citations, duplicate pages, index completeness, and one appended log entry.
- Report scope mode, eligible and classified counts, every status count, reconciled and unexplained stale provenance, processed and uncertain sources, unresolved-verification additions/removals, created/updated pages, internal batching, historical full-page recommendations, federation changes, the permitted synchronization claim, and source-immutability evidence.

If any source changed, stop, report a hard failure, and do not conceal it by modifying the source again.

## Updating Source Roots

When the user says "update the sources for the wiki":

1. Clarify whether they mean add/remove a declared source root or ingest new files already under a declared root.
2. Inspect the proposed root read-only and check scope/nested-workspace risks.
3. Show the exact schema change and consequences.
4. Require the user to explicitly name and authorize the exact source-root change before editing the declaration; never infer it from repository layout.
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
- ingestion was truncated or reordered against the user's instruction;
- a routine manifest, batching, uncertainty, or historical-treatment checkpoint interrupted a safe run;
- a detected historical group was given a full source page automatically instead of light treatment plus an optional post-run recommendation;
- a detected historical group was given anything other than mine-and-fold plus light history without a later explicit user instruction;
- mine-and-fold plus light history used a guessed or contradictory history location;
- coverage or provenance was dropped for any historical item, rather than only its depth and filing being reduced;
- history-aware behavior was hardcoded to a folder name, artifact family, page taxonomy, or output folder rather than driven by context and the schema;
- the active schema does not declare or reference a valid machine-readable coverage contract after the compatibility bridge, or the bridge guessed any source meaning;
- the schema and coverage contract disagree on source roots;
- represented-and-unchanged sources were reopened solely to backfill unresolved verification;
- an unresolved item with the exact adjacent disposition marker was re-listed;
- an unresolved-page entry omitted its source path, owning section, or checkbox text;
- any selected eligible identity is absent from the manifest, duplicated, or silently classified as unchanged;
- the reconciliation helper exits `1` and its findings remain unresolved, or exits `2` and validity is unknown;
- stale provenance remains unexplained by a current identity's `previous_paths`;
- an uncertain or skipped identity is hidden from the user or included in a synchronized status claim;
- a `named-source` or `root-full` run claims the entire workspace wiki is synchronized; or
- the post-synthesis reconciliation is skipped, allowing source-state drift during the run to go undetected.

## Coverage Helper Contract

`scripts/reconcile_wiki_sources.py` and `references/coverage-reconciliation-contract.md` are required parts of this skill bundle. The script uses only the Python standard library, reads UTF-8, writes no files, emits JSON, and uses exit `0` for a clean inventory/check, `1` for coverage or claim findings, and `2` for operational failure.

The helper deliberately does not decide semantic freshness. The agent supplies evidence-backed classifications; the helper proves that the selected eligible identity set, manifest, provenance, stale paths, and status claim reconcile without gaps. This separation prevents a generic tool from hardcoding one workspace's taxonomy or pretending that timestamps establish equality.

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

Before this skill creates or materially edits the first first-party durable artifact in a session, invoke `exact-model-confirmation-gate`. The gate must finish before any new `Original writing LLM` or current-run Agent Change Log `Model` value is written.

- Reuse the gate's verified identity for later durable-artifact writes while the exact model context, acting agent, task or thread, and execution environment remain unchanged. Do not ask again during that stable session.
- If authoritative current runtime or session evidence cannot establish the exact model, stop before the first write and ask the user once. Cache a valid answer only for the current stable session.
- Invalidate prospectively when the user reports a model change or authoritative evidence shows that the model, agent, task or thread, or execution environment changed. Never rewrite historical provenance or change-log rows.
- Keep reasoning effort, service tier, provider, model family, and agent family separate from exact identity. Reject labels such as `Medium`, `Priority`, `OpenAI`, `GPT-5`, and `Codex Agent` as substitutes for a full model identity.
- Do not inspect configuration, environment data, credentials, logs, transcripts, or unrelated files by default. Only the gate's genuinely unavoidable file-backed branch may invoke `tread-lightly`, request one model field, and accept it only when it authoritatively identifies the current session. This skill does not gain a blanket `tread-lightly` dependency.
- Use `Not recorded` only when no interactive user is available, the user cannot identify the model, or exact identity remains safely unresolvable after the permitted attempt.

If `exact-model-confirmation-gate` is unavailable and no verified stable-session result already exists, fail closed before the artifact write rather than guessing, silently using `Not recorded`, or performing broader discovery.

**Validation check:** Confirm the dependency is named in this skill and its README; the canonical caller block is byte-identical to `exact-model-confirmation-gate/references/canonical-caller-block.md`; first-write blocking, one-time confirmation, stable-session reuse, proactive change, context invalidation, identity separation, targeted lookup, unresolved fallback, and append-only history pass the shared deterministic suite; and no historical row was rewritten.

## Validation

Run `python -X utf8 scripts/test_reconcile_wiki_sources.py` and require exit `0`. The regression suite must cover a source added after the last sync, renamed or moved provenance, unreliable timestamps, exact-case nested-workspace exclusions, historical-source provenance, a truncated manifest, a named-source run attempting a workspace-wide claim, semantic directory bundles, source-state drift during a run, stale provenance, and schema-supported skip reasons.

Validate the complete folder-style skill with `quick_validate.py` in Python UTF-8 mode. Confirm the helper and contract reference are included in every synchronized copy and prove recursive byte parity against the local master.

Report the resolved workspace, schema and coverage contract used or created, exact declared source roots, scope mode, detection method, eligible/classified/status counts, reconciled/unexplained stale provenance, processed/uncertain/skipped sources, unresolved-verification changes, wiki outputs, permitted synchronization claim, federation actions, and before/after source-state result. State ingest order, one-shot or internal-batch execution, every historical group receiving light treatment, every optional full-page recommendation, and per-pass immutability. State plainly whether the autonomous run passed or failed and surface non-blocking advice only after completed work.
