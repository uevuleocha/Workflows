---
name: global-sync
description: Propagate an existing local-master artifact (skills now; agents/sub-agents as a future stub mode) out to the configured global install locations (Codex, Claude, Antigravity, Hermes, zCode), validating every copy. Use when the user explicitly invokes /global-sync, use global-sync, "sync this skill globally", "sync all skills", "re-sync after an update", "push this skill to Codex/Claude/Antigravity/Hermes/zCode", or clear equivalents asking to propagate something that already exists locally — not to design or create a new one.
---

# Global Sync

Propagate an artifact that **already exists** in the local master out to the configured global install locations, then validate every copy. This is the single, repeatable sync workflow for the whole ecosystem: standalone when the user updates a skill by hand, and as the mandatory sync step called by `global-skills-creator` and `global-skills-creator-auto`.

This skill does not design or create artifacts. If the named artifact does not exist in the local master, stop and point the user to `global-skills-creator` (guided) or `global-skills-creator-auto` (autonomous) instead.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## UTF-8 Rule

Always use UTF-8 for every skill, workflow, markdown, YAML, and helper script copied or validated through this skill. When validating, run Python in UTF-8 mode with `-X utf8`. Preserve UTF-8 content across every target copy.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/global-sync`
- `use global-sync`
- `use the global-sync skill`
- `sync this skill globally`
- `sync all skills`
- `re-sync after an update`
- `push this skill to Codex, Claude, Antigravity, Hermes, and zCode`
- clear equivalents asking to propagate an existing local-master artifact to the global installs

## Modes

- **Mode A — Skills (fully built).** Propagate a folder-style skill (or all skills) from the local master `Skills/` folder to each global skills target.
- **Mode B — Agents / Sub-agents (stub, not implemented).** Reserved for propagating custom sub-agents once the user starts saving them. See the Mode B section.

Pick the mode from context. Default to Mode A unless the user clearly names an agent/sub-agent artifact.

## Default Path Stack (Mode A)

Resolve these before copying. On Uzo's machine the maintainer defaults are:

```text
Local master:
C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\Skills\<skill>\

Codex global:
C:\Users\Admin\.codex\skills\<skill>\

Claude global:
C:\Users\Admin\.claude\skills\<skill>\

Antigravity global:
C:\Users\Admin\.gemini\config\skills\<skill>\

Hermes global:
C:\Users\Admin\AppData\Local\hermes\skills\Personal\<skill>\

zCode global:
C:\Users\Admin\.zcode\skills\<skill>\
```

These are known-good defaults for Uzo's machine, not universal paths. On any other machine, resolve the user's own `~/.codex/skills/`, `~/.claude/skills/`, `~/.gemini/config/skills/`, Hermes app-data skills directory, and `~/.zcode/skills/`, and translate examples into the host OS path style. Never invent a path — if a target base directory is missing, stop and ask the user for the replacement path for that specific target.

## Hermes Specifics (Mode A)

Hermes groups skills by **category subfolder** (each folder becomes a category in the Hermes desktop app), unlike the flat Codex/Claude/Antigravity targets. Synced skills go under a `Personal/` category:

```text
C:\Users\Admin\AppData\Local\hermes\skills\Personal\<skill>\
```

`Personal` is the default grouping used in this skill and its README. An adopter who already has a `Personal/` folder, or who prefers a different category, can tell the agent to use another name — but `Personal` is a sensible default anyone can keep.

Ensure a category `DESCRIPTION.md` exists at `...\hermes\skills\Personal\DESCRIPTION.md`, matching Hermes' one-line frontmatter convention. If it is missing, create it:

```yaml
---
description: Personal reusable skills synced from the Workflows local master. Cross-agent workflow skills authored for use across Claude, Codex, Antigravity, and Hermes.
---
```

## Mode A Workflow

1. **Resolve scope.** A named skill, a comma-separated list of skills, or `all` (every folder under the local master `Skills/`).
2. **Confirm each named skill exists in the local master.** If a named skill is missing locally, stop and report it — this skill never creates artifacts.
3. **Validate the local master first.** Run `quick_validate.py` (UTF-8 mode) on each in-scope local master skill and read each result per `Reading the Validator's Result`. If any skill exits `1` with empty stderr, it is invalid: stop and report — never propagate a broken skill to the global targets. If any run exits `1` with non-empty stderr, or exits anything other than `0` or `1`, validation did not complete: stop, and copy nothing.
4. **Verify target base directories.** For each of Codex, Claude, Antigravity, Hermes, and zCode, confirm the global skills base directory exists. If one is missing, stop and ask for the replacement path for that target (do not guess).
5. **Copy per target.** For each in-scope skill × each target: create the destination skill folder if missing (Hermes → under `Personal/`; zCode → flat under `~/.zcode/skills/`), then true-copy with `Copy-Item -Recurse -Force` (not `Write` — a real copy preserves content faithfully) of `SKILL.md`, `README.md`, `agents/openai.yaml`, and any `scripts/`, `references/`, or `assets/` present.
6. **Ensure Hermes category file.** Confirm or create `...\hermes\skills\Personal\DESCRIPTION.md`.
7. **Validate every copy.** Run `quick_validate.py` (UTF-8 mode) against each synced copy at each target. Read each result from its exit code per `Reading the Validator's Result`.
8. **Verify byte parity.** For each in-scope skill × each target, run the recursive parity check from `Verifying a Sync` between the target copy and its resolved local master. **A target is synced only when its validation exits `0` AND its parity is clean.** Validation alone is not sufficient — do not proceed to Report on validation alone.
9. **Report.** A skill × target table carrying **both** the validation result and the parity result, plus any replacement paths used and any targets skipped (with the reason).

