# Agent Instructions — Workflows

This workspace is the **home for Uzo's skills**. It holds the **local master copies** of reusable skills — created from scratch, adapted from others' work, or brought in for personal workflows. Skill work *starts here*, then syncs outward to the global agent installs (Codex, Claude, Antigravity, Hermes, zCode). This repo may become public one day, so treat everything here as potentially world-readable.

This workspace runs on a simple model: **Workflows** (markdown SOPs + skills) say what to do, you're the **Agent** deciding how, and **Tools** (skills + built-ins) do the executing.

For LLM wiki setup, sync, query, or lint work, read and obey `wiki/wiki-schema.md`.

## Core Conventions

- **Files inside folders start with `x.)`** — this is a **hard rule with a fixed set of exceptions**, not a suggestion. Every file saved into a workspace folder gets a sequential index (`1.) `, `2.) `…; `0.)` allowed for a preamble). **The only exceptions:** structural/special files (`CLAUDE.md`, `AGENTS.md`, `README.md`, `SKILL.md`, dotfiles, config); files a skill or script generates under its own naming scheme; and any case where the user explicitly says not to use the numbering convention. Outside those exceptions, always apply it — if unsure whether something qualifies, apply the prefix.
- **`tmp/` is strictly temporary.** Throwaway files only, deletable at any time when the user says so. Never store anything durable there.
- **UTF-8 for everything** — skill, markdown, YAML, and helper-script text. Never rely on the Windows default encoding. Validate folder-style skills with Python in UTF-8 mode (`-X utf8`).
- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables.

## Skills Workflow (the core job of this workspace)

- **Local master first.** All skill creation/edits begin in `skills/<name>/`. Finish and let the user verify the local master **before** any global sync. Global sync runs only when the user explicitly asks — never in the same pass as the local edit. The exceptions are `global-skills-creator` and `global-skills-creator-auto`, which are designed to create-and-sync after their own approval flow.
- **Folder-style skills mirror structure** — each keeps `SKILL.md` + `README.md` (a compulsory, very brief what-it-does note, with related-skill pointers when the skill calls or pairs with others) + `agents/openai.yaml` across the local master and every global copy.
- **Sync targets (path stack):**
  - Local master: `skills/<name>/`
  - Codex: `C:\Users\Admin\.codex\skills\<name>\`
  - Claude: `C:\Users\Admin\.claude\skills\<name>\`
  - Antigravity: `C:\Users\Admin\.gemini\config\skills\<name>\`
  - Hermes: `C:\Users\Admin\AppData\Local\hermes\skills\Personal\<name>\`
  - zCode: `C:\Users\Admin\.zcode\skills\<name>\`
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

Keep explanations tight; use a short analogy only when it genuinely clarifies.

End every response with a Mode footer:

- If no mode is active → `Mode = N/A`
- If one mode is active → `Mode = <Mode Name>`
- If multiple modes are active → `Modes = Mode A + Mode B + ... + Mode Z` (include every active mode exactly once)

Skills that emit the Mode footer while active (open-ended list — grows as new mode-aware skills are added):

- **Brainstorm** — persists until exited
- **Debug** — persists until exited
- **Initialize** — one-time only (footer appears on the single initialization response, not subsequent responses)
- **LTNEY** — persists until exited

When needed, check individual skill files for how the mode should be named in the footer.

## Workspace Layout

> **Layout sync status:** `current` · last verified 2026-07-16 (wiki/ added as the schema-driven, gitignored Workflows knowledge map; Archive tier differences user-accepted)
>
> Keep this tree honest. If the real workspace and this tree disagree — a new folder/file that isn't shown here, or an entry here that no longer exists — **prompt the user before continuing substantive work**. The user may: (a) add the entry to the tree, (b) prune or replace something to keep it lean, or (c) decline the change. In every case, once the user has reviewed, reset the status line to `current` with today's date so the next agent doesn't re-raise it. Prefer a lean schema over an exhaustive one — prompt to prune before the tree sprawls; the goal is a map, not an inventory.

```
C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\
├── .claude/                     ← Claude Code workspace config (settings.local.json, … etc)
├── .codex/                      ← Codex workspace config (settings.local.json)
├── .antigravity/                ← Antigravity workspace config (settings.local.json)
├── .agents/                     ← Machine-local agent state (gitignored; never pushed)
├── AGENTS.md                    ← Agent wrapper (Codex/Antigravity) → points to CLAUDE.md
├── CLAUDE.md                    ← This file. Canonical workspace contract.
├── README.md                    ← Human-facing overview of the skills home
├── skills/                      ← Local master copies of reusable skills
│   └── <skill-name>/
│       ├── SKILL.md             ← The skill's procedure + frontmatter
│       ├── README.md            ← Compulsory brief description + related skills
│       └── agents/openai.yaml   ← Codex UI metadata (mirrored across all copies)
├── wiki/                        ← LLM-maintained knowledge map (gitignored; schema-driven)
├── Archive/                     ← Durable artifacts (gitignored; not pushed)
│   ├── Summaries/               ← Session summaries (owned by session-summary)
│   └── Tasks/                   ← Pending/done housekeeping tasks (owned by task-this)
└── tmp/                         ← Strictly temporary scratch; safe to delete anytime
```
