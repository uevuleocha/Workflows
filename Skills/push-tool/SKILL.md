---
name: push-tool
description: Copy a cTrader tool folder (Indicator or Robot) from the cAlgo Sources directory into the matching Uzzy Ecosystem Tools/Sources directory so the agent's workspace mirrors the latest version compiled in cTrader. Use when the user explicitly invokes /push-tool, says push tool, push-tool, push the tool, push a named tool, or clearly asks to sync a cAlgo tool folder back into the workspace. This skill only ever copies cAlgo to workspace, never the reverse, and never touches the cAlgo directory itself.
---

# Push Tool

Automate the manual step of copying a cTrader tool folder from `cAlgo\Sources\` into the matching `Uzzy Ecosystem\Tools\Sources\` directory so the agent always works against the latest compiled version of the tool.

This skill replaces the user's repetitive manual file-copy workflow. It does not edit code, build code, or write into `cAlgo\`. It only mirrors a single tool folder in one direction: cAlgo to workspace.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

The agent must never write into `cAlgo\`. The cTrader IDE paste step (chat code block to cAlgo) stays manual and is outside this skill's scope.

## Direction Rule

This skill copies in one direction only:

```text
C:\Users\Admin\OneDrive\Documents\cAlgo\Sources\(Indicators|Robots)\<ToolName>\
        |
        v
C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Tools\Sources\(Indicators|Robots)\<ToolName>\
```

The reverse direction (workspace to cAlgo) is never performed by this skill. If a user request implies the reverse direction, stop and clarify.

## Invocation

Treat these as direct invocation and begin the skill workflow:

- `/push-tool`
- `use the push-tool skill`
- `push the tool`
- `push <ToolName>`
- clear equivalents where the user names this skill or asks to sync a cAlgo tool folder into the workspace

## Supported Invocation Forms

The skill supports four entry points. The default is context-driven.

1. **Context-driven (default).** `/push-tool` with no arguments. The agent infers the tool name and type (Indicator or Robot) from the current chat context, i.e. whichever tool the conversation has been working on. If context is ambiguous or missing, the agent asks the user before any copy action.
2. **Explicit name and type (form A).** `/push-tool <ToolName> <indicator|robot>`. Example: `/push-tool UzzyScalper indicator`. No inference required.
3. **Name only, infer type (form B).** `/push-tool <ToolName>`. The agent checks `cAlgo\Sources\Indicators\` and `cAlgo\Sources\Robots\` to determine type. If the tool exists in only one location, proceed. If it exists in both or neither, ask before acting.
4. **Batch / multi-push (form D).** `/push-tool <ToolA>, <ToolB>, ...`. Comma-separated list. Each tool is resolved independently using the same inference rules. The agent may also accept `/push-tool multiple` and then ask follow-up questions to gather the list and per-tool type.

## Required Inputs

Before performing any copy, the skill must know:

1. **Tool name(s)** — the exact folder name(s) inside `cAlgo\Sources\(Indicators|Robots)\`.
2. **Tool type for each tool** — Indicator or Robot.

If either is missing or ambiguous after checking chat context and the cAlgo directory, ask the user. Do not guess.

## Paths

Source root:

```text
C:\Users\Admin\OneDrive\Documents\cAlgo\Sources\
```

Destination root:

```text
C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Tools\Sources\
```

Subfolders:

- Indicators: `Indicators\<ToolName>\`
- Robots: `Robots\<ToolName>\`

Version history (backups):

```text
https://github.com/uevuleocha/Uzzy-Ecosystem  (git commit history on main)
```

Log:

```text
"C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Archive\Live\Documentation\Personal\Logs\1.) push-log.md"
```

## Runtime Validation

Each run performs four checks:

1. **Pre-copy source check (A).** Confirm the source folder `cAlgo\Sources\<Type>\<ToolName>\` exists. If it does not, hard-error and stop. Report the missing path to the user. Do not attempt fallback inference or partial copies.
2. **Pre-copy destination check (B).** Confirm the destination folder `Uzzy Ecosystem\Tools\Sources\<Type>\<ToolName>\` exists. If it does not, create it.
3. **Staging & remote pre-flight (C).** At run start:
   - Check `git diff --cached`. If unrelated changes are already staged (e.g. by another agent or an earlier command), proceed safely — every commit in this skill is pathspec-scoped and cannot include them — but mention the unrelated staged files in the user-facing report.
   - `git fetch origin`. If `origin/main` is ahead of local `main` (or histories diverge), **hard-stop**: report the remote commits and stop. Never improvise a pull, rebase, or merge mid-run — the user decides how to update local `main` first.
   - Check for pre-existing unpushed local commits (`git log origin/main..main`). A branch push always delivers the whole chain, so this run's push would ship them too. If any exist, list their hashes, messages, and signing agents, and **ask the user for approval** before proceeding. The user's answer gates the push.
   - Record the starting commit hash for the run's report.
4. **Post-copy file-count check (D).** After the copy, count the files written to the destination this run and include the count in the log line and the user-facing report.

## Copy Behavior

- **Folder scope.** Copy the entire source folder contents. No filtering. Include `.cs`, `.csproj`, `bin\`, `obj\`, `*.user`, and any other files present in the cAlgo folder.
- **Overlay copy.** Write new and changed files into the destination. Do not delete files in the destination that are absent from the source. The cAlgo folder is treated as the source of truth for files it contains; extras in the workspace are left alone.
- **Commit first (pre-copy seal, tool-scoped).** Before writing any file in the destination, stage and commit only the tool's own folder (`git add` and `git commit` both pathspec-scoped to `"Tools/Sources/<Type>/<ToolName>"`) so the outgoing version is sealed in git history before it is overwritten. Skip only if that folder has no uncommitted changes.
- **Commit and push after (post-copy seal, tool-scoped).** After the overlay copy, stage and commit only the tool's folder (pathspec-scoped), capture the commit hash, append the log line, seal the log in its own follow-up commit, and push both to `origin main`. If the overlay changed nothing, follow the three-way no-change rule in Workflow step 8 (zero-trace no-op, snapshot-only, or mixed batch). No local folder backups are ever created.
- **Never sweep the whole repo.** This skill never runs `git add -A`, and every `git commit` carries a pathspec limited to the pushed tool folder(s) and `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"` — so even files another agent pre-staged before the run cannot ride along. Other tools' in-progress work is never swept into a push-tool commit.

