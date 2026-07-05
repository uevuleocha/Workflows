---
name: stage-commit-push
description: Deterministic stage, commit, and push workflow for the current Git repo. Say "all" to stage everything currently diffed, or name specific files/paths to scope it to just those. Use when the user explicitly invokes /stage-commit-push, use stage-commit-push, "stage commit push", "stage, commit, and push", or clear equivalents asking for a repeatable push workflow, as opposed to the read-only /git-diff check.
---

# Stage Commit Push

A single, reliable workflow for staging, committing, and pushing changes to a Git remote, so the same steps happen the same way every time regardless of which agent runs it.

This skill mutates the user's real Git staging area, creates a commit, and pushes to a remote. It pairs well with `/git-diff` for a prior read-only look, but does not require it.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/stage-commit-push`
- `use stage-commit-push`
- `use the stage-commit-push skill`
- `stage commit push`
- `stage, commit, and push`
- clear equivalents asking for a repeatable stage/commit/push workflow

This skill only ever runs on explicit invocation — never trigger it implicitly from a general "push this" remark without the user naming the skill or clearly asking for the full stage+commit+push sequence.

## Scope Modes

1. **All.** The user says `all`, `everything`, or `push everything`. Stage every current tracked change, modification, and untracked file: `git add -A`.
2. **Particular.** The user names specific file(s), path(s), or folder(s). Stage only those, pathspec-scoped: `git add -A -- <path1> <path2> ...`, so nothing else — including anything another agent or process may have pre-staged — rides along.

If the request is ambiguous (neither a clear "all" nor a clear list of paths), ask once before staging anything.

## Repo Determination (mandatory)

This workspace can sit inside a nested hub/workspace repo structure (a hub tracks only final-tier workspace READMEs; each workspace is its own independent repo). Because of that:

1. Resolve the actual repo root via `git rev-parse --show-toplevel` for the current directory (or the directory the user names).
2. State which repo you are operating in before staging, committing, or pushing.
3. If the user's intent spans two repos (for example, a shared README that must be committed in both the workspace repo and the hub repo), treat each repo as its own separate run and say so explicitly. Never mix changes from two repos into one commit.

## Pre-Flight Checks (mandatory, before staging)

1. `git fetch origin`.
2. If `origin/<branch>` is ahead of or diverged from local `<branch>`, hard-stop: report the remote commits, stage/commit/push nothing, and let the user decide how to update local `<branch>` first.
3. Check for pre-existing unpushed local commits: `git log origin/<branch>..<branch>`. A push delivers the whole chain, so if any exist, list their hashes and messages and get explicit user approval before proceeding — this run's push would ship them too.

## Commit Message And Signing

Draft a concise commit message from the actual staged diff — imperative mood, why over what, 1-2 sentences — following the same drafting discipline used for any other commit in this workspace.

Append a signing trailer identifying the agent that ran this skill, matching the convention already used by `push-tool`:

```text
Agent: <AgentName>
```

`<AgentName>` is the agent actually executing the run (e.g. `Claude`, `Codex`, `Antigravity`) — not a hard-coded value.

## Workflow

1. Determine scope (All vs Particular) from the user's request; ask once if ambiguous.
2. Resolve and state the repo (Repo Determination).
3. Run pre-flight checks (fetch, diverge hard-stop, pre-existing-commits gate).
4. Stage per the scope rules above.
5. Draft the commit message and append the `Agent: <AgentName>` trailer.
6. Commit, using a heredoc-style message to preserve formatting.
7. Push to `origin <branch>`.
8. Report: repo, scope (files staged), commit hash and message, agent, and push confirmation.

This skill runs end-to-end once scope is given — invoking it with a clear scope ("all" or named paths) is itself the user's approval to commit and push; there is no extra confirmation round-trip before step 6, mirroring `push-tool`'s one-shot execution style. The only stops are the pre-flight hard-stop and pre-existing-commits gate in step 3.

## Safety Rules

- Never `git add -A` or `git add .` in Particular mode — always pathspec-scoped to the named files/paths.
- Never force-push, rewrite git history, or skip hooks.
- Never push when the remote is ahead of or diverged from local — hard-stop only, no improvised pull/rebase/merge.
- Never push pre-existing unpushed commits without the user's explicit approval at pre-flight.
- Never commit changes from two repos into one commit.
- Always state which repo is being operated on before any mutating command.

## Out Of Scope

- Resolving merge conflicts — stop and ask the user.
- Creating branches, pull requests, or tags.
- Any destructive Git operation (reset --hard, force-push, history rewrite).

## Reporting Format

```text
Staged, committed, and pushed in <repo>.
- Scope: <all | specific paths listed>
- Commit: <short hash> - "<message>"
- Agent: <AgentName>
- Pushed to: origin/<branch>
```

Remote-ahead hard-stop: report the remote commits found at pre-flight, state that nothing was staged, committed, or pushed, and stop — the user decides how to update local first.

## Validation

After a run:

- Confirm the repo root matches intent.
- Confirm the staged file list matches the requested scope (all vs named paths).
- Confirm the commit was created with the drafted message and `Agent: <AgentName>` trailer.
- Confirm the push succeeded and report the new remote hash.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
