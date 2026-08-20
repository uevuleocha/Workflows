---
name: github-file-this
description: Publish any GitHub involvement — issues (bugs and enhancements), pull requests, discussions, and comments — through a mandatory evidence-currency check, open-and-closed duplicate search, in-chat draft review, explicit approval gate, redaction pass, and gh CLI, then record every publication — stamped with its recording-time last-checked timestamp — to the workspace GitHub Involvements document in the same pass. Also track (passively follow) any GitHub issue, pull request, or discussion the user did not create or participate in, recording it with a `passive` marker after explicit approval. Use when the user invokes /github-file-this or $github-file-this, asks to file or open a GitHub issue or pull request, comment on a GitHub thread, track or follow a GitHub post, or clearly requests publication to GitHub.
---

# GitHub File This

Take a GitHub involvement from evidence to an approved public outcome, and record it so it is never lost. Verify that the evidence is current, search for duplicates, show the exact proposed public text in chat, publish only after explicit approval, and append every successful publication — and every approved track request — to the workspace's GitHub Involvements document in the same pass.

This skill supersedes `github-issue-this`. It widens the filing scope from issues alone to every involvement type, and adds the recording obligation that was previously missing. The recording obligation is the point: a filing skill that does not record produces exactly the untracked backlog this system exists to end.

## Project Contract

Obey the active workspace contract, permissions, public-repository safeguards, and secret-handling rules. This skill authorizes no publication until its own review gate is satisfied.

## Invocation

Treat these as direct invocation:

- `/github-file-this`
- `$github-file-this`
- `use github-file-this`
- `file an issue`
- `open a GitHub issue`
- `open a pull request`
- `comment on this`
- `track this`
- `follow this`
- `watch this`
- `raise this upstream`
- clear equivalents requesting a GitHub publication or passive track of any kind

A neutral request to draft text without publishing may use the drafting portions, but it does not authorize filing, commenting, or tracking.

## Publication Types

This skill publishes four involvement types. The Workflow safeguards below apply to every type; the bug-specific duplicate and OG logic applies to defect issues.

| Type            | Typical `gh` action                                         | Involvements section  |
| --------------- | ----------------------------------------------------------- | --------------------- |
| Issue - bug     | `gh issue create` or `gh issue comment`                     | Issues - Bugs         |
| Issue - enhance | `gh issue create` or `gh issue comment`                     | Issues - Enhancements |
| Pull request    | `gh pr create` or `gh pr comment`                           | Pull Requests         |
| Discussion      | `gh api` GraphQL discussion mutation                        | Discussions           |
| Comment         | `gh issue comment` or `gh pr comment` on an existing thread | owning section        |

A comment is never filed into its own section. It attaches to an existing thread and is recorded against that thread's entry, or against the owning section if the thread is not yet tracked.

Separately, this skill tracks any GitHub issue, pull request, or discussion the user did not create or participate in — a passive involvement recorded with the `passive` marker. See `Tracking (Passive Involvement)`.

## Required Inputs

Resolve, per proposed involvement:

1. The explicit `OWNER/REPO` target. More than one repository is allowed.
2. The involvement statement and the evidence supporting it.
3. The tested version, build, commit, configuration, platform, and restart or reload state relevant to the behavior, when a defect is involved.
4. The intended public scope and any cross-project relationship.

Use repository targets the user supplied or that are unambiguous in the active working context. Never invent or guess a repository, number, or URL. Ask one focused question if any target cannot be established safely.

## Workflow

Perform these ten stages in order for every proposed involvement. A multi-repository run may advance each involvement independently, but no involvement may skip a stage.

### 1. Establish Targets

- State every target as `OWNER/REPO` and map one involvement to each target.
- Keep each repository's involvement self-contained. Mention another project only with a one-line cross-reference when needed.
- Do not argue project A's defect inside project B's issue or PR.

### 2. Verify Evidence Currency

- Record when the evidence was produced and the exact version, build, commit, configuration, platform, and restart or reload boundary it describes.
- Identify every later version change, configuration change, rebuild, reinstall, or restart that could plausibly have altered the behavior.
- If such a change exists, say that the evidence is stale and propose the cheapest controlled confirming test.
- Do not call drafting complete and do not enter the review gate until the confirming test has been run or the current environment itself provides equivalent evidence.
- Separate directly observed facts from inference. Never convert old observations into current claims.

