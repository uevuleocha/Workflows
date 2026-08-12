---
name: workspace-setup
description: Set up a new workspace, restore an existing workspace to parity, or maintain universal workspace standards in the hub. Inspects against the universal standards checklist, uses set-the-stage to brief the user before any changes, and supports one-shot or phased execution. Use when the user invokes /workspace-setup, asks to set up a workspace, check workspace parity, align a workspace, or create/update universal workspace standards.
---

# Workspace Setup

Set up, audit, and restore parity for any workspace in Uzzy's AI OS. This skill owns the universal-standards checklist, the inspection, the classification, and the execution orchestration. It uses `set-the-stage` to present an evidence-based briefing to the user before any mutations.

## Project Contract

This skill operates under the project's canonical contract (`CLAUDE.md`, `AGENTS.md`). Safety rules, path scope, destructive-operation gates, one-editor-per-file, secret safety, repository boundaries, and user-change preservation apply unchanged.

## The Local Clone — Statefulness Anchor

This is the core design principle: **every child workspace gets its own local working copy of the universal standards document.** The clone is the skill's statefulness mechanism. It lets the agent know — across sessions, across agents — exactly where to start without guessing.

- **Clone path:** `Archive/Live/Documentation/Personal/AI OS & Knowledge Bases/` relative to the target workspace root. This path is fixed across all workspaces.
- **Master filename:** the Hub's authoritative standard uses `N.) Universal Workspace Standards + Setup & Parity Checklist_Master.md`. The current Hub master is `3.) Universal Workspace Standards + Setup & Parity Checklist_Master.md`.
- **Clone filename:** every child workspace uses `N.) Universal Workspace Standards + Setup & Parity Checklist_{Workspace Name} Clone.md`. Assign the next available workspace-local `N.)` number in that Subject folder, replace `{Workspace Name}` with the canonical workspace name while preserving its established spelling and casing, and never leave the placeholder braces in the filename. For example, Workflows uses `1.) Universal Workspace Standards + Setup & Parity Checklist_Workflows Clone.md`.
- **Clone presence is the first baseline signal:**
  - No clone found → no prior `workspace-setup` baseline exists; the local anchor must be created as part of this run. Clone absence alone does not prove the workspace is new — it only means `workspace-setup` has never established a baseline here. Determine workspace age/state from all available evidence (contract files, Git repo, README, folder structure). An established workspace without a clone is still `Existing workspace` — the missing clone is an anchor/parity gap, not proof of freshness.
  - Clone found → a prior baseline exists; compare it against the current hub version to detect drift and stage only the items that have changed.
- **Clone content:** a faithful copy of the universal standards document from the hub, plus clearly separated workspace-specific annotations where appropriate. The universal standards content must remain synchronized with the hub; workspace-specific notes live in their own clearly delimited section so future syncs can update the shared content without touching local vocabulary.
- **Checklist state:** task markers and indented `Workspace status` notes in a child clone are workspace-local state. They must survive Hub synchronization and must never be copied back into the Hub master.
- **Sync is transport, not authorship.** Updating the clone is not new authorship — it is synchronization of the hub's standards into the workspace's local reference. Preserve provenance from the source; do not overwrite workspace-specific provenance or local annotations.

## Invocation

Treat these as direct invocation:

- `/workspace-setup`
- `use workspace-setup`
- `use the workspace-setup skill`
- `set up this workspace`
- `check workspace parity`
- `align this workspace`
- `setup workspace`
- `restore workspace parity`
- clear equivalents asking to create, audit, align, or restore a workspace against universal standards

## Hub vs Child Routing

The skill behaves differently depending on where it is invoked.

### Hub Maintenance Direction

