---
name: doc-this
description: Create or update durable documentation in the nested Live Documentation tree using the workspace house style and per-Subject numbering. Categories are Personal, Resources, or Articles, chosen by the document's nature. Use when the user invokes /doc-this or asks to create durable documentation.
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

Infer before asking, and ask only when genuinely ambiguous:

- `Articles` — the artifact is an article.
- `Resources` — the artifact is a resource, or the user designates it as one.
- `Personal` — user-authored documentation that is neither an article nor a
  resource.

Category is decided by nature, not source. An article or resource remains in
its category whether authored by the user, found online, or supplied by a
friend. There is no Personal article or Personal resource.

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
- `category` must be exactly `Personal`, `Resources`, or `Articles`.
- Subject folders and category folders are never numbered.
- Compute `N` from numbered files in that exact category/Subject folder only,
  starting at `1` and using one past the highest existing number.
- Never overwrite, renumber, or reclaim an existing document number.
- `Archive\Live\Reference\` does not exist and must never be used.

## Required Inputs

Infer these from context when safe: title/topic, source material, category,
Subject, target workspace (current by default), and optional analogy/for-dummies
layering (off by default).

## Workflow

1. Determine title, source, category, Subject, and target workspace.
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
source, overwrite a file, silently reconcile Legacy, or delete Legacy without
explicit permission.

## Validation

After create/update, confirm the expected path exists; category and Subject are
unnumbered; numbering is correct within the exact folder; house style is intact;
no file was overwritten; and UTF-8 was preserved.

After migration, confirm no docs remain loose above category folders, numbering
is clean in Legacy/destinations, and before/after inventories match by content.

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep
stdout and stderr separate.