This stage is mandatory because the reference workflow nearly published a claim based on a superseded build. A same-build retest converted it into controlled current evidence.

### 3. Search For Duplicates

Run the preflight and duplicate search in `Duplicate Search And Classification`. Search before presenting the draft. Include open and closed items, search both titles and bodies, and surface near-matches even when they appear non-identical. The user decides whether a match is duplicative.

### 4. Draft In Chat

- Produce one draft per target repository using `references/issue-and-review-templates.md`.
- Write the title and exact body that would be posted. Do not write a body file yet.
- Keep claims reproducible, versioned, evidence-backed, concise, and scoped to the owning repository.
- Mark unknowns honestly. Do not invent logs, versions, steps, mechanisms, impact, or expected behavior.

### 5. Stop For Explicit Review

- Show the exact public text in chat and ask for an explicit decision for each involvement.
- Amendments return to stage 4 and require a new review of the revised text.
- Approval is bound to the exact displayed title and body or comment. Any material change invalidates it.
- Ambiguous enthusiasm or action language such as `looks good`, `next`, `go ahead with the work`, or `keep going` does not satisfy this checkpoint unless it explicitly approves the displayed public text for posting.
- Silence, earlier greenlight for investigation, and approval of another involvement never count.

This checkpoint is non-skippable. Nothing is posted during the turn that first presents a draft.

### 6. Redact Before Publishing

Review the approved text again immediately before publication. Remove or generalize:

- secrets, credentials, tokens, cookies, private keys, and connection strings;
- private usernames, machine names, instance identifiers, and account identifiers;
- internal absolute paths, workspace layout, private repository details, and local-only URLs; and
- community, workspace, server, channel, or conversation identifiers not required to understand the involvement.

Preserve technically necessary public identifiers. When the target or evidence is credential-adjacent, invoke `tread-lightly` and do not proceed until its safe-handling requirements are satisfied. If redaction materially changes approved text, return to stage 5 for approval of the redacted version.

### 7. Publish Through `gh`

Only after explicit approval, write the approved body to a uniquely named UTF-8 file under the active workspace's `tmp/github-file-this/` directory. State the full temporary path when it is created.

For a new issue, run:

```text
gh issue create --repo OWNER/REPO --title "<approved title>" --body-file "<temporary body file>"
```

For a pull request, run:

```text
gh pr create --repo OWNER/REPO --title "<approved title>" --body-file "<temporary body file>"
```

For an approved comment on an existing issue or PR, run:

```text
gh issue comment NUMBER --repo OWNER/REPO --body-file "<temporary comment file>"
```

For discussions, use the `gh api` GraphQL or REST mutation appropriate to the action, and record the returned URL the same way as every other outcome.

Capture the returned URL directly from successful `gh` stdout. Every URL reported as an outcome must come from actual command output; never reconstruct one. Remove only the exact temporary body file after the command completes, whether it succeeds or fails. Remove the run folder only when it is empty.

If publication fails, preserve the approved chat draft, report the command's safe error summary, and stop for that involvement. Never retry, alter text, switch repositories, or fall back to a different publication mechanism silently. In a partial multi-item success, report each successful URL and keep failed items pending; never repost successful ones.

### 8. Record In The Involvements Document

After and only after a successful publication, append it to the workspace's GitHub Involvements document in the same pass. Follow the `The Involvements Document` contract below: resolve the owning section for the involvement type, take the next ordinal within that section, and write an entry carrying the section ordinal, the real GitHub number, the marker `active`, the status `pending`, the full URL, and a last-checked timestamp stamped at recording time. For a comment on an already-tracked thread, update that thread's entry (set status to `updated` and refresh its last-checked timestamp) rather than creating a duplicate entry.

The document is owned by `doc-this` for creation, placement, and numbering. When the document does not exist, invoke `doc-this` to create it at `Archive/Live/Documentation/Personal/GitHub/N.) GitHub Involvements.md` with the five sections in fixed order, then append. This skill appends entries only; it never renumbers or restructures the document, and it never touches the Done section.

### 9. Create The Durable Outcome Report

After and only after a successful public action, invoke `report-this` in Mode A once per public outcome:

- for a new issue or PR, record the real filed-issue or PR URL and the approved title/body as the outcome;
- for a comment, record the target thread URL and the returned comment URL as the outcome; and
- if the user chooses to post nothing, create no outcome report because no public action occurred.