## Logging

After a successful push, append one line per tool to `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"`:

```text
[YYYY-MM-DD HH:MM] pushed <Type>\<ToolName> (<N> files, commit <hash>, agent: <AgentName>)
```

Example:

```text
[2026-05-22 14:32] pushed Robots\Uzzy TRUTH (12 files, commit a1b2c3d, agent: Claude)
```

Snapshot-only variant (overlay produced no tracked changes, but step 5 sealed uncommitted edits in a pre-push snapshot — `<hash>` is the snapshot commit):

```text
[YYYY-MM-DD HH:MM] pushed <Type>\<ToolName> (0 changed files from cAlgo, pre-push snapshot commit <hash>, agent: <AgentName>)
```

A completely unchanged run (no snapshot, no overlay changes) writes **no log line at all** — the run leaves zero trace in the repo and is reported in chat only. This keeps the workspace clean: a log line with no commit to seal it would leave `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"` dirty.

`<hash>` is the short hash of the **tool commit** (the commit that sealed the synced tool files — the backup that matters), not the log commit. The log line is written *after* the tool commit exists and is then sealed in its own small follow-up commit; a commit's own hash can never be written inside that same commit.

`<AgentName>` is the agent actually executing the run — not a hard-coded list. Currently in use: `Claude`, `Codex`, `Antigravity`; any future agent (e.g. a new tool the user adopts) signs with its own truthful name.

For a batch run, write one line per tool, in execution order. If `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"` does not exist, create it with a single `# Push Log` heading at the top and then append the first entry.

