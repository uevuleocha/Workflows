---
name: github-involvement
description: Own the workspace GitHub Involvements document after creation — check tracked items (both active and passive) for updates, re-stamping each checked entry's last-checked timestamp, report what changed since last check, move closed items to the Done section, and run a bounded retroactive sweep to find active involvements that predate the system. It never files anything. Use when the user invokes /github-involvement, use github-involvement, asks to check tracked GitHub items, sync the involvements list, mark an involvement done, or sweep GitHub history into the document.
---

# GitHub Involvement

Own the workspace GitHub Involvements document after creation: check what was filed for updates, report what changed since the last check, move closed items to the Done section, and run a bounded retroactive sweep for involvements that predate the system.

This skill never files anything. Publication belongs to `github-file-this`. This skill and `github-file-this` read and write the same document, but only this skill may touch the Done section, and only `github-file-this` publishes.

## Project Contract

Obey the active workspace contract, permissions, public-repository safeguards, and secret-handling rules. This skill performs no publication of any kind.

## Invocation

Treat these as direct invocation:

- `/github-involvement`
- `$github-involvement`
- `use github-involvement`
- `check my GitHub involvements`
- `sync the involvements list`
- `mark an involvement done`
- `sweep GitHub history into the document`
- clear equivalents requesting tracking, update-check, closure, or retroactive sweep

A request to file, comment, or track is out of scope: route it to `github-file-this`.

## Required Inputs

Resolve:

1. The workspace whose Involvements document to work on. Read the channel description or the active working context to determine the workspace.
2. For a closure, the specific entry (section and ordinal, or the full URL) the user declares done.
3. For a sweep, the GitHub account to search against, which is `@me` by default.

Use only targets the user supplied or that are unambiguous in context. Never invent a repository, number, or URL.

## The Involvements Document

The document lives at:

```text
Archive/Live/Documentation/Personal/GitHub/N.) GitHub Involvements.md
```

`N` is computed by `doc-this` from that folder; never hardcode it. The document is owned by `doc-this` for creation, placement, and numbering; this skill and `github-file-this` read and write entries, nothing more. When the document does not exist, invoke `doc-this` to create it at `Archive/Live/Documentation/Personal/GitHub/N.) GitHub Involvements.md` with the five sections in fixed order, then proceed.

### Sections

The document carries these sections in this fixed order, with Done always last:

| #   | Section               | Contents                                       |
| --- | --------------------- | ---------------------------------------------- |
| 1   | Issues - Bugs         | Defect reports filed, commented on, or tracked |
| 2   | Issues - Enhancements | Feature and improvement requests or tracked    |
| 3   | Discussions           | Discussion threads participated in or tracked  |
| 4   | Pull Requests         | PRs opened, reviewed, or tracked               |
| 5   | Done                  | Everything closed, merged, or retired          |

### Numbering and entries

Numbering restarts within each section. Section 1 has its own 1, 2, 3; section 2 starts again at 1. Continuous numbering across sections would renumber every row below any insertion.

The Done section has its own sequence, in finalization order — the order things were closed, not the order they were filed.

Every entry carries both numbers — the row's own ordinal within its section and the real GitHub number — plus the full URL, never a bare `#NNNN`. They are different facts and conflating them is the predictable failure.

Every entry also carries an involvement marker: `active` (the user or an agent created or participated in it) or `passive` (the user is only following it). Publications and retroactive-sweep finds are `active`; a track request is `passive`. The marker is a per-entry field, never a status and never a section.

Every open entry also ends with a last-checked timestamp — ` --- YYYY-MM-DD-HH:mm:ss` after the status, read from the machine clock at write time, 24-hour, no zone suffix — recording when that entry's upstream state was last observed. The timestamp is per-entry state, never file state: a run re-stamps only the entries it actually checked, so a scoped check leaves every other entry honestly reading "not looked at since then," while a whole-document check re-stamps every open entry. `github-file-this` stamps a newly recorded entry at recording time, because publishing or approving it observes its state. Entries that predate this field simply gain their first timestamp the next time an agent observes and writes them; never backfill an invented timestamp. A row moved to Done keeps whatever timestamp it last carried, frozen — Done is never re-checked, so its timestamps cannot go stale.

Statuses for open items: `pending`, `updated`, `almost done`. Closure moves the row to Done rather than setting a status.