Pass the verified evidence, duplicate decision, redaction summary, and actual `gh` result to `report-this`. That skill owns report numbering, durable location, provenance, Feedback Section, Agent Change Log, table alignment, and report structure. Never finalize a report for a failed or unperformed public action.

### 10. Finalize The Report In The Same Pass

Immediately invoke `finalize-report` for every report created in stage 9, using the successful `gh` output as completion evidence.

This is the named **Public Outcome Same-Pass Finalization Exception** to the workspace rule that normally separates execution from finalization. The public issue, PR, discussion, or comment already exists before the report is created, so the report is born already reported; leaving it pending would misstate reality. The exception applies only to the outcome reports created by this run and never permits finalizing a report for an action that did not succeed.

## Tracking (Passive Involvement)

A user may want to follow a GitHub issue, pull request, or discussion they did not create and have not participated in — for example, to learn when the needle moves. This is a **track**, not a publication. Nothing is posted to GitHub.

Perform these steps for a track request:

1. **Resolve the target.** Establish the `OWNER/REPO`, the involvement type, and the real GitHub number or URL from the user's supplied or unambiguous reference. Never invent a repository, number, or URL.
2. **Check the document.** Confirm the thread is not already tracked in the Involvements document (any section, any marker). If it is, say so and stop; offer to re-check it via `github-involvement` instead.
3. **Show the entry.** Present the exact entry that would be recorded — the owning section, the next ordinal in that section, the real GitHub number, the marker `passive`, the status `pending`, the full URL, and a last-checked timestamp stamped at recording time — in chat.
4. **Stop for explicit review.** Require an explicit approval of that exact entry. Ambiguous enthusiasm or action language does not satisfy this checkpoint. Nothing is recorded during the turn that first presents it.
5. **Record.** On approval, append the entry to the owning section with marker `passive` in the same pass. Follow the `The Involvements Document` contract for the section, ordinal, and URL. Create the document via `doc-this` when it does not exist, exactly as for a publication.

A track produces no public action, so there is no `gh` publication, no outcome report, and no `finalize-report`. The recording write is the whole deliverable.

## GitHub Preflight

Run preflight before the user invests effort reviewing a draft:

```text
gh auth status
gh repo view OWNER/REPO --json nameWithOwner,hasIssuesEnabled,url
```

Require successful authentication and `hasIssuesEnabled: true` for issue targets. If either check fails, stop that target before drafting and explain the smallest next step. Do not expose authentication material in the command, output, or response.

## Duplicate Search And Classification

### Search Coverage

Derive several concise terms from the symptom, affected component, error text, and platform. Use more than one query when vocabulary varies. Search every target repository with `--state all` and both title and body coverage, for example:

```text
gh issue list --repo OWNER/REPO --state all --search "<terms> in:title,body" --limit 100 --json number,title,state,createdAt,url,labels,body
```

Inspect likely matches rather than relying on search snippets. Retrieve comments and repository-visible relationship evidence when needed:

```text
gh issue view NUMBER --repo OWNER/REPO --comments --json number,title,state,createdAt,url,labels,body,comments
```

Report each credible or near match with its number, state, title, creation date, age, and URL. Search results are evidence, not an automatic decision.

### Identify The OG Bug Report

Resolve the comment target in this strict order:

1. **Classify by type.** Retain only genuine defect reports. Discard fix or change tickets, pull-request trackers, feature requests, RFC or design discussions, epics or meta-trackers, and support questions, regardless of age.
2. **Choose by age.** Among the eligible bug reports, select the earliest-created one as the OG Bug Report.

Never apply earliest-wins before type classification. Only the OG Bug Report may receive the evidence comment. Later duplicates are context only.

Use repository evidence to classify type and canonical status, in roughly this reliability order:

1. Explicit triage comments such as `Duplicate of #X`.
2. Cross-reference density showing which report is the hub.
3. Title grammar: work-item prefixes such as `fix(...)`, `feat(...)`, or `chore(...)` versus report grammar such as `[Bug]:`, `crash`, or `hangs when`.
4. Label sets, especially `duplicate` labels pointing away from a satellite.
5. Linked pull requests indicating implementation tracking rather than evidence collection.

When two or more similar eligible bug reports have no consolidation signals, choose the earliest-created report without asking another question. Stop for a conflict only when maintainers visibly consolidated genuine bug reports onto a later report. Present the earliest report, the later consolidated report, both creation dates, and the consolidation evidence; ask the user which should receive the comment.

