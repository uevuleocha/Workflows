---
name: claude-workspace-chat-migration
description: "Safely migrate Claude Desktop chat sessions between workspaces. Use when the user asks to move/reassign Claude Code chats, sessions, transcript JSONL, sidebar project grouping, working directory, workspace memory, or session sidecar data from one local workspace/project to another. Covers the required state surfaces: the CLI transcript JSONL, adjacent Claude project data such as memory, session subagents, and session tool-results, and the Claude Desktop chat store with backups, one-session testing, manifests, and verification."
---

# Claude Workspace Chat Migration

Migrate Claude Desktop chat sessions from one workspace to another by making the local Claude state surfaces agree:

1. Layer A — CLI transcript JSONL under `C:\Users\Admin\.claude\projects\<encoded-path>\<cliSessionId>.jsonl`. The encoded folder name is the workspace path with every `:`, `\`, and space replaced by `-` (e.g. `C:\Users\Admin\Uzzys Universe` becomes `C--Users-Admin-Uzzys-Universe`). The sidebar/CLI grouping for a chat is the encoded folder its transcript lives in; each record also carries a top-level `cwd` used to resume in the right directory.
2. Adjacent Claude project data under the same encoded folder: workspace `memory/`, plus per-session `<cliSessionId>\subagents\` and `<cliSessionId>\tool-results\` folders. These are path-keyed state and must move with the workspace/session they belong to; they are not disposable cache.
3. Layer B — Desktop chat store under `C:\Users\Admin\AppData\Roaming\Claude\claude-code-sessions\<account>\<group>\local_*.json`. Each chat has one record (linked to Layer A by `cliSessionId`) carrying `cwd`, `originCwd`, and `title` — the fields that drive the Desktop sidebar group and title.

Use this skill only for Claude Desktop local session/workspace migration. Do not use it to edit project source code.

Claude has these local state surfaces for workspace migration. There is no SQLite thread index and no global-state hints file (those are Codex concerns). Do not invent additional layers.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\Uzzys World`.
- Destination workspace path, for example `C:\Users\Admin\Uzzys Universe`.
- CLI session ID(s) to migrate (the `cliSessionId`, which is also the transcript filename stem).
- The Layer B Desktop record path for each session (`...\claude-code-sessions\...\local_*.json`).
- Confirmation that Claude Desktop and every Claude Code session are fully closed before applying writes.

If the user only provides chat titles, first map titles to session IDs, transcript paths, and Desktop records using read-only inspection of the projects folder and the Desktop chat store. Do not guess when duplicate titles exist.

## Runtime Selection

This skill has two sides. Which side runs depends on the runtime context, not on the model vendor or model family.

- If the skill is being run inside Claude Desktop / Claude local runtime, run the **Front-Door Workflow**.
- If the skill is being run by a non-Claude helper agent while Claude Desktop is fully closed, run the **Execution Workflow**.

Examples:

- Codex or another non-Claude agent may run the **Execution Workflow** if Claude is fully closed, even when that helper agent uses a non-Anthropic model.
- Claude itself should not run the **Execution Workflow** against live Claude state. Claude should run the **Front-Door Workflow**, prepare the artifacts, and stop before the closed-Claude execution handoff.

## Safety Rules

