---
name: new-workspace
description: Bootstrap a fresh or nearly empty workspace as its own local Git repository with generic contract files, base Archive and tmp folders, an empty .gitignore, and a first commit. Use for /new-workspace, use new-workspace, set up a new workspace from scratch, or clear equivalents requesting this lightweight bootstrap. Does not trigger on bare initialize; use workspace-setup for established-workspace parity.
---

# New Workspace

Create the minimum usable workspace from frozen bundled templates. This is the lightweight Option A bootstrap; `workspace-setup` owns full universal-standards parity, platform settings, standards clones, and wiki setup. `/initialize` owns chat-session intake and is unrelated.

## Project Contract And Scope

Obey the active project contract and runtime permissions. Writes stay inside the confirmed target. Never edit the hub, its ignore rules, index, submodules, or commits. Hub coverage is intentionally left to the next hub session's coverage scan. Never overwrite or delete an existing target file, add a remote, or push. Never create `.gitkeep`, platform settings, a wiki, or a standards clone.

## Resolve And Confirm Identity

Use the current working directory unless the user names another existing folder. Resolve its absolute path and inspect its actual entries. Do not create a missing target or guess a replacement. Infer identity from its path: Uzzys Universe is Tier 0, Galaxy Tier 1, Solar System Tier 2, World Tier 3, and Continent Tier 4. Do not invent deeper tier terms; ask when unknown. A World workspace has no parent World. Outside that hierarchy, ask for the appropriate identity rather than fabricating ancestry.

Before any bootstrap mutation, present one pre-filled block the user may approve whole or correct line by line:

```text
Target = <absolute existing directory>
Workspace name = <name>
Tier number / term = <number> / <World, Continent, or confirmed term>
Parent World = <name or None for a World>
Solar System = <name>
One-line purpose = <proposed sentence>
Settings references = root .codex/ plus .agents/ for Antigravity, Hermes, zCode
First commit = Yes (unless you ask to skip)
```

Explain that settings paths are conditional references only; this bootstrap creates no settings. Wait for explicit identity approval, unless the user already supplied and approved these exact values. Surface any requested template-path variation before writing; do not silently restore the retired root platform layout.

## Pre-flight

1. Enumerate target entries, including hidden ones. Record every existing required item as skipped. Preserve an existing `.gitignore` byte-for-byte, even when nonempty.
2. If either `CLAUDE.md` or `AGENTS.md` contains non-whitespace text, treat the workspace as established: stop without changes and recommend `workspace-setup`. An existing README alone or empty contract stub is partial setup: skip it and continue with missing items. Never claim preserved empty stubs are fully populated contracts.
3. Reject file/directory type collisions, symlinks or junctions in managed paths, redirected Git metadata, and targets that resolve through links. A `.git` file is an existing repository marker, never permission to reinitialize it; stop if its external metadata would violate target-only writes.
4. Run the helper's read-only preview with the confirmed identity. It validates templates and repository isolation before changing anything. If an existing repository has staged changes, an operation in progress, external metadata, or cannot be verified as rooted at the target, stop. Do not reset, unstage, or repair it.
5. Confirm Git and the user's commit identity are available. Missing identity is a blocker for the default commit; ask the user to configure it or explicitly choose no commit. Never change global Git configuration.

## Bootstrap

Use Python 3.10+ and Git. Locate `scripts/bootstrap.py` relative to this installed skill, never relative to the target. Pass arguments as separate values without shell interpolation. First run without `--apply`; after identity approval run the same arguments with `--apply --confirmed`.

```text
python -X utf8 <skill>/scripts/bootstrap.py --target <path> --name <name> --tier World --solar-system <name> --purpose <sentence>
```

For Continent or deeper, also pass `--world <parent-world>`. The agent confirms the numerical tier in the identity block; the helper uses the approved term, not a guessed path depth. Pass `--no-commit` only on explicit user instruction. For a requested nonempty new ignore file, pass `--gitignore-content <exact-approved-text>`; otherwise it is zero bytes. An existing ignore file is always preserved.

The helper performs these ordered operations:

