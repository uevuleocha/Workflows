---
name: stage-commit-push
description: Deterministic, explicitly invoked stage/commit/push workflow with scoped staging, remote safety gates, and optional user-approved pointer-only synchronization when the current repository is a parent hub submodule.
---

# Stage Commit Push

Stage, commit, and push one repository deterministically. When the repository is
a submodule of an ancestor hub, optionally synchronize only its gitlink in a
separate, user-approved hub commit after proving the nested commit is pushed.

## Invocation

Run only for `/stage-commit-push`, `use stage-commit-push`, `stage commit push`,
`stage, commit, and push`, or an equally explicit full-workflow request.

## Scope Modes

1. **All:** stage the current repository with `git add -A`.
2. **Particular:** stage only user-named paths with
   `git add -A -- <path>...`.

If scope is ambiguous, ask before mutation. In Particular mode, an unnamed
submodule pointer is never eligible for staging or synchronization.

## Repository Determination

1. Resolve the current repository with `git rev-parse --show-toplevel` and state
   it before mutation.
2. Walk ancestors outside that root and inspect candidate repositories'
   `.gitmodules` plus tracked mode `160000` entries.
3. Treat the current repository as nested only when its canonical path exactly
   matches a registered submodule path in an ancestor repository. Record the hub
   root, submodule name, and hub-relative path.
4. Do not infer nesting merely because another `.git` directory exists above it.
5. Never mix nested-repository content and hub changes in one commit.

## Pre-Flight for Any Repository

Before staging:

1. Resolve branch and upstream; require a configured `origin` and upstream unless
   the host contract explicitly defines another approved remote.
2. Run `git fetch origin`.
3. Hard-stop if the remote is ahead or the histories diverged.
4. List `git log <upstream>..HEAD`; require explicit user approval before a push
   that would include pre-existing unpushed commits.
5. Snapshot pre-existing staged paths. Particular mode must not let unrelated
   pre-staged paths ride along; stop and ask rather than resetting user state.

## Nested Repository Push

1. Stage only the chosen scope.
2. Verify the staged path list exactly matches scope.
3. Draft an imperative commit message based on the staged diff.
4. Append `Agent: <Platform>` where Platform is the executing agent platform
   (for example Hermes, Codex, Claude, Antigravity, or zCode), never the model.
5. Commit and push the nested repository.
6. Prove the pushed commit is reachable from its configured upstream after a
   fetch, for example with `git merge-base --is-ancestor HEAD <upstream>` and
   matching/reachable remote evidence. A successful `git push` message alone is
   not sufficient if the upstream is ambiguous.

If the current repository is not a registered submodule, report success and stop.

## Hub Pointer Synchronization

Pointer synchronization is a second repository operation, never an implicit
extension of the nested commit.

### User gate

Before any hub staging or commit, obtain explicit approval unless the user
already opted into hub pointer synchronization for this run. The initial
stage/commit/push invocation authorizes the nested repository only; it does not
silently authorize a hub commit.

### Eligibility gates

Proceed only if all are true:

- the nested `HEAD` was proved pushed to its upstream;
- the hub still tracks the exact named path as mode `160000`;
- the hub worktree's submodule path resolves to the just-pushed nested repository;
- `git status --porcelain=v2 -z` and a direct nested status check prove the
  nested worktree has no lowercase-`m` uncommitted-content condition;
- in Particular mode, the user explicitly named or separately approved this
  submodule pointer;
- the hub has an `origin`, branch, and upstream;
- `git fetch origin` shows the hub remote is not ahead or diverged;
- the user approved any pre-existing unpushed hub commits;
- no unrelated path is already staged in the hub.

Lowercase `m` is not syncable. A hub records only a committed SHA, never nested
working-tree content. Leave `m` visible and stop; do not try to capture it.

### Pointer-only hub operation

1. Record the hub's staged-path list and full porcelain status.
2. Stage exactly one path:
   `git -C <hub> add -- <hub-relative-submodule-path>`.
3. Verify the staged diff contains exactly that one path and that its mode is
   `160000` before and after. Use `git diff --cached --name-only -z` and
   `git diff --cached --raw`.
4. Verify the staged new gitlink SHA equals the proved-pushed nested `HEAD`.
5. Commit separately with a scoped message such as
   `Bump <name> submodule pointer to <sha7>` and the executing-platform trailer.
6. Push the hub branch to its upstream.
7. Fetch and verify the remote hub now records the expected gitlink SHA.

Never use `git add -A` or `git add .` for pointer synchronization. Never stage a
second path. If another path appears staged, stop before commit and preserve user
state; do not reset it without approval.

## Failure and Recovery

- If the nested push fails, do not touch the hub.
- If pushed-commit proof fails, do not touch the hub.
- If a hub pre-flight or user gate fails, leave the successful nested push intact
  and report the pointer as not synchronized.
- If hub push fails after the pointer-only commit, report the local hub commit as
  unpushed; do not rewrite, amend, force-push, or hide it.
- Never pull, merge, rebase, reset, clean, skip hooks, or force-push as an
  improvised recovery.

## Reporting

Report the two repositories separately:

```text
Nested repository:
- Repo: <path>
- Scope: <all | named paths>
- Commit: <sha> — <subject>
- Pushed/proved at: <upstream>

Hub pointer synchronization:
- Status: <not applicable | declined | blocked | committed and pushed>
- Hub: <path>
- Pointer path: <path>
- Pointer commit: <sha or N/A>
- Verified remote gitlink: <sha or N/A>
```

## Validation

- Confirm the nested staged list matched scope and the commit carried the correct
  executing-platform trailer.
- Confirm the nested commit is reachable from the upstream before hub mutation.
- Confirm the hub commit, when made, changes exactly one `160000` gitlink.
- Confirm scoped mode never stages an unnamed pointer.
- Confirm lowercase `m` blocks pointer synchronization.
- Confirm remote-ahead, diverged, pre-existing-commit, and unrelated-staged-change
  gates were respected independently in both repositories.

When updating this skill, run the folder-style skill validator with Python UTF-8
mode and test two-repository behavior only in disposable repositories.