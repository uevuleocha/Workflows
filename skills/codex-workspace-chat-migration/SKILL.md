---
name: codex-workspace-chat-migration
description: "Safely migrate Codex Desktop chat sessions between workspaces. Use when the user asks to move/reassign Codex chats, sessions, rollout JSONL transcripts, sidebar project grouping, copied working directory, or workspace ownership from one local workspace/project to another. Covers the three required layers: session JSONL metadata, .codex-global-state.json workspace hints, and the live state_5.sqlite threads cwd/sandbox_policy DB, with backups, one-session testing, batch manifests, and verification."
---

# Codex Workspace Chat Migration

Migrate Codex Desktop chat sessions from one workspace to another by making three state layers agree:

1. Session transcript JSONL metadata under `C:\Users\Admin\.codex\sessions\...` or `archived_sessions\...`.
2. `C:\Users\Admin\.codex\.codex-global-state.json` top-level `thread-workspace-root-hints`.
3. The live `state_5.sqlite` table `threads`, columns `cwd` and `sandbox_policy`. Current Codex builds may store this at `C:\Users\Admin\.codex\state_5.sqlite`; older or secondary installs may store it at `C:\Users\Admin\.codex\sqlite\state_5.sqlite`. Always discover which DB contains the target thread rows before writing.

Use this skill only for Codex Desktop local session/workspace migration. Do not use it to edit project source code.

## UI-Facing Transcript And Parsed-Value Rule

Codex can store or reference the same session ID in more than one transcript JSONL. The transcript discovered first by scanning `sessions/**/*.jsonl` is not always the transcript Codex Desktop opens. The UI-facing transcript is the path recorded in `state_5.sqlite.threads.rollout_path`.

Front-door manifests must therefore distinguish:

- `transcript_path` — the primary transcript chosen for backward compatibility.
- `ui_rollout_path` or `rollout_path_from_sqlite` — the SQLite `threads.rollout_path` value that Codex UI uses.
- `all_transcript_paths` — every discovered JSONL containing the target session ID, including archived/fork transcripts when present.
- `transcript_paths_to_migrate` — the exact transcript paths the helper should write. Prefer this list when present; use it to exclude later handoff/review transcripts that merely mention the session ID.

Execution must migrate `transcript_paths_to_migrate` when present. Otherwise, migrate the UI-facing rollout transcript and any other explicitly listed target transcript paths. Verification must parse JSONL and inspect structured values. Do not rely on raw text search for old paths, because JSON escaping and path case variants can hide stale parsed values.

