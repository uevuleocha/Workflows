# Agent Instructions — Uzzy Skills

This workspace is the **home for Uzo's skills**. It holds the **local master copies** of reusable skills — created from scratch, adapted from others' work, or brought in for personal workflows. Skill work *starts here*, then syncs outward to the global agent installs (Codex, Claude, Antigravity). This repo may become public one day, so treat everything here as potentially world-readable.

This workspace runs on a simple model: **Workflows** (markdown SOPs + skills) say what to do, you're the **Agent** deciding how, and **Tools** (skills + built-ins) do the executing.

## Core Conventions

- **Files inside folders start with `x.)`** — this is a **hard rule with a fixed set of exceptions**, not a suggestion. Every file saved into a workspace folder gets a sequential index (`1.) `, `2.) `…; `0.)` allowed for a preamble). **The only exceptions:** structural/special files (`CLAUDE.md`, `AGENTS.md`, `README.md`, `SKILL.md`, dotfiles, config); files a skill or script generates under its own naming scheme; and any case where the user explicitly says not to use the numbering convention. Outside those exceptions, always apply it — if unsure whether something qualifies, apply the prefix.
- **`tmp/` is strictly temporary.** Throwaway files only, deletable at any time when the user says so. Never store anything durable there.
- **UTF-8 for everything** — skill, markdown, YAML, and helper-script text. Never rely on the Windows default encoding. Validate folder-style skills with Python in UTF-8 mode (`-X utf8`).
- **All Markdown tables must be pipe-aligned — no exceptions.** Before writing any table in any artifact, cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Then compute each column's maximum cell width (now always ≤80 characters) across the header, separator, and every row, and pad every cell to that width so the `|` characters stack vertically in raw text. This applies to every table an agent writes, not only Estimated Effort tables.

## Skills Workflow (the core job of this workspace)

- **Local master first.** All skill creation/edits begin in `skills/<name>/`. Finish and let the user verify the local master **before** any global sync. Global sync runs only when the user explicitly asks — never in the same pass as the local edit. The one exception is `global-skills-creator-auto`, which is designed to create-and-sync in a single pass.
- **Folder-style skills mirror structure** — each keeps `SKILL.md` + `agents/openai.yaml` across the local master and every global copy.
- **Sync targets (path stack):**
  - Local master: `skills/<name>/`
  - Codex: `C:\Users\Admin\.codex\skills\<name>\`
  - Claude: `C:\Users\Admin\.claude\skills\<name>\`
  - Antigravity: `C:\Users\Admin\.gemini\config\skills\<name>\`
- **Never invent a path.** If a target directory is missing, stop and ask — don't guess.
- Prefer an existing skill over improvising. `global-skills-creator` (guided) and `global-skills-creator-auto` (autonomous) own skill creation and cross-agent sync.

## Public-Repo Safety Guard

This repo is intended to go public eventually. Before any push — and **always** before the user makes the repo public — verify nothing private is tracked:

- Confirm `.gitignore` excludes `.env`, `.claude/`, `.codex/`, `.antigravity/`, `.agents/`, `Archive/`, and `tmp/`.
- If the user says they're about to make this public (or add a remote), **warn first**, then check `git status`/`git ls-files` for secrets, tokens, machine-specific paths, or local settings before proceeding. Flag anything questionable and wait for confirmation.

## Safety & Precedence

- **Destructive ops need explicit approval** — no force-push, hard reset, branch merge, `rm -rf`, or deleting files the user didn't ask you to, without a clear "do it."
- **Ask when ambiguous.** On coin-flip cases, ask rather than guess.
- **Precedence:** most recent direct user instruction → `CLAUDE.md` → `AGENTS.md` wrapper.

## Definition of Done (applies to every prompt)

Before acting, define what "done" looks like — either the user's explicit criteria or a sensible inferred one — and hold it while you work, looping OBSERVE → THINK → ACT until it's met. DoD applies to *every* request, not just formal tasks or plans. If you genuinely can't infer it (the ask is ambiguous or a coin-flip), **ask before acting** rather than guessing. You don't need to recite the DoD aloud unless the user asks — but state it plainly when it helps remove ambiguity between us.

## Communication & Mode Footer

Keep explanations tight; use a short analogy only when it genuinely clarifies. End each reply with a Mode footer: `Mode = N/A` when no mode is active, `Mode = <Name>` for one, or `Modes = A + B` for several (Brainstorm, Debug, LTNEY, Initialize, etc.).

## Workspace Layout

> **Layout sync status:** `current` · last verified 2026-07-05
>
> Keep this tree honest. If the real workspace and this tree disagree — a new folder/file that isn't shown here, or an entry here that no longer exists — **prompt the user before continuing substantive work**. The user may: (a) add the entry to the tree, (b) prune or replace something to keep it lean, or (c) decline the change. In every case, once the user has reviewed, reset the status line to `current` with today's date so the next agent doesn't re-raise it. Prefer a lean schema over an exhaustive one — prompt to prune before the tree sprawls; the goal is a map, not an inventory.

```
C:\Users\Admin\Uzzys Universe\Galaxies\Tools\Uzzy Skills\
├── .claude/                     ← Claude Code workspace config (settings.local.json, … etc)
├── .codex/                      ← Codex workspace config (settings.local.json)
├── .antigravity/                ← Antigravity workspace config (settings.local.json)
├── .agents/                     ← Machine-local agent state (gitignored; never pushed)
├── AGENTS.md                    ← Agent wrapper (Codex/Antigravity) → points to CLAUDE.md
├── CLAUDE.md                    ← This file. Canonical workspace contract.
├── README.md                    ← Human-facing overview of the skills home
├── Documentation/               ← Supporting notes and workspace documentation
├── skills/                      ← Local master copies of reusable skills
│   └── <skill-name>/
│       ├── SKILL.md             ← The skill's procedure + frontmatter
│       └── agents/openai.yaml   ← Codex UI metadata (mirrored across all copies)
├── Archive/                     ← Durable artifacts (gitignored; not pushed)
│   ├── Summaries/               ← Session summaries (owned by session-summary)
│   └── Tasks/                   ← Pending/done housekeeping tasks (owned by imp-upd-task)
└── tmp/                         ← Strictly temporary scratch; safe to delete anytime
```