- Start with one session when testing a new migration pattern.
- Do not modify any Claude state while Claude Desktop or any Claude Code session is running.
- Back up every touched file before mutation.
- Back up every touched adjacent data folder before moving it.
- Do not globally replace paths across `C:\Users\Admin\.claude` or the Desktop chat store.
- Edit only structured workspace metadata: the transcript's top-level `cwd`, and the Desktop record's `cwd` and `originCwd`. Do not rewrite user/assistant prose just because it mentions the old path.
- Move adjacent `memory/`, `<cliSessionId>\subagents\`, and `<cliSessionId>\tool-results\` directories byte-for-byte. Do not rewrite their contents during relocation.
- Workspace `memory/` is **whole-workspace state**, shared by every chat in the encoded project folder — not per-selected-chat state. Only relocate it for a whole-workspace migration. A `memory_move` block requires `memory_scope: "whole_workspace"` (the whole workspace is moving) or `memory_scope: "none"` (skip it for a selected-chat migration). The helper hard-refuses any other scope — including an **absent** scope, which is never defaulted — rather than guessing. See **Memory Ownership**.
- Preserve JSONL format: one JSON object per line.
- Preserve the Layer B file's existing byte/encoding state. Detect whether the record already has a UTF-8 BOM and keep that state; never add or strip a BOM. Read transcript JSONL BOM-safely so a pre-existing BOM does not break parsing.
- Keep a rollback path by preserving backups.
- Save every backup to the unified backup folder, never scattered next to originals (see **Backup Location**).

## Nested Workspaces

Workspaces are sometimes **nested inside another workspace** — e.g. a hub with sub-workspaces under it. This shape is common in some setups but is **not assumed universal** (this skill may be used anywhere), so the transform must be context-aware: it changes only the `cwd` values that genuinely point at the **old** location and are **not already at or under the destination**, and it never force-rewrites a value that is already correct.

Classification per value (destination = `new`, source = `old`):

- **Exact old root** → rewritten to `new`. This is checked *first*, so that even when `old` is itself nested under `new` (source-under-destination) the exact old root is still rewritten rather than swallowed by the already-destination guard.
- **Already at/under `new`** → left unchanged (idempotent). This is the guard that prevents a doubled, corrupt path like `…\Workflows\MilkyWay\Tools\Workflows\Skills` when `new` is nested under `old`.
- **A different subtree of `old`** → for a plain *side-by-side* move the `old` prefix is swapped for `new`; for a *nested* move (either direction) the value is **left unchanged** rather than fabricating a `new`-relative path (`old\Family\Heart` must never become `new\Family\Heart`).

`remap_cwd` enforces this, and verification rejects both residual old-workspace values **and** doubled-destination values (a doubled path begins with `new` and would otherwise pass unnoticed). The chat's true residence is guaranteed by the transcript's destination folder plus the Desktop record's `cwd`/`originCwd`, not by stamping every per-line breadcrumb.

## Memory Ownership (selected-chat vs whole-workspace)

Claude's workspace `memory/` folder under `~/.claude/projects/<encoded>/memory/` is **whole-workspace state**: it is shared by every chat whose transcript lives in that encoded folder, not private to any one selected chat. Moving it as an undocumented side effect of a selected-chat migration would silently drag other chats' memory to the destination.

The `adjacent_data_relocation.memory_move` block therefore requires an explicit scope, and the helper hard-refuses to guess:

- `memory_scope: "whole_workspace"` — only valid when the whole workspace (every chat in the encoded folder) is moving to the destination. The memory folder moves with it.
- `memory_scope: "none"` — skip the memory move entirely. Use this for a selected-chat migration where only specific chats (and their per-session sidecars) move, leaving the shared workspace memory at the source.

Any other scope value is a hard error, and so is an absent one: when a `memory_move` block is declared without `memory_scope`, the helper stops instead of assuming `whole_workspace`. Do not invent a partial/merge mode: Claude stores memory as path-keyed files this skill never rewrites during relocation, so there is no safe merge semantic.

Per-session `<cliSessionId>\subagents\` and `<cliSessionId>\tool-results\` sidecars are scoped to one session by their path, so they are safe to move for a selected-chat migration without a scope declaration.

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the Claude directory, grouped per run:

```
C:\Users\Admin\.claude\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.claude/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per migration run, e.g. `claude-workspace-chat-migration-20260621-142709`.
- Keep the original filename inside that subfolder so a whole run can be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically. When backing up manually, copy into the same `~/.claude/user-backups/<run-timestamp>/` folder.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Historical/Manifests/Claude/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Historical/Manifests/Claude/
<workspace_root>/Archive/Historical/Manifests/Claude/
./Archive/Historical/Manifests/Claude/
```

All three notations mean the same thing: the `Archive/Historical/Manifests/Claude/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Codex or Antigravity helper executing a Claude migration still uses the `Claude` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Create the manifest through the `manifest-this` skill. `manifest-this` owns the content, the sequential `N.) ` prefix (next integer after the highest existing numbered file in the `Claude` platform folder), the migration grammar `N.) Who + Topic + What` -> `N.) <Platform> <Topic> Manifest.md` (Title Case with spaces; for example `1.) Claude Trading Chats Manifest.md`), and the always-historical placement under `Archive/Historical/Manifests/Claude/`. **The manifest default format for migration skills is Markdown (`.md`), not HTML** - pass the Markdown override to `manifest-this`. The Markdown manifest embeds the exact native JSON payload in a fenced block so the Execution Workflow can recover it. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