Use case-insensitive old-path matching for structured workspace fields, but always write the canonical destination path exactly as supplied by the manifest.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\OneDrive\Documents\Uzzy Ecosystem`.
- Destination workspace path, for example `C:\Users\Admin\Tools\Codex-token-dashboard`.
- Session ID(s) to migrate.
- Transcript JSONL path for each session ID, including the SQLite `threads.rollout_path` UI-facing transcript when present.
- Confirmation that Codex Desktop is fully closed before applying writes.

If the user only provides chat titles, first map titles to session IDs and transcript paths using read-only inspection of `session_index.jsonl`, both possible `state_5.sqlite` locations, and `sessions/**/*.jsonl`. Do not guess when duplicate titles exist.

## State DB Discovery Rule

Do not hard-code a single SQLite state path. Codex Desktop state has appeared in both of these locations:

- `C:\Users\Admin\.codex\state_5.sqlite`
- `C:\Users\Admin\.codex\sqlite\state_5.sqlite`

Front-door discovery must inspect both paths read-only and record:

- `candidate_state_dbs` - every candidate checked.
- `selected_state_db` - the DB that contains exactly one row for each target session ID.
- `state_db_selection_reason` - why that DB was selected.
- per-DB row counts for the target session IDs.

If only one DB contains exactly one row for every target session, use that DB. If both DBs contain exact target rows, do not tiebreak by mtime or any other guess: stop, report both candidates, and have the manifest set `selected_state_db` explicitly. If the target rows are split across DBs or any target has zero/multiple rows, stop and report the mixed state before execution.

Execution helpers must consume the selected DB path from the manifest, re-check exactly one row per target immediately before writing, and back up only the selected DB plus its `-wal` and `-shm` sidecars. Do not touch the other DB unless the manifest explicitly lists target rows there.

## Runtime Selection

This skill has two sides. Which side runs depends on the runtime context, not on the model vendor or model family.

- If the skill is being run inside Codex Desktop / Codex local runtime, run the **Front-Door Workflow**.
- If the skill is being run by a non-Codex helper agent while Codex Desktop is fully closed, run the **Execution Workflow**.

Examples:

- Hermes or another non-Codex agent may run the **Execution Workflow** if Codex is fully closed, even when that helper agent uses an OpenAI model.
- Codex itself should not run the **Execution Workflow** against live Codex state. Codex should run the **Front-Door Workflow**, prepare the artifacts, and stop before the closed-Codex execution handoff.

## Safety Rules

- Start with one session when testing a new migration pattern.
- Do not modify any Codex state while Codex Desktop is running.
- Back up every touched file before mutation.
- Do not globally replace paths across `C:\Users\Admin\.codex`.
- Do not modify historical conversation prose unless the field is a structured `session_meta` or `turn_context` workspace metadata field.
- Do not edit unrelated session rows, transcript files, global state keys, product code, or source workspace files.
- Preserve JSONL format: one JSON object per line.
- Use SQLite transactions for `state_5.sqlite`; do not raw-edit SQLite files.
- Keep a rollback path by preserving backups.
- Save every backup to the unified backup folder, never scattered next to originals (see **Backup Location**).

## Nested Workspaces

Workspaces are sometimes **nested inside another workspace** — e.g. a hub with sub-workspaces under it. This shape is common in some setups but is **not assumed universal** (this skill may be used anywhere), so the path transform must be context-aware: it changes only the values that genuinely point at the **old** location and are **not already at or under the destination**, and never force-rewrites a value that is already correct.

Classification per value (destination = `new`, source = `old`):

- **Exact old root** → rewritten to `new` (checked first, so a source-under-destination exact root is still rewritten).
- **Already at/under `new`** → left unchanged (idempotent) — the guard that prevents a doubled, corrupt path when `new` is nested under `old`.
- **A different subtree of `old`** → *side-by-side* move swaps the prefix; *nested* move (either direction) leaves the value unchanged rather than fabricating a `new`-relative path.

`replace_path` remaps whole path **values** prefix-anchored — not a global substring rewrite. This both stops the nested doubling and prevents sibling-prefix corruption (`…Universe` inside `…Universe2`); the trade-off is that a workspace path embedded mid-string is intentionally left alone. The SQLite pass additionally rejects any doubled-destination `cwd` after write.

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the Codex directory, grouped per run:

```
C:\Users\Admin\.codex\user-backups\<run-timestamp>\<slot>-<original filename>
```

- Equivalent notation: `~/.codex/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per migration run, e.g. `codex-workspace-chat-migration-20260616-073846`.
- Each backup keeps the original filename behind a numbered `<slot>-` prefix so two originals that share a basename (for example `state_5.sqlite` from both candidate directories) can never flatten onto one backup file, and a whole run can still be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically and records an explicit **backup manifest**: one `{"original": <absolute original path>, "backup": <backup path>}` pair per file. Restoration uses only the recorded original path — never a location guessed from the backup's basename — and each restored file is verified byte-for-byte against its backup. When backing up manually, copy into the same `~/.codex/user-backups/<run-timestamp>/` folder and keep your own original→backup notes.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Historical/Manifests/Codex/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Historical/Manifests/Codex/
<workspace_root>/Archive/Historical/Manifests/Codex/
./Archive/Historical/Manifests/Codex/
```

All three notations mean the same thing: the `Archive/Historical/Manifests/Codex/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Claude or Antigravity helper executing a Codex migration still uses the `Codex` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Every manifest saved in `Archive/Historical/Manifests/Codex/` must start with the next sequential `N.) ` prefix based only on the highest existing numbered file in that platform folder. Use `N.) <descriptive-manifest-name>.json`; for example, `1.) codex_workspace_chat_migration_manifest.json`. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/report summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in your final report that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Historical/Summaries/Migration/Codex/`
- Create the `Codex` platform folder if it does not exist.
- Sequence number: the next integer after the highest existing `N.)` file in the `Codex` platform folder only.
- Filename style: `N.) <Agent> <Topic> <Handoff|Execution Report> Summary N.md` (Codex/front-door uses `Handoff`; helper/execution uses `Execution Report`).

**Scope of each summary.** Each side summarizes only its own portion; do not re-summarize the other side beyond referencing the handoff.

- Front-Door (Codex) summary covers Codex's portion of the chat: from when migration was first raised, through gathering the user's inputs, read-only discovery, manifest building, and the handoff package — everything Codex did and gathered and everything the user asked to migrate. It is the handoff to the helper agent.
- Execution (helper agent) summary covers the helper's portion: the Codex handoff it received, plus everything it did to apply the three layers, verify, and (if needed) roll back. It is written so Codex can review the migration afterward, alongside the user's own visual check.

## Front-Door Workflow

Use this workflow when the skill is started from Codex Desktop / Codex local runtime.

This is the native front door of the skill. Codex uses it to gather user inputs, discover the real session metadata from source-of-truth files, build the manifest and handoff artifacts, and then stop before execution.

### Front-Door Inputs

Collect or confirm these user inputs up front:

- the chat titles, screenshots, or explicit session list the user wants migrated
- the destination workspace path
- any explicit exclusions

Do not ask the user to supply source workspace roots when those can be discovered from Codex state. The user may know the destination workspace, but Codex should discover the actual per-session source paths from the stored metadata.

### Front-Door Discovery

For the requested sessions, discover the real values from Codex's source-of-truth files. Do not infer or guess them. See the **Read-Only Mapping Workflow** below for the step-by-step discovery procedure.

- discover session IDs
- discover transcript JSONL paths, including all JSONLs containing the session ID and the SQLite `threads.rollout_path` UI-facing path
- discover old workspace roots per session
- discover whether any sessions are projectless
- discover the relevant `state_5.sqlite` rows and current `cwd` / `sandbox_policy` / `rollout_path`
- discover whether the requested sessions come from one source workspace or multiple source groups

Use read-only inspection of:

- `C:\Users\Admin\.codex\session_index.jsonl`
- `C:\Users\Admin\.codex\sessions`
- `C:\Users\Admin\.codex\archived_sessions`
- `C:\Users\Admin\.codex\state_5.sqlite`
- `C:\Users\Admin\.codex\sqlite\state_5.sqlite`
- `C:\Users\Admin\.codex\.codex-global-state.json` when relevant to projectless threads, hints, or heartbeat permission state

For rename migrations where old and new workspace paths are known, also sweep the selected state DB for every row whose `threads.cwd` still points at the old workspace. Mark these rows in the manifest as:

- `requested` - explicitly named by the user or shown in the screenshot.
- `extra_old_bound` - not explicitly requested, but still bound to the old workspace.
- `internal_or_system_like` - small approval/reviewer/system-looking threads that are still bound to the workspace.

Ask or confirm whether extras should be included when the user did not already approve migrating all old-bound rows.

For rename migrations, classify old-bound rows by both request scope and user-visible impact.

First determine the user's intent:

- `selected_chat_migration` - the user named specific chats and does not require the old workspace/project group to disappear.
- `workspace_group_migration` - the user wants the old workspace/project moved, renamed, consolidated, or no longer visible as a separate group.

For every row still bound to the old workspace, assign:

- `requested` - explicitly named by the user, shown in the screenshot, or included by the user's workspace-level migration intent.
- `visible_old_bound` - not explicitly named, but likely visible in the sidebar because it has a normal user-facing title, appears in screenshots, or is not system/reviewer-like.
- `internal_or_system_like` - approval, reviewer, permission, system, or helper rows that may not be normal user-facing chats.

Do not use `extra_old_bound` as a quiet holding category for visible chats. If a row is visible or likely visible, classify it as `visible_old_bound` and add `visible_sidebar_blocker: true`.

When `workspace_group_migration` is the user's intent, all `requested` and `visible_old_bound` rows should be included in the default execution set unless the user explicitly excludes them. Internal/system-like rows should be listed separately and require explicit approval before migration.

Before handoff, clearly state:

- how many rows will migrate by default;
- how many visible old-bound rows, if any, will remain;
- whether the old workspace/project group will still appear after execution;
- which internal/system-like rows are paused for explicit decision.

If any `visible_sidebar_blocker` would remain and the user has not explicitly approved that outcome, stop before handoff and ask for confirmation.

## Redirect History, Do Not Abandon Stale Bindings

A migration is complete only when all in-scope structured workspace bindings are redirected from the source workspace to the destination workspace.

For `workspace_group_migration`, the scope is the whole old workspace/project group. Every visible chat, hidden/internal helper row, reviewer/approval row, transcript metadata record, global-state hint, SQLite row, sandbox policy, and sidebar/grouping index that is bound to the source workspace must be re-homed to the destination unless the user explicitly excludes it.

For `selected_chat_migration`, the scope is narrower. Only the selected chat(s) and their related records move, but every structured binding tied to those chat(s) must move. This includes UI rollout transcripts, duplicate/fork transcripts selected for migration, child/helper/internal/reviewer rows, global hints, sandbox policies, and any derived index entries linked to the selected chat(s).

Do not delete historical/internal rows just because they are not visible. Prefer re-homing them so history remains intact but no longer points at a stale workspace path. Deletion is destructive and requires separate explicit approval.

Verification must parse structured values, not raw text search, and confirm:

- no in-scope `threads.cwd` value points at the old workspace;
- no in-scope `sandbox_policy` structured path points at the old workspace;
- no in-scope transcript `session_meta` or `turn_context` cwd/workspace_roots value points at the old workspace;
- no in-scope global-state hint or writable-root points at the old workspace;
- no visible sidebar blocker remains under the old workspace;
- any intentionally excluded internal/system rows are listed explicitly with the reason they were left behind.

### Front-Door Output

Once discovery is complete:

1. Save a sequentially numbered `N.) ` manifest under the active workspace's `Archive/Historical/Manifests/Codex/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to Codex's portion of the chat, pre-fill the skill's inputs, and save it under `Archive/Historical/Summaries/Migration/Codex/`. Apply the availability guard if the skill is not loaded.
3. Group sessions by real discovered old workspace when needed. If there are mixed-source sessions, represent them as separate source groups rather than flattening them into one assumed old workspace.
4. Clearly identify whether a target session is projectless and record the real projectless source cwd if so.