A fix ticket is never the evidence destination: it tracks work, closes with implementation, and does not remain the public place where affected users and maintainers accumulate defect evidence.

### Duplicate-Found Stop

Finding a duplicate neither auto-aborts nor auto-proceeds. Stop that issue and present all four items together, using the duplicate-stop template:

1. Every duplicate or near-match, with number, state, title, creation date, age, and URL.
2. The explicitly named OG Bug Report and why it survived type classification.
3. The unchanged new-issue draft.
4. A ready-to-post OG comment draft.

Then offer exactly two publication choices for that issue: `file it anyway` or `post the comment`. Both drafts must already be visible so one reply can resolve the branch. Each issue in a multi-repository run is decided independently.

The comment draft is not a compressed copy of the issue. Open by identifying it as additional evidence for the existing report, and include only what the thread lacks: a fresh reproduction, newer-version confirmation, additional affected configuration, corrected mechanism, or other new evidence. Keep it short. If the material adds nothing, say so and recommend posting nothing, but still show both drafts so the user may overrule.

Posting a comment requires explicit approval of that exact comment text. Approval of the new-issue draft does not approve the comment, and vice versa.

## The Involvements Document

Every publication is recorded to the workspace's GitHub Involvements document, located at:

```text
Archive/Live/Documentation/Personal/GitHub/N.) GitHub Involvements.md
```

`N` is computed by `doc-this` from that folder; never hardcode it. The document is owned by `doc-this` for creation, placement, and numbering; this skill and `github-involvement` read and write entries, nothing more.

### Sections

The document carries these sections in this fixed order, with Done always last:

| #   | Section               | Contents                                       |
| --- | --------------------- | ---------------------------------------------- |
| 1   | Issues - Bugs         | Defect reports filed, commented on, or tracked |
| 2   | Issues - Enhancements | Feature and improvement requests or tracked    |
| 3   | Discussions           | Discussion threads participated in or tracked  |
| 4   | Pull Requests         | PRs opened, reviewed, or tracked               |
| 5   | Done                  | Everything closed, merged, or retired          |

### Numbering and entries

Numbering restarts within each section. Section 1 has its own 1, 2, 3; section 2 starts again at 1. Continuous numbering across sections would renumber every row below any insertion.

The Done section has its own sequence, in finalization order — the order things were closed, not the order they were filed.

Every entry carries both numbers — the row's own ordinal within its section and the real GitHub number — plus the full URL, never a bare `#NNNN`. They are different facts and conflating them is the predictable failure.

Every entry also carries an involvement marker: `active` (the user or an agent created or participated in it) or `passive` (the user is only following it). Publications and retroactive-sweep finds are `active`; a track request is `passive`. The marker is a per-entry field, never a status and never a section.

Every open entry also ends with a last-checked timestamp — ` --- YYYY-MM-DD-HH:mm:ss` after the status, read from the machine clock at write time, 24-hour, no zone suffix — recording when that entry's upstream state was last observed. The timestamp is per-entry state, never file state: a run re-stamps only the entries it actually checked, so a scoped check leaves every other entry honestly reading "not looked at since then," while a whole-document check re-stamps every open entry. This skill stamps a newly recorded entry at recording time, because publishing or approving it observes its state; a comment on an already-tracked thread refreshes that entry's timestamp in the same write. Entries that predate this field simply gain their first timestamp the next time an agent observes and writes them; never backfill an invented timestamp. A row moved to Done keeps whatever timestamp it last carried, frozen — Done is never re-checked, so its timestamps cannot go stale.

Statuses for open items: `pending`, `updated`, `almost done`. Closure moves the row to Done rather than setting a status.

A discussion moves to Done only when the user says so, and can be reopened the same way. Never infer a discussion is finished from staleness, and never invent a staleness heuristic.

The Done section is read-only to this skill. This skill appends to the open sections and never touches Done. `github-involvement` owns Done exclusively.

## Review Output

Read and follow `references/issue-and-review-templates.md` before composing the issue body, ordinary review turn, duplicate-found stop, or OG comment. Keep the rendered draft easy to copy and compare. Do not put publication decisions in a table.

## Public-Action Safety

- Treat issue, PR, discussion, and comment creation as consequential external writes.
- Use only the explicitly approved repository and exact approved text.
- Do not close, edit, label, assign, subscribe, or otherwise mutate an item unless the user separately requests it, except the recording write this skill performs.
- Do not use browser automation or a web form as an unannounced fallback for `gh`.
- Never include secrets or unnecessary private identifiers.
- Never claim a public action succeeded without successful `gh` output.