## Mode B — Agents / Sub-agents (STUB, not implemented)

Not built yet. Reserved for the day the user starts saving custom sub-agents and wants their propagation automated. What is already confirmed, to save future work:

- Claude Code custom sub-agents are **single Markdown files** with YAML frontmatter (`name`, `description`, `tools`, optionally `model`), living at `.claude/agents/<name>.md` (project-level, discovered by walking up to the repo root) or `~/.claude/agents/<name>.md` (user-global). This is a **single-file** shape, not a folder — so Mode A's folder-copy logic does not apply as-is.
- Codex, Antigravity, Hermes, and zCode sub-agent conventions are **not yet confirmed**. Codex's `AGENTS.md` is a single contract/wrapper file, **not** a registry of individually named sub-agents — do not assume equivalence.

**Before building Mode B:** confirm each platform's real sub-agent mechanism (if any), decide the target path stack for single-file agents, then mirror Mode A's shape — resolve path stack → validate local → copy → validate targets — adapted for single-file artifacts. Until then, if a user asks to sync an agent, explain that Mode B is a stub and stop.

## Reading the Validator's Result

**Decide pass/fail from the process exit code, capturing stdout and stderr separately. Never by comparing `quick_validate.py`'s stdout text.**

The validator terminates its output with a platform-specific line ending — on Windows, `Skill is valid!\r\n`. A string comparison against `"Skill is valid!"` fails on a perfectly valid skill because of the trailing `\r`. This has happened, across 30 copies at once.

| Exit  | stderr    | Meaning                     | Action                                     |
|-------|-----------|-----------------------------|--------------------------------------------|
| `0`   | —         | Skill is valid              | Proceed.                                   |
| `1`   | empty     | Skill is invalid            | stdout explains why. Fix the skill, rerun. |
| `1`   | non-empty | Validator / runtime failure | Stop. Validity is unknown. Do not "fix".   |
| other | —         | Validation did not complete | Stop. Claim neither pass nor fail.         |

Exit `1` is **overloaded**: an invalid skill and a crash inside the validator produce the same code. **Non-empty stderr is the discriminator.** An invalid skill writes its reason to stdout and leaves stderr empty; a crashed validator writes its traceback to stderr and leaves stdout empty.

**Never merge the streams.** `2>&1` destroys the discriminator. Do not test for an English traceback substring either — that breaks under a non-English locale, a different Python implementation, or a validator that catches its own exception.

Treat a crash as *unknown validity*, never as a failed skill — "fixing" a skill that was never broken is the worse error.

Anything other than exit `0` against a copied file means that copy is **not** synced. A validator that could not run is not a pass.

Use stdout only to tell the *user* what went wrong. Never to decide.

## Verifying a Sync

A copy is verified by exactly two format-independent checks. **Do not add a third.**

1. **The exit code** (per `Reading the Validator's Result`) — the copy is a valid skill.
2. **Recursive byte parity** between the target copy and its resolved local master — the copy is exactly the master.