### Front-Door Stop Boundary

The Front-Door Workflow stops after Codex has:

- gathered the user inputs
- discovered the real session metadata
- built the manifest
- built the handoff summary by explicitly invoking the `session-summary` skill (Codex-scoped; see **Session Summary Integration**)
- identified the destination workspace and any source groups

At that point, if the migration must touch live Codex state, Codex should stop and hand execution to a non-Codex helper agent that can run while Codex Desktop is fully closed.

## Read-Only Mapping Workflow

When preparing a batch or front-door package for another agent:

1. Read `C:\Users\Admin\.codex\session_index.jsonl` for current titles and IDs.
2. Search `C:\Users\Admin\.codex\sessions` and `C:\Users\Admin\.codex\archived_sessions` for each session ID to locate every transcript path containing that ID.
3. Query both candidate `state_5.sqlite` paths and select the DB containing exactly one target row per session. Treat `rollout_path` from the selected DB as the UI-facing transcript path and include it even when another transcript was discovered first:
   - `id`
   - `title`
   - `rollout_path`
   - `cwd`
   - `sandbox_policy`
   - `rollout_path` as `ui_rollout_path` / `rollout_path_from_sqlite`
4. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
5. Produce a manifest with one entry per session. If multiple transcript files contain the session ID, include all of them and mark the SQLite rollout path:
   - `title`
   - `id`
   - `transcript_path`
   - `ui_rollout_path` / `rollout_path_from_sqlite`
   - `all_transcript_paths`
   - `transcript_paths_to_migrate`
   - `state_db_path`
   - `candidate_state_dbs`
   - `selected_state_db`
   - `state_db_selection_reason`
   - `old_workspace`
   - `new_workspace`
   - classification such as `requested`, `extra_old_bound`, or `internal_or_system_like`
   - whether `session_index`, transcript, global state, and SQLite row were found.

