---
name: finalize-session
description: Finalize the current conversational work by running session-name and session-summary together in one pass. Use when the user invokes /finalize-session, $finalize-session, use finalize-session, "finalize this session", "name and summarize this session", "wrap up and name this chat", or clear equivalents asking for combined chat-session naming plus a durable session summary. A thin orchestrator only — session-name owns the eight naming suggestions and session-summary owns the durable artifact. Requires a compulsory chat-session identifier, treats one unlabeled number as that identifier, routes optional summary overrides only when unambiguous, completes both children in the same pass, and never renames, closes, archives, or deletes the actual platform chat.
---

# Finalize Session

Finalize the current conversational work by running `session-name` and `session-summary` together in the same pass.

This skill is a **convenience orchestrator**. It owns invocation routing, input preflight, dependency guards, cross-turn resume behavior, and the combined completion receipt. It owns nothing else.

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

| Child skill      | What it owns                                                                 |
|------------------|------------------------------------------------------------------------------|
| `session-name`   | The eight grounded chat-label suggestions and all naming rules                |
| `session-summary`| The durable summary artifact, numbering, ACTS structure, and completion receipt|

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

- the eight-option foundation/synthesis naming algorithm, uppercase display-start rule, verbatim-prefix rule, Hermes 100-character cap, or non-blocking completion semantics — `session-name` owns these;
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

Once every required input is resolved, run both children **in the same conversational turn**:

1. **Run `session-name`** with the supplied chat-session identifier as its verbatim prefix. It must emit exactly eight suggestions and must **not** wait for a private user selection. A missing selection is never pending work and never blocks the summary.
2. **Run `session-summary`**, passing only the overrides actually supplied. It creates or updates its durable artifact and returns its completed-values receipt.
3. **Complete the wrapper** only after both child outcomes are delivered.

The final response must contain:

- the eight name suggestions with the supplied prefix;
- the `session-summary` completed-values receipt and a clickable path to the saved artifact; and
- a concise confirmation that both child workflows completed.

## Clarification And Resume

Preflight catches what can be caught early, but children keep their own clarification rights.

- If `session-summary` later hits a genuine clarification gate (an outside-project destination, a filesystem restriction, a higher-priority contract rule), it may ask. Do not suppress that.
- On resume, continue **only the unfinished child operation**. Never emit a second set of eight names and never create a duplicate summary artifact.
- Record enough current-conversation state to know which child completed. Do **not** create a separate durable orchestration artifact merely for checkpointing.

Resume is automatic on the user's reply. The user never re-invokes `finalize-session` to continue an in-flight run.

## Boundaries

Do:

- confirm both children are available before doing anything;
- collect the compulsory chat-session identifier first;
- pass supplied overrides through and let the children infer the rest;
- run both children in one pass and report both outcomes; and
- preserve each child's independent invocation.

Do not:

- rename, archive, delete, close, or otherwise mutate the actual chat/session in Codex, Claude, Antigravity, Hermes, zCode, or any other host — this skill produces **name suggestions and a summary artifact only**, and must never claim otherwise;
- wait for a `session-name` selection or treat a missing selection as pending work;
- treat a lone number as a summary file number;
- overwrite an existing summary artifact;
- reimplement child logic or weaken a child contract; or
- persist as a mode or emit a Mode footer of its own.

## Independent Child Invocation

`session-name` alone still gives names only. `session-summary` alone still gives the durable recap only. Neither child redirects a standalone invocation through this wrapper, and neither acquires a dependency on it. Adding `finalize-session` changes nothing about `session-name`'s non-blocking completion semantics or `session-summary`'s direct-invocation behavior.

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

`finalize-session` complete — `session-name` emitted eight suggestions and `session-summary` saved the durable artifact. Selecting a name is optional; nothing was renamed.
```

## Behavior Scenarios

1. **Identifier supplied:** both children run in the same turn; eight prefixed names plus the summary receipt are returned.
2. **Identifier missing, runtime prompt available:** collect the identifier through the host input mechanism, then run both children in the same turn.
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
14. **Missing `session-name`:** stop before execution and name the missing dependency.
15. **Missing `session-summary`:** stop before execution and name the missing dependency.
16. **Standalone child invocation:** `session-name` and `session-summary` behave exactly as before, unaffected by this wrapper.
17. **Platform mutation boundary:** never rename, close, archive, or delete the chat, and never claim to have done so.

## Related Skills

- `session-name` — required child; owns the eight chat-label suggestions.
- `session-summary` — required child; owns the durable summary artifact.
- `session-summary`'s finalizer family (`finalize-plan`, `finalize-task`, `finalize-prompt`, …) is unrelated: `finalize-session` finalizes *conversational deliverables*, not a durable artifact lifecycle.

## Validation

When creating or updating this skill, validate the folder with `quick_validate.py` in Python UTF-8 mode (`-X utf8`), reading pass/fail from the process exit code with stdout and stderr captured separately. Exercise every Behavior Scenario above, and additionally confirm:

- both dependency guards stop before any partial execution;
- the compulsory identifier is always resolved before either child begins;
- the runtime-prompt path and the chat-fallback-with-automatic-resume path are both covered;
- one-number defaulting, labeled dual-number routing, and ambiguous-number clarification behave as specified;
- lowercase child suffixes survive verbatim;
- supplied overrides route correctly and absent values remain inferred;
- a resume never duplicates the eight names or the summary artifact and never requires reinvocation;
- `session-name` remains non-blocking and `session-summary` retains its clarification rights;
- standalone invocation of both children is unchanged;
- no platform chat mutation is attempted or claimed;
- every Markdown table this skill emits satisfies the Markdown Table Alignment rule above; and
- all coupled metadata (`README.md`, `agents/openai.yaml`) agrees with this file.
