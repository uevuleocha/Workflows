---
name: stage-commit-push
description: Deterministic, explicitly invoked stage/commit/push workflow with scoped staging, remote safety gates, and automatic loud hub pointer synchronization when the current repository is a parent hub submodule.
---

# Stage Commit Push

Stage, commit, and push one repository deterministically. When the repository is a submodule of an ancestor hub, automatically synchronize its gitlink in a separate hub commit loudly after proving the nested commit is pushed (unless the user explicitly opts out).

## Invocation

Run only for `/stage-commit-push`, `use stage-commit-push`, `stage commit push`, `stage, commit, and push`, or an equally explicit full-workflow request.

An explicit invocation with an unambiguous scope authorizes the ordinary safe workflow end to end: pre-flight, scoped staging, commit-message drafting, commit, push, pushed-commit proof, and eligible pointer-only hub synchronization. Do not pause for routine approvals once the scope is known. Stop only for a missing required input or a safety condition named by this skill.

## Scope Modes

1. **All:** stage the current repository with `git add -A`.
2. **Particular:** stage only user-named paths with `git add -A -- <path>...`.

If scope is ambiguous, ask before mutation. In Particular mode, the named paths govern only the current repository's commit. Eligible pointer-only hub synchronization remains a separate automatic follow-up and does not expand that nested staging scope.

## Repository Determination

1. Resolve the current repository with `git rev-parse --show-toplevel` and state it before mutation.
2. Walk ancestors outside that root and inspect candidate repositories' `.gitmodules` plus tracked mode `160000` entries.
3. Treat the current repository as nested only when its canonical path exactly matches a registered submodule path in an ancestor repository. Record the hub root, submodule name, and hub-relative path.
4. Do not infer nesting merely because another `.git` directory exists above it.
5. Never mix nested-repository content and hub changes in one commit.

## Pre-Flight for Any Repository

Before staging:

1. Resolve branch and upstream; require a configured `origin` and upstream unless the host contract explicitly defines another approved remote.
2. Run `git fetch origin`.
3. Hard-stop if the remote is ahead or the histories diverged.
4. List `git log <upstream>..HEAD`; require explicit user approval before a push that would include pre-existing unpushed commits.
5. Snapshot pre-existing staged paths. Particular mode must not let unrelated pre-staged paths ride along; stop and ask rather than resetting user state.

## Nested Repository Push

1. Stage only the chosen scope.
2. Verify the staged path list exactly matches scope.
3. Draft an imperative commit message based on the staged diff.
4. Append `Agent: <Platform>` where Platform is the executing agent platform (for example Hermes, Codex, Claude, Antigravity, or zCode), never the model.
5. Commit and push the nested repository.
6. Prove the pushed commit is reachable from its configured upstream after a fetch, for example with `git merge-base --is-ancestor HEAD <upstream>` and matching/reachable remote evidence. A successful `git push` message alone is not sufficient if the upstream is ambiguous.

If the current repository is not a registered submodule, report success and stop.

## Hub Pointer Synchronization

Pointer synchronization is a second repository operation, never an implicit extension of the nested commit.

### Default behavior

Hub pointer synchronization is **ON by default** for nested repositories. Unless the user explicitly opts out during invocation (e.g., "no hub sync", "do not sync hub pointer", "nested only"), automatically proceed with hub pointer synchronization after nested push pre-flight/verification succeeds and eligibility gates pass. If the user explicitly opts out, skip hub pointer synchronization and report status as `declined by user`.

### Eligibility gates

Proceed only if all are true:

- the nested `HEAD` was proved pushed to its upstream;
- the user did not explicitly opt out of hub pointer synchronization;
- the hub still tracks the exact named path as mode `160000`;
- the hub worktree's submodule path resolves to the just-pushed nested repository;
- `git status --porcelain=v2 -z` and a direct nested status check prove the nested worktree has no lowercase-`m` uncommitted-content condition;
- the hub has an `origin`, branch, and upstream;
- `git fetch origin` shows the hub remote is not ahead or diverged;
- the user approved any pre-existing unpushed hub commits;
- no unrelated path is already staged in the hub.

Lowercase `m` is not syncable. A hub records only a committed SHA, never nested working-tree content. Leave `m` visible and stop; do not try to capture it.

### Pointer-only hub operation

1. Record the hub's staged-path list and full porcelain status.
2. Stage exactly one path: `git -C <hub> add -- <hub-relative-submodule-path>`.
3. Verify the staged diff contains exactly that one path and that its mode is `160000` before and after. Use `git diff --cached --name-only -z` and `git diff --cached --raw`.
4. Verify the staged new gitlink SHA equals the proved-pushed nested `HEAD`.
5. Commit separately with a scoped message such as `Bump <name> submodule pointer to <sha7>` and the executing-platform trailer.
6. Push the hub branch to its upstream.
7. Fetch and verify the remote hub now records the expected gitlink SHA.

Never use `git add -A` or `git add .` for pointer synchronization. Never stage a second path. If another path appears staged, stop before commit and preserve user state; do not reset it without approval.

## Failure and Recovery

- If the nested push fails, do not touch the hub.
- If pushed-commit proof fails, do not touch the hub.
- If a hub pre-flight or user gate fails, leave the successful nested push intact and report the pointer as not synchronized.
- If hub push fails after the pointer-only commit, report the local hub commit as unpushed; do not rewrite, amend, force-push, or hide it.
- Never pull, merge, rebase, reset, clean, skip hooks, or force-push as an improvised recovery.

## Reporting

Always report both repositories loudly and explicitly in the output log and final response:

```text
Nested repository:
- Repo: <path>
- Scope: <all | named paths>
- Commit: <sha> — <subject>
- Pushed/proved at: <upstream>

Hub pointer synchronization (ALWAYS REPORT LOUDLY):
- Status: <committed and pushed | declined by user | blocked | not applicable>
- Hub: <path>
- Pointer path: <path>
- Pointer commit: <sha or N/A>
- Verified remote gitlink: <sha or N/A>
```

## Markdown Table Alignment

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

## Validation

- Confirm the nested staged list matched scope and the commit carried the correct executing-platform trailer.
- Confirm the nested commit is reachable from the upstream before hub mutation.
- Confirm auto hub pointer synchronization defaults to ON unless explicitly opted out by the user.
- Confirm Particular mode applies its named-path scope only to the current repository and does not require a second approval for eligible pointer-only hub synchronization.
- Confirm hub pointer synchronization status is always reported loudly.
- Confirm the hub commit, when made, changes exactly one `160000` gitlink.
- Confirm scoped mode never stages an unnamed pointer.
- Confirm lowercase `m` blocks pointer synchronization.
- Confirm remote-ahead, diverged, pre-existing-commit, and unrelated-staged-change gates were respected independently in both repositories.
- Confirm the portable Markdown Table Alignment section remains present.

When updating this skill, run the folder-style skill validator with Python UTF-8 mode and run `python -B -X utf8 scripts/test_autonomy.py`. The test uses only disposable repositories under the workspace `tmp/` folder and removes its fixture afterward.
