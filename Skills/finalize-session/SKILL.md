---
name: finalize-session
description: Finalize the current conversational work by running session-name, asking the current agent to reconcile session evidence against the current workspace wiki's unresolved-verification page, creating session-summary with any reconciliation changes included, and then offering temporary-file cleanup. Use when the user invokes /finalize-session, $finalize-session, use finalize-session, "finalize this session", "name and summarize this session", "wrap up and name this chat", or clear equivalents. Requires a compulsory chat-session identifier, treats one unlabeled number as that identifier, routes optional summary overrides only when unambiguous, and never renames, closes, archives, or deletes the actual platform chat.
---

# Finalize Session

Finalize the current conversational work by running `session-name`, reconciling concrete current-session evidence against the current workspace wiki's unresolved-verification page, creating `session-summary` with any reconciliation changes included, and then offering temporary-file cleanup.

This skill is a **convenience orchestrator**. It owns invocation routing, input preflight, dependency guards, cross-turn resume behavior, the unresolved-verification checkpoint, the temporary-file cleanup offer, and the combined completion receipt.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, UTF-8 requirements, and file-edit restrictions apply unchanged. Orchestration does not broaden authority.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/finalize-session`
- `$finalize-session`
- `use finalize-session`
- `use the finalize-session skill`
- "finalize this session"
- "name and summarize this session"
- "wrap up and name this chat"
- clear equivalents asking for combined chat-session naming plus a durable session summary

A direct invocation authorizes the complete combined workflow once the compulsory chat-session identifier is resolved. Do not add a separate preview, confirmation, or greenlight step beyond the identifier preflight and any genuine ambiguity clarification defined below.

This is a **one-shot helper, not a mode.** It emits no Mode footer of its own. Obey any footer required by an active host mode.

## Required Dependencies

`finalize-session` requires both child skills:

| Child skill       | What it owns                                                                    |
| ----------------- | ------------------------------------------------------------------------------- |
| `session-name`    | The eight grounded chat-label suggestions and all naming rules                  |
| `session-summary` | The durable summary artifact, numbering, ACTS structure, and completion receipt |

### Dependency availability guard

Before orchestrating anything, confirm both children are loaded and invocable.

- If either child is unavailable, name the missing dependency and stop **before** any partial execution.
- Do not silently approximate a missing child, do not emit hand-written names, and do not write a plain fallback summary that loses the child's contract.
- If only one child ran before the other was found missing, disclose exactly which one completed and which did not. Never issue a combined receipt claiming both succeeded.

Use this wording:

```text
`finalize-session` cannot run: `<missing child>` is not available.
Load it, or invoke `<available child>` directly if you only want that half.
```

## Thin Orchestration Boundary

`finalize-session` **does not** reimplement, restate, or override:

- the direct context-rich eight-option naming algorithm, uppercase display-start rule, verbatim-prefix rule, Antigravity 70-character cap, Hermes 100-character cap, or non-blocking completion semantics — `session-name` owns these;
- summary Subject/Topic/number inference, collision safety, `🎭 ACTS` structure, Definition of Done ACT, provenance, delegated return-report shape, artifact serialization, or the completed-values receipt — `session-summary` owns these;
- either child's validation logic, lifecycle rules, or platform behavior.

When a child's contract and this file appear to disagree, the child wins for anything the child owns.

## Input Grammar

### The compulsory input

The **chat-session identifier** passed to `session-name` is the only compulsory input specific to `finalize-session`.

- Accept a supplied parent identifier (`39`) or lowercase-child identifier (`39a`) **verbatim**, following the current `session-name` grammar.
- **Never normalize a lowercase child suffix.** `39a` stays `39a`; it never becomes `39`.
- The identifier is passed through to `session-name` as its opt-in `N.)` prefix input.

### The one-number rule

When exactly one unlabeled number or identifier accompanies the invocation, it is **always** the chat-session identifier.

**Never** treat a lone number as the session-summary file number. The summary file number is optional and is normally inferred by `session-summary` from the selected Subject namespace.

### Two-number routing

If both a chat-session identifier and a summary file-number override are supplied, route each **only when its purpose is explicit** from a label or surrounding syntax — for example `session 39a, summary number 7`, `chat=39a summary=7`, or equivalently unambiguous phrasing.

If two numbers are present and their roles are genuinely unclear, ask **one** concise clarification **before either child runs**. Do not guess.

```text
Two numbers were supplied. Which is the chat-session identifier and which is the summary file number?
```

### Optional summary guidance

These may accompany the invocation and are passed through to `session-summary` **only when supplied**:

- Subject
- Topic
- summary file number
- in-project Directory

Anything not supplied stays inferred by `session-summary` under its own rules. Never invent a value merely to fill a slot, and never confuse the chat-session identifier with the summary artifact's permanent number.

An explicit summary-number override is honored under `session-summary`'s no-overwrite safety: if the requested number is already occupied, that skill advances to the next available integer and reports the number actually used. `finalize-session` never forces an overwrite and never resolves a collision itself.

## Preflight

Resolve every identifiable input **before** either child begins.

1. **Confirm both dependencies are available** (see the guard above). Stop if either is missing.
2. **Resolve the chat-session identifier.**
   - Supplied → use it verbatim.
   - Missing → collect it. **Prefer the host's runtime ask-user pop-up/input mechanism when one is actually available.** Use it to request the chat-session identifier directly.
   - If the agent cannot invoke such a runtime prompt, ask for the identifier **in chat**, end that turn **without running either child**, and resume the same `finalize-session` invocation automatically when the user replies. **Do not require the user to invoke the skill again.**
3. **Resolve number ambiguity** using the input grammar above. Ask one clarification only when two numbers are genuinely indistinguishable.
4. **Collect optional summary overrides** that were actually supplied.

Preflight never produces partial child output. Until preflight completes, no names are emitted and no summary artifact exists.

Chat-fallback wording:

```text
What is the chat-session identifier for this session? (e.g. `39` or `39a`)
I'll run `session-name` and `session-summary` as soon as you reply — no need to re-invoke `finalize-session`.
```

## Combined Execution

Once every required input is resolved, run the workflow **in the same conversational turn**:

1. **Run `session-name`** with the supplied chat-session identifier as its verbatim prefix. It must emit exactly eight suggestions and must **not** wait for a private user selection. A missing selection is never pending work and never blocks reconciliation or the summary.
2. **Reconcile unresolved verification**, using the current agent and current-session evidence under the procedure below. Do not invoke another verification or finalization skill.
3. **Run `session-summary`**, passing only the overrides actually supplied. If reconciliation changed a finalized artifact, also pass the exact reconciliation receipt forward as current-session evidence so the new summary records the source path, checkbox or disposition change, appended change-log row, and supporting evidence in its chronological ACTS, final state, files, and verification sections. If reconciliation changed nothing, continue normally without manufacturing a reconciliation event in the summary. The child creates or updates its durable artifact and returns its completed-values receipt.
4. **Offer temporary-file cleanup**, assembling and presenting agent-created temporary files across all workspaces written to during the session, and offering the user the choice to delete none (default), some, or all.
5. **Complete the wrapper** after child deliverables, the reconciliation receipt, and the cleanup offer are presented.

The final response must contain:

- the eight name suggestions with the supplied prefix;
- the `session-summary` completed-values receipt and a clickable path to the saved artifact;
- a concise unresolved-verification receipt stating what was checked, dispositioned, unchanged, unavailable, or absent;
- the temporary-file cleanup offer with full paths and purpose notes, or a single-line notice if no temporary files were created; and
- a concise confirmation that both child workflows completed.

## Unresolved Verification Reconciliation

This checkpoint instructs the executing agent to compare the work and evidence from the current chat against unresolved items already discovered by the current workspace's wiki. The skill is an instruction; it is not an independent actor, background job, or additional child skill.

### 1. Resolve the wiki scope

- Default to the workspace root in which `finalize-session` was invoked.
- Read that workspace's `wiki/wiki-schema.md` only when it exists, then resolve its structural unresolved-verification page, normally `wiki/unresolved-verification.md`.
- Do not search a hub, parent, sibling, or other workspace by default.
- Check another workspace's wiki only when the user explicitly named that workspace during this session.
- If the current workspace has no schema or unresolved page, report `Unresolved verification: No current-workspace page available.` and continue. Do not invoke `wiki-this` or `wiki-sync` automatically.

### 2. Compare against concrete current-session evidence

Read each unresolved entry's source artifact path, owning section, and item text. Compare it only with concrete evidence produced or inspected in this chat: completed workflow results, tests, command output, user confirmation, created durable artifacts, or other directly observed evidence.

- A plausible inference, similar task, or optimistic interpretation is not verification.
- Do not reopen unrelated files or perform new implementation merely to make an item pass.
- If an entry lacks an exact resolvable source path and item, report it as unresolved and do not guess.

### 3. Apply only supported source edits

When concrete evidence proves an item:

1. Open the exact finalized source artifact named by the wiki entry.
2. Change only that item's `- [ ]` marker to `- [x]`.
3. Append the required `Agent Change Log` row using the machine-clock timestamp, current agent, exact model, action, and narrow scope.
4. Preserve the artifact's filename, finalized status, original provenance, all unrelated content, and historical log rows.

When the current session instead establishes that an item is deliberately left unticked for a known tested reason, leave the box unticked and add this standardized line directly beneath that exact checkbox:

```text
Verification disposition: intentionally left unchecked -- <reason>.
```

Append the same required change-log row. This explicit disposition, not an ordinary explanation elsewhere, tells the next `wiki-sync` not to list the item again.

If neither outcome is concretely supported, change nothing. `finalize-session` must still complete.

### 4. Leave wiki refresh to the next sync

Do not edit `unresolved-verification.md` during this checkpoint and do not run `wiki-sync`. The finalized artifact is the source of truth; after its checkbox or disposition changes, the next normal sync sees it as changed and refreshes the wiki entry. Report the source edits made and any items left untouched.

## Temporary-File Cleanup Offer

The temporary-file cleanup step runs last, after `session-name`, unresolved-verification reconciliation, and `session-summary` have completed.

### 1. Placement and non-blocking lifecycle

The cleanup step runs last. It must never gate, block, or delay naming or summarizing. If the user abandons the session before or during the offer, nothing is deleted, which is the safe and correct outcome.

### 2. Collect (agent-created temporary files only)

Assemble the list of temporary files the agent created during this session.

- **Scope is agent-created files only** — never files the user created, and never pre-existing files the agent merely read, inspected, or edited.
- **Transcript tracking over directory scanning:** Prefer reconstructing the list from the session's own record of file writes over scanning `tmp/` wholesale. A directory scan surfaces files created by other sessions, other agents, or the user, and offering to delete those is a severe failure.
- **Handling provenance-uncertain files:** If a temporary file's provenance is genuinely uncertain (cannot authoritatively prove it was created in this session), list it and explicitly flag it as provenance-uncertain in chat rather than hiding it or claiming it.

### 3. Cross-workspace scope

The workspace `tmp/` directory is the default location, but the list must include agent-created temporary files in any other workspace's `tmp/` the agent wrote to during the session (e.g. nested submodules, tools, or root hub workspaces). A session that touches multiple workspaces can leave scratch files in more than one place, and a cleanup step that checks only the current workspace gives false assurance.

### 4. Chat presentation shape and empty list

Present the list in chat with the **full path** of each file so the user can identify each one without opening it. Where useful, note briefly what each file was for.

- **Empty list:** If no agent-created temporary files were created during the session, state so in a single line (e.g. `Temporary files: None created during this session.`) and finish — do not manufacture a prompt for an empty list.

### 5. Choice offer and default-to-keep

Offer the user three options:
1. **Delete none** (the default).
2. **Delete a selected subset** (explicitly named).
3. **Delete all**.

The default is always to delete nothing. Deletion happens only upon an explicit user instruction naming what to remove. Session finalization does not constitute implicit deletion authority, and an ambiguous reply must never be treated as authority to delete.

### 6. Execute and confirm

When the user gives an explicit instruction to delete, delete exactly the selected files, then confirm in chat what was deleted and what was kept. Never delete anything silently.

### 7. Non-duplication with report staging cleanup

Cleanup of staged send-ready report copies (`tmp/<subject>-reports-send-ready/`) remains strictly owned by `finalize-report`. `finalize-session` does not duplicate, list, or override staged report cleanup.

## Clarification And Resume

Preflight catches what can be caught early, but children keep their own clarification rights.

- If `session-summary` later hits a genuine clarification gate (an outside-project destination, a filesystem restriction, a higher-priority contract rule), it may ask. Do not suppress that.
- On resume, continue **only the unfinished operation**. Never emit a second set of eight names, repeat a completed reconciliation edit, or create a duplicate summary artifact.
- Record enough current-conversation state to know which child completed. Do **not** create a separate durable orchestration artifact merely for checkpointing.

Resume is automatic on the user's reply. The user never re-invokes `finalize-session` to continue an in-flight run.

## Boundaries

Do:

- confirm both children are available before doing anything;
- collect the compulsory chat-session identifier first;
- pass supplied overrides through and let the children infer the rest;
- run both children in one pass and report both outcomes;
- check the current workspace's unresolved-verification page without invoking another skill;
- tick only evidence-proven source items or add the exact adjacent disposition marker for deliberately unticked items;
- append a truthful change-log row for every finalized-artifact edit;
- complete unresolved-verification reconciliation before creating the summary and carry every reconciliation edit into that new summary;
- preserve filenames, finalized status, provenance, and unrelated content;
- present agent-created temporary files with full paths across all touched workspaces;
- default to keeping all temporary files unless explicit deletion instructions are received;
- handle the empty-list case in a single line without prompting;
- flag provenance-uncertain files explicitly; and
- preserve each child's independent invocation.

Do not:

- rename, archive, delete, close, or otherwise mutate the actual chat/session in Codex, Claude, Antigravity, Hermes, zCode, or any other host — this skill produces **name suggestions and a summary artifact only**, and must never claim otherwise;
- wait for a `session-name` selection or treat a missing selection as pending work;
- treat a lone number as a summary file number;
- overwrite an existing summary artifact;
- reimplement child logic or weaken a child contract;
- search other workspace wikis unless the user explicitly named them;
- edit the unresolved-verification wiki page or run `wiki-sync` from this checkpoint;
- tick an item from inference, similarity, or unsupported optimism;
- call another verification or finalization skill to perform the source edit;
- delete any temporary file without explicit user instruction;
- offer to delete files the agent did not create (user-created or pre-existing files);
- scan `tmp/` wholesale and attribute foreign files to this session;
- create the session summary before unresolved-verification reconciliation;
- omit a reconciliation source edit from the session summary;
- block or delay `session-name`, unresolved-verification reconciliation, or `session-summary` with the cleanup step;
- duplicate or override `finalize-report`'s staged-copy cleanup; or
- persist as a mode or emit a Mode footer of its own.

## Independent Child Invocation

`session-name` alone still gives names only. `session-summary` alone still gives the durable recap only. Neither child redirects a standalone invocation through this wrapper, and neither acquires a dependency on it. Adding `finalize-session` changes nothing about `session-name`'s non-blocking completion semantics or `session-summary`'s direct-invocation behavior.

## Deterministic Markdown Table Aligner Integration

When unresolved-verification reconciliation materially edits a finalized Markdown artifact containing tables, invoke `markdown-table-aligner` after the semantic edit and before handoff. Run its read-only `check` first; use staged `format` only for safe padding findings, review the diff, adopt it, rerun `check`, and prove idempotence. The helper never decides whether a checkbox is verified or authors a change-log row.

## Markdown Table Alignment

Every Markdown table this skill writes or causes to be written must be visually pipe-aligned. Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `→ see note [row-id]` (using that row's own identifier — its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view.

Rendered visual alignment is authoritative; raw `|` indices are diagnostic only, because Unicode display width (emoji, arrows, wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. When a table exceeds approximately 120 characters in total width, narrow the columns and move detail to notes so it renders on one line without word-wrapping.

## Output Shape

```text
Eight session-name suggestions:

1. 39a.) [option]
2. 39a.) [option]
3. 39a.) [option]
4. 39a.) [option]
5. 39a.) [option]
6. 39a.) [option]
7. 39a.) [option]
8. 39a.) [option]

Created and saved using these inferred values:

1. Subject: [used value]
2. Topic: [used value]
3. Session Number: [used value]
4. Directory: [resolved absolute path]

Saved file: [clickable path]

Unresolved verification: [checked N, dispositioned N, unchanged N, or no page available]

Temporary files created this session:
- `C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows\tmp\scratch_log.txt` (command output capture)

Would you like to delete any of these temporary files?
(Options: delete none [default], delete all, or specify files to remove)

`finalize-session` complete — `session-name` emitted eight suggestions, unresolved verification was reconciled before `session-summary` saved the durable artifact, and temporary-file cleanup was offered. Selecting a name is optional; nothing was renamed.
```

When no temporary files were created during the session, replace the temporary file block with:

```text
Temporary files: None created during this session.
```

## Behavior Scenarios

1. **Identifier supplied:** the same turn runs naming, reconciliation, summary creation, and cleanup in that order; eight prefixed names plus the reconciliation and summary receipts and temporary-file cleanup offer are returned.
2. **Identifier missing, runtime prompt available:** collect the identifier through the host input mechanism, then run both children and cleanup offer in the same turn.
3. **Identifier missing, no runtime prompt:** ask in chat, end the turn with neither child executed, and resume automatically on reply.
4. **One unlabeled number:** routes to `session-name` as the chat-session identifier, never to the summary.
5. **Two labeled numbers:** chat identifier goes to `session-name`, summary number goes to `session-summary`.
6. **Two ambiguous numbers:** one clarification before either child runs.
7. **Parent identifier:** `39` used verbatim as `39.)` on all eight labels.
8. **Child identifier:** `39a` used verbatim as `39a.)`; the `a` is never dropped.
9. **No summary overrides:** `session-summary` infers Subject, Topic, number, and Directory itself.
10. **Summary overrides supplied:** only the supplied values are passed; the rest stay inferred.
11. **Summary-number collision:** `session-summary` advances to the next available integer and reports the number used; nothing is overwritten.
12. **No name selection reported:** the run completes anyway; the summary is never blocked.
13. **Child clarification mid-run:** resume completes only the unfinished child, with no duplicate names or duplicate artifact.
14. **Temporary files created in one workspace:** lists all agent-created temporary files with full paths and offers deletion choices.
15. **Temporary files created across multiple workspaces:** lists all agent-created temporary files across all touched workspace `tmp/` directories with full paths.
16. **No temporary files created:** emits `Temporary files: None created during this session.` in one line without prompting for deletion.
17. **User declines temporary file deletion or reply is ambiguous:** keeps all temporary files in place; deletes nothing.
18. **User explicitly specifies deletion subset or all:** deletes only the requested files and confirms what was deleted and what was kept.
19. **Provenance-uncertain temporary file:** listed and explicitly flagged as uncertain in chat rather than claimed or hidden.
20. **Missing `session-name`:** stop before execution and name the missing dependency.
21. **Missing `session-summary`:** stop before execution and name the missing dependency.
22. **Standalone child invocation:** `session-name` and `session-summary` behave exactly as before, unaffected by this wrapper.
23. **Platform mutation boundary:** never rename, close, archive, or delete the chat, and never claim to have done so.
24. **Current workspace unresolved match:** concrete session evidence ticks the exact finalized-artifact item and appends one change-log row before summary creation; the new summary records the edit and evidence.
25. **Deliberately unticked item:** adds the exact adjacent disposition marker and one change-log row without ticking the box before summary creation; the new summary records the edit and reason.
26. **No evidence match:** changes no artifact and completes normally.
27. **No unresolved page:** reports the absence and continues to cleanup.
28. **Other workspace not named:** never searches it.
29. **Other workspace explicitly named:** may check only that additional named workspace's page.
30. **Wiki remains stale until sync:** edits only the source artifact and never invokes `wiki-sync`.
31. **No reconciliation change:** proceeds directly into normal summary creation without inventing a reconciliation event in the summary.

## Related Skills

- `session-name` — required child; owns the eight chat-label suggestions.
- `session-summary` — required child; owns the durable summary artifact.
- `finalize-report` — owns staged-copy cleanup for reports; not duplicated here.
- `markdown-table-aligner` — validates tables after a direct finalized-artifact edit.
- `exact-model-confirmation-gate` — resolves the exact model before a direct change-log write.
- `session-summary`'s finalizer family (`finalize-plan`, `finalize-task`, `finalize-prompt`, …) is unrelated: `finalize-session` finalizes *conversational deliverables*, not a durable artifact lifecycle.

## Validation

When creating or updating this skill, validate the folder with `quick_validate.py` in Python UTF-8 mode (`-X utf8`), reading pass/fail from the process exit code with stdout and stderr captured separately. Exercise every Behavior Scenario above, and additionally confirm:

- both dependency guards stop before any partial execution;
- the compulsory identifier is always resolved before either child begins;
- the runtime-prompt path and the chat-fallback-with-automatic-resume path are both covered;
- one-number defaulting, labeled dual-number routing, and ambiguous-number clarification behave as specified;
- lowercase child suffixes survive verbatim;
- supplied overrides route correctly and absent values remain inferred;
- a resume never duplicates the eight names, a completed reconciliation edit, or the summary artifact and never requires reinvocation;
- `session-name` remains non-blocking and `session-summary` retains its clarification rights;
- the strict order is `session-name` -> unresolved-verification reconciliation -> `session-summary` -> temporary-file cleanup;
- every reconciliation source edit is present in the newly created summary, while a no-change reconciliation does not manufacture summary content;
- temporary files across all written workspaces are included by full path;
- default-to-keep is enforced and deletion requires explicit user instructions;
- the empty-list case produces a single-line notice without prompting;
- provenance-uncertain files are flagged explicitly;
- non-duplication with `finalize-report` staged cleanup is preserved;
- current-workspace-only unresolved lookup, exact source resolution, evidence discipline, direct checkbox/disposition edits, change-log append, and no-match continuation are covered;
- unresolved reconciliation never edits the wiki page, runs `wiki-sync`, calls another verification/finalization skill, changes filenames/status, or searches unnamed workspaces;
- finalized artifacts edited by this skill pass `markdown-table-aligner` when they contain tables;
- standalone invocation of both children is unchanged;
- no platform chat mutation is attempted or claimed;
- every Markdown table this skill emits satisfies the Markdown Table Alignment rule above; and
- all coupled metadata (`README.md`, `agents/openai.yaml`) agrees with this file.

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