**Availability guard (both workflows).** Before the manifest step, confirm the `manifest-this` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `manifest-this` skill is not loaded. It is required to create or update the migration manifest. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, write the manifest by hand in the same folder with the same naming and grammar, then note in your handoff or feedback summary that the dedicated skill was unavailable.
- Never silently skip the manifest.

When a migration is staged (e.g. one-session test first, then the rest), prefer updating the existing manifest in place through the `manifest-this` skill (update mode) to reflect what is done and what remains, rather than creating a second file, unless the sessions come from more than one source workspace. One source workspace means one manifest.

## Front-Door Workflow

Use this workflow when the skill is started from Claude Desktop / Claude local runtime.

This is the native front door of the skill. Claude uses it to gather user inputs, discover the real session metadata from source-of-truth files, build the manifest and handoff artifacts, and then stop before execution.

### Front-Door Inputs

Collect or confirm these user inputs up front:

- the chat titles, screenshots, or explicit session list the user wants migrated
- the destination workspace path
- any explicit exclusions

Do not ask the user to supply source workspace roots when those can be discovered from Claude state. The user may know the destination workspace, but Claude should discover the actual per-session source paths from the stored metadata.

### Front-Door Discovery

For the requested sessions, discover the real values from Claude's source-of-truth files. Do not infer or guess them. See the **Read-Only Mapping Workflow** below for the step-by-step discovery procedure.

- discover CLI session IDs
- discover transcript JSONL paths (encoded projects folder + `<cliSessionId>.jsonl`)
- discover adjacent workspace/session data in the source encoded folder: `memory/`, `<cliSessionId>\subagents\`, and `<cliSessionId>\tool-results\`
- discover the Layer B Desktop record path per session
- discover old workspace roots per session (from the transcript `cwd` and the Desktop record `cwd`)
- discover whether the requested sessions come from one source workspace or multiple source groups

Use read-only inspection of:

- `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\` for transcript filenames (= session IDs)
- `C:\Users\Admin\AppData\Roaming\Claude\claude-code-sessions\<account>\<group>\local_*.json` for `cliSessionId`, `cwd`, `originCwd`, `title`

### Front-Door Output

Once discovery is complete:

1. Create the manifest by explicitly invoking the `manifest-this` skill (Markdown default; see **Manifest Storage**), saved under the active workspace's `Archive/Historical/Manifests/Claude/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion, pre-fill the skill's inputs, and save it under `Archive/Historical/Summaries/Migration/Claude/`. Apply the availability guard if the skill is not loaded.
3. Group sessions by real discovered old workspace when needed. If there are mixed-source sessions, represent them as separate source groups rather than flattening them into one assumed old workspace.

### Front-Door Stop Boundary

The Front-Door Workflow stops after Claude has:

- gathered the user inputs
- discovered the real session metadata
- built (or updated) the manifest
- built the handoff summary by explicitly invoking the `session-summary` skill (helper-scoped; see **Session Summary Integration**)
- identified the destination workspace and any source groups

At that point, if the migration must touch live Claude state, Claude should stop and hand execution to a non-Claude helper agent that can run while Claude Desktop is fully closed.

## Read-Only Mapping Workflow

When preparing a batch or front-door package for another agent:

1. List `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\*.jsonl` — each filename stem is a `cliSessionId`.
2. List `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\memory\`, if present.
3. For every target session ID, list adjacent `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\<cliSessionId>\subagents\` and `...\<cliSessionId>\tool-results\`, if present.
4. For each desired chat, find its Layer B record by scanning `...\claude-code-sessions\<account>\<group>\local_*.json` for the one whose `cliSessionId` matches; read its `title`, `cwd`, `originCwd`.
5. Confirm the transcript's top-level `cwd` matches the old workspace.
6. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
7. Produce a manifest with one entry per session:
   - `title`
   - `cli_session_id`
   - `desktop_record` (full path to the `local_*.json`)
   - optional `transcript_path` (else the helper computes it from the workspace + id)
   - whether the transcript and Desktop record were found.
   - optional `sessions[].sidecars` discovery metadata when present:
     - workspace-level `memory/` source and destination
     - per-session `subagents/` and `tool-results/` source and destination
8. If adjacent data must be moved by the helper script, also produce a top-level `adjacent_data_relocation` execution plan:
   - `memory_move` for workspace-level `memory/`
   - `sidecar_relocations` for per-session `subagents/` and `tool-results/`
   - `then_delete` for deleting the old encoded folder only after true-empty verification

Important: `sessions[].sidecars` is human-readable discovery/audit metadata. It is not, by itself, a helper-script execution instruction. If a manifest only records sidecars under `sessions[].sidecars`, the helper can migrate transcripts and Desktop records but will not know which adjacent folders to move.

## Execution Workflow

Use this workflow only when a non-Claude helper agent is running and Claude Desktop is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and feedback summary generation.

### Two-Layer Apply Workflow

Only apply after the user or handoff explicitly greenlights execution and Claude Desktop is closed.

#### Layer A: CLI Transcript

For each target session:

1. Confirm the old transcript exists at `<encoded-old-workspace>\<cliSessionId>.jsonl`.
2. Back up the transcript file before writing.
3. Create the new projects dir `C:\Users\Admin\.claude\projects\<encoded-new-workspace>\` if missing.
4. For every JSONL record with a top-level `cwd` equal to the old workspace (or under it), rewrite that `cwd` to the destination workspace. Do not touch `content` or other prose.
5. Write the transformed transcript to `<encoded-new-workspace>\<cliSessionId>.jsonl` and verify every non-empty line still parses as JSON, with the expected count of destination `cwd` values and zero residual old-workspace `cwd` values (exact root **and** descendants, e.g. `old\subdir`).
6. Remove the old transcript from the old projects dir only after the destination is verified (the chat must live in exactly one projects folder).

**Canonical JSONL reserialization is intentional.** A changed record is parsed, its `cwd` rewritten, and the object re-serialized with `json.dumps(..., separators=(",", ":"), ensure_ascii=False)`. This normalizes spacing/separator style for changed lines only; unchanged lines are copied byte-for-byte. This is deliberate — JSONL has no canonical byte layout, and a fragile byte-level patcher to preserve cosmetic whitespace would be strictly more dangerous than reserializing. Lines that did not change are never rewritten.

#### Layer B: Desktop Chat Store

For each target session's `local_*.json`:

1. Back up the record before writing.
2. Detect the file's current encoding state (UTF-8, with or without a BOM).
3. Rewrite only `cwd` and `originCwd` from the old workspace to the destination workspace.
4. Preserve all other keys (including `cliSessionId`, `title`, `model`, permissions) and preserve the detected BOM/no-BOM state on write.
5. Verify the file still parses as JSON and that `cliSessionId` and `title` are unchanged.

#### Adjacent Project Data: Memory and Sidecars

For each source encoded workspace:

1. Discover whether `memory/` exists. If present, treat it as whole-workspace state (see **Memory Ownership**): only move it when the manifest declares `memory_scope: "whole_workspace"`. With `memory_scope: "none"` leave it at the source. Back it up and move it to the destination encoded workspace's `memory/` folder, creating the destination parent if missing. **If a destination `memory/` already exists, hard-refuse** rather than guessing how to merge or replace it — replacement requires explicit user approval and a verified backup, and this skill does not invent a merge semantic.
2. For each target `cliSessionId`, discover sibling `<cliSessionId>\subagents\` and `<cliSessionId>\tool-results\` folders. Back up each present folder before moving.
3. Move each sidecar folder to the encoded workspace where that session's `<cliSessionId>.jsonl` now lives. In mixed-destination batches, do not assume one destination for every sidecar; route by the manifest's `adjacent_data_relocation.sidecar_relocations` destination.
4. Preserve sidecar contents byte-for-byte. Do not parse, rewrite, or normalize files inside these folders.
5. After relocation, verify every moved destination folder exists, every source folder is gone, and the source encoded workspace is truly empty before it is eligible for deletion.

True-empty means `0` files and `0` subdirectories remain, not merely `0` `.jsonl` transcripts.

### Helper Script

Use `scripts/migrate_claude_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. The helper consumes the native JSON recovered from the durable manifest into an approved temporary `.json` (see **Durable Artifact Format Handling**); keep the durable Markdown manifest in `Archive/Historical/Manifests/Claude/` (see **Manifest Storage**).

The helper script belongs to the **Execution Workflow** side. It is not the front door. Claude may help discover inputs and generate the manifest, but a non-Claude helper agent should run the script while Claude Desktop is fully closed.

Expected manifest shape:

