---
name: report-this
description: "Create, update, or reopen durable reports in two modes, including evidence-first issue reports and source-backed analytical reports. Saves pending reports with permanent numbering and a dismissible lifecycle footer. Use when the user invokes /report-this, asks to report a bug, or asks for a durable report on a subject."
---

# Report This

Create, update, or reopen a durable report. Mode A is a platform or issue report;
Mode B is an analytical or professional report. Both use one lifecycle:
`pending` in Live, then `reported` in Historical through `finalize-report`.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval
gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/report-this` or `use report-this`
- `report this bug to <platform>` or an equivalent durable issue-report request
- `write a report on <subject>` or an equivalent durable analytical-report request
- `make a report`, `save this as a report`, or `report file`

If the user wants only an in-chat answer, create no file. Route plans to
`plan-this`, tasks to `task-this`, prompts to `prompt-this`, documentation to
`doc-this`, and report closure to `finalize-report`.

## Two Report Modes

Infer confidently and ask one question only when genuinely ambiguous:

- **Mode A — Platform / Issue:** a malfunction, defect, incident, vendor, or
  team target. Use the evidence-first issue template.
- **Mode B — Analytical / Professional:** an article, paper, video, event,
  dataset, decision, or topic. Use the thesis-and-analysis template.

Mode affects the body only. Never encode a mode tag in the report or use it to
choose a lifecycle state.

## Required Inputs

Infer before asking:

1. Mode.
2. Subject — a broad, reusable folder category.
3. Topic/title — the specific report filename body.
4. Audience and source/evidence material.
5. Whether this is create, update, or reopen.

Ask only for inputs that cannot be inferred safely. Settle Subject and Topic
collaboratively; avoid one Subject folder per file.

## Create, Update, Or Reopen

- **Create:** no matching report exists or the user requests a distinct report.
- **Update:** the user references a pending report or asks to revise it.
- **Reopen:** the user references a reported file and asks to revise, extend, or
  reopen it. Move it from Historical to the matching Live Subject folder, rename
  `_reported.md` to `_pending.md`, preserve its number, update the footer to
  `PENDING ⌛`, and retain its original created date. Record that it was reopened.
- Ask when multiple plausible reports match. Never overwrite a collision.

`report-this` is the only workflow that reopens a report. It never finalizes one.

## Location And Permanent Numbering

```text
Pending:  <root>\Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
Reported: <root>\Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

Folders are never numbered. Files alone carry `N.)`. For a new report, compute
`N = max(all N.) in Live/Reports/<Subject> plus all N.) in
Historical/Reports/<Subject>) + 1`, starting at `1`. Assign the number once for
life; never renumber, reclaim gaps, or calculate from only one side.

Create the required unnumbered Subject folder when allowed. Stop on a filename
or number collision.

## Mode A Body

Use `references/mode-a-template.md`. Required sections are Report Metadata,
Title, Environment, Summary, Root Cause with evidence, Steps to Reproduce,
Expected Behavior, Workaround, Suggested Fixes, Outcome, and Notes.

Facts, observations, hypotheses, and recommendations must remain distinguishable.
Never invent reproduction steps, versions, logs, root causes, or outcomes. Mark
unknown fields clearly.

## Mode B Body

Use `references/mode-b-template.md`. Required core sections are Report Metadata,
Executive Summary, Overview of the Source, Key Points / Findings, Analysis /
Discussion, Conclusion, and References / Sources. Background / Context and
Recommendations / Takeaways may be omitted only in a compact report when they
add no material value.

Keep source-faithful summary separate from author analysis or inference. If a
source cannot be fully accessed, say so and do not fabricate its contents. For a
blocked source, look for an authoritative canonical or cross-posted version
before asking for user-provided text or screenshots.

## Contract And Effort Controls

A Prompt Contract is optional by default. Use `prompt-contracts` when the user
asks for explicit acceptance criteria or when a complex Mode B assignment needs
a testable thesis, source, analysis, citation, or delivery gate. Keep any
contract in a clearly labeled workspace-only section above the footer.

An Estimated Effort table is optional. Include one only when the report itself
commissions or evaluates multi-phase follow-up work.

## Dismissible Footer

Every report ends with the exact footer from
`references/dismissible-footer.md`. The official report begins at line 1 with
its title or report content; never put workflow status or mode metadata at the
top. The footer carries only lifecycle and dates, includes no mode tag, and
instructs the user to delete everything below the final divider before external
delivery.

Footer cardinality is strict: every report contains exactly one canonical
dismissible footer. Creation appends the footer once. Update and reopen locate
the existing footer and replace or normalize that block in place; they never
append another footer. If update/reopen finds no footer or more than one footer,
stop and repair the report to exactly one canonical footer before continuing.

## Workflow

1. Read the relevant source/evidence and determine create, update, or reopen.
2. Infer Mode, Subject, Topic, audience, and required body depth.
3. Resolve ambiguity before writing; do not guess evidence or source content.
4. For create, calculate the combined Live plus Historical number.
5. For reopen, collision-check the Live destination before moving and renaming.
6. For creation, draft the body and append the exact pending footer once. For
   update/reopen, replace or normalize the one existing footer in place. Never
   append a footer during update/reopen. Preserve unrelated user-authored content.
7. Write UTF-8 and verify the path, filename, required sections, source honesty,
   and footer.
8. Report the path, Mode used, Subject, number, and any access limitations.

## Boundaries

Do not finalize reports, send them externally, claim an issue was reproduced
without evidence, fabricate inaccessible sources, store a mode tag, create a top
lifecycle header, or overwrite a destination. `finalize-report` exclusively owns
the pending-to-reported transition.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to durable reports and every later reopen, evidence, or content update.

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

This skill owns report mode, evidence, sections, source honesty, dismissible
footer, Subject, permanent number, path, update/reopen behavior, and lifecycle.
When co-invoked with `html-this` or `pdf-this`, run the full report workflow and
save only the requested `.html` or `.pdf` artifact unless the user requests
multiple formats. The format skill may improve presentation but must preserve
the report's facts, evidence boundaries, and lifecycle footer meaning.

Treat same-stem `.md`, `.html`, and `.pdf` variants as one report and one
numbering entry. Update or reopen the complete sibling set together. This
section overrides `.md`-only examples only for the co-invoked run;
`_pending`/`_reported` rules remain.

## Validation

After create/update/reopen, confirm:

- the expected Live path exists and the Historical source is absent after reopen
- Subject is unnumbered and `N.)` is permanent and collision-free
- filename ends in `_pending.md`
- the selected mode's required sections exist
- summary and analysis are distinct in Mode B
- unknown or inaccessible evidence is labeled honestly
- the exact dismissible pending footer is last
- exactly one canonical dismissible footer exists
- UTF-8 was preserved

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep
stdout and stderr separate.
