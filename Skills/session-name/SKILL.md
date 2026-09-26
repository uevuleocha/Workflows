---
name: session-name
description: Suggest exactly eight direct, context-rich chat-session names grounded in the session's narrative center, meaningful change, outcome, distinguishing context, and strongest evidence. Use when the user invokes /session-name, asks to name the chat, requests eight session names, or asks for longer names. Draft the eight visible options directly without a larger candidate pool, rank the strongest overall name first, and never default to a From-X-to-Y opening. Every label begins with an uppercase display word. Selection and opt-in N.) prefix are optional. Mechanically enforce Codex's 60-character cap, Antigravity/Gemini's 70-character cap, and Hermes's 100-character cap including any prefix, plus the Claude/zCode 240-character default excluding the prefix. Suggestion-only; never renames a chat or creates a file.
---

# Session Name

Offer exactly eight grounded, naturally varied, context-rich **chat-session names** - the labels shown in a platform's session sidebar or UI. Delivering the eight suggestions completes this one-shot helper. The user's eventual selection is private and optional; nothing is renamed and nothing is written to disk.

## Invocation

Treat these as direct invocation and begin the skill:

- `/session-name`
- `use session-name`
- `use the session-name skill`
- "name this session"
- "give me session name options"
- "suggest a name for this chat"
- "top eight names for this session"
- clear equivalents asking for chat-session-name suggestions

The skill may be invoked at session end or midway through a session. It may also be co-invoked with other work; its output is never a checkpoint or early-return condition.

## When Not To Use It

- Naming a file, plan, task, prompt, or report -> use the relevant artifact-owning skill.
- Writing a session recap -> use `session-summary`. The two skills may run together, but neither waits for the other.

## Workflow

1. **Establish the host and governing budget before drafting.** Resolve one of these rules from known host context only:
   - Codex: 60 characters including any optional prefix.
   - Antigravity/Gemini: 70 characters including any optional prefix.
   - Hermes: 100 characters including any optional prefix.
   - Claude/zCode: 240 characters by default, excluding any optional prefix.
   If the host is genuinely unknown, use the most restrictive relevant cap and state the assumption. Never investigate or probe the host.
2. **Read the session.** Review what the conversation actually did: the principal subject, work performed, problem or motivation, decisions made, constraints preserved, outcomes reached, scope covered, and evidence produced. Never invent a generic angle.
3. **Resolve the optional prefix without asking a preliminary question.** The `N.)` identifier is opt-in and is never guessed.
   - A supplied parent or lowercase-child identifier is used verbatim on all eight options: `17a` becomes `17a.)`.
   - An explicit no-prefix request omits it.
   - Silence about a prefix means the opt-in was not exercised; emit unprefixed suggestions without asking.
   - A prefix request with no identifier produces unprefixed suggestions plus one brief omission note; never stop or ask.
4. **Build the session fact map.** Capture only facts supported by the conversation, using these lenses when applicable:
   - primary subject, artifact, system, or question;
   - meaningful action or change;
   - problem, motivation, or previous limitation;
   - concrete outcome;
   - distinguishing decision, constraint, or tradeoff;
   - scope, reach, or affected environments; and
   - strongest verification or real-world evidence.
   Omit lenses that add no real information. This map is working context, not user-facing output.
5. **Resolve the narrative center.** Rank the facts by what mattered most to the user and identify the clearest account of what the session was really about. Prefer causal meaning over chronology and significance over a list of milestones. The narrative center normally combines the primary subject with the meaningful change or outcome and the context that makes it distinctive.
6. **Draft exactly eight names directly.** Do not draft a larger candidate pool, brainstorm 12-16 alternatives, or expose discarded candidates. Produce the eight deliverable names in one generation pass from the fact map and narrative center. Each name may emphasize a different truthful interpretation, but no fixed option number owns a required angle.
7. **Apply the context-quality gate.** Every option must be independently useful and should normally identify:
   - the primary subject; and
   - the meaningful action, change, outcome, or distinguishing evidence.
   For a substantial session, add the highest-value supporting facts that explain why the work mattered or how it was proven. Reject shallow variants that merely reshuffle `built`, `shipped`, `completed`, `validated`, or similar milestone words around the same nouns. Rank the strongest overall representation first, then order the remaining options by usefulness rather than by template.
