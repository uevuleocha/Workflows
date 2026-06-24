---
name: codex-workspace-chat-migration
description: "Safely migrate Codex Desktop chat sessions between workspaces. Use when the user asks to move/reassign Codex chats, sessions, rollout JSONL transcripts, sidebar project grouping, copied working directory, or workspace ownership from one local workspace/project to another. Covers the three required layers: session JSONL metadata, .codex-global-state.json workspace hints, and .codex/sqlite/state_5.sqlite threads cwd/sandbox_policy, with backups, one-session testing, batch manifests, and verification."
---

# Codex Workspace Chat Migration

Migrate Codex Desktop chat sessions from one workspace to another by making three state layers agree:

1. Session transcript JSONL metadata under `C:\Users\Admin\.codex\sessions\...` or `archived_sessions\...`.
2. `C:\Users\Admin\.codex\.codex-global-state.json` top-level `thread-workspace-root-hints`.
3. `C:\Users\Admin\.codex\sqlite\state_5.sqlite` table `threads`, columns `cwd` and `sandbox_policy`.

Use this skill only for Codex Desktop local session/workspace migration. Do not use it to edit project source code.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\OneDrive\Documents\Uzzy Ecosystem`.
- Destination workspace path, for example `C:\Users\Admin\Tools\Codex-token-dashboard`.
- Session ID(s) to migrate.
- Transcript JSONL path for each session ID.
- Confirmation that Codex Desktop is fully closed before applying writes.

If the user only provides chat titles, first map titles to session IDs and transcript paths using read-only inspection of `session_index.jsonl`, `state_5.sqlite`, and `sessions/**/*.jsonl`. Do not guess when duplicate titles exist.

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

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the Codex directory, grouped per run:

```
C:\Users\Admin\.codex\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.codex/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per migration run, e.g. `codex-workspace-chat-migration-20260616-073846`.
- Keep the original filename inside that subfolder so a whole run can be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically. When backing up manually, copy into the same `~/.codex/user-backups/<run-timestamp>/` folder.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Manifests/Codex/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Manifests/Codex/
<workspace_root>/Archive/Manifests/Codex/
./Archive/Manifests/Codex/
```

All three notations mean the same thing: the `Archive/Manifests/Codex/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Claude or Antigravity helper executing a Codex migration still uses the `Codex` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Every manifest saved in `Archive/Manifests/Codex/` must start with the next sequential `N.) ` prefix based only on the highest existing numbered file in that platform folder. Use `N.) <descriptive-manifest-name>.json`; for example, `1.) codex_workspace_chat_migration_manifest.json`. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/report summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in your final report that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Summaries/Migration/Codex/`
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
- discover transcript JSONL paths
- discover old workspace roots per session
- discover whether any sessions are projectless
- discover the relevant `state_5.sqlite` rows and current `cwd` / `sandbox_policy`
- discover whether the requested sessions come from one source workspace or multiple source groups

Use read-only inspection of:

- `C:\Users\Admin\.codex\session_index.jsonl`
- `C:\Users\Admin\.codex\sessions`
- `C:\Users\Admin\.codex\archived_sessions`
- `C:\Users\Admin\.codex\sqlite\state_5.sqlite`
- `C:\Users\Admin\.codex\.codex-global-state.json` when relevant to projectless threads, hints, or heartbeat permission state

### Front-Door Output

Once discovery is complete:

1. Save a sequentially numbered `N.) ` manifest under the active workspace's `Archive/Manifests/Codex/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to Codex's portion of the chat, pre-fill the skill's inputs, and save it under `Archive/Summaries/Migration/Codex/`. Apply the availability guard if the skill is not loaded.
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
2. Search `C:\Users\Admin\.codex\sessions` and `C:\Users\Admin\.codex\archived_sessions` for each session ID to locate transcript paths.
3. Query `C:\Users\Admin\.codex\sqlite\state_5.sqlite` table `threads` for each ID:
   - `id`
   - `title`
   - `rollout_path`
   - `cwd`
   - `sandbox_policy`
4. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
5. Produce a manifest with one entry per session:
   - `title`
   - `id`
   - `transcript_path`
   - `state_db_path`
   - `old_workspace`
   - `new_workspace`
   - whether `session_index`, transcript, global state, and SQLite row were found.

## Execution Workflow

Use this workflow only when a non-Codex helper agent is running and Codex Desktop is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and reporting.

### Three-Layer Apply Workflow

Only apply after the user or handoff explicitly greenlights execution and Codex Desktop is closed.

#### Layer 1: Transcript JSONL

For each target transcript:

1. Confirm the file exists.
2. Confirm at least one `session_meta.payload.id` equals the target session ID.
3. Back up the transcript file before writing.
4. For JSONL records where `type` is `session_meta`:
   - update `payload.cwd` from old workspace to new workspace.
5. For JSONL records where `type` is `turn_context`:
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
4. Preserve all unrelated keys.
5. Verify the file parses as JSON.

Note: Codex Desktop may rehydrate `writableRoots` on launch. Sidebar grouping depends more strongly on `state_5.sqlite.threads.cwd` than on this writable-roots value.

#### Layer 3: SQLite Thread Index

In `C:\Users\Admin\.codex\sqlite\state_5.sqlite`:

1. Back up `state_5.sqlite`; also back up `-wal` and `-shm` if they exist before opening the DB.
2. Confirm exactly one `threads` row exists for the session ID.
3. Update only that row:
   - `cwd` should use the extended path shape: `\\?\C:\...`.
   - `sandbox_policy` JSON should replace structured old workspace path strings with the destination path, including `.git`, `.agents`, and `.codex` subpaths.
4. Use a SQLite transaction.
5. Run `PRAGMA integrity_check`.
6. Verify row count and non-target rows are unchanged.

### Helper Script

Use `scripts/migrate_codex_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. Save the manifest you pass to it under the workspace's `Archive/Manifests/Codex/` folder (see **Manifest Storage**).

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

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- Transcript JSONL parses line by line.
- First or relevant `session_meta.payload.cwd` is the destination workspace.
- `.codex-global-state.json` parses and has the destination hint.
- `state_5.sqlite` `PRAGMA integrity_check` returns `ok`.
- `threads.cwd` is `\\?\<destination workspace>` for each migrated session.
- `threads.sandbox_policy` contains destination structured paths and no old workspace structured paths.
- Non-target SQLite rows are unchanged.
- User reopens Codex Desktop and confirms:
  - chat appears under the destination project,
  - chat stays there after startup settles,
  - `Copy > Copy working directory` returns destination,
  - chat opens/resumes normally.

### Execution Summary

After verification passes and before considering the migration closed, produce an execution report by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the Codex handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Summaries/Migration/Codex/` so Codex can review it. Apply the availability guard if the skill is not loaded.

### Failure And Rollback

If anything fails before commit, stop and report the failing session ID and file. If a post-write verification fails, restore from backups before attempting another approach. If the UI still moves the chat back after all three layers agree, inspect `logs_2.sqlite` around startup and search for additional project membership tables or derived caches.