## Execution Workflow

Use this workflow only when a non-Codex helper agent is running and Codex Desktop is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and reporting.

### Pre-flight Guards (apply only)

Before any write when `--apply` is requested:

1. **Process guard (fail-closed):** check that no Codex Desktop process (`Codex.exe`) is running. If one is detected, abort — the migration cannot safely proceed while Codex holds open its state files. If the probe itself fails (exception, timeout, or empty/unusable output), abort as well: an unknown probe result is never interpreted as "Codex is not running".
2. **Non-empty-WAL guard:** check the selected `state_5.sqlite`'s WAL file (`state_5.sqlite-wal`). If it exists and is non-empty, abort — Codex may still be running or may not have committed pending transactions. An empty or absent WAL is safe (Codex checkpoints on shutdown).
3. Back up every file that will be touched **before** opening any of them for write.
4. Confirm the selected state DB is unambiguous. If multiple candidate DBs contain exactly one target row per session, the helper **hard-stops** with the candidate list rather than guessing by mtime. The manifest must explicitly set `selected_state_db` to resolve ambiguity.

### Three-Layer Apply Workflow

Only apply after the user or handoff explicitly greenlights execution and Codex Desktop is closed.

#### Layer 1: Transcript JSONL

For each target transcript:

1. Confirm the file exists.
2. Confirm at least one `session_meta.payload.id` equals the target session ID in every transcript path being changed. Include the UI-facing SQLite `threads.rollout_path` transcript even when it differs from `transcript_path`.
3. Back up the transcript file before writing.
4. For JSONL records where `type` is `session_meta` and `payload.id` equals the target session ID:
   - update `payload.cwd` from old workspace to new workspace using case-insensitive old-path matching.
