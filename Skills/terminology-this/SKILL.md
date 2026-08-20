---
name: terminology-this
description: Create or extend durable Terminology documents with a canonical three-pass explanation for every term. Use when the user invokes /terminology-this, $terminology-this, asks for a terminology document, asks to add a word or term to an existing terminology reference, or gives a term after "terminology-this:".
---

# Terminology This

Create new Terminology documents and add terms to existing ones while keeping the document's opening term list, term sections, and One-Line Summary consistent. This skill authors the terminology-specific content; `doc-this` owns the durable documentation write, placement, numbering, and house style.

## Project Contract

Obey the active workspace contract, permissions, durable-artifact rules, and UTF-8 requirements. Terminology documentation is born under `Archive\Live\Documentation\` and has no finalizer or Historical move.

## Invocation

Treat these as direct invocation:

- `/terminology-this`
- `$terminology-this`
- `use terminology-this` or `use the terminology-this skill`
- `make a terminology document for <subject>`
- `add <term> to the <subject> terminology document`
- `terminology-this: <term>` when the conversational subject identifies the target

Select Mode A when no Terminology document exists for the subject. Select Mode B when one already exists and the user wants one or more terms added.

## Dependencies

| Skill                           | Requirement | Role                                          |
| ------------------------------- | ----------- | --------------------------------------------- |
| `doc-this`                      | Hard        | Owns every documentation create/update write  |
| `analogy`                       | Preferred   | Authors each `Analogy` pass                   |
| `for-dummies`                   | Preferred   | Authors each `For dummies` pass               |
| `exact-model-confirmation-gate` | Hard        | Resolves model attribution before first write |
| `markdown-table-aligner`        | Via owner   | `doc-this` runs it at the file-write boundary |

Before either mode writes, confirm `doc-this` is available. If it is unavailable, stop and ask the user to make it available; do not reproduce its numbering, path, or house-style logic inline.

Prefer `analogy` and `for-dummies` when they are available. If either is unavailable, continue by applying that skill's method inline: write a concise, accurate everyday comparison for `Analogy`, and a literal jargon-free beginner explanation for `For dummies`. Do not block an otherwise complete Terminology update on either soft dependency.

`exact-model-confirmation-gate` is a hard dependency for the first model-attributed durable write in a stable session. `doc-this` remains the real file owner and must run `markdown-table-aligner` when the document contains Markdown tables.

## Target Resolution

Resolve the target from the current conversation before asking the user:

1. Use an explicitly named Terminology document or subject.
2. Otherwise infer the platform, tool, or domain already being discussed.
3. Search only the relevant documentation subject when needed to confirm the exact document.
4. Ask one short question only when no document exists for the inferred subject, two documents plausibly match, or the subject is genuinely ambiguous.

In Mode B, state the inferred target path before writing so the user can cheaply catch a wrong inference. Do not ask which document to use when the conversation makes the subject unambiguous; for example, during a Buzz session, `terminology-this: variable` targets the Buzz Terminology document.

## Canonical Terminology Structure

Build new documents in this order:

1. `# <Title>`.
2. `**What this is:**` followed by one orienting paragraph that names every covered term, says that every term receives a real definition, an analogy, and a for-dummies explanation, and tells the reader they may return to any section without reading top to bottom.
3. A `---` divider.
4. `## Agent Provenance` using the current five-row workspace schema, followed by a divider.
5. One `## <Term>` section per term. Each term carries `**What it means:**`, `**Analogy:**`, and `**For dummies:**` in that fixed order.
6. `## One-Line Summary` containing one bold continuous sentence that recaps every term.
7. `## Feedback Section`, present even when empty.
8. `## Agent Change Log` as the final section using the current five-column workspace schema.

`One-Line Summary`, `Agent Provenance`, `Feedback Section`, and `Agent Change Log` are structural sections, not terms, and never receive the three passes.

A term may earn extra material ahead of its three required passes when that material genuinely improves understanding. Preserve useful precedents such as etymology, distinctions, caveats, or a worked example; never remove them merely to normalize a document. The three required passes still appear in their fixed order after any optional extra material.

For a long document, grouping headers such as `# PART ONE - Foundations` may be added above logical groups at roughly fifteen terms or more. Grouping is optional and must not disturb the term-section shape.

## Naming Convention

