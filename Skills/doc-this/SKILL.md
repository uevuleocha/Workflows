---
name: doc-this
description: Create or update durable documentation in the nested Live Documentation tree using a user-selected or context-appropriate category, the workspace house style, and per-Subject numbering. Use when the user invokes /doc-this or asks to create durable documentation.
---

# Doc This

Create or update durable reference, architecture, or how-to documentation in:

```text
<root>\Archive\Live\Documentation\<category>\<Subject>\N.) <Title>.md
```

`doc-this` is a lifecycle-free cousin: documentation is born Live and stays
Live. It has no finalizer and no Historical move.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval
gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/doc-this`, `use doc-this`, or `use the doc-this skill`
- `make a documentation file`, `document this`, or `write this up as documentation`
- clear equivalents requesting a durable documentation artifact

If the user wants a plan, task, report, prompt, or summary, route to `plan-this`,
`task-this`, `report-this`, `prompt-this`, or `session-summary` respectively.

## Category And Subject

Use any appropriate, unnumbered top-level category. An explicit user-provided
category always wins. Otherwise infer a sensible broad category from context;
ask only when the category is genuinely ambiguous and a wrong choice would
materially affect placement.

Useful defaults and examples include `Personal`, `Resources`, and `Articles`,
but they are not an exhaustive allowlist. Do not force an artifact into one of
these categories when another category better matches the user's intent.

Then select a broad, reusable Subject folder. Folders are never numbered. Avoid
creating a unique Subject for every file.

## House Style

Every document uses:

1. `# <Title>`.
2. `**What this is:**` followed by one orienting paragraph.
3. `---` divider.
4. Topic-appropriate `##` sections, with dividers between major groups when useful.
5. `## One-Line Summary` containing one bold recap paragraph.

Use analogy or for-dummies layering only when the user explicitly requests it.

## Permanent Path And Numbering

- Destination:
  `Archive\Live\Documentation\<category>\<Subject>\N.) <Title>.md`.
- Subject folders and category folders are never numbered.
- Compute `N` from numbered files in that exact category/Subject folder only,
  starting at `1` and using one past the highest existing number.
- Never overwrite, renumber, or reclaim an existing document number.
- `Archive\Live\Reference\` does not exist and must never be used.

## Required Inputs

Infer these from context when safe: title/topic, source material, category,
Subject, target workspace (current by default), and optional analogy/for-dummies
layering (off by default). Preserve any explicit user-provided category.

## Workflow

1. Determine title, source, category, Subject, and target workspace. Use an
   explicit user category; otherwise infer a broad category and ask only when
   a materially important ambiguity remains.
2. Inspect the exact category/Subject folder and calculate the next number.
3. Compose the full draft in house style.
4. Ask how to proceed with an interactive question when available: Draft first
   (recommended), Make the artifact immediately, or Other.
5. On approval, create the needed unnumbered folders and write the UTF-8 file.
6. Report the category, Subject, assigned number, and path.

If no interactive tool exists, ask the same proceed question in chat and wait.
Do not skip this choice unless the user already explicitly instructed immediate
creation.

## Legacy Migration Offer

When old documentation exists at top-level `Documentation\` or loose under a
flat `Archive\Live\Documentation\`, offer a preservation-first migration:

1. Inventory all files and collision-check
   `Archive\Live\Documentation\Personal\Legacy\`.
2. Move every pre-existing document into `Personal\Legacy\` as a true move,
   preserving UTF-8 and content; renumber cleanly `1..n` by prior order only
   when the migration is authorized.
3. Scan and suggest category/Subject destinations, but let the user approve or
   edit the mapping before arranging files.
4. Renumber `1..n` within each approved destination and repair affected links.
5. Ask permission before deleting an empty Legacy folder. Never delete a
   non-empty Legacy folder.

If categorization, order, or a collision is ambiguous, stop rather than guess.

## Boundaries

Do not create a documentation lifecycle/finalizer, write outside
`Archive\Live\Documentation\`, use the phantom Reference path, categorize by
source against the user's explicit choice, create a unique Subject for every
file, overwrite a file, silently reconcile Legacy, or delete Legacy without
explicit permission. Do not treat `Personal`, `Resources`, and `Articles` as an
exhaustive category allowlist.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to durable documentation and every later material documentation edit.

For every in-scope artifact:

- place an `## Agent Provenance` section near the top with `Content owner`,
  `Original writing agent`, `Created`, and `Artifact role`;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`,
  `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` near the bottom, recording the date,
  acting agent, action, and concise scope for every material edit;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather
  than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves
to `Uzo`; do not confuse content ownership with the agent that performed the
filesystem write. Do not inject provenance into product source, third-party
files, databases, generated caches, skill definitions, schema-sensitive or
machine-consumed files, or other operational files unless their schema
explicitly supports it.

## Durable Artifact Format Handling

This skill owns documentation content, category, Subject, title, numbering,
location, and update semantics. When co-invoked with `html-this` or `pdf-this`,
run this workflow normally but save only the requested `.html` or `.pdf`
artifact unless the user requests multiple formats. Keep every required
documentation section; hand only serialization and format validation to the
format skill.

Same-stem `.md`, `.html`, and `.pdf` siblings are one logical document and one
numbering entry. Update all existing siblings together. This section overrides
`.md`-only path examples only during a co-invoked format run.

## Validation

After create/update, confirm the expected path exists; the selected or inferred
category was honored; category and Subject are unnumbered; numbering is correct
within the exact category/Subject folder; house style is intact; no file was
overwritten; and UTF-8 was preserved.

After migration, confirm no docs remain loose above category folders, numbering
is clean in Legacy/destinations, and before/after inventories match by content.

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep
stdout and stderr separate.
