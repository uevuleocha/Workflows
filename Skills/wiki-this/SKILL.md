---
name: wiki-this
description: Set up a schema-driven plain-markdown wiki in the current workspace. Use when the user invokes /wiki-this, says use wiki-this, make this workspace a wiki, set up a wiki here, initialize the workspace wiki, or asks to establish a new LLM-maintained wiki with declared read-only source roots.
---

# Wiki This

Set up a new, workspace-owned LLM wiki whose taxonomy and page formats are declared by that workspace's own `wiki/wiki-schema.md`.

This skill creates the wiki system. Use `wiki-sync` to maintain it afterward.

## Project Contract

Read and obey the current workspace's canonical contract before doing anything. Its safety, naming, encoding, approval, and direct-edit rules remain in force.

## Invocation

Treat these as direct invocation:

- `/wiki-this`
- `use wiki-this`
- `make this workspace a wiki`
- `set up a wiki here`
- `initialize the workspace wiki`

If `wiki/wiki-schema.md` already exists, do not overwrite it. Explain that the workspace already has a wiki and offer `wiki-sync` instead. If only part of the scaffold exists, inventory it and propose a repair; do not silently replace it.

## Non-Negotiable Boundaries

- Scope is the current workspace root. Do not create a wiki elsewhere.
- Every declared source root is read-only while wearing the wiki-maintainer role: never edit, move, rename, or delete a source.
- The wiki is plain Markdown. Do not create, configure, or require an Obsidian vault; Obsidian may be an optional viewer only.
- Create no `CLAUDE.md`, `AGENTS.md`, or other workspace marker inside `wiki/`.
- Do not assume a universal taxonomy. Page types, folders, and formats must be chosen for this workspace and recorded in its schema.
- Never descend into a nested workspace while inspecting candidate sources.

## Required Inputs

Infer what is safe, then ask only for decisions that materially shape the wiki:

1. Current workspace root.
2. Source roots: existing workspace-relative paths that feed the wiki.
3. Wiki purpose and primary readers.
4. Context-appropriate page types/categories and their page formats. Among them, a history location and light-history page format, since `wiki-sync` files light history pages there by mandatory default. Treat it as one of the page types you propose, not as a separate question to put to the user.
5. Federation relationship, if this workspace belongs to a larger wiki system.
6. Whether `wiki/` should be tracked or ignored under wiki-follows-sources.
7. Whether to run an initial `wiki-sync` after setup or stop at the scaffold.

Source roots and taxonomy require user confirmation before files are written. Never infer consent to make source directories or reorganize existing material.

## Setup Workflow

### 1. Resolve and inspect the workspace

- Treat the workspace in which the skill was invoked as the scope root.
- Read its canonical contract and relevant structural documentation.
- Check for an existing `wiki/`, `wiki/wiki-schema.md`, root `CLAUDE.md`, and root `AGENTS.md`.
- Identify nested workspaces by the host workspace's marker rule. At minimum, treat child directories containing canonical agent-contract markers as separate workspaces and exclude their contents from source inspection.
- Inspect only enough candidate material to propose source roots and taxonomy.
- When the established Hub `wiki/wiki-schema.md` is available through the workspace context or as a user-provided reference, read it as a starter example to adapt. Copy its operating concerns, not its workspace-specific roots, taxonomy, folders, or paths. If it is unavailable, do not invent a Hub path or make setup depend on it.

### 2. Propose the wiki design

Present a compact checkpoint containing:

- confirmed workspace root;
- proposed workspace-relative source-root list;
- proposed page types/categories, folders, and page formats;
- within them, the proposed history location and light-history page format, named explicitly so the user approves it rather than inheriting it silently. Say plainly what it is for: `wiki-sync` applies mine-and-fold + light history to historical source groups by mandatory default and must have a declared place to file them, otherwise the first sync stops to request a schema amendment;
- proposed `wiki/` tree containing `wiki-schema.md`, `index.md`, and `log.md`;
- exact pointer lines to add to root `CLAUDE.md` and `AGENTS.md`;
- whether to track or ignore `wiki/` under the wiki-follows-sources rule: when sources are published, publish the wiki; when sources are intentionally ignored/private, normally ignore the wiki too. Present the choice without forcing a default;
- federation behavior, if applicable;
- whether the first sync is included and, if so, the requested ingest scope and order. Any proposed batching must be confirmed by the user first.