8. **Apply the language-quality gate.** Names must sound natural, direct, descriptive, and sensible. Avoid stitched clauses, inflated claims, generic headlines, repeated sentence skeletons, and artificial synonyms. Do not default to an opening shaped as `From X to Y`; use journey framing only when the user explicitly requests it. Material distinctness is semantic: two names are not meaningfully different merely because their word order changed.
9. **Apply earned detail for the host.** Character ceilings are limits, not universal target lengths.
   - On Claude and zCode, do not compress a substantial session into capped-host labels merely because shorter names fit. Use the available 240-character budget for grounded context when that context helps the name capture the session. There is no minimum length, and thin sessions still deserve concise names.
   - On Codex, Antigravity/Gemini, and Hermes, preserve the narrative center and highest-value distinguishing facts through density: precise verbs, compact compounds, and removal of scaffolding. Never truncate words or drop the session's central meaning merely to fit.
   - Natural variation is expected. Never pad names, force uniform lengths, or cluster all eight near a ceiling.
10. **Measure every complete label before emitting.** Count mechanically, never by eye.
    - Codex: count the complete paste-ready label including the optional prefix; require `<= 60`.
    - Antigravity/Gemini: count the complete paste-ready label including the optional prefix; require `<= 70`.
    - Hermes: count the complete paste-ready label including the optional prefix; require `<= 100`.
    - Claude/zCode: count the descriptive label excluding the optional prefix; require `<= 240` unless the user explicitly requested longer names.
    The presentation list numbers `1. ` through `8. ` are excluded. Rewrite and recount any invalid label. Do not emit until all eight pass.
11. **Emit all eight and continue.** Delivering the eight valid suggestions is terminal success for `session-name`. Never ask the user to choose, wait for a selection, or leave co-invoked work pending.

## Naming Rules

- **Exactly eight visible suggestions.** Generate those eight directly. Never create a hidden 12-16-option pool.
- **Narrative-center fidelity.** The set must capture what the session was actually about, not merely inventory completed steps.
- **Subject plus meaning.** Every option should normally name the subject and the meaningful change, outcome, or evidence.
- **Strongest first.** Option 1 is the best overall representation, not a compulsory angle.
- **No fixed slots.** No option is required to be outcome-led, artifact-led, method-led, headline-led, or a synthesis of earlier options.
- **No default journey opening.** Never begin with `From ... to ...` unless the user explicitly asks for that construction.
- **Uppercase display start.** After any optional prefix, the first descriptive word begins with an uppercase letter. Preserve intentionally lowercase identifiers such as `session-name`, `npm`, or `zCode` when they occur later; rewrite the lead naturally rather than altering canonical casing.
- **Grounded and materially distinct.** Each option communicates a different useful interpretation or emphasis without inventing facts.
- **Earned detail.** Rich sessions receive more grounded context where the host permits it; length never substitutes for meaning.
- **Natural length variation.** A maximum is neither a quota nor a target band. Never shorten a valid name solely to create margin, and never pad one to consume capacity.
- **Suggestion-only.** Never rename, archive, close, or mutate the platform session.

## Host Length Rules

- **Codex:** 60-character hard cap for the complete label, including any optional prefix, spaces, and punctuation. Exactly 60 passes; 61 fails.
- **Antigravity/Gemini:** 70-character hard cap for the complete label, including any optional prefix, spaces, and punctuation. Exactly 70 passes; 71 fails.
- **Hermes:** 100-character hard cap for the complete label, including any optional prefix, spaces, and punctuation. Exactly 100 passes; 101 fails.
- **Claude/zCode:** 240-character default maximum for the descriptive label, excluding any optional prefix. Substantial sessions may use more of this capacity when grounded context earns it.
- **Longer general-host refinement:** on Claude and zCode, an explicit request for longer, richer, expanded, or more detailed names overrides the 240-character default when useful. The user need not supply another maximum. The new eight may exceed 240 reasonably, but must remain useful rather than padded or rambling. This refinement never overrides the Codex, Antigravity/Gemini, or Hermes hard caps.
- **Presentation numbering:** the visible `1. ` through `8. ` list numbers are never part of the pasted label or any host count.

## Selection And Co-Invocation

- Selection is private, optional, and outside this skill's completion contract.
- A later voluntary selection may be acknowledged naturally but changes no state.
- A later request for longer names is a fresh refinement that immediately emits eight expanded suggestions without asking for a character maximum.
- When co-invoked, emit the names at an appropriate point and continue the remaining work in the same turn.

## Mid-Session Use

When invoked midway through a session, name only the work completed so far and briefly note that the name may evolve if the focus changes. Still emit exactly eight suggestions and complete without requesting a selection.

## Output Shape

Use a simple numbered list:

```text
Eight session-name suggestions:

1. [best overall context-rich name]
2. [materially distinct grounded name]
3. [materially distinct grounded name]
4. [materially distinct grounded name]
5. [materially distinct grounded name]
6. [materially distinct grounded name]
7. [materially distinct grounded name]
8. [materially distinct grounded name]
```

