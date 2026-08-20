---
name: github-sync
description: Autonomously run git-diff and then stage-commit-push in one continuous pass using a user-supplied All or Particular scope, preserving both skills' safety gates and automatic hub-pointer synchronization. Use for /github-sync all, /github-sync particular with named paths, use github-sync, GitHub sync all, GitHub sync particular, and clear equivalents asking to inspect, stage, commit, and push the current repository end to end.
---

# GitHub Sync

Inspect the current repository, then stage, commit, push, and when applicable synchronize its parent hub pointer in one continuous safe workflow.

## Project Contract

Obey the active workspace contract and runtime permission model. This skill coordinates `git-diff` and `stage-commit-push`; it never weakens or replaces either dependency's safety rules.

## Invocation

Begin for:

- `/github-sync all`
- `/github-sync particular <path>...`
- `use github-sync all`
- `GitHub sync all`
- `GitHub sync particular <path>...`
- clear equivalents that explicitly request the complete inspect, stage, commit, and push workflow

A direct invocation with an unambiguous scope authorizes the ordinary safe workflow end to end. Do not insert a preview, approval, or handoff pause between the two child skills. Report non-blocking observations after execution.

## Required Input

The invocation must supply exactly one staging scope:

1. **All:** pass `All` to `stage-commit-push`.
2. **Particular:** pass the exact user-named paths to `stage-commit-push` without widening or rewriting them.

If the scope is missing or genuinely ambiguous, ask for it before mutation. This is a required user-owned input, not a routine approval gate. Preserve an explicit `no hub sync`, `nested only`, or equivalent opt-out and pass it through unchanged.

## Dependency Gate

Both `git-diff` and `stage-commit-push` must be installed and available. If either is unavailable, stop before mutation, name the missing dependency, and point to its install route. Never improvise a partial replacement for either workflow.

## Continuous Workflow

1. Resolve the current repository through `git-diff` and run its complete read-only workflow.
2. Preserve its canonical report as the pre-mutation evidence packet. Do not treat ordinary dirty-state findings as a reason to ask whether to continue; the requested staging scope already supplies that decision.
3. Immediately invoke `stage-commit-push` with the exact All or Particular scope and any explicit hub-sync opt-out from the original invocation.
4. Let `stage-commit-push` draft the commit message, commit, push, prove the remote result, and automatically perform eligible pointer-only hub synchronization.
5. Stop only when a dependency identifies one of its genuine safety conditions or when a required input is missing. Never bypass remote-ahead/diverged, pre-existing-unpushed-commit, unrelated-staged-state, dirty nested-content, missing remote/upstream, destructive-recovery, or secret-safety gates.
6. After success or a required stop, report both the pre-mutation diff result and the complete `stage-commit-push` outcome, including the loud hub-pointer status.

## Failure And Recovery

- If `git-diff` cannot resolve a repository or cannot complete its read-only evidence collection, do not invoke `stage-commit-push`.
- If `stage-commit-push` stops before mutation, report its exact required input or safety condition together with the completed diff evidence.
- If the nested push succeeds but hub synchronization is blocked, preserve that successful push and report the pointer status exactly as `stage-commit-push` requires.
- Never improvise pull, merge, rebase, reset, clean, hook bypass, force-push, remote replacement, or credential handling.

## Reporting

Lead with one of these outcomes:

- `GitHub sync completed.`
- `GitHub sync stopped safely before mutation.`
- `Nested push completed; hub pointer synchronization was blocked.`

Then include:

- requested scope and repository;
- the canonical `git-diff` result;
- nested/current repository commit and pushed-proof result;
- hub pointer synchronization status, hub path, pointer path, commit, and verified remote gitlink; and
- any genuine stop condition or non-blocking follow-up.

Do not ask a post-execution approval question merely because a recommendation or optional improvement exists.

## Markdown Table Alignment

Every Markdown table this skill writes - including the delegated canonical `git-diff` report - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

The child `git-diff` workflow owns the delegated table content; this chat-only orchestrator preserves that validated output and does not create a file-based Markdown table.

## Validation

- Run the official folder-style skill validator with Python UTF-8 mode.
- Run `python -B -X utf8 scripts/test_github_sync_contract.py`.
- Confirm All and Particular scopes are passed through exactly.
- Confirm missing scope stops before mutation.
- Confirm `git-diff` always precedes `stage-commit-push` with no routine approval pause.
- Confirm both dependencies' genuine safety gates remain authoritative.
- Confirm automatic eligible hub-pointer synchronization remains ON unless the user explicitly opts out.
- Confirm the `## Markdown Table Alignment` section remains present and delegated tables preserve the child workflow's aligned canonical output.

Test Git mutation behavior only through the disposable suites shipped by `git-diff` and `stage-commit-push`.
