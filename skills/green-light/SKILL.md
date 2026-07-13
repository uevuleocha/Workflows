---
name: green-light
description: Proceed with a user-approved task after explicit greenlight, while preserving surgical code-block delivery, exact placement instructions, no-full-code defaults, Antigravity greenlight behavior, and all project-contract safety rules. Use when the user explicitly invokes /green-light, use green-light, greenlight, green light, or one of the configured approval phrases for a named task.
---

# Green Light

Proceed with the user's approved task while preserving the project's safety rules and surgical delivery style.

This skill is a permission and delivery protocol. It means the agent has the user's greenlight for the named task, not a blanket bypass of the project's canonical contract, product-code safeguards, or runtime permission prompts.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

For product source files, preserve the manual-copy workflow defined in the project contract. Default to surgical code blocks, lines, method snippets, and exact placement instructions in chat unless the user explicitly authorizes direct product-code edits.

## Invocation

Treat these as direct invocation and proceed with the named task:

- `/green-light`
- `use green-light`
- `use the green-light skill`
- `greenlight`
- `green light`

The configured greenlight phrases are also valid when the task being approved is clear:

- `make the edit`
- `greenlight`
- `approved`
- `execute plan`
- `go ahead`
- `apply changes`
- `do it`
- `push to drive`

If the user explicitly invokes this skill, do not ask a second time whether the agent has permission to proceed with the named task. Proceed within the safety boundaries and runtime permission model.

## Ambiguous Greenlight Handling

If a greenlight phrase appears but the skill was not explicitly invoked and the intended task or permission scope is unclear, ask whether the user intended to invoke `green-light`.

Use this prompt shape:

```text
Do you want me to treat that as `green-light` for the named task and proceed under the project's surgical delivery rules?
```

Ask before proceeding when:

- the phrase could be casual agreement rather than task approval
- more than one task is active
- direct file edits might be implied but not clearly authorized
- product source files could be affected
- the task touches global skill paths or other paths outside the project root

Do not ask when the user explicitly invoked `green-light` and the task is clear.

## Greenlight Scope

Greenlight applies only to the named task or clearly active task. It can authorize the agent to proceed with:

- surgical code blocks, lines, or method snippets
- an implementation plan through `plan-this`
- a skill creation or update through `global-skills-creator`
- plan finalization through `finalize-plan`
- a session summary through `session-summary`
- non-product file edits when the user clearly approved those edits
- global skill sync when the approved task includes local + Codex + Claude + Antigravity copies

Greenlight does not authorize:

- direct product source-file edits unless explicitly authorized
- destructive operations such as deletion, reset, overwrite, or force changes without separate explicit approval
- full product code dumps by default
- unrelated edits outside the named task

If the task needs another skill, use that skill normally and treat `green-light` as the approval to proceed through that workflow.

## Surgical Code Delivery

For product code, never generate the full code by default. Give only the blocks, lines, or method snippets needed, step by step, block by block, or line by line, and tell the user exactly where to put them.

When delivering code:

- prefer the smallest useful line or block update
- provide exact placement instructions
- state whether the user should add, replace, or delete the block
- when practical, use agent discretion to deliver useful batches: more than one phase, block, or substantial part at once, as long as the batch stays reviewable and does not overload the agent or user
- split large changes into phases or parts when safer
- avoid sending all changes at once when staged delivery is clearer
- preserve the user's manual-copy workflow defined by the project contract

Use full methods only when a full method replacement is clearer or safer than fragmented block edits. Do not provide full product files unless the user explicitly asks for a full file.

## Method Block Rules

When generating a method block:

- include a brief XML `/// <summary>` when the method does not already have one
- preserve existing comments inside the method when they still refer to retained logic
- do not delete comments that still explain surviving behavior
- if replacing only part of a method, provide the exact old block or location and the replacement block
- if deleting logic, tell the user exactly which methods, blocks, or lines to delete

If a method already has an XML `/// <summary>`, preserve it unless the method behavior materially changes and the summary needs a small update.

## Antigravity Greenlight Rule

For Antigravity, explicit invocation of `green-light` means Antigravity already has the greenlight for the named task and should not come back to ask whether it has permission to proceed.

Antigravity must still obey:

- the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`)
- product source-file direct-edit restrictions
- the manual-copy workflow defined by the project contract
- the user's requested task scope

If `green-light` was not explicitly invoked and the phrase is ambiguous, Antigravity should ask whether the user intended to invoke `green-light` before proceeding.

## Output Modes

Use the output mode implied by the greenlit task:

- **Surgical code blocks:** send exact blocks, line updates, or method snippets with placement instructions.
- **Lines only:** send only the specific lines to add, replace, or delete.
- **Phased delivery:** split code or instructions into batches when the change is risky or large; where practical, include multiple phases, blocks, or a complete large phase in one batch to preserve momentum without sacrificing reviewability.
- **Implementation plan:** use `plan-this` to create or update the active plan.
- **Skill creation or update:** use `global-skills-creator` or `global-skills-creator-auto` according to the user's requested workflow.
- **Plan finalization:** use `finalize-plan`.
- **Session summary:** use `session-summary`.
- **Direct fix:** only when the user clearly authorized edits for the relevant files and the edits are allowed by project safety rules.

If the requested output mode conflicts with the project's canonical contract or runtime safety rules, follow the stricter rule and explain the constraint briefly.

## Validation

After completing a greenlit task:

- confirm what was delivered or changed
- confirm every edited file is inside the allowed path for that task per the project's canonical contract
- run the narrowest relevant verification available
- report any verification that could not be run

When creating or updating this skill itself, validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