5. For JSONL records where `type` is `turn_context` in a target transcript:
   - update `payload.cwd`.
   - update `payload.workspace_roots`.
   - update structured sandbox/permission entries containing the old workspace.
6. Do not rewrite `event_msg`, `response_item`, or user/assistant prose just because it mentions the old path.
7. Verify every non-empty line still parses as JSON.

#### Layer 2: Global State

In `C:\Users\Admin\.codex\.codex-global-state.json`:

1. Back up the file before writing.
2. Add/update top-level `thread-workspace-root-hints[session_id] = destination workspace`.
3. If present, update `electron-persisted-atom-state.heartbeat-thread-permissions-by-id[session_id].sandboxPolicy.writableRoots` to the destination workspace.
4. If present, update `thread-writable-roots[session_id]` to the destination workspace.
5. When the manifest explicitly marks the old project root as fully migrated, remove that exact old root from `electron-saved-workspace-roots` and `project-order`. Do not remove unrelated roots.
4. Preserve all unrelated keys.
5. Verify the file parses as JSON.

Note: Codex Desktop may rehydrate `writableRoots` on launch. Sidebar grouping depends more strongly on `state_5.sqlite.threads.cwd` than on this writable-roots value.

#### Layer 3: SQLite Thread Index

In the selected live `state_5.sqlite` path recorded in the manifest:

1. Re-check that exactly one `threads` row exists for every target session ID in the selected DB.
2. Back up `state_5.sqlite`; also back up `-wal` and `-shm` if they exist before opening the DB.
3. Update only target rows:
   - `cwd` should use the extended path shape: `\\?\C:\...`.
   - `sandbox_policy` JSON should replace structured old workspace path strings with the destination path, including `.git`, `.agents`, and `.codex` subpaths.
4. Use a SQLite transaction.
5. Run `PRAGMA integrity_check`.
6. Verify row count and non-target rows are unchanged.

### Helper Script