When invoked in the Uzzys Universe hub (`C:\Users\Admin\Uzzys Universe\`), interpret the request as creating, refining, or registering a universal workspace standard. The hub is where universal standards are authored and maintained.

1. Determine whether the user wants to update the hub reference implementation (`CLAUDE.md`, `AGENTS.md`), the universal standards document, or both.
2. Classify the proposed rule as **universal** (every workspace), **conditional** (only when the feature applies), or **workspace-specific** (hub-only).
3. Never promote a hub-only behavior into every workspace merely because it appears in the hub.
4. When a rule is universal, ensure it is represented explicitly and trackably in the standards document.
5. Preserve user review gates for material wording or classification decisions.

### Child Setup/Parity Direction

When invoked in any non-hub workspace, use the standards document as the universal compliance baseline and the hub `CLAUDE.md` and `AGENTS.md` as reference implementations.

1. Look for the local clone of the standards document first (see The Local Clone section above).
2. If the clone exists, read it as the workspace's current known baseline. Diff it against the current hub version to detect what has drifted.
3. If the clone is absent, record the missing clone as an anchor/parity gap. Determine `New workspace` versus `Existing workspace` from complete workspace evidence (contract files, Git repo, README, folder structure), not from clone absence. Assign the appropriate parity verdict independently. Stage creation of the missing local anchor as part of the relevant execution phase — clone absence alone must never force `Full setup required`.
4. Adapt hub material to the target workspace's purpose and the user's current instructions. Never blindly copy hub-only cosmology, nested-workspace, submodule, or hub `.gitignore` rules into an ordinary workspace unless it manages the same concerns.

## Inspection

Before proposing any changes, inspect the target workspace against the complete applicable checklist. The checklist categories are:

| Cat | Category                              | Scope                                         |
| --- | ------------------------------------- | --------------------------------------------- |
| A   | Assessment and Scope                  | Resolve root, classify, record identity       |
| B   | Required Root Structure               | CLAUDE.md, AGENTS.md, README.md, Archive, tmp |
| C   | CLAUDE.md Universal Standards         | All 17 sections incl. glossary, North Star    |
| D   | AGENTS.md Wrapper Parity              | Four sections, split Codex/.agents paths      |
| E   | Platform Coordination Settings        | JSON validation, template parity, no secrets  |
| F   | README, Documentation, Artifact Rules | Map marker, provenance, N.) numbering         |
| G   | Conditional Git and Secret Safety     | .gitignore, .env, secret exclusion            |
| H   | Conditional Wiki Requirements         | wiki-schema.md, schema pointers               |
| I   | Conditional Hub/Nested-Workspace      | Markers, README tracking, submodule pointers  |
| J   | Verification and User Handoff         | Re-scan, syntax checks, user presentation     |

The authoritative checklist lives in the universal standards document. When the local clone exists, use it as the reference. When it does not, read the hub copy at:

```
C:\Users\Admin\Uzzys Universe\Archive\Live\Documentation\Personal\AI OS & Knowledge Bases\3.) Universal Workspace Standards + Setup & Parity Checklist_Master.md
```

If the Hub master has moved, locate the current numbered `_Master.md` artifact in the same Subject folder, confirm with the user when ambiguous, and repair references rather than creating a second standard.

## Classification

After inspection, issue both labels:

**Workspace state:**
- `New workspace` — the workspace itself is genuinely new (no CLAUDE.md, no AGENTS.md, no .git, no README). Determine this from complete workspace evidence, not from clone absence alone.
- `Existing workspace` — the workspace already has contract files, a Git repository, or other workspace markers. An existing workspace without a local standards clone is still `Existing workspace` — the missing clone is an anchor/parity gap to be filled, not proof of freshness.

**Parity verdict:**
- `Full setup required` — the workspace lacks most or all required structure
- `Updates required for parity` — some items are compliant but drift exists
- `Already aligned` — every applicable checklist item has current evidence

Treat an existing compliant item as **evidence, not something to delete**. Report it as **Already compliant** so the user can see what was inspected and why no action is needed. Mark an item complete only when current evidence supports it.

## Durable Checklist State

The child clone is the durable execution ledger for its workspace. During every authorized setup or parity run, persist the result in that same clone rather than reporting completion only in chat.

- `[x]` means the item is currently resolved by direct evidence: implemented and verified, already compliant and verified, or conditionally not applicable with an explicit reason.
- `[ ]` means the item is pending, failed, blocked, ambiguous, or lacks current evidence. Never tick by assumption, prior chat claims, elapsed time, or mere file existence when the requirement is broader.
- For a conditional item that does not apply, use `[x]` and add an indented plain-text note directly below it in the form `Workspace status: N/A - <specific reason>.` Never use N/A to hide applicable unfinished work.
- Stable implementation items remain checked while their implementation still exists, but later evidence of drift resets the affected item to `[ ]`.
- Recurring verification items record the latest successful observation, not permanent completion. Re-run them on every applicable parity pass, refresh the verification date, and reset an affected item to `[ ]` when current evidence is missing or fails.
- Keep the authoritative requirement wording verbatim. Only the task marker and clearly prefixed workspace-status note are local state.

### Workspace Parity Status

Every child clone must contain a clearly separated `## Workspace Parity Status` section immediately before `## Workspace-Local Synchronization Annotation`. Maintain this visually pipe-aligned two-column table:

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Workspace           | Canonical workspace name                   |
| Verdict             | Full setup / Updates required / Aligned    |
| Hub master          | Current numbered `_Master.md` artifact     |
| Master synchronized | YYYY-MM-DD by truthful agent               |
| Checklist verified  | YYYY-MM-DD by truthful agent               |
| Recurring checks    | Current / Pending re-verification          |
| Evidence            | Short summary; details in Agent Change Log |

Update the table only from current evidence. `Already aligned` requires every applicable item to be `[x]`, every non-applicable conditional item to carry its reason, recurring checks to be current for this run, and no unresolved blocker.

