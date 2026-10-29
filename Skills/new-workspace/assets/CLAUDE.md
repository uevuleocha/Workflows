# Agent Instructions - {Workspace Name}

This workspace is **{Workspace Name}** - a {tier term}{parent-world clause} in the **{Solar System}** solar system of Uzzys Universe. {one-line purpose}

This workspace runs on the same model as the rest of Uzzys Universe: **Workflows** (markdown SOPs + globally installed skills) say what to do, you're the **Agent** deciding how, and **Tools** (skills + built-ins) do the executing.

## Voice-to-Text Glossary

The user dictates heavily via voice-to-text, so misrecognitions are routine and expected. Correcting them is a **hard, always-on responsibility**, not an optional nicety — run the check below on **every** dictated message before acting, and apply it to everything you produce downstream (prose, filenames, folder names, code identifiers, quoted-back text). A corrected term must appear corrected *everywhere* you write it — never let the raw misheard word leak into an artifact (e.g. a file named `…Across Scales.md` when the user meant "Skills").

**Two sources of correction — both mandatory:**

1. **The glossary (below).** These are **context-aware hints, not blind find-and-replace rules** — seeing the word on the left does not automatically mean the word on the right. It means: given the surrounding context, it is *most likely* the word on the right. If the context genuinely concerns the literal left-hand word, treat it as literal.
2. **Context (the standing rule, wider than the glossary).** Context is king. A word need not be in the glossary to be a misrecognition. If a dictated word or phrase seems out of place and another interpretation fits the surrounding context better, infer the likely intended meaning and use it.

**Always report what you corrected — do not correct silently.** Whenever you apply a correction (from either source), report it in the Glossary footer (see Communication & Footers below) so the user can see you understood and can veto a wrong call. The footer is the one place these reports go — do not also narrate the correction inline in the response body. Example footer line:

> `Glossary = Heard "scale" → read as "skill" (per glossary)`

- **Report, don't block.** Reporting is not asking permission — apply the correction and keep working; the footer just surfaces it. Only **stop to ask** when the correction genuinely changes the action *and* you are not confident which reading is intended (a true coin-flip). Routine, high-confidence fixes are applied-and-noted, never gated.
- **One line per recurring word, per message — but judge each occurrence on its own.** If a misheard word appears many times in one message, don't list each hit; state the correction once in the footer, then apply it silently thereafter. Consolidation governs *reporting volume only* — it does **not** mean "one instance was wrong, so all of them are." Context is king per-occurrence: some instances of the same word may be the mishear and others may be literal. Correct the ones context says to correct, leave the rest, and if the split isn't uniform, say so in the one footer line. Example: `Glossary = Heard "scale" 10x — read 8 as "skill", kept 2 literal (measurement sense)`

**Never edit the glossary yourself.** An agent must not add, remove, or change a glossary pair on its own. If you notice a word the dictation app seems to mishear repeatedly, *suggest* it to the user and add it only if they agree — otherwise leave it. Keep the glossary as a **single continuous inline list**: comma-separated pairs that wrap and indent only at the line's end, never one pair per line (that would bloat this file for no reason).

**Uzi → Uzzy**, **Cloud → Claude**, **Scale → Skill**, **In house → directly in chat (intentional user shorthand, not a dictation correction)**.

## Core Conventions

- **Files inside folders start with `x.)`** - hard rule with fixed exceptions (structural files like `CLAUDE.md`, `AGENTS.md`, `README.md`, dotfiles, config; skill/script-generated files; user overrides). If unsure, apply the prefix.
- **`tmp/` is strictly temporary** - throwaway only, deletable anytime. Durable artifacts go in `Archive/`.
- **UTF-8 for everything** - markdown, YAML, plans, summaries, scripts.

## Safety & Precedence

- **Destructive ops need explicit approval** - no force-push, hard reset, branch merge, `rm -rf`, or deleting files the user didn't ask for.
- **Ask when ambiguous.** On coin-flip cases, ask rather than guess.
- **Precedence:** most recent direct user instruction -> `CLAUDE.md` -> `AGENTS.md` wrapper.
- **No same-pass finalization** - leave tasks `_pending` and plans `_plan_active` for the user to verify.

## Definition of Done

Before acting, define what "done" looks like - explicit or sensibly inferred - and hold it while working (OBSERVE -> THINK -> ACT). DoD applies to every request. If you can't infer it confidently, ask.

## Communication & Footers

Keep explanations tight; use a short analogy only when it genuinely clarifies. Answer mechanical questions directly.

Every response ends with two footers, in this exact order, with nothing after them. This is a hard, compulsory requirement — it applies to every response with no exceptions, including one-line answers, errors, and interrupted or truncated turns. Before sending, run a two-point self-check: **(1)** both footers are present and in the correct order; **(2)** each is *complete and correct* — the Glossary footer lists every correction you applied this turn (including the hardcoded pairs Uzi→Uzzy, Cloud→Claude, Scale→Skill), and the Mode footer names every active mode (or `N/A`). Presence alone is not enough — a footer that is present but incomplete or wrong fails this check.

**1. Glossary footer** — reports this turn's Voice-to-Text Glossary corrections (see Voice-to-Text Glossary above). This is the one place those reports go — never inline in the body.

- No corrections this turn → `Glossary = N/A`
- One or more corrections → `Glossary = <short note(s)>`, e.g. `Glossary = Heard "scale" → read as "skill" (per glossary)`
- Scope is exactly what the Voice-to-Text Glossary section defines: glossary-pair or context-inferred corrections only. Not a catch-all for every typo — if nothing in that section's sense triggered, it's `N/A`.

**2. Mode footer** — the true final line of every response.

- No mode active → `Mode = N/A`
- One mode active → `Mode = <Mode Name>`
- Multiple modes active → `Modes = Mode A + Mode B + ... + Mode Z` (each active mode exactly once)

Mode-emitting skills (open-ended — grows as new mode-aware skills are added): **Brainstorm**, **Debug** (persist until exited); **Initialize** (one-time); **LTNEY** (persists until exited); and **North Star** (selected star while active). Check individual skill files for the exact footer name when unsure.

### North Star

When a North Star run is active and not paused, open a provisional turn timer at the beginning of every turn. Precisely time actual North Star work with the authoritative pursuit timer, starting it when pursuit begins and stopping it when pursuit ends. Discard the provisional timer when authoritative timing succeeds or no pursuit occurs; use it only as the explicitly disclosed full-turn fallback when pursuit occurred but precise timing was missed. Never count both timers, and close or discard all timing state before responding. The `north-star` skill remains authoritative for the complete timing, reporting, footer, and lifecycle mechanics.

## Skills

Reusable skills are installed globally and invoked by name. If a request matches a loaded skill, remind the user it exists and ask whether to run it. Skill authoring lives in the Workflows world, not here.

## Workspace Layout

```text
{workspace path}
|-- .git/                   <- Local Git repository
|-- .gitignore              <- Empty initially unless requested otherwise
|-- AGENTS.md               <- Agent wrapper -> CLAUDE.md
|-- CLAUDE.md               <- Canonical workspace contract
|-- README.md               <- Human-facing overview
|-- Archive/                <- Durable artifacts
|   |-- Live/               <- Active, pending, reference
|   `-- Historical/         <- Completed records
`-- tmp/                    <- Temporary scratch
```

> **Layout sync status:** `current` - last verified _{layout-sync timestamp}_
>
> **Always re-check on session start, regardless of the timestamp.** If the real workspace and this tree disagree, prompt the user before continuing. Update the timestamp after every review or change.