```json
{
  "old_workspace": "C:\\Users\\Admin\\Uzzys World",
  "new_workspace": "C:\\Users\\Admin\\Uzzys Universe",
  "sessions": [
    {
      "title": "0.) First of Many --> Setup",
      "cli_session_id": "5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19",
      "desktop_record": "C:\\Users\\Admin\\AppData\\Roaming\\Claude\\claude-code-sessions\\<account>\\<group>\\local_33716310-....json"
    },
    {
      "title": "1.) Already Moved Session",
      "cli_session_id": "9b1c2d3e-....",
      "desktop_record": "C:\\Users\\Admin\\AppData\\Roaming\\Claude\\claude-code-sessions\\<account>\\<group>\\local_9b1c2d3e-....json",
      "status": "done"
    }
  ]
}
```

A session entry with `"status": "done"` is skipped by the helper (`is_done()`). Use it to mark a session already migrated in a staged manifest so a re-run over the same manifest does not touch it again.

When adjacent Claude project data must move, include a top-level `adjacent_data_relocation` block:

- `memory_move`: `source`, `destination`, `memory_scope` (`whole_workspace` or `none`; **mandatory** — an absent scope is a hard stop), a **mandatory** `expected_files` block with expected `files`/`directories` counts, and optionally `allow_missing_source: true` (see the missing-source rule below)
- `sidecar_relocations`: entries with `session_id`, `sidecar_kind`, `source`, `destination`, `dest_encoded_folder`, a **mandatory** `expected_files` block with expected `files`/`directories` counts, and optionally `allow_missing_source: true`

**Missing-source rule:** a declared relocation whose source does not exist is a **hard stop** — it never silently succeeds as a no-op. The only exemption is an entry that explicitly sets `allow_missing_source: true` **and** declares `expected_files` with both `files: 0` and `directories: 0`; that combination is treated as an intentional, manifest-declared no-op and reported as skipped. `allow_missing_source` with any non-zero (or undeclared) expected count is itself a hard stop.
- `then_delete`: source encoded folder to delete only after true-empty verification

Example:

```json
{
  "adjacent_data_relocation": {
    "memory_move": {
      "source": "C:\\Users\\Admin\\.claude\\projects\\<old-encoded>\\memory",
      "destination": "C:\\Users\\Admin\\.claude\\projects\\<new-encoded>\\memory",
      "memory_scope": "whole_workspace",
      "expected_files": { "files": 3, "directories": 0 }
    },
    "sidecar_relocations": [
      {
        "session_id": "5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19",
        "sidecar_kind": "tool-results",
        "source": "C:\\Users\\Admin\\.claude\\projects\\<old-encoded>\\5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19\\tool-results",
        "destination": "C:\\Users\\Admin\\.claude\\projects\\<new-encoded>\\5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19\\tool-results",
        "dest_encoded_folder": "<new-encoded>",
        "expected_files": { "files": 12, "directories": 1 }
      }
    ],
    "then_delete": "C:\\Users\\Admin\\.claude\\projects\\<old-encoded>"
  }
}
```

The old `third_pass_leftover_relocation.aux_relocations` name came from an earlier staged cleanup pass. The helper may keep a small fallback for archived manifests, but new manifests must use `adjacent_data_relocation.sidecar_relocations`.

The helper must dry-run this block before apply, back up every source folder under `~/.claude/user-backups/<run-timestamp>/`, move the folders byte-for-byte, **verify each destination's file/directory count against the manifest's mandatory `expected_files` block** (a mismatch is a hard error, and an absent or empty `expected_files` block is itself a hard error — verification is never silently skipped; a missing declared source is also a hard error unless the entry sets `allow_missing_source: true` with declared counts of exactly 0 files and 0 directories, in which case it is reported as an intentional skipped no-op), verify destinations and source absence, verify true-empty, and only then delete `then_delete`.

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- The new projects dir `<encoded-new-workspace>` exists and contains `<cliSessionId>.jsonl` for each migrated session.
- The migrated transcript parses line by line, with zero old-workspace `cwd` values. Residual detection is **descendant-aware**: a value at or under the old workspace (including `old\subdir`) counts as residual, not only the exact old root, so a stale descendant cannot pass silently. If the manifest recorded an expected count of destination `cwd` values, confirm it.
- The old transcript no longer exists in the old projects dir for each migrated session.
- Each migrated Desktop record has `cwd` and `originCwd` equal to the destination workspace, with `cliSessionId` and `title` unchanged and the original BOM/no-BOM state preserved.
- Workspace `memory/`, if present and in scope, exists in the destination encoded workspace and no longer exists in the source encoded workspace, and its destination file/directory count matches the manifest's mandatory `expected_files` block.
- Each target session's `subagents/` and `tool-results/` sidecar folders, if present and in scope, exist beside the destination transcript folder and no longer exist under the source encoded workspace, with destination counts matching the manifest's mandatory `expected_files` blocks.
- Every relocation reported as skipped is either `memory_scope: "none"` or an explicit `allow_missing_source: true` entry with declared zero counts — no relocation silently no-opped on a missing source.
- Before deleting any source encoded workspace folder, recursively verify it contains `0` files and `0` subdirectories.
- Non-target sessions (transcripts and Desktop records) are unchanged.
- User reopens Claude Desktop and confirms:
  - chat appears under the destination project,
  - chat stays there after startup settles,
  - chat opens/resumes normally and can send/receive a message.