Use `scripts/migrate_codex_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. Save the manifest you pass to it under the workspace's `Archive/Historical/Manifests/Codex/` folder (see **Manifest Storage**).

The helper script belongs to the **Execution Workflow** side. It is not the front door. Codex may help discover inputs and generate the manifest, but a non-Codex helper agent should run the script while Codex Desktop is fully closed.

Expected manifest shape:

```json
{
  "old_workspace": "C:\\Users\\Admin\\OneDrive\\Documents\\Uzzy Ecosystem",
  "new_workspace": "C:\\Users\\Admin\\Tools\\Codex-token-dashboard",
  "sessions": [
    {
      "id": "019ec3c2-e70c-7f92-928c-2f5a795cebef",
      "title": "4.) Codex Token dashboard repos Phase 1",
      "transcript_path": "C:\\Users\\Admin\\.codex\\sessions\\2026\\06\\13\\rollout-...jsonl"
    }
  ]
}
```

Optional top-level keys the helper consumes:

- `selected_state_db` — explicit path with `\\?\\` form; selects exactly one DB when candidates are ambiguous.
- `candidate_state_dbs` — list of every candidate DB inspected; recorded for audit.
- `cleanup_old_project_root` (boolean) — remove the old workspace path from `electron-saved-workspace-roots` and `project-order` once every target session is confirmed migrated. Default: false (preserve non-target roots).
- `cleanup_old_workspace_root` (boolean) — alias for `cleanup_old_project_root`. When either is true, only the exact old-root strings are cleaned; unrelated roots are never removed.

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- Transcript JSONL parses line by line, including every listed `all_transcript_paths` and the SQLite `threads.rollout_path` transcript. The helper re-parses every transcript after write **at its recorded authoritative path** — never a basename guessed under `~/.codex` — to confirm the migration was persisted; a missing recorded path is a verification failure. It is not enough that `migrate_transcript` reported success; the on-disk file must contain the session's `session_meta` with a hard parse.
- Parsed target `session_meta.payload.cwd` is the destination workspace; verification must parse JSON values, not raw escaped text.
- `.codex-global-state.json` **re-parses after write**: every migrated session's `thread-workspace-root-hints` entry must **exist and equal the destination workspace** on-disk — an absent hint is a verification failure, not a pass. The file must never contain an empty `electron-persisted-atom-state` key inserted by the migration — the helper only writes keys it actually modified.
- `state_5.sqlite` `PRAGMA integrity_check` returns `ok`; the selected DB was unambiguous (no silent mtime tiebreak).
- `threads.cwd` is `\\?\<destination workspace>` for each migrated session.
- `threads.sandbox_policy` contains destination structured paths and no old workspace structured paths.
- For `workspace_group_migration`, every in-scope structured old-workspace binding has been redirected unless explicitly excluded in the manifest and final report.
- For `selected_chat_migration`, every structured binding tied to the selected chat(s), including related child/helper/internal/reviewer rows, has been redirected unless explicitly excluded in the manifest and final report.
- Any excluded internal/system rows are listed with their IDs, current workspace binding, visibility status, and reason for exclusion.
- Non-target SQLite rows are unchanged.
- User reopens Codex Desktop and confirms:
  - chat appears under the destination project,
  - chat stays there after startup settles,
  - `Copy > Copy working directory` returns destination,
  - chat opens/resumes normally.

### Execution Summary

After verification passes and before considering the migration closed, produce an execution report by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the Codex handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Historical/Summaries/Migration/Codex/` so Codex can review it. Apply the availability guard if the skill is not loaded.

### Failure And Rollback

If anything fails before commit, stop and report the failing session ID and file. **Coordinated backup restoration:** if a post-write verification fails (transcript re-parse, global-state re-parse, or SQLite integrity), the helper automatically restores every file to its **recorded original path** from the run's explicit original→backup manifest (never matching by basename), verifying each restored file byte-for-byte, so the state DB, global state, and every touched transcript return to pre-migration state — the migration is fully rolled back in one pass rather than requiring manual reassembly of individual files. Any file that cannot be restored and verified is reported loudly rather than skipped. Only after restoration is confirmed may the operator try a different approach. If the UI still moves the chat back after all three layers agree, inspect parsed JSONL in the SQLite `threads.rollout_path` transcript first, then inspect `electron-saved-workspace-roots`, `project-order`, `logs_2.sqlite` around startup, and any additional project membership tables or derived caches.