## Workflow

1. **Identify inputs.** Determine tool name(s) and type(s) using the rules in `Supported Invocation Forms` and `Required Inputs`. If ambiguous, ask the user. Do not act on a guess.
2. **Pre-copy source check (A).** For each tool, verify the source folder exists. If not, hard-error, report the missing path, and stop. For a batch, stop the whole batch.
3. **Pre-copy destination check (B).** For each tool, verify or create the destination folder.
4. **Staging & remote pre-flight (C).** Note any unrelated already-staged changes for the report (they are never included in this skill's commits). `git fetch origin`; hard-stop if `origin/main` is ahead or diverged. If pre-existing unpushed local commits exist, list them (hash, message, signing agent) and ask the user for approval before proceeding — the push in step 10 would deliver them too. Record the starting commit hash.
5. **Pre-copy commit (seal outgoing version, tool-scoped).** If the tool's folder has uncommitted changes, run exactly:

```powershell git add -- "Tools/Sources/<Type>/<ToolName>" git commit -m "push-tool: pre-push snapshot <Type>\<ToolName> | Agent: <AgentName>" -- "Tools/Sources/<Type>/<ToolName>" ```

   The pathspec on `git commit` guarantees pre-staged unrelated files cannot ride along. Skip if that folder is already clean. For a batch, the pathspec lists every named tool's folder. If this snapshot commit is created, capture its short hash — it matters for the no-change case in step 8.
6. **Overlay copy.** Copy every file from the source folder to the destination folder, overwriting existing files. Do not delete extras in the destination.
7. **Post-copy file-count check (D).** Count the files written this run.
8. **Tool commit (seal synced version).** Run exactly:

```powershell git add -- "Tools/Sources/<Type>/<ToolName>" git commit -m "push-tool: synced <Type>\<ToolName> | Agent: <AgentName>" -- "Tools/Sources/<Type>/<ToolName>" ```

   A batch uses one commit whose pathspec lists every named tool's folder; list each tool in the body. Capture the short commit hash. **If the overlay produced no tracked changes** (cAlgo and workspace already identical), never create an empty marker commit — instead apply the three-way no-change rule:
   - **Completely unchanged run** (no snapshot commit at step 5, overlay changed nothing): write no log line, create no commits, skip to step 11 and report "already up to date." The chat report is the record of the run; the workspace is left exactly as found.
   - **Snapshot-only run** (step 5 created a pre-push snapshot, overlay changed nothing): the snapshot is this run's product. Log it using the snapshot-only line format with the snapshot commit's hash, seal the log per step 9, push, and report the snapshot hash honestly — do not claim "no commits were created."
   - **Batch with mixed results:** commit and log the changed tools normally; report unchanged tools as in-sync per the rules above. Never abort the batch because some tools were unchanged.
9. **Log + log commit.** Append one line per tool to `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"` using the captured hash, then run exactly:

```powershell git add -- "Archive/Live/Documentation/Personal/Logs/1.) push-log.md" git commit -m "push-tool: log <Type>\<ToolName> | Agent: <AgentName>" -- "Archive/Live/Documentation/Personal/Logs/1.) push-log.md" ```

   Skipped only on a completely unchanged run (no log line was written, so there is nothing to seal). No path through this workflow may leave `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"` modified but uncommitted.
10. **Push.** Push all commits created by this run (snapshot, tool, and log commits as applicable), plus any pre-existing commits the user explicitly approved at pre-flight, to `origin main`. A remote-ahead push is never attempted — that was hard-stopped at step 4.
11. **Report.** Tell the user what was pushed, the file count, the tool commit hash, the signing agent, any unrelated staged files noticed at pre-flight, and — when applicable — which pre-existing commits the push also delivered and that the user approved them. For a batch, report one bullet per tool.

## Reporting Format

Single-tool success:

```text
Pushed <Type>\<ToolName>.
- Files copied: <N>
- Sealed on GitHub: commit <hash> (tool commit)
- Agent: <AgentName>
- Log: "Archive/Live/Documentation/Personal/Logs/1.) push-log.md" updated and committed.
- (If applicable) Unrelated staged files noticed at pre-flight: <paths> — untouched by this run.
- (If applicable) Pre-existing unpushed commits also delivered (user-approved at pre-flight): <hashes>.
```

Remote-ahead hard-stop: report the remote commits found at pre-flight, state that no copy, commit, or push was performed, and stop — the user decides how to update local `main`.

Completely unchanged run: report "already up to date" — no commits created, no log line written, workspace left exactly as found.

Snapshot-only run: report that cAlgo and the workspace were already identical, but the tool's uncommitted local edits were sealed and pushed as pre-push snapshot commit `<hash>` (logged with the snapshot-only line).

Batch with mixed results: one bullet per tool — changed tools show the normal success fields, unchanged tools show the applicable wording above. The batch never aborts because some tools were unchanged.

Batch success: one bulleted entry per tool with the same fields, followed by a single line confirming the log was updated once.

Failure (source missing): name the missing source path, state that no copy or commit was performed, and stop.

## Safety Rules

- Never write into `cAlgo\`. The skill is read-only for that directory.
- Never copy in the reverse direction (workspace to cAlgo).
- Never delete files in the destination that are not present in the source. Use overlay, not mirror.
- Always seal the outgoing version with a tool-scoped pre-copy commit before overwriting (skip only when the tool's folder is already clean — the version is then already sealed).
- Never stage paths outside the pushed tool's folder and `"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"`, and always pathspec-scope every `git commit` to those same paths. No `git add -A` and no bare `git commit` in this skill — parallel agents' in-progress or pre-staged work must never be swept into a push-tool commit.
- Never rewrite git history or force-push. Old versions must remain recoverable forever.
- Never attempt a push when `origin/main` is ahead of or diverged from local `main` — hard-stop at pre-flight and let the user decide how to update local `main`.
- Never push pre-existing unpushed commits (another agent's or otherwise) without the user's explicit approval at pre-flight. A branch push delivers the whole chain, so this is the only way to keep the "push-tool pushes only its own work" promise.
- **Known limit of the guarantee:** pre-flight cannot detect a commit made by another agent *during* the run. True isolation would require serialized git operations; the user's session practice — never run git operations in two apps simultaneously (one microphone at a time) — is what closes that gap. Do not claim stronger isolation than this.
- Always hard-error on a missing source folder. Do not attempt to recover by guessing the tool type or name.
- Treat chat-context inference as a hint, not a fact. When in doubt, ask the user.

## Version History / Recovery

Git history on `origin main` (GitHub: `uevuleocha/Uzzy-Ecosystem`, private) is the backup system. Every push run produces commits that permanently seal the pre-push and post-push versions of the tool. No local backup folders are created; `tmp\push-backups\` is retired (its final contents remain recoverable from commit `2ae445c` and earlier history).

To recover an older version of a tool:

```text
git log --oneline -- "Tools/Sources/<Type>/<ToolName>"          # list every sealed version git checkout <hash> -- "Tools/Sources/<Type>/<ToolName>"        # restore that version into the workspace
```

Versions can also be browsed per-file on GitHub via the file's History view.

**End-of-session full sync (outside this skill).** Because push-tool commits are tool-scoped, other workspace changes (plans, summaries, tasks, other tools' edits) stay local and uncommitted during the session. At the end of a work session, the user may ask any agent to push the whole workspace (`git add -A` → commit → push) to guarantee GitHub fully mirrors the laptop. That full sync is a user-requested action, not part of this skill.

## Out of Scope

- Building or compiling tools.
- Editing `.cs` files in either directory.
- Copying anything from the workspace into `cAlgo\`.
- Creating local backup folders (git history on GitHub is the backup system).
- Rewriting git history, force-pushing, or deleting old commits.
- Diffing source code between cAlgo and workspace beyond a file count.
