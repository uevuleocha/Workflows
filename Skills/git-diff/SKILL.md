---
name: git-diff
description: Read-only Git status and diff reporting with explicit rename-on/off totals, correct porcelain rename parsing, and an always-on submodule pointer table in submodule-bearing repositories.
---

# Git Diff

Report the complete state of a Git repository without changing its real index, working tree, commits, or remotes.

## Invocation

Begin for `/git-diff`, `git-diff`, `use git-diff`, `check git diff`, and clear equivalents asking for the current repository's overall diff and status.

## Safety Contract

- This workflow is read-only by default.
- Never run `git add`, `git commit`, `git restore`, `git clean`, or a mutating submodule command against the real repository.
- The temporary-index calculation must use a temporary file outside the real index and remove it on success or failure.
- If the user later explicitly asks to stage changes, leave this workflow and use the repository's approved staging workflow.
- A hub can record only a submodule's committed SHA. It cannot capture or push uncommitted nested-repository content.

## Execution Workflow

### 1. Resolve the repository

1. Run `git rev-parse --show-toplevel`; stop if it fails.
2. Record the repository name, branch, upstream, ahead/behind counts, staged, unstaged, and untracked paths.
3. Do not assume that the current directory is the repository root.

### 2. Collect file-level state

- Use NUL-delimited commands for machine parsing: `git status --porcelain=v1 -z`, `git diff --numstat -z`, and `git diff --cached --numstat -z`.
- Classify staged and unstaged columns independently.
- Preserve paths exactly; do not split on spaces, colons, or Windows drive letters.
- List untracked paths separately.

### 3. Parse rename and copy records correctly

For `git status --porcelain=v1 -z`, an `R` or `C` status consumes two path fields. After the status field's path, consume the following NUL-delimited field as the paired source/old path. Never reinterpret that old path as another status entry.

When deriving the after-file set:

- remove the source/old path;
- add the destination/new path;
- derive folder additions/deletions from the before and after file sets.

A rename within one directory must not create a bogus folder addition or deletion.

### 4. Calculate both Grand Total views safely

Use a temporary index for each view so untracked files are included without touching the user's staging area. Resolve the real index with `git rev-parse --git-path index`, create a unique sibling temporary path, set `GIT_INDEX_FILE` only for the child commands, run `git read-tree HEAD`, and stage into that temporary index only. Remove it in a guaranteed cleanup step.

Run and label both totals deliberately:

1. `renames OFF (moves = delete + add)` using `git -c diff.renames=false diff --cached --shortstat`.
2. `renames ON (moves detected)` using `git -c diff.renames=true diff --cached --shortstat`.

Both lines always appear. Follow them with one sentence explaining that a gap normally represents moves/renames and is expected; if equal, say there was no rename gap.

### 5. Calculate TOTALS

- `before` is the file set from `git ls-tree -r --name-only -z HEAD`.
- Derive `after` from the correctly parsed porcelain records.
- `Folders` is the added/deleted parent-directory set count.
- `Files` is the added/deleted file-set count.
- `Lines` sums staged and unstaged numstat plus line counts for untracked regular files. Report binary entries separately; never coerce `-` to zero silently.
- TOTALS uses rename-aware semantics. Do not call a rename's old path a new file.

### 6. Always inspect submodule pointers

Detect submodules from tracked mode `160000` entries and use `.gitmodules` for path/name metadata when present. If either source suggests submodules, reconcile the inventory and report inconsistencies.

For every tracked submodule, collect without mutation:

- pinned SHA: parent `HEAD` gitlink (`git ls-tree HEAD -- <path>`);
- local HEAD: `git -C <path> rev-parse HEAD` when initialized;
- marker from `git status --porcelain=v2 -z` submodule state (`S<c><m><u>`) plus pinned/local SHA comparison;
- state: `in sync`, `pointer behind`, `dirty content`, `both`, `uninitialized`, or `missing/inconsistent metadata`.

Marker meanings:

- `M` = local submodule commit differs from the parent's pinned SHA (`S.C..` or direct SHA mismatch evidence);
- `m` = tracked or untracked working-tree content exists inside the submodule (`S..M.` / `S...U` evidence);
- `Mm`/combined evidence = both conditions;
- `–` = clean and pinned/local SHAs match.

Render the Pointers table on every run in a submodule-bearing repository, even when every row is clean. Cross-reference the host workspace's terminology for `M` versus `m` and `HEAD` when one exists. From inside a nested repository, do not claim to know an ancestor hub's pinned SHA unless the user explicitly names and authorizes inspection of that hub.

## Canonical Report Shape

Every agent must emit sections in this exact order. Omit an empty file section; never omit `Submodule Pointers` when the repository has submodules. All Markdown tables must be pipe-aligned in raw text and every cell must be at most 80 characters.

```markdown
Here's your `/git-diff` for **<Repo Name>**. <one-line characterization>

**Branch:** `<branch>` — <up to date | ahead N | behind N | diverged>.

### Staged
| File     | Change |
|----------|--------|
| `<path>` | <kind> |

### Modified (unstaged, tracked)
| File     | Stat   |
|----------|--------|
| `<path>` | +A/−D  |

### Untracked (new additions)
- `<path>`

### Submodule Pointers — <all N in sync, zero drift ✅ | N with drift ⚠️>
| Submodule | Marker | Pinned | Local HEAD | State |
|-----------|--------|--------|------------|-------|
| `<path>`  | –/M/m  | <sha7> | <sha7>     | ...   |

### Grand Total (temp index, includes untracked)
renames OFF (moves = delete + add): <N> files changed, +A -D
renames ON  (moves detected):       <N> files changed, +A -D
<rename-gap explanation>

### TOTALS
=== TOTALS ===
Folders   +A   -D
Files     +A   -D
Lines     +X   -Y

Nothing staged or committed — this was read-only.
```

## Verification

- Confirm the real index checksum and `git status --porcelain=v1 -z` output are unchanged before and after the run.
- Verify both rename modes were explicitly pinned and labelled.
- On rename fixtures, confirm each `R`/`C` consumes its paired old path and a same-directory rename reports `Folders +0 -0`.
- On submodule fixtures, verify clean, pointer-drift, dirty-content, combined, and uninitialized states where available.
- Confirm the Pointers table appears for clean submodule-bearing repositories.

When updating this skill, run the folder-style skill validator with Python UTF-8 mode and validate behavior only in disposable repositories.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;
