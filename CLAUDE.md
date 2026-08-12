# Agent Instructions — Workflows

This workspace is the **home for Uzo's skills**. It holds the **local master copies** of reusable skills — created from scratch, adapted from others' work, or brought in for personal workflows. Skill work *starts here*, then syncs outward to the global agent installs (Codex, Claude, Antigravity, Hermes, zCode). This repo may become public one day, so treat everything here as potentially world-readable.

References to "the hub," "the hub workspace," "the universe," "the AI OS," "the second brain," or "Uzzys Universe" all mean the root workspace at `C:\Users\Admin\Uzzys Universe\` (Uzzy's Universe).

This workspace runs on a simple model: **Workflows** (markdown SOPs + skills) say what to do, you're the **Agent** deciding how, and **Tools** (skills + built-ins) do the executing.

For LLM wiki setup, sync, query, or lint work, read and obey `wiki/wiki-schema.md`.

## Voice-to-Text Glossary

The user dictates heavily. Apply confident context-aware corrections without blocking progress, use corrected terms consistently downstream, and report every correction in the Glossary footer. Ask only when competing readings would materially change the action. Never edit the maintained glossary without user approval.

**Uzi → Uzzy**, **Cloud → Claude**, **Scale → Skill**, **In house → directly in chat (intentional user shorthand, not a dictation correction)**.

## Core Conventions

- **Files inside folders start with `x.)`** — this is a **hard rule with a fixed set of exceptions**, not a suggestion. Every file saved into a workspace folder gets a sequential index (`1.) `, `2.) `…; `0.)` allowed for a preamble). **The only exceptions:** structural/special files (`CLAUDE.md`, `AGENTS.md`, `README.md`, `SKILL.md`, dotfiles, config); files a skill or script generates under its own naming scheme; and any case where the user explicitly says not to use the numbering convention. Outside those exceptions, always apply it — if unsure whether something qualifies, apply the prefix.
- **`Archive/` is durable; `tmp/` is temporary.** Durable artifacts belong in `Archive/`. Keep only throwaway files in `tmp/`, report any temporary files created, and offer cleanup when their purpose is complete.
- **Temporary files live in the workspace `tmp/` and nowhere else.** An agent must not write them to a location outside the workspace -- a harness-provided scratchpad, a session temp directory, or a system temp path -- for anything the user might want to inspect. Those locations are invisible to the user, so a file placed there cannot be reviewed, corrected, or trusted. State the **full path** the first time a temporary file is created. This binds every agent regardless of what its own harness instructions suggest: a scratchpad outside the workspace is not a substitute for `tmp/`.
- **UTF-8 for everything** — skill, markdown, YAML, and helper-script text. Never rely on the Windows default encoding. Validate folder-style skills with Python in UTF-8 mode (`-X utf8`).
- **Natural prose wrapping.** Store ordinary Markdown paragraphs as continuous physical lines and let the editor soft-wrap them unless a schema, formatter, surrounding artifact, or the user requires fixed-width wrapping.
- **Durable-artifact provenance.** Every skill, new or existing, that creates first-party durable artifacts must give those artifacts agent provenance and an append-only agent change log. Place `Agent Provenance` **immediately after the opening block** — the title, status, and lifecycle lines most artifacts begin with — as the canonical two-column `Field | Value` table carrying exactly five rows in this order: `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, `Artifact role`. Place the `Agent Change Log` as the **last section**, except where the skill already reserves the last position for something else (encoded machine state, a required trailer), in which case it sits immediately above that reserved section. Render the change log as a five-column `Date and Time | Agent | Model | Action | Scope` table. Preserve `Content owner` and record the original writing agent truthfully. Do not inject provenance into product source code, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.
- **`Original writing LLM` is the model, not the agent.** `Claude Agent` is the agent family; `Claude Opus 5` is the LLM. They occupy separate rows and neither substitutes for the other. Use `Not recorded` when the model is genuinely unknown — inferring it from the agent label is inference, not record — and never backfill it into an existing artifact.
- **Change-log timestamps are read, never estimated.** Use `YYYY-MM-DD-HH:mm:ss` on a 24-hour clock, obtained from the machine clock at write time (for example `Get-Date -Format "yyyy-MM-dd-HH:mm:ss"`). Write no zone suffix; the machine is already in the user's zone. Leave historical date-only rows exactly as written rather than backfilling them — a log carrying both shapes is correct, and the boundary between them is itself information. A plausible invented timestamp is worse than a date-only one, because it looks authoritative while being fiction in a log whose only job is establishing sequence.
- **Feedback sections carry cross-agent messages.** Every artifact that carries a DEFINITION OF DONE, a Verification Checklist, or checkboxes an executing agent later ticks must also carry a `## Feedback Section`, present and empty by default, immediately above the `## Agent Change Log`. Entries are append-only and numbered `### Feedback N — date — agent — short descriptor`, starting at 1 and never renumbered; a correction is a new entry, never an edit to an earlier one. An empty Feedback Section is correct and must never be pruned for being empty. This is how an orchestrator, a verifier, and an implementer talk to each other through the artifact rather than through a chat session none of them shares.
- **Three artifact-integrity rules bind artifact-authoring and artifact-finalizing skills.** **Checklist Tick Discipline:** the executing agent ticks every box its own evidence supports, in the same pass; an unticked box means "not done," never "done but awaiting confirmation." **No Invented Sync Constraints:** never write "local master only" or "no global sync in this pass" into a DEFINITION OF DONE, Verification Checklist, CONSTRAINT, or FAILURE unless the user asked for it. **Non-Blocking Wiki And Git Items:** never write a wiki sync, `stage-commit-push` run, GitHub push, or submodule pointer bump into those sections as a completion criterion, and never gate finalization on one — publication follows finalization, because finalizing renames and moves the artifact. The carve-out: an artifact *whose subject is* the wiki or Git work legitimately carries such items. Each rule has one canonical wording, carried verbatim by every skill that holds it; rule 1 is emitted into artifacts, rules 2 and 3 bind the authoring agent only.
- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.
- **Propagate pipe alignment into skills.** Every skill in this workspace obeys the Markdown table alignment rule above — new or existing, being authored or being updated. There is no grandfather clause. On top of that, **every skill that writes Markdown tables must include the complete alignment rule in its own `SKILL.md` plus a validation check that enforces it**, so the rule stays portable after global installation instead of depending on this contract. "Writes tables" covers both durable artifacts the skill creates and tables it prints into chat. A skill that writes no tables anywhere is exempt from carrying the section — do not add it as boilerplate, and do not fail such a skill for lacking it. When updating an existing table-writing skill that lacks the section, add it in that pass.
- **Use deterministic alignment at file ownership boundaries.** Every skill that creates or materially edits a file containing Markdown tables must invoke `markdown-table-aligner` after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization. A clean helper check is authoritative for monospaced Unicode alignment; renderer-specific pixel offsets are not defects. Chat-only output, pure serializers, and helper-owned schema artifacts are exempt from redundant calls, but the portable rule above still applies wherever a skill writes tables.
- **Codex workspace configuration stays at the root.** Codex owns `.codex/` and may create or update `config.toml` when workspace sandbox settings change. Keep that harness-managed file untouched and place Codex `settings.local.json` beside it. `.agents/` contains only Antigravity, Hermes, and Z Code coordination homes.

