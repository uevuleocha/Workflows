---
name: git-diff
description: When invoked via /git-diff or git-diff, checks if the workspace is a Git repository. If it is, the agent runs git status, git diff --stat, and a temporary-index diff to collate and report tracked changes, untracked files, overall repository status, and a Grand Total diff count.
---

# Git Diff Skill

This skill provides a comprehensive overview of the current Git workspace state, including tracked changes, untracked files, and a safe Grand Total diff count using a temporary index.

## Invocation

Treat these as direct invocation and begin the workflow:
- `/git-diff`
- `git-diff`
- `use git-diff`
- `what is the git diff status`
- `check git diff`
- clear equivalents where the user asks for the overall git diff and status of the current workspace.

## Execution Workflow

1. **Verify Target:** Check if the current workspace (or the one the user explicitly refers to) contains a `.git` directory. If it doesn't, inform the user that it is not a Git repository.
2. **Collate Status:** Execute `git status` to determine the current branch, up-to-date status, untracked files, and staged/unstaged tracked changes.
3. **Collate Tracked Diff Stats:**
   - Execute `git diff --stat` to get a summary of insertions and deletions for unstaged tracked changes.
   - If there are staged changes, execute `git diff --cached --stat` to capture those stats as well.
4. **Calculate Grand Total (Safe Temporary Index):**
   - Run the following PowerShell command exactly as written to safely calculate the grand total of all changes (including untracked files) without altering the user's actual staging area:
     `$env:GIT_INDEX_FILE = '.git/tmp_index'; git read-tree HEAD; git add .; git diff --cached --shortstat; Remove-Item .git/tmp_index; Remove-Item env:GIT_INDEX_FILE`
5. **Calculate TOTALS:**
   - Derive the three-level TOTALS using this Python-reference approach (run with `-X utf8`):
     - `before` = file set from `git ls-tree -r --name-only HEAD`
     - Parse `git status --porcelain`: `D` entries → deleted files (drop from after-set); `A` and `??` entries → added files (add to after-set)
     - Derive dir sets from all parent dirs of each file path; `added_dirs` = after-set dirs − before-set dirs; `deleted_dirs` = before-set dirs − after-set dirs
     - Lines: sum `git diff --numstat` + `git diff --cached --numstat` for staged/unstaged; add `wc -l` of each `??` untracked file as additions
6. **Compile the Report:** Formulate a clear chat response that includes:
   - Branch status
   - A list of modified tracked files with their diff stats.
   - A clear list of untracked files (explicitly called out as untracked additions).
   - The Grand Total diff count obtained from the temporary index step.
   - The always-on TOTALS block at the end:
     ```
     === TOTALS ===
     Folders   +A   -D
     Files     +A   -D
     Lines     +X   -Y
     ```
7. **Report to User:** Output the compiled report directly in the chat. Do not create any durable artifact files unless explicitly asked.

## Diligence Rule

Do not execute a permanent `git commit`, `git add .`, `git restore`, or `git clean` on the user's real staging area without explicit user permission. This skill is strictly for read-only status and diff reporting by default.

**Exception:** If the user reviews the `/git-diff` report and explicitly says something like "looks great, add them all" or "go ahead and stage everything," you are authorized to run `git add .` normally to officially pull the untracked and modified files into the staging area.