## The Briefing — Using set-the-stage

After inspection and classification, use `set-the-stage` to present an evidence-based briefing to the user **before any mutations**. The briefing must:

- identify what is already compliant;
- identify what remains;
- list dependencies;
- state verification still needed;
- flag blockers or unknowns;
- recommend the best next move.

`set-the-stage` is read-only. It owns the briefing shape; this skill owns the audit and orchestration. Do not duplicate the complete checklist inside `set-the-stage`, and do not make `set-the-stage` own setup execution.

## Execution Styles

After the briefing and user approval, support two execution styles:

### One-Shot

Apply all safe, authorized parity changes in a single pass, then verify the complete applicable checklist.

### Phased

Execute an agreed subset, preserve the remaining checklist state, report the checkpoint, and continue only when the user directs or the governing workflow authorizes continuation.

Neither style weakens approval gates, destructive-operation rules, one-editor-per-file rules, secret safety, repository boundaries, or user-change preservation.

## Authority Order

When conflicts arise, follow this priority:

1. The user's current direct instructions and target-workspace context.
2. Universal and applicable conditional requirements in the standards document.
3. The current hub `CLAUDE.md` and `AGENTS.md` as structural and behavioral reference implementations.
4. Existing target-workspace rules that do not conflict with higher-priority instructions or universal safety requirements.

## Mandatory Verbatim Copying

Whenever the universal standards document, hub `CLAUDE.md` or `AGENTS.md`, or another authoritative setup source supplies actual instruction text for insertion or copying, treat it as compulsory exact-parity material. Copy it verbatim: never compress, compact, paraphrase, shorten, reorder, change punctuation, or omit any part. Adapt only clearly marked placeholders or text the source expressly permits agents to adapt. If supplied text conflicts with the target context, stop and surface the conflict instead of silently rewriting it.

The following named blocks are standing exact-parity requirements:

1. **North Star paragraph** — the timing-fallback paragraph from the standards document must appear verbatim in every workspace `CLAUDE.md`. On every parity run, compare and verify exact textual match.

2. **Canonical hub Voice-to-Text Glossary example list** — the current shared list from the hub must retain the hub's exact order and wording. On every parity run, compare the hub glossary list with the target's shared list and stage every added, changed, or removed hub entry for synchronization.

The current canonical shared glossary list is:

> **Uzi → Uzzy**, **Cloud → Claude**, **Scale → Skill**, **In house → directly in chat (intentional user shorthand, not a dictation correction)**.

Preserve genuinely workspace-specific glossary entries in a clearly separated local list. Never overwrite them or confuse them with the canonical hub entries. Context-aware adaptation applies only where the authoritative source has not supplied actual insertion text or has expressly allowed adaptation.

## Local Clone Synchronization

The local clone must stay synchronized with the hub standards document.

### When the clone is absent

1. Create the `Archive/Live/Documentation/Personal/AI OS & Knowledge Bases/` folder if it does not exist.
2. Assign the next `N.)` number based on what already exists in that Subject folder.
3. Resolve the canonical workspace name from the workspace identity and create `N.) Universal Workspace Standards + Setup & Parity Checklist_{Workspace Name} Clone.md`, replacing the placeholder with that exact name.
4. Copy the Hub master faithfully.
5. Add a workspace-local provenance note identifying this as a synchronized local copy, not new authorship.

### When the clone exists

1. Read the current local clone.
2. Read the current hub standards document.
3. Diff the universal standards content to identify added, changed, or removed items. For comparison only, normalize local `[x]` markers to `[ ]` and exclude `Workspace status` notes plus the complete workspace-local status and annotation sections.
4. Stage the synchronization changes for user review.
5. Apply changes to the same file in place — do not create a duplicate, do not renumber, do not overwrite workspace-specific annotations, checklist state, parity status, or append-only provenance history.
6. Preserve a marker only when the requirement text is unchanged and current evidence still supports it. Leave every new or materially changed requirement `[ ]` until it is verified during the current run.
7. Re-evaluate conditional N/A notes and recurring checks; never carry either forward mechanically.
8. Preserve clearly separated workspace-specific sections intact.

### Clone preservation rules

- Never create a duplicate standards copy.
- Never renumber an existing copy.
- Never overwrite local provenance.
- Never silently discard workspace-specific rules or annotations.
- Never erase or blindly preserve local task markers, N/A reasons, or parity status; re-evaluate them from current evidence.
- Treat synchronization as transport, not new authorship.

## Conditional Rules

Apply conditional checklist categories only when the workspace uses the relevant feature:

- **Git (category G):** only when the workspace is or should be a Git repository.
- **Wiki (category H):** only when the workspace has or is getting an LLM wiki.
- **Hub/Nested-Workspace (category I):** only when the workspace manages nested workspaces.
- **`.env` / `.env.example`:** only when the project genuinely requires environment variables.

Never let conditional rules leak into unrelated workspaces.

## Platform Settings

Every workspace must use the split platform-coordination layout:

- `.agents/.antigravity/settings.local.json`
- `.agents/.hermes/settings.local.json`
- `.agents/.zcode/settings.local.json`
- `.codex/settings.local.json` at the workspace root beside Codex's harness-managed `config.toml`

Codex owns the root `.codex/` directory. Never move, replace, or edit its `config.toml` merely to establish parity; migrate only the workspace coordination JSON into the same root directory and point the Codex wrapper there. The shared `.agents/` directory contains exactly the Antigravity, Hermes, and Z Code homes.

Settings are template-equivalent by platform across all workspaces, not byte-for-byte identical. Adapt workspace identity and workspace-relative paths. Preserve justified deviations explained in `notes`. Never store secrets in coordination settings.

## Failure Conditions

Any of these means the run is not done:

- The skill treats the standards document as only a contract/file-structure guide.
- It blindly clones the hub contract into child workspaces or promotes hub-only rules universally.
- It fails to synchronize the canonical hub glossary list exactly.
- It compresses, compacts, paraphrases, shortens, reorders, repunctuates, omits, or silently rewrites actual instruction text supplied by an authoritative setup source.
- It creates duplicate standards copies, renumbers an existing copy, overwrites local provenance, or silently discards workspace-specific rules.
- It reports completion without persisting evidence-backed task markers and current parity status in the child clone.
- It leaves an unsupported item checked, treats a recurring verification as permanent, or marks an applicable unfinished item N/A.
- It leaves Codex coordination duplicated under both `.codex/` and `.agents/.codex/`, changes harness-managed `config.toml`, or restores the retired four-home `.agents/` model.
- It mutates a workspace before providing the required briefing and obtaining applicable authority.
- It makes `set-the-stage` own setup execution or duplicates the complete checklist into that skill.
- `SKILL.md` or `README.md` says or implies that every workspace without a local standards clone is necessarily a fresh workspace.
- Required files, routing branches, validations, or evidence are missing.
- It claims completion without evidence or claims global availability from a local-master-only change.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization. Its parity checks must also confirm that applicable future artifact skills retain both this integration and the portable rule.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;
- confirm every applicable file-based Markdown-table skill carries `## Deterministic Markdown Table Aligner Integration`, declares the dependency, and places the call at its real ownership boundary, while delegated and pure-format cases are recorded as exemptions;

After creating or updating this skill:

- validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`);
- confirm hub invocation routes to universal-standard maintenance and does not misclassify hub-only rules as universal;
- confirm a nearly empty workspace is classified as new/full setup and receives a complete staged checklist;
- confirm an established but drifting workspace is classified as existing/updates required and reports already-compliant items separately;
- confirm a fully compliant workspace is classified as existing/already aligned without manufacturing work;
- confirm an absent local standards copy receives the correct next local number and path;
- confirm every newly created child clone is named `N.) Universal Workspace Standards + Setup & Parity Checklist_{Workspace Name} Clone.md` with the canonical workspace name substituted exactly and no placeholder braces remaining;
- confirm the Hub source resolves to the numbered `Universal Workspace Standards + Setup & Parity Checklist_Master.md` artifact rather than a child clone;
- confirm an existing local standards copy is updated in place without duplication, renumbering, provenance loss, or blind overwrite;
- confirm child-clone task markers persist evidence-backed state, conditional N/A items carry specific reasons, and unsupported items remain unchecked;
- confirm stable implementation and recurring verification are distinguished, recurring checks refresh on every applicable run, and drift resets affected markers;
- confirm the required Workspace Parity Status table is present, current, visually pipe-aligned, and consistent with the final verdict;
- confirm Hub synchronization normalizes markers for comparison, excludes workspace-local notes and sections, preserves supported unchanged state, and leaves new or materially changed requirements pending until verified;
- confirm every supplied block of actual instruction text is copied verbatim, with changes limited to marked placeholders or expressly adaptable text, while unsupplied structural guidance is adapted to child context;
- confirm canonical hub glossary examples synchronize exactly, including newly added hub entries, while separately identified workspace-specific entries remain intact;
- confirm conditional Git, wiki, hub, and nested-workspace requirements activate only when applicable;
- confirm Codex coordination resolves only through root `.codex/settings.local.json`, `config.toml` is preserved byte-for-byte, and `.agents/` contains exactly Antigravity, Hermes, and Z Code coordination homes;
- confirm `set-the-stage` produces the briefing before mutations and remains read-only itself;
- confirm one-shot and phased paths preserve safety and user approval boundaries.