With a supplied identifier, every pasted label carries the identical verbatim prefix. Without one, every label is unprefixed. If a requested prefix lacked an identifier, add one brief omission note before or after the list, then continue any co-invoked work.

## Compression Example

A capped-host breach is made denser rather than truncated:

```text
FAIL: 48.) Autonomous GitHub Sync Was Fully Implemented and Then Successfully Proven Across Two Different zCode Workspaces
PASS: 48.) Autonomous GitHub Sync Proven Across Two zCode Workspaces
```

The passing label retains the narrative center and real-world evidence while removing scaffolding. Counts remain working notes and are never shown beside emitted suggestions unless the user asks.

## Failure Conditions

Any of these means the skill failed:

- Emitting other than exactly eight visible suggestions.
- Drafting a larger hidden candidate pool or spending output on discarded alternatives.
- Retaining fixed option slots or a foundation/synthesis dependency.
- Omitting the primary subject or meaningful session change from a name without a compelling natural-language reason.
- Producing shallow variants that repeat the same milestone sentence with reordered nouns or synonyms.
- Defaulting to a `From X to Y` opening without explicit user preference.
- Artificially compressing a substantial general-host session as though it had a capped-host limit.
- Padding a name, inventing context, or using length as a substitute for meaning.
- Emitting any label over its governing cap or visually estimating a capped label instead of measuring it.
- Truncating a word, guessing or altering an identifier, beginning with a lowercase descriptive word, or claiming the chat was renamed.

## Behavior Scenarios

1. **No prefix preference:** emit eight unprefixed suggestions immediately.
2. **Explicit no-prefix:** emit eight unprefixed suggestions immediately.
3. **Prefix requested without identifier:** emit eight unprefixed suggestions plus the omission note.
4. **Parent identifier:** preserve `37` verbatim as `37.)` on all eight.
5. **Child identifier:** preserve `37b` verbatim as `37b.)` on all eight.
6. **Direct generation:** draft exactly eight deliverable options; create no larger candidate pool.
7. **Dense completed session:** use the fact map and narrative center to include meaningful context, outcome, and evidence rather than a milestone inventory.
8. **Thin session:** remain concise; do not pad toward a host ceiling.
9. **No useful method angle:** do not manufacture one and do not reserve an option for it.
10. **Journey framing not requested:** no option begins with `From ... to ...`.
11. **Journey framing requested:** the construction may be used when grounded and natural.
12. **Codex with prefix:** mechanically verify all eight complete labels are at most 60.
13. **Antigravity with prefix:** mechanically verify all eight complete labels are at most 70.
14. **Hermes with prefix:** mechanically verify all eight complete labels are at most 100.
15. **General host:** mechanically verify every descriptive label is at most 240 by default, excluding the prefix.
16. **Exactly-at-cap label:** accept 60, 70, 100, or 240 under the governing accounting rule without shortening for margin.
17. **Over-cap label:** rewrite densely and recount; never truncate or emit with an apology.
18. **Lowercase technical identifier:** use an uppercase natural lead and preserve canonical casing later.
19. **Longer general-host request:** immediately provide eight richer names that may reasonably exceed 240 without requesting another maximum; capped-host limits remain binding.
20. **No selection reported:** treat the invocation as complete after option 8.
21. **Co-invoked work:** emit all eight and continue without pausing.

## Related Skills

- `finalize-session` calls `session-name` and `session-summary` in one pass while supplying the chat-session identifier as the verbatim prefix.
- `session-summary` writes the independent durable recap; neither workflow waits for a reported name selection.
- Artifact-owning skills name plans, tasks, prompts, reports, and files; `session-name` labels only the platform chat.

## Validation

When creating or updating this skill:

- run `python -X utf8 scripts/test_session_name_contract.py` and require exit 0;
- run the official folder validator in Python UTF-8 mode and require exit 0 with empty stderr;
- confirm exactly eight direct outputs, no larger candidate pool, no fixed option slots, and no foundation/synthesis dependency;
- confirm the fact map, narrative center, subject-plus-meaning gate, strongest-first ordering, earned-detail behavior, and anti-shallow-rephrasing rules remain explicit;
- confirm journey framing is prohibited by default and no worked example models a `From X to Y` opening;
- exercise Codex, Antigravity/Gemini, Hermes, and general labels with prefixes and mechanically confirm their respective 60-including-prefix, 70-including-prefix, 100-including-prefix, and 240-excluding-prefix rules;
- confirm exactly-at-cap labels pass and one-over labels fail under each accounting rule;
- confirm optional prefix, uppercase display start, longer general-host refinement, selection-optional behavior, and suggestion-only scope remain intact; and
- confirm `README.md` and `agents/openai.yaml` describe the same direct, context-rich eight-option behavior.