1. Initialize `git init -b main` only if no target `.git` exists; otherwise skip initialization and preserve the existing branch and history. Verify Git's top level and metadata remain in the target before any staging or commit.
2. Create missing `AGENTS.md`, `CLAUDE.md`, and `README.md` using bundled templates, exclusive file creation, and UTF-8.
3. Create only missing `tmp/`, `Archive/`, `Archive/Live/`, and `Archive/Historical/` directories. Existing Archive/tmp roots are skipped; missing child folders may still be created.
4. Create missing `.gitignore`, empty by default.
5. Stage and commit only the root files created by this run. Never stage all files. Disable hooks and signing for this bootstrap commit so repository automation cannot write outside the target. On an existing repository, this is an additional commit only when files were created; never rewrite history or force `main`. Empty folders are intentionally untracked.
6. Print a JSON receipt of created/skipped entries, branch, commit, and remaining context, then the exact closing reminder below.

On failure, report the error and any created items. Do not delete or roll back automatically. Re-inspect before retrying: a partial failed run may now contain real contracts and require `workspace-setup`. The helper is intended for a single editor; stop if another process may be editing the target.

## Frozen Templates

Use only `assets/AGENTS.md`, `assets/CLAUDE.md`, and `assets/README.md` at runtime. Never read Chess or the hub to generate a workspace. The frozen sources were adapted from Chess on 2026-10-17; the glossary and complete Communication & Footers section were copied verbatim from the hub that day. Future standards refreshes are explicit skill-maintenance work.

Placeholders: `{Workspace Name}`, `{tier term}`, `{Tier Term}`, `{World}`, `{Solar System}`, `{one-line purpose}`, `{workspace path}`, `{layout-sync timestamp}`, and `{parent-world clause}`. The renderer derives the parent clause: empty for World; otherwise ` under the **<World>** world`. It rejects braces and multiline identity values and fails before writes if any placeholder remains. Layout timestamps come from the runtime clock. Store paragraphs as continuous lines.

## Report

Report every created and skipped item, the actual repository root, current branch, and commit result or explicit no-commit choice. Verify all seven top-level entries (`.git`, `.gitignore`, three contract files, `Archive`, `tmp`) and both Archive children. Distinguish a successful fresh bootstrap from preserved partial files requiring later attention. Never assert Claude sidebar grouping is verified by Git checks alone.

End the task report with this reminder, before any required Glossary/Mode footers:

> This is a lightweight bootstrap. When you want full universal-standards parity for this workspace, run `workspace-setup`.

## Governance Classification

This skill is exempt from exact-model attribution and durable-artifact provenance injection: it creates operational workspace contracts, a root README marker, Git metadata, and empty directories, not an Archive artifact or model-attributed document. Do not add provenance tables to those operational templates. It writes no Markdown tables; table-authoring and deterministic-aligner dependencies are therefore exempt. If its outputs later expand into durable artifacts or tables, reclassify it through the creator workflow before adding those outputs.

## Validation

- Run the official `quick_validate.py` on this skill with `python -X utf8`; judge its exit code, keeping stdout and stderr separate.
- Run `python -X utf8 <skill>/scripts/test_bootstrap.py --scratch <new-directory-under-workspace-tmp>`. The suite retains its fixtures for review and refuses an existing scratch directory.
- Verify fresh World and Continent cases: required entries, empty ignore, no placeholders, exact repo root, one commit on main, only the four generated root files committed, no remote, and closing reminder.
- Verify partial files remain byte-identical, established workspaces stop without mutation, staged changes are preserved, wrong types/redirects are refused, explicit no-commit works, and missing identity is reported before writes.
- Compare bundled glossary and footer sections byte-for-byte with the approved frozen source during authoring; verify natural wrapping, settings paths, no Chess-specific content, and the seven-item layout.
- Confirm `/initialize` remains excluded and `workspace-setup` remains the follow-up. Recheck the exemption classification if outputs change.
- Inspect hub status before and after controlled tests; no change may be caused by this skill. Retain evidence in the invoking task's existing feedback artifact when requested, not as an extra runtime output.
- Test-folder removal requires explicit user approval and verified absolute paths inside the scratch root. Real Claude sidebar grouping and later hub coverage require subsequent user-observed use.