## Skills Workflow (the core job of this workspace)

- **Local master is authoritative.** Never edit a global skill copy first or alone. Prefer updating and validating `Skills/<name>/` for user review before a later authorized sync. When the user invokes `global-skills-creator-auto`, explicitly requests same-pass global sync, or gives equivalent clear authorization, update and validate the local master first, then sync the approved global copies in that same pass. Without sync authority, stop after local verification.
- **Folder-style skills mirror structure** — each keeps `SKILL.md` + `README.md` (a compulsory, very brief what-it-does note, with related-skill pointers when the skill calls or pairs with others) + `agents/openai.yaml` across the local master and every global copy.
- **Sync targets (path stack):**
  - Local master: `Skills/<name>/`
  - Codex: `C:\Users\Admin\.codex\skills\<name>\`
  - Claude: `C:\Users\Admin\.claude\skills\<name>\`
  - Antigravity: `C:\Users\Admin\.gemini\config\skills\<name>\`
  - Hermes: `C:\Users\Admin\AppData\Local\hermes\skills\Personal\<name>\`
  - zCode: `C:\Users\Admin\.zcode\skills\<name>\`
- **Never invent a path.** If a target directory is missing, stop and ask — don't guess.
- Prefer an existing skill over improvising. `global-skills-creator` (guided) and `global-skills-creator-auto` (autonomous) own skill creation and cross-agent sync.

## Public-Repo Safety Guard

This repo is intended to go public eventually. Before any push — and **always** before the user makes the repo public — verify nothing private is tracked:

- Confirm `.gitignore` excludes `.env`, `.claude/`, `.codex/`, `.antigravity/`, `.agents/`, `Archive/`, `wiki/`, and `tmp/`.
- If the user says they're about to make this public (or add a remote), **warn first**, then check `git status`/`git ls-files` for secrets, tokens, machine-specific paths, or local settings before proceeding. Flag anything questionable and wait for confirmation.
- Remember that `.gitignore` does not untrack files or erase Git history.

## Safety & Precedence

- **Destructive ops need explicit approval** — no force-push, hard reset, branch merge, `rm -rf`, or deleting files the user didn't ask you to, without a clear "do it."
- **One editor per file.** Preserve existing user changes. If another agent or session may be editing the same file, stop and confirm before writing.
- **Stay within authority.** Do not expand a task into materially different work without authorization.
- **Ask when ambiguous.** On coin-flip cases, ask rather than guess.
- **Precedence:** most recent direct user instruction → `CLAUDE.md` → `AGENTS.md` wrapper.

## Secret-Safe Inspection

Never expose secrets in chat, tool output, logs, transcripts, documentation, screenshots, patches, or commits. Treat `.env` and credential stores as sensitive. Inspect only necessary key names, structure, presence, formatting, or validity and return redacted results. If a secret is exposed, do not repeat it; warn the user and recommend immediate rotation or revocation.

## Objectivity & Anti-Sycophancy

Be respectful and evidence-led. Do not flatter or agree automatically. Identify unsafe, incomplete, flawed, or contradictory assumptions; separate facts, inference, opinion, and uncertainty; and recommend the most defensible next action.

## Agent Loop

Every task follows **OBSERVE → THINK → ACT → OBSERVE AGAIN** until its Definition of Done is met. Time spent or attempted work is not completion evidence.

## Definition of Done (applies to every prompt)

Before acting, define what "done" looks like — either the user's explicit criteria or a sensible inferred one — and hold it while you work, looping OBSERVE → THINK → ACT until it's met. DoD applies to *every* request, not just formal tasks or plans. If you genuinely can't infer it (the ask is ambiguous or a coin-flip), **ask before acting** rather than guessing. You don't need to recite the DoD aloud unless the user asks — but state it plainly when it helps remove ambiguity between us.

## Task & Plan Lifecycle

Follow an active task or plan when it covers the current work unless the user redirects. Do not finalize tasks or plans in the same pass that executes them; leave them pending or active for user verification and invoke the matching finalizer only when explicitly requested. Incomplete work or a nearly exhausted budget is not evidence of completion.

## Self-Improvement Loop

When something fails, identify the root cause, correct the process or implementation, verify the correction, capture the reusable lesson in the appropriate local workflow or documentation, and continue with the stronger system. Do not silently modify global skills or canonical instructions.

## Communication & Footers

Keep explanations tight; use a short analogy only when it genuinely clarifies.

End every response with exactly two footers in this order, with the Mode footer last:

1. `Glossary = N/A` or a concise report of every voice-to-text correction applied that turn.
2. The Mode footer below.

Mode footer:

- If no mode is active → `Mode = N/A`
- If one mode is active → `Mode = <Mode Name>`
- If multiple modes are active → `Modes = Mode A + Mode B + ... + Mode Z` (include every active mode exactly once)

Skills that emit the Mode footer while active (open-ended list — grows as new mode-aware skills are added):

- **Brainstorm** — persists until exited
- **Debug** — persists until exited
- **Initialize** — one-time only (footer appears on the single initialization response, not subsequent responses)
- **LTNEY** — persists until exited
- **North Star** — uses the selected star while its run is active

When needed, check individual skill files for how the mode should be named in the footer.

## North Star

When a North Star run is active and not paused, open a provisional turn timer at the beginning of every turn. Precisely time actual North Star work with the authoritative pursuit timer, starting it when pursuit begins and stopping it when pursuit ends. Discard the provisional timer when authoritative timing succeeds or no pursuit occurs; use it only as the explicitly disclosed full-turn fallback when pursuit occurred but precise timing was missed. Never count both timers, and close or discard all timing state before responding. The `north-star` skill remains authoritative for the complete timing, reporting, footer, and lifecycle mechanics.

## Workspace Layout

> **Layout sync status:** `current` · last verified 2026-08-04 (root Codex control plane and three `.agents` homes reviewed)
>
> Keep this tree honest. If the real workspace and this tree disagree — a new folder/file that isn't shown here, or an entry here that no longer exists — **prompt the user before continuing substantive work**. The user may: (a) add the entry to the tree, (b) prune or replace something to keep it lean, or (c) decline the change. In every case, once the user has reviewed, reset the status line to `current` with today's date so the next agent doesn't re-raise it. Prefer a lean schema over an exhaustive one — prompt to prune before the tree sprawls; the goal is a map, not an inventory.

```
C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\
├── .agents/                     ← Antigravity, Hermes, and Z Code coordination
│   ├── .antigravity/settings.local.json
│   ├── .hermes/settings.local.json
│   └── .zcode/settings.local.json
├── .claude/                     ← Claude platform-owned workspace state
├── .codex/                      ← Codex harness-owned workspace configuration
│   ├── config.toml              ← Harness-managed sandbox/workspace settings
│   └── settings.local.json      ← Codex coordination settings
├── .obsidian/                   ← Optional Obsidian viewer state
├── AGENTS.md                    ← Four-platform wrapper → points to CLAUDE.md
├── CLAUDE.md                    ← This file. Canonical workspace contract.
├── README.md                    ← Human-facing overview of the skills home
├── Skills/                      ← Local master copies of reusable skills
│   └── <skill-name>/
│       ├── SKILL.md             ← The skill's procedure + frontmatter
│       ├── README.md            ← Compulsory brief description + related skills
│       └── agents/openai.yaml   ← Codex UI metadata (mirrored across all copies)
├── wiki/                        ← LLM-maintained knowledge map (gitignored; schema-driven)
├── Archive/                     ← Durable artifacts (gitignored; not pushed)
│   ├── Live/                    ← In-progress plans, prompts, tasks, North Stars, etc.
│   │   └── North Stars/         ← IN PROGRESS North Stars by unnumbered Subject
│   └── Historical/              ← Finalized/completed durable artifacts
│       └── North Stars/         ← FINALIZED North Stars by matching Subject
└── tmp/                         ← Strictly temporary scratch; safe to delete anytime
```