Derive page types from context. A software wiki, research wiki, book wiki, and business wiki may need different taxonomies. Reuse an established taxonomy only when it fits; never force one merely because another workspace uses it.

Use the Hub schema only as an adaptable example of a complete rulebook. The new workspace's approved needs remain authoritative.

Wait for explicit approval or revisions before creating or editing files.

### 3. Create the scaffold

After approval:

1. Create `wiki/` at the current workspace root.
2. Create `wiki/wiki-schema.md`, `wiki/index.md`, and `wiki/log.md`.
3. Create only the category folders declared by the approved schema, including the approved history location.
4. Add the approved short wiki pointer to root `CLAUDE.md` and `AGENTS.md`. If one is absent, follow the project contract: do not invent a replacement marker or create a contract file without approval.
5. Append an `init` entry to `log.md` using the schema's log convention.
6. Apply the user's approved wiki-follows-sources choice to `.gitignore` only when that file and edit are inside the authorized workspace scope. Preserve unrelated ignore rules.

The schema is the single source of truth for:

- declared source roots;
- read-only role rules;
- workspace scoping and nested-workspace exclusions;
- taxonomy, folder mapping, naming, page formats, and citation rules;
- the history location and light-history page format that `wiki-sync`'s mandatory mine-and-fold + light history default requires. Propose one as part of the taxonomy for user approval on every setup, because without it `wiki-sync` must stop on first contact with a historical group and request a schema amendment. Derive its name and shape from this workspace's approved taxonomy; do not copy a folder name from another workspace;
- index and log conventions;
- federation rules;
- sync, query, and lint behavior supported by this wiki.

### 4. Verify setup

- Confirm all created paths are inside the current workspace.
- Confirm every source path is unchanged.
- Confirm the schema contains the approved source roots and taxonomy.
- Confirm the schema declares a history location and light-history page format, so `wiki-sync`'s mandatory default is runnable. If the user declined one, report that first sync will stop on any historical group and request a schema amendment.
- Confirm `index.md` and `log.md` match the schema.
- Confirm root pointer lines resolve to `wiki/wiki-schema.md`.
- Confirm no workspace marker exists inside `wiki/`.
- Report created files and any deferred decisions.

### 5. Optional first sync

If the user approved an initial sync, invoke `wiki-sync` as a separate operation after setup verification. Pass through the user's requested ingest scope and order exactly.

If the discovered ingest manifest is large, `wiki-sync` may propose batches for quality, but must show the batch plan and receive confirmation before batching. If the user requests one-shot ingestion, everything at once, or a specific order, follow that instruction; do not substitute agent-selected batches. Each confirmed batch is a separate sync pass with its own source-immutability check.

During the optional first sync, `wiki-sync` detects any source group that appears mostly historical and applies **mine-and-fold + light history** to it as its mandatory default, without asking. That treatment is `wiki-sync`'s contract, not this skill's; do not restate it, weaken it, or reintroduce a per-group approval step here. `wiki-sync` stops for permission only when it has a specific strong reason to give a historical group full source pages instead. Never hardcode detection to summaries or another folder name, and never invent a history folder outside the approved schema.

Otherwise stop and hand off with the exact next step.

## Failure Conditions

Stop and report instead of claiming success if:

- a source was changed, moved, renamed, or deleted;
- the workspace root or source-root list is ambiguous;
- an existing schema would be overwritten;
- taxonomy was imposed without user approval;
- a nested workspace would be traversed;
- a marker file would be placed inside `wiki/`;
- setup created or required an Obsidian vault;
- ingest was silently batched, truncated, or reordered against the user's instruction;
- the approved schema declares no history location or light-history page format, so `wiki-sync`'s mandatory mine-and-fold default cannot run on first sync without a later schema amendment;
- a per-group approval step for historical treatment was reintroduced, contradicting `wiki-sync`'s mandatory default.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to human-facing wiki pages whose schema permits provenance; never add it to `wiki-schema.md` or another schema-sensitive control file.

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

Report the resolved workspace root, approved source roots, created scaffold, pointer status, source-immutability evidence, and whether `wiki-sync` is next. Also report the wiki-follows-sources choice, any approved initial-sync order or batching decision, whether the schema declares a history location and light-history page format, and every historical group `wiki-sync` handled during first sync with the treatment it applied.
