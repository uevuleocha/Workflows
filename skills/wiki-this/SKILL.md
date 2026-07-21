---
name: wiki-this
description: Set up a schema-driven plain-markdown wiki in the current workspace. Use when the user invokes /wiki-this, says use wiki-this, make this workspace a wiki, set up a wiki here, initialize the workspace wiki, or asks to establish a new LLM-maintained wiki with declared read-only source roots.
---

# Wiki This

Set up a new, workspace-owned LLM wiki whose taxonomy and page formats are
declared by that workspace's own `wiki/wiki-schema.md`.

This skill creates the wiki system. Use `wiki-sync` to maintain it afterward.

## Project Contract

Read and obey the current workspace's canonical contract before doing anything.
Its safety, naming, encoding, approval, and direct-edit rules remain in force.

## Invocation

Treat these as direct invocation:

- `/wiki-this`
- `use wiki-this`
- `make this workspace a wiki`
- `set up a wiki here`
- `initialize the workspace wiki`

If `wiki/wiki-schema.md` already exists, do not overwrite it. Explain that the
workspace already has a wiki and offer `wiki-sync` instead. If only part of the
scaffold exists, inventory it and propose a repair; do not silently replace it.

## Non-Negotiable Boundaries

- Scope is the current workspace root. Do not create a wiki elsewhere.
- Every declared source root is read-only while wearing the wiki-maintainer role:
  never edit, move, rename, or delete a source.
- The wiki is plain Markdown. Do not create, configure, or require an Obsidian
  vault; Obsidian may be an optional viewer only.
- Create no `CLAUDE.md`, `AGENTS.md`, or other workspace marker inside `wiki/`.
- Do not assume a universal taxonomy. Page types, folders, and formats must be
  chosen for this workspace and recorded in its schema.
- Never descend into a nested workspace while inspecting candidate sources.

## Required Inputs

Infer what is safe, then ask only for decisions that materially shape the wiki:

1. Current workspace root.
2. Source roots: existing workspace-relative paths that feed the wiki.
3. Wiki purpose and primary readers.
4. Context-appropriate page types/categories and their page formats.
5. Federation relationship, if this workspace belongs to a larger wiki system.
6. Whether `wiki/` should be tracked or ignored under wiki-follows-sources.
7. Whether to run an initial `wiki-sync` after setup or stop at the scaffold.

Source roots and taxonomy require user confirmation before files are written.
Never infer consent to make source directories or reorganize existing material.

## Setup Workflow

### 1. Resolve and inspect the workspace

- Treat the workspace in which the skill was invoked as the scope root.
- Read its canonical contract and relevant structural documentation.
- Check for an existing `wiki/`, `wiki/wiki-schema.md`, root `CLAUDE.md`, and
  root `AGENTS.md`.
- Identify nested workspaces by the host workspace's marker rule. At minimum,
  treat child directories containing canonical agent-contract markers as
  separate workspaces and exclude their contents from source inspection.
- Inspect only enough candidate material to propose source roots and taxonomy.
- When the established Hub `wiki/wiki-schema.md` is available through the
  workspace context or as a user-provided reference, read it as a starter example
  to adapt. Copy its operating concerns, not its workspace-specific roots,
  taxonomy, folders, or paths. If it is unavailable, do not invent a Hub path or
  make setup depend on it.

### 2. Propose the wiki design

Present a compact checkpoint containing:

- confirmed workspace root;
- proposed workspace-relative source-root list;
- proposed page types/categories, folders, and page formats;
- proposed `wiki/` tree containing `wiki-schema.md`, `index.md`, and `log.md`;
- exact pointer lines to add to root `CLAUDE.md` and `AGENTS.md`;
- whether to track or ignore `wiki/` under the wiki-follows-sources rule: when
  sources are published, publish the wiki; when sources are intentionally
  ignored/private, normally ignore the wiki too. Present the choice without
  forcing a default;
- federation behavior, if applicable;
- whether the first sync is included and, if so, the requested ingest scope and
  order. Any proposed batching must be confirmed by the user first.

Derive page types from context. A software wiki, research wiki, book wiki, and
business wiki may need different taxonomies. Reuse an established taxonomy only
when it fits; never force one merely because another workspace uses it.

Use the Hub schema only as an adaptable example of a complete rulebook. The new
workspace's approved needs remain authoritative.

Wait for explicit approval or revisions before creating or editing files.

### 3. Create the scaffold

After approval:

1. Create `wiki/` at the current workspace root.
2. Create `wiki/wiki-schema.md`, `wiki/index.md`, and `wiki/log.md`.
3. Create only the category folders declared by the approved schema.
4. Add the approved short wiki pointer to root `CLAUDE.md` and `AGENTS.md`.
   If one is absent, follow the project contract: do not invent a replacement
   marker or create a contract file without approval.
5. Append an `init` entry to `log.md` using the schema's log convention.
6. Apply the user's approved wiki-follows-sources choice to `.gitignore` only
   when that file and edit are inside the authorized workspace scope. Preserve
   unrelated ignore rules.

The schema is the single source of truth for:

- declared source roots;
- read-only role rules;
- workspace scoping and nested-workspace exclusions;
- taxonomy, folder mapping, naming, page formats, and citation rules;
- index and log conventions;
- federation rules;
- sync, query, and lint behavior supported by this wiki.

### 4. Verify setup

- Confirm all created paths are inside the current workspace.
- Confirm every source path is unchanged.
- Confirm the schema contains the approved source roots and taxonomy.
- Confirm `index.md` and `log.md` match the schema.
- Confirm root pointer lines resolve to `wiki/wiki-schema.md`.
- Confirm no workspace marker exists inside `wiki/`.
- Report created files and any deferred decisions.

### 5. Optional first sync

If the user approved an initial sync, invoke `wiki-sync` as a separate operation
after setup verification. Pass through the user's requested ingest scope and
order exactly.

If the discovered ingest manifest is large, `wiki-sync` may propose batches for
quality, but must show the batch plan and receive confirmation before batching.
If the user requests one-shot ingestion, everything at once, or a specific
order, follow that instruction; do not substitute agent-selected batches. Each
confirmed batch is a separate sync pass with its own source-immutability check.

During the optional first sync, `wiki-sync` must also detect and name any source
group that appears mostly historical, then ask whether to ingest it normally or
use the optional mine-and-fold + light history treatment. Never assume consent,
never hardcode detection to summaries or another folder name, and never invent a
history folder outside the approved schema. Pass every group decision through to
`wiki-sync` exactly.

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
- ingest was silently batched, truncated, or reordered against the user's
  instruction;
- a historical group received mine-and-fold or light-history treatment without
  being named and explicitly approved by the user.

## Validation

Report the resolved workspace root, approved source roots, created scaffold,
pointer status, source-immutability evidence, and whether `wiki-sync` is next.
Also report the wiki-follows-sources choice, any approved initial-sync order or
batching decision, and every history-aware group choice made during first sync.