A discussion moves to Done only when the user says so, and can be reopened the same way. Never infer a discussion is finished from staleness, and never invent a staleness heuristic.

The Done section is read-only to `github-file-this`. This skill owns Done exclusively.

## Procedure

### Check For Updates

For each open entry — active or passive — query GitHub for changes since that entry's last-checked timestamp: new comments, status changes, merges, or closures.

- Use `gh issue view NUMBER --repo OWNER/REPO --json state,updatedAt,comments` and `gh pr view NUMBER --repo OWNER/REPO --json state,updatedAt` as appropriate.
- Compare against the state recorded in the document.
- Re-stamp every entry actually checked in this run — changed or not — with the run's clock time in ` --- YYYY-MM-DD-HH:mm:ss` form, replacing that entry's earlier timestamp. An entry carrying no timestamp yet (recorded before the field existed) simply gains its first one here. An entry not checked in this run keeps its existing timestamp untouched.
- Honor scoped checks: when the user names one entry or a subset, check and re-stamp only those entries, leaving every other open entry's timestamp alone.
- Do not re-check Done items unless explicitly told to.

### Report What Changed

Report only what changed since the last check: which entries gained comments, changed status, merged, or closed. Give each change its entry reference and full URL. Say plainly when nothing changed. State the run's scope — which entries were checked and re-stamped — so a scoped check is visibly scoped and a whole-document check is visibly complete.

### Move To Done

When an item closes, merges, or is retired, move its row to the Done section, preserving its section ordinal, real GitHub number, and last-checked timestamp (now frozen), and record the full URL. Use the Done section's own finalization-order sequence.

A discussion moves to Done only when the user declares it done. An issue or PR that closed or merged moves to Done on evidence of that closure.

### Retroactive Sweep

Populate the document from history using these searches, which are global across GitHub so no repository enumeration is needed:

| Involvement type       | Method                             | Available    |
| ---------------------- | ---------------------------------- | ------------ |
| Issues authored        | `gh search issues --author @me`    | Yes          |
| Issues commented on    | `gh search issues --commenter @me` | Yes          |
| Pull requests authored | `gh search prs --author @me`       | Yes          |
| Discussions            | Weak CLI support; GraphQL required | Out of scope |

Coverage is deliberately partial and applies to active involvements only — items you authored or commented on. A passive (tracked-only) item is never retroactive: it is tracked from the moment you ask `github-file-this` to track it, so there is no earlier history to sweep. Discussions are not recoverable through these searches, but are trackable going forward via `github-file-this`. State these limits plainly rather than implying completeness. Sweep-recorded entries carry a last-checked timestamp stamped at sweep time — the sweep observes each find's current state while enumerating it.

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

## Markdown Table Alignment

Every Markdown table this skill writes — inside a durable artifact or into chat — must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Boundaries

Do not:

- file, comment on, or otherwise publish anything — route publication to `github-file-this`;
- infer a discussion is finished from staleness or invent a staleness heuristic;
- move a row to Done without evidence of closure, or without the user's declaration for a discussion;
- renumber entries, or conflate the section ordinal with the real GitHub number;
- emit a bare `#NNNN` instead of a full markdown link;
- imply the retroactive sweep recovered discussions or passive items; or
- hardcode the document's `N` number.

## Validation

Before synchronization or handoff:

1. Run the official `quick_validate.py` against this folder with Python `-X utf8`, keeping stdout and stderr separate and deciding pass/fail from the exit code.
2. Run the shared exact-model carrier validator and confirm the canonical block is byte-identical.
3. Confirm the skill files nothing: no `gh issue create`, `gh pr create`, `gh issue comment`, or `gh pr comment` appears in this skill.
4. Confirm the Involvements document contract (five sections in fixed order, per-section numbering, Done last with finalization-order sequence, both numbers plus full URL, last-checked timestamp tail on every open entry, user-declared discussion exit, Done owned here) matches `github-file-this` identically.
5. Confirm the retroactive sweep states its three working methods plainly and confirms active-only coverage (discussions and passive items out of scope).
6. Confirm the timestamp mechanics: scoped checks re-stamp only the entries actually checked, whole-document checks re-stamp every open entry, pre-field entries gain their first timestamp at next check, sweep finds are stamped at sweep time, Done rows stay frozen, and no timestamp is ever backfilled or written with a zone suffix.