### Running the parity check (choose the one that exists in your shell)

Resolve and confirm both absolute paths before comparing.

- **Real recursive `diff` available** (Git Bash, macOS, Linux):

  ```bash
  diff -r "<local-master>" "<target-copy>"
  ```

- **PowerShell / Windows** — `diff` there resolves to `Compare-Object`, which does **not** implement Unix `diff -r`, and `diff.exe` is often absent from PATH. Use Git's recursive comparison instead:

  ```powershell
  git diff --no-index --quiet -- "<local-master>" "<target-copy>"
  ```

**Exit meanings (both commands share this contract):**

| Exit  | Meaning                                    | Action                                        |
|-------|--------------------------------------------|-----------------------------------------------|
| `0`   | Byte-identical                             | Parity clean. Copy verified.                  |
| `1`   | Differences exist                          | Not synced. Re-copy and re-check.             |
| other | Comparison failed (tool missing, bad path) | **Parity unknown.** Stop; do not claim clean. |

Do not silently fall back to `Compare-Object`, a content grep, or a "looks fine" — a comparison that could not run is **not** a pass, exactly as a validator that could not run is not a pass.

**Parity is the proof. Byte-identical means identical — content, wording, rules, and all.** Once the parity check exits `0`, the target contains exactly what the master contains. There is nothing left to check inside the copy.

**Never grep a target copy to confirm a rule propagated.** If the master carries the rule and the copy is byte-identical to the master, the copy carries the rule. That is arithmetic, not evidence. A content grep on a verified copy can add no information — it can only produce a **false negative** when the search string trips over incidental text form (a trailing `\r`, a `:` in a path, `**bold**` inside a matched phrase). This has happened three times in this project; every time the sync was fine and the grep was broken.

**If you want to confirm a rule exists at all, grep the local master — once — not the copies.** The copies inherit it by parity.

### When a text match is genuinely unavoidable

- **Match a bare token, never a prose fragment.** `previous_max` is safe; `only when current-session evidence` is not — Markdown emphasis, line wrapping, or punctuation will break it.
- **Normalize before matching** if prose is unavoidable: strip `\r`, strip `*`/`_` emphasis markers, collapse whitespace. Then match.
- **Two Windows landmines, permanently:** never `2>&1` when a validator's stderr is the discriminator; never `awk -F:` on a path that begins with a drive letter (`C:`).

### A self-contradicting result halts

If two checks disagree — parity says identical while a grep says a rule is missing — **stop and treat the grep as broken until proven otherwise.** Parity is format-independent and cannot be fooled by text shape; an ad-hoc grep can. Do not "resolve" the contradiction by reasoning about which is right after the fact. The stronger check already answered; the weaker one manufactured the conflict. Delete the weaker check.

## Safety Rules

- **Additive / overwrite only.** Write new and changed files into each target. Never delete a skill from a global target just because it is absent from the local master — pruning is a separate, explicitly requested action, never done here.
- **Never invent a missing directory.** If a target base directory does not exist, stop and ask for the replacement path for that specific target.
- **Never claim success without validation.** Only report a target as synced after the copied files exist and `quick_validate.py` has **exited `0`** against them. A validator that could not run is not a pass, and a stdout string match is not a result.
- **True copy, not rewrite.** Use `Copy-Item -Recurse -Force`, not `Write`, so content is preserved faithfully.
- **Local-master-broken means stop.** A skill that fails local validation is never propagated.

## Validation

After a run, the two format-independent checks from `Verifying a Sync` are the whole verification:

- Confirm each in-scope local master skill exited `0` from `quick_validate.py` before any copy.
- Confirm each synced copy exists at each target, exited `0` from `quick_validate.py`, and is **byte-identical to its local master** via the recursive parity check in `Verifying a Sync` (`diff -r`, or `git diff --no-index --quiet` in PowerShell).
- Confirm the Hermes `Personal/DESCRIPTION.md` exists.
- Report the full skill × target × result table carrying **both** validation exit and parity exit, plus replacement paths used (or `none`), and any manual UI checks still needed.

**Do not add a content grep of the target copies to this validation.** Parity already proves the copies match the master. Any rule you might grep for is covered by the parity check; a grep can only add a false negative. If you want to confirm a rule was authored, grep the local master once — never the copies.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
