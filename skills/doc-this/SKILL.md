---
name: doc-this
description: Create or update a documentation file in the workspace's Documentation/ folder using this workspace's house style (a "What this is" intro, ## sections, and a closing One-Line Summary), with mandatory X.) numbering inferred from existing files. Use when the user explicitly invokes /doc-this, use doc-this, use the doc-this skill, "make a documentation file", "document this", "write this up as documentation", or clear equivalents.
---

# Doc This

Turn a topic, conversation, or reference material into a documentation file that matches this workspace's established Documentation house style, saved at `Documentation/X.) <Title>.md` with the mandatory numbering.

This skill is for durable reference/architecture/how-to documentation, not for plans (`imp-upd-plan`), tasks (`imp-upd-task`), or session summaries (`session-summary`). If the user asks for one of those instead, use that skill.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/doc-this`
- `use doc-this`
- `use the doc-this skill`
- `make a documentation file`
- `document this`
- `write this up as documentation`
- clear equivalents where the user wants a new or updated file in the workspace's `Documentation/` folder

## House-Style Template (mandatory shape)

Every documentation file created by this skill follows this shape, matching the workspace's existing `Documentation/` files:

1. `# <Title>` — the document's title, as an H1.
2. `**What this is:**` — one paragraph directly under the title, orienting the reader on what the doc covers and when to come back to it.
3. `---` divider.
4. Body in `##` sections. The number and shape of sections is adapted to the topic — use judgment, informed by the source material or conversation. When the doc covers several discrete sub-topics (e.g., one per term or concept), separate each with its own `---` divider.
5. Closing `## One-Line Summary` — a single bolded paragraph recapping the whole document.

**Optional layering:** only when the user explicitly asks for it, invoke the `analogy` and/or `for-dummies` skills and fold each pass into the relevant section as a sub-part (e.g., "What it means" / "Analogy" / "For dummies" stacked under one heading), rather than defaulting to this for every doc.

## Numbering Rule (mandatory)

- Filename: `Documentation/X.) <Title>.md`.
- `X` is never literal or hard-coded. Glob the workspace's `Documentation/` folder for existing numbered files and use the next available integer, starting at `1`.
- If `Documentation/` does not exist yet in the target workspace, create it.
- Never overwrite an existing numbered file. If the derived filename would collide, re-check the folder — something was missed.
- Renaming a doc's title after creation is a separate, explicitly user-requested step; the assigned number does not change unless the user asks to renumber.

## Required Inputs

Before drafting, make sure these are known or safely inferable from context:

1. **Title / Topic** — infer from conversation if clear; otherwise ask.
2. **Source material** — conversation context, a file to summarize, or content the user provides directly.
3. **Target workspace** — defaults to the current workspace's `Documentation/` folder.
4. **Analogy / for-dummies layering** — defaults to no (real definitions only) unless the user asks for it.

## Workflow

1. Determine title/topic and target `Documentation/` folder; create the folder if it does not exist.
2. Glob existing `Documentation/*.md` files and determine the next available `X`.
3. Compose the full draft body in the house-style shape.
4. **Ask the user how to proceed**, using the agent's interactive structured-question/elicitation tool if the current runtime exposes one (in Claude Code, this is the `AskUserQuestion` tool):

   > "How would you like me to proceed?"
   > 1. **Draft first** — show the draft, you confirm or request edits, then I write the file. *(default/recommended)*
   > 2. **Make the artifact immediately** — skip the chat review, write the numbered file now.
   > 3. **Other** — free text; follow what the user types.

   - **Fallback**, if no such runtime tool is available: ask the same question as plain chat text and wait for the user's next message before continuing. This ends the turn — a degraded but acceptable fallback, not the preferred path.
5. Branch on the answer:
   - **Draft first:** show the full draft in chat; wait for explicit approval or edits; write the file only after approval.
   - **Immediately:** write `Documentation/X.) <Title>.md` right away, then report.
   - **Other:** follow the user's typed instruction.
6. Report the file path and the number assigned.

## Output Rules

- Documentation files only ever live under the workspace's `Documentation/` folder.
- UTF-8 always.
- Do not create, edit, or rename any file outside `Documentation/` as part of this skill.

## Safety Rules

- Never overwrite an existing numbered file.
- Never touch product/source files.
- Never renumber or rename an existing doc without the user explicitly asking for it.
- Do not skip the proceed-choice step (Workflow step 4) even when the topic seems obvious.

## Validation

After creating or updating a doc:

- Confirm the file exists at the expected `Documentation/X.) <Title>.md` path.
- Confirm the house-style shape is present: title, `What this is` intro, `##` sections, closing `One-Line Summary`.
- Confirm no existing numbered file was overwritten.
- Confirm UTF-8 was used.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