### Execution Feedback

After verification passes and before considering the migration closed, produce an execution feedback summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Historical/Summaries/Migration/Claude/` so the user (and the front-door agent) can review it. Apply the availability guard if the skill is not loaded. If the helper updates the manifest (for example marking sessions applied or recording a rollback), do so through the `manifest-this` skill (update mode) so the artifact, its number, and its change log stay consistent.

### Failure And Rollback

If anything fails before a session is fully written, stop and report the failing session ID and file. If a post-write verification fails, restore from backups before attempting another approach. If the UI still shows a chat under the old group after both layers agree, re-confirm the encoded folder name and the Desktop record `cliSessionId` link, and inspect for any additional Desktop-side cache before retrying.

## Agent Provenance For Durable Artifacts

The migration manifest is a first-party durable artifact and must carry schema-safe agent provenance. `manifest-this` renders the visible Agent Provenance table and append-only Agent Change Log in the manifest artifact; the embedded native JSON payload keeps its own top-level `agent_provenance` object containing `content_owner`, `original_writing_agent`, `original_writing_llm`, `created`, `artifact_role`, and an append-only `change_log`. Each change-log item records the clock-read `YYYY-MM-DD-HH:mm:ss` timestamp, truthful acting agent, that agent's `model`, action, and concise scope. Preserve the original writer and the original writing model permanently.

The helper for this skill accepts additional top-level manifest metadata, but never add provenance to application databases, transcripts, caches, registries, backups, or other migrated operational state. If another manifest consumer has a strict schema that rejects the metadata, keep the native execution manifest unchanged and place provenance in an approved human-readable companion instead.

`session-summary` separately owns provenance for migration handoff and execution summaries. An HTML or PDF rendition must visibly preserve the native manifest's original creator and identify the agent that performed the conversion.

## Durable Artifact Format Handling

This skill owns migration discovery, safety gates, manifest schema, execution, backups, verification, and handoff/feedback scope. When co-invoked with `html-this` or `pdf-this`, pass the requested format to `session-summary` and create only the requested human-readable handoff/feedback format.

The migration manifest is created through `manifest-this`, whose default format for migration skills is Markdown (`.md`) with the exact native JSON embedded in a fenced block. If the user explicitly requests an HTML-only or PDF-only manifest, `manifest-this` embeds the exact JSON through the format skill. Before execution, recover the JSON to an approved temporary `.json`, validate the original manifest schema, and give only that temporary file to the migration helper; remove it afterward per the workspace temporary-file policy. Backups, databases, transcripts, and app state always remain in their required native formats. Treat same-stem format variants as one manifest.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/feedback summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in your final feedback summary that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Historical/Summaries/Migration/Claude/`
- Create the `Claude` platform folder if it does not exist.
- Sequence number: the next integer after the highest existing `N.)` file in the `Claude` platform folder only.
- Filename templates — the migration grammar `N.) Who + Topic + What`. These override the `session-summary` skill's default filename convention: pre-fill the filename so the output uses this exact shape, with no trailing `Summary N` and no `Execution` wording.
  - Handoff, written by the front-door agent: `N.) <Front-Door Agent> <Topic> Handoff.md` — e.g. `1.) Claude Trading Chats Handoff.md`
  - Feedback, written by the helper agent: `N.) <Helper Agent> <Topic> Feedback.md` — e.g. `2.) Hermes Trading Chats Feedback.md`

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.