- Category defaults to `Personal`; an explicit user-supplied category always wins.
- Subject is the unnumbered platform, tool, or domain folder, such as `Buzz`, `GitHub`, `Obsidian`, or `Codex`.
- Both `N.) <Subject> Terminology.md` and `N.) Terminology.md` are valid.
- Prefer the Subject-prefixed filename for a named product when it reads naturally.
- Prefer the bare filename for a domain or when the Subject would be long or awkward as a prefix.
- `N` is whatever `doc-this` computes from numbered files in that exact category and Subject folder. Never hardcode `1`.
- Never rename or renumber an existing Terminology document merely to make it match the preferred form.

## Mode A - Create

1. Establish the subject, explicit or inferred category, and initial term list. Ask only for a genuinely missing input that would materially change the document.
2. Choose the natural title and one of the two valid filename forms. Do not compute `N`.
3. Research each term enough to write an accurate `What it means` pass. Never invent facts to fill the shape.
4. Use `analogy` when available for each concise comparison; otherwise apply its method inline.
5. Use `for-dummies` when available for each plain-language pass; otherwise apply its method inline.
6. Compose the complete canonical document, including every term in the opening list and One-Line Summary.
7. Invoke `doc-this` with the category, Subject, chosen title, and complete draft. `doc-this` alone resolves the folder, assigns `N`, applies durable-artifact requirements, invokes the table aligner when applicable, and performs the write.
8. Report the created path and the terms covered.

An explicit request to create immediately, including an active `green-light`, satisfies `doc-this`'s creation-choice gate. Otherwise preserve that gate.

## Mode B - Add A Word

1. Infer and state the exact target document. Ask only under the ambiguity conditions in Target Resolution.
2. Read the target in full before editing. Preserve its title, filename form, numbering, grouping, useful extra passes, historical provenance, and existing change-log rows.
3. Confirm the requested terms are not already present under the same name or an obvious equivalent. If a term already exists, ask whether the user wants it revised instead of duplicating it.
4. Author each new term's `What it means`, `Analogy`, and `For dummies` passes, using the preferred helpers when available.
5. Place each new term in the most natural existing group or before `One-Line Summary` when no grouping applies.
6. Update the `What this is` paragraph so its term list names every term now covered.
7. Rewrite the bold One-Line Summary as one continuous sentence that recaps every term, including the additions.
8. Invoke `doc-this` to apply the complete update. It owns the durable write, provenance and change-log behavior, UTF-8 preservation, and the deterministic table-alignment pass.
9. Re-read the saved document and confirm the new sections, opening term list, and One-Line Summary agree.

Do not modify, rename, or renumber any other Terminology document during the update.

## Durable Artifact Requirements

For new documents, require the current `doc-this` five-row Agent Provenance table, an empty-by-default Feedback Section immediately above the Agent Change Log, and the five-column append-only Agent Change Log as the final section.

When updating a legacy Terminology document, preserve historical content and attribution exactly. Apply `doc-this`'s current update rules without guessing missing historical model identities or rewriting old rows.

## Deterministic Markdown Table Aligner Integration

This skill authors terminology content but delegates every file create/update to `doc-this`, which is the real file-ownership boundary. Require `doc-this` to invoke `markdown-table-aligner` after semantic content is complete and before the final save whenever the document contains Markdown tables. Do not run a redundant second formatting pass above or below that owner boundary.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

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

## Boundaries

Do not reimplement `doc-this` numbering, path resolution, or house style; hardcode `N`; treat either filename form as defective; rename or renumber existing documents for conformity; leave the opening term list or One-Line Summary stale; apply the three-pass rule to structural sections; create a Terminology finalizer or lifecycle; modify unrelated Terminology documents; or guess missing historical attribution.

## Validation

- Run the official `quick_validate.py` against this folder with Python `-X utf8`, keeping stdout and stderr separate and deciding pass/fail from the exit code.
- Confirm Mode A delegates placement, numbering, house style, and the write to `doc-this`.
- Confirm Mode B states an inferred target, preserves the existing document, and updates the term list plus One-Line Summary.
- Confirm both filename forms are valid and `N` is never hardcoded.
- Confirm term sections require the three passes in fixed order while structural sections are exempt and optional extra passes remain allowed.
- Confirm `doc-this` is hard, `analogy` and `for-dummies` have soft fallbacks, and the README names every shipped dependency.
- Confirm the canonical Exact Model Attribution block is byte-identical to its source and passes the shared carrier validator.
- Confirm the Markdown Table Alignment rule remains complete and `doc-this` owns the deterministic aligner call at the file boundary.
- Smoke-test these decisions: create for a new subject; add one term to an obvious conversational target; add several terms; reject a duplicate; ask when two targets plausibly match; preserve a legacy filename and extra-pass section.
