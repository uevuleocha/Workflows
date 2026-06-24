---
name: inspect
description: Cross-check recently applied code batches and sync to the latest user-provided version for the current session. Use when the user explicitly invokes /inspect, use inspect, use the inspect skill, or asks to verify that recently applied blocks/lines/methods were added correctly before the next phase.
---

# Inspect

Cross-check a recently applied code batch and sync the assistant's working context to the latest user-provided version for the current session.

This skill is for post-batch verification and state sync after the user applies or sends code changes. It is not debug mode, not a broad code review, and not a code generation workflow.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

For product source files, preserve the manual-copy workflow defined in the project contract. Inspect code the user provides or explicitly points to inside `<project root>\Sources\`, but do not directly edit product source files unless the user separately and explicitly authorizes direct product-code edits.

Default output is chat only: verification, issues if any, current-session sync confirmation, and next-phase readiness.

## Invocation

Treat these as direct invocation and begin the inspect workflow:

- `/inspect`
- `use inspect`
- `use the inspect skill`
- clear equivalents where the user explicitly names this skill

Use this skill when the user asks a batch-verification style question, such as:

- "How does the code and the updates we just made look?"
- "Confirm I made the changes properly."
- "Confirm you see the latest version of the code I just sent."
- "Update your memory with this version."
- "Next please."

If the user asks for a broader bug diagnosis, use `debug` instead. If the user asks for permission to proceed with a task, use `green-light`. If the user asks for new implementation planning, use `imp-upd-plan`.

## Inspect Scope

Inspect only the latest relevant code batch, file version, or phase the user wants checked.

This skill should verify:

- whether the latest code version is visible
- whether the requested blocks, lines, or methods appear to have been applied
- whether placement looks correct
- whether obvious duplicate, missing, or malformed code exists
- whether XML `/// <summary>` requirements were preserved or added where needed
- whether relevant comments were preserved when logic remains
- whether the assistant should use this latest code as the active current-session context

Do not turn this into a broad repository audit unless the user explicitly asks for one.

## Required Inputs

If the latest code and task scope are already visible, do not ask unnecessary questions. Inspect the provided material.

If anything important is missing, ask only for the missing or uncertain item:

```text
I can inspect this batch, but I need the latest version first.

1. Which component/file should I inspect?
2. Is this the latest version after your applied batch?
3. Which batch or phase should I verify against?
```

For product source files, prefer inspecting the user-provided latest file or the working copy under `<project root>\Sources\`, per the project's canonical contract.

## Inspection Checklist

Use the smallest checklist that fits the batch. For code batches, check:

1. **Latest version visibility**
   - Confirm you see the newest code version the user sent or pointed to.
   - Treat it as the active working context for this session after inspection.

2. **Applied-change correctness**
   - Confirm expected blocks, lines, methods, fields, parameters, or enum entries are present.
   - Check that replacements landed in the right method, class, region, or anchor area.
   - Check that old conflicting blocks were removed when the instructions required removal.

3. **Placement and structure**
   - Look for obvious brace, nesting, duplicate-method, duplicate-field, or unreachable-code issues.
   - Check that the change fits the surrounding local pattern.

4. **XML summaries and comments**
   - Confirm method blocks have XML `/// <summary>` descriptions where expected.
   - If a modified method lacked a summary and the batch should have added one, flag it.
   - Confirm existing comments were preserved when they still describe retained logic.

5. **Scope and safety**
   - Confirm no unexpected full-file rewrite was introduced.
   - Confirm product source-file direct edits were not performed by the agent unless explicitly authorized.

6. **Next-phase readiness**
   - State whether the batch is ready for the next phase.
   - If not ready, list the smallest corrections needed before continuing.

## Current-Session Memory Sync

When the user says to "update your memory with this version," treat the latest inspected code as the active working context for the current session.

If the inspected batch changes bot or indicator architecture in a way that should be preserved later, mention that a documentation update may be useful at session end, but do not write it without approval.

## Output Format

Lead with the inspection result.

Use this shape when everything looks good:

```text
I see the latest version, and the batch looks properly applied.

Confirmed:
- [specific applied change]
- [specific placement or structure confirmation]
- XML summaries/comments: [status]

I am now using this latest version as the active working context for this session.
Ready for the next phase.
```

Use this shape when issues exist:

```text
I see the latest version, but this batch needs correction before the next phase.

Issues:
- [specific issue and location]
- [specific missing/misplaced/duplicated block]

Corrections needed:
- [smallest correction instruction]

I will treat this latest version as the current working context, with the above issue list pending.
```

Do not generate new code unless the user asks for the correction blocks or invokes `green-light` for the next work step.

## Boundaries

Do:

- confirm latest-code visibility
- verify recent batch placement and structure
- flag missing or duplicated blocks
- check XML `/// <summary>` expectations
- confirm current-session working context
- stand by for the next phase

Do not:

- edit product source files directly without separate explicit authorization
- generate the next batch of implementation code unless the user asks for it
- turn inspection into full Debug mode unless the user invokes `debug`

## Validation

After an inspection:

- state whether the latest version was visible
- state whether the batch was applied properly
- list any issues or corrections
- confirm current-session context sync
- state whether the next phase is ready

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