## Multi-Repository Runs

Maintain a separate state for each involvement: target, evidence-currency result, duplicate candidates, OG classification, displayed drafts, approval decision, publication result, recording write, and report URL. One item may be filed, another redirected to an OG comment, and a third remain blocked. A failure or duplicate decision for one target does not silently decide another.

## Exact Model Attribution

Before this skill creates or materially edits the first first-party durable artifact in a session, invoke `exact-model-confirmation-gate`. The gate must finish before any new `Original writing LLM` or current-run Agent Change Log `Model` value is written.

- Reuse the gate's verified identity for later durable-artifact writes while the exact model context, acting agent, task or thread, and execution environment remain unchanged. Do not ask again during that stable session.
- If authoritative current runtime or session evidence cannot establish the exact model, stop before the first write and ask the user once. Cache a valid answer only for the current stable session.
- Invalidate prospectively when the user reports a model change or authoritative evidence shows that the model, agent, task or thread, or execution environment changed. Never rewrite historical provenance or change-log rows.
- Keep reasoning effort, service tier, provider, model family, and agent family separate from exact identity. Reject labels such as `Medium`, `Priority`, `OpenAI`, `GPT-5`, and `Codex Agent` as substitutes for a full model identity.
- Do not inspect configuration, environment data, credentials, logs, transcripts, or unrelated files by default. Only the gate's genuinely unavoidable file-backed branch may invoke `tread-lightly`, request one model field, and accept it only when it authoritatively identifies the current session. This skill does not gain a blanket `tread-lightly` dependency.
- Use `Not recorded` only when no interactive user is available, the user cannot identify the model, or exact identity remains safely unresolvable after the permitted attempt.

If `exact-model-confirmation-gate` is unavailable and no verified stable-session result already exists, fail closed before the artifact write rather than guessing, silently using `Not recorded`, or performing broader discovery.

**Validation check:** Confirm the dependency is named in this skill and its README; the canonical caller block is byte-identical to `exact-model-confirmation-gate/references/canonical-caller-block.md`; first-write blocking, one-time confirmation, stable-session reuse, proactive change, context invalidation, identity separation, targeted lookup, unresolved fallback, and append-only history pass the shared deterministic suite; and no historical row was rewritten.

## Markdown Table Alignment

Every Markdown table this skill writes — inside a durable artifact or into chat — must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Boundaries

Do not:

- publish an issue, PR, discussion, or comment — or record a tracked item — without explicit approval of the exact displayed text;
- treat evidence-currency verification as optional;
- fabricate repository names, issue numbers, URLs, versions, evidence, or outcomes;
- skip open-and-closed title-and-body duplicate search;
- comment on a non-bug work item or a later duplicate;
- collapse a genuine later-canonical conflict without asking;
- write any pre-approval body file;
- leak a secret, private path, or unnecessary community identifier;
- emit a bare `#NNNN` instead of a full markdown link;
- touch the Done section of the Involvements document;
- finalize a report for a public action that did not succeed; or
- author or edit the local master from a different workspace.

## Validation

Before synchronization or handoff:

1. Run `python -X utf8 scripts/test_policy.py` and require exit `0`.
2. Run the official `quick_validate.py` against this folder with Python `-X utf8`, keeping stdout and stderr separate and deciding pass/fail from the exit code.
3. Run the shared exact-model carrier validator and confirm the canonical block is byte-identical.
4. Confirm the skill is a delegated durable-artifact caller: `report-this` owns the report write and its Markdown tables, while this skill owns the public-action gate, the recording write, and same-pass orchestration.
5. Confirm the reference templates present separate multi-repository drafts, the four-part duplicate stop, and the exact two-way decision.
6. Confirm no workflow test creates a real GitHub issue or comment without a separately supplied disposable repository and explicit approval of the exact test text.
7. Confirm reaction publication is fully removed (no `Reaction` type, no `react to this` trigger, no reaction mutation) and the `Tracking (Passive Involvement)` path with `active`/`passive` markers is present.
8. Confirm every entry this skill records — publication, comment refresh, or passive track — carries the ` --- YYYY-MM-DD-HH:mm:ss` last-checked tail stamped at recording time, agreeing with `github-involvement`'s document contract exactly.
