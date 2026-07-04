---
name: inspect
description: Inspect and audit whatever the user points at — verify a recently applied code batch (any language), or audit any file, skill, document, or artifact for mistakes, issues, consistency, or things to learn/adapt. Use when the user explicitly invokes /inspect, use inspect, use the inspect skill, asks to verify that recently applied blocks/lines/methods were added correctly, or asks to inspect/audit/check a file or artifact.
---

# Inspect

Inspect or audit whatever the user points at, and report findings clearly. This skill lives up to its name: it is the general "check this for me" workflow, with a dedicated fast path for verifying a code batch the user just applied.

There are two modes, auto-selected by context:

- **Mode A — Code-Batch Verification.** The user just applied or sent code and wants it checked before the next phase. Works for any programming language. This is the original inspect behavior, generalized.
- **Mode B — General Inspection / Audit.** The user points at any file, skill, document, config, or artifact and asks you to inspect/audit/check it — for mistakes, issues, consistency, or to learn or adapt something.

This skill is not Debug mode, not a code-generation workflow, and not a permission gate. If the user wants a broad bug diagnosis, use `debug`. If the user wants permission to proceed with a task, use `green-light`. If the user wants new implementation planning, use `imp-upd-plan`.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged. Default output is chat only: findings, issues if any, and next-step readiness. Do not edit files unless the project contract and the user both authorize it.

## Invocation

Treat these as direct invocation and begin the inspect workflow:

- `/inspect`
- `use inspect`
- `use the inspect skill`
- clear equivalents where the user explicitly names this skill

Mode A (code-batch) also triggers on batch-verification phrasing, such as:

- "How does the code and the updates we just made look?"
- "Confirm I made the changes properly."
- "Confirm you see the latest version of the code I just sent."
- "Update your memory with this version."
- "Next please."

Mode B (general audit) also triggers on phrasing like:

- "Inspect this file / skill / doc."
- "Audit this for mistakes / issues / consistency."
- "Check this and tell me if it's done well."
- "Look this over and tell me what we can learn / adapt / reuse."

## Mode Selection

Pick the mode from context; do not ask if it is obvious:

- If the target is applied/pasted code, a code diff, or a source file the user just changed → **Mode A**.
- If the target is any other file, skill, document, config, or artifact, or the user asks you to audit/check/learn-from something → **Mode B**.
- If genuinely ambiguous, ask one short question: "Do you want a code-batch verification, or a general audit of this file?"

Scope stays tight in both modes: inspect only what the user pointed at. Do not expand into a whole-repository audit unless the user explicitly asks for one.

---

## Mode A — Code-Batch Verification (any language)

Verify a recently applied code batch and sync your working context to the latest version the user provided for this session.

### A1. Universal code checks (language-independent)

1. **Latest version visibility** — confirm you see the newest version the user sent or pointed to, and treat it as the active working context for this session after inspection.
2. **Applied-change correctness** — confirm expected blocks, lines, methods, functions, fields, parameters, or enum entries are present, and that replacements landed in the right function/class/region/anchor. Confirm old conflicting blocks were removed when removal was required.
3. **Placement and structure** — look for obvious brace/bracket/indentation, nesting, duplicate-definition, or unreachable-code issues. Confirm the change fits the surrounding local pattern.
4. **Comments** — confirm existing comments were preserved when they still describe retained logic.
5. **Scope and safety** — confirm no unexpected full-file rewrite was introduced, and that the agent did not directly edit product source files unless separately and explicitly authorized.
6. **Next-phase readiness** — state whether the batch is ready for the next phase; if not, list the smallest corrections needed.

### A2. Language-aware doc-comment check

Detect the language from the file extension or content, and apply the matching documentation-comment convention rather than assuming one:

- C# → XML doc comments (`/// <summary>`)
- Python → docstrings
- Java → Javadoc (`/** ... */`)
- JavaScript / TypeScript → JSDoc (`/** ... */`)
- Other languages → that language's idiomatic doc-comment form

If a modified public method/function lacked a doc comment and the batch should have added one, flag it. If the language has no established doc-comment convention, skip this check.

### A3. Ecosystem profile (opt-in sub-case)

Only when the target is a `.cs` file inside the Uzzy Ecosystem `Sources\` tree, additionally:

- Require XML `/// <summary>` descriptions on method blocks where expected.
- Enforce the manual-copy `.cs` workflow from that project's contract: prefer inspecting the user-provided latest file or the working copy under `<project root>\Sources\`, and do not directly edit product `.cs` files.

Everywhere else, this profile does not apply.

### A4. Current-session memory sync

When the user says to "update your memory with this version," treat the latest inspected code as the active working context for the current session. If the batch changes architecture in a way worth preserving, mention that a documentation update may be useful at session end, but do not write it without approval.

---

## Mode B — General Inspection / Audit

The user points at a file, skill, document, config, or artifact. Read it, then inspect it **for whatever the user asked** — and only that, unless they invite a wider look.

1. **Confirm the target and the goal.** Identify exactly what to inspect and why: mistakes, issues, consistency with a standard, correctness, clarity, or to learn/adapt/reuse something. If the goal is unstated and not obvious, ask one short question.
2. **Read the target fully** before judging. For folder-style skills, read `SKILL.md` and any referenced resources.
3. **Inspect against the stated goal**, checking as relevant:
   - correctness and internal consistency
   - alignment with the project's conventions and canonical contract
   - missing, duplicated, malformed, contradictory, or outdated content
   - clarity, structure, and whether it does what it claims
   - anything reusable or worth adapting, when the user asked to learn/adapt
4. **Report findings**, most important first, each with a specific location and a concrete suggestion. Separate "must fix" from "optional / nice-to-have."
5. **State readiness** — whether the artifact is good as-is, or what the smallest set of changes would be.

Do not rewrite or edit the target in this mode unless the user explicitly asks. Reporting comes first.

## Required Inputs

If the target and goal are already clear, do not ask unnecessary questions — just inspect. Only ask for what is genuinely missing:

```text
I can inspect this, but I need one thing first:

1. Which file / batch / artifact should I inspect?
2. (Mode A) Is this the latest version after your applied batch?
3. What should I inspect it for — correctness, issues, consistency, or something to learn/adapt?
```

## Output Format

Lead with the result.

When everything looks good:

```text
I inspected [target]. It looks good.

Confirmed:
- [specific check that passed]
- [specific placement / consistency confirmation]
- Doc comments / conventions: [status]

[Mode A only] I am now using this latest version as the active working context for this session.
Ready for the next phase.
```

When issues exist:

```text
I inspected [target]. It needs attention before moving on.

Issues:
- [specific issue and location]
- [specific missing / misplaced / duplicated / inconsistent item]

Suggested corrections:
- [smallest correction]

[Mode A only] I will treat this latest version as the current working context, with the above issues pending.
```

## Boundaries

Do:

- confirm what you are inspecting and why
- verify code-batch placement/structure (Mode A) or audit the artifact against the stated goal (Mode B)
- flag missing, duplicated, malformed, inconsistent, or outdated content
- apply the language-appropriate doc-comment convention (Mode A)
- confirm current-session working context (Mode A) and next-step readiness

Do not:

- edit files directly without separate explicit authorization
- generate the next batch of implementation code unless the user asks for it
- expand into a full repository audit unless the user explicitly asks
- turn inspection into full Debug mode unless the user invokes `debug`

## Validation

After an inspection, state: what was inspected, whether it passed or what the issues are, any suggested corrections, and whether the next step is ready. For Mode A, also confirm the latest version was visible and the current-session context is synced.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
