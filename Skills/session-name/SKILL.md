---
name: session-name
description: Suggest exactly eight descriptive, naturally varied chat-session names grounded in the current session. Use when the user invokes /session-name, use session-name, asks to name the chat, requests eight session names, or asks for longer names initially or as a later refinement. Options 1-4 lead with Outcome, Artifact/Tool, Method, and Headline Result; options 5-8 adaptively synthesize their strongest material and may carry richer integrated detail. Every label begins with an uppercase display word. Selection and the opt-in N.) prefix are optional and non-blocking. Outside Hermes, 240 characters excluding any prefix is the default maximum; a plain request for longer names may reasonably exceed it without a user-supplied character count. On Hermes, every complete label is at most 100 characters including any prefix. Suggestion-only — it never renames a chat or creates, moves, or renames a file.
---

# Session Name

Offer exactly eight grounded suggestions for a descriptive, naturally varied **chat-session name** — the label shown in the platform's session sidebar/UI. Delivering the eight suggestions completes this one-shot helper. The user's eventual selection is private and optional; nothing is renamed and nothing is written to disk.

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

The skill may be invoked at **session end** or **midway through** a session. It may also be co-invoked with other work; its output is never a checkpoint or early-return condition.

## When NOT to use it

- **Naming a file, plan, task, prompt, or report** → use the relevant `-this` skill (`plan-this`, `task-this`, `prompt-this`, or `report-this`). `session-name` labels only the chat session.
- **A written recap of the session** → use `session-summary`. The two skills may run together, but neither depends on the other and a session-name selection is never compulsory summary input.

## Workflow

1. **Read the session.** Review what this conversation actually did so far — work performed, decisions made, problems solved, artifacts handled, and outcomes reached. Use only grounded session content; never invent a generic angle.
2. **Resolve the optional prefix without asking a preliminary question.** The `N.)` session-identifier prefix is opt-in and identifiers are never guessed.
   - If the user supplies an identifier or clearly says "this is session 20," use that identifier **verbatim** on all eight options. Preserve lowercase child suffixes: `17a` becomes `17a.)`, never `17.)`.
   - If the user explicitly declines a prefix, omit it.
   - If the user says nothing about a prefix, treat the opt-in as not exercised and produce eight unprefixed suggestions without asking.
   - If the user explicitly requests a prefix but supplies no identifier, produce eight unprefixed suggestions, briefly note that the prefix was omitted because no identifier was supplied, and continue. Never stop, ask, wait, infer, or guess.
3. **Draft options 1-4 as the foundation set.** Each option may combine any applicable facets, but it must lead with its assigned facet and remain meaningfully distinct:
   1. **Outcome-led** — lead with what the session accomplished.
   2. **Artifact/Tool-led** — lead with the principal artifact, system, or tool while still beginning with an uppercase display word. If the canonical identifier is lowercase, rewrite the lead naturally rather than placing that identifier first; for example, use `Session-Name Skill Upgraded ...`, not `session-name Upgraded ...`.
   3. **Method-led** — lead with the approach, workflow, or technique.
   4. **Headline Result-led** — lead with the strongest newsworthy result.
4. **Draft options 5-8 as adaptive syntheses.** Write these only after considering options 1-4. For each synthesis, identify complementary strengths, facts, phrases, and emphasis from the foundation set, then rewrite them into one cohesive, natural name that usually communicates a richer integration than any single foundation angle. Reorganize, expand, compress, sharpen, or newly phrase grounded material when useful. Because a synthesis may carry more integrated information, it may naturally be longer than options 1-4, but literal extra length is never mandatory. It must not mechanically concatenate fragments, repeat a foundation option, pad wording, inflate the outcome, or introduce ungrounded claims. Options 5-8 must differ materially from one another.
5. **Apply the host length and user-preference rules to each complete label.** Include any visible list number and optional session prefix only as specified below. Do not compress every option into a uniform length band; let the session substance, foundation angle, synthesis depth, host, and any explicit request for longer names determine natural variation.
6. **Emit all eight suggestions and continue.** Delivering the eight valid suggestions is terminal success for `session-name`. Never ask the user to choose, promise later confirmation, wait for a response, or leave any turn, task, workflow, delegation, goal, or co-invoked skill pending because no selection was reported. Continue all co-invoked work in the same turn.

## Naming Style And Length Rules

- **Exactly eight.** Options 1-4 are the four foundation angles; options 5-8 are four adaptive syntheses. No more and no fewer.
- **Uppercase display start.** After any optional `N.)` prefix, the first descriptive word of every option must begin with an uppercase letter. This applies especially to Artifact/Tool-led option 2. Preserve the canonical casing of intentionally lowercase technical identifiers such as `session-name`, `npm`, or `zCode` when they appear later in the label; if one would otherwise lead, prepend or rewrite with an uppercase natural descriptor instead of altering the identifier or allowing a lowercase start.
- **Grounded and distinct.** Every option must accurately reflect the current session and provide a useful alternative emphasis.
- **Natural rather than stitched.** Options 5-8 must read as newly composed names, not joined clauses copied from options 1-4.
- **Natural length variation.** Do not force all eight names toward the same length. Foundation options may stay focused; synthesis options may use more space when their richer integration earns it. Semantic richness matters more than character count, so options 5-8 do not have to be longer and no option may be padded merely to create a length difference.
- **Outside Hermes: 240-character default maximum excluding the optional session prefix.** Stay at or below 240 characters by default. This is a maximum, not a quota: a thin session still deserves shorter names, while a substantial session should not be compressed merely to keep every option inside a Hermes-like range.
- **Outside Hermes, an explicit request for longer names overrides the default maximum when useful.** The user may ask for longer, richer, more detailed, or expanded names either in the original invocation or after receiving the first eight. The user does not need to specify a character count or replacement maximum, and the agent must not ask for one. Produce eight reasonably expanded, still useful names; they may exceed 240 characters when the added grounded detail earns it, but never become rambling, padded, or unreasonable.
- **On Hermes: 100-character hard cap for the complete paste-ready option, including any `N.)` prefix, spaces, and punctuation.** Use only known host context; do not probe or investigate Hermes. Measure after applying the prefix. Compress intelligently until every option fits without cutting words or removing the facts that make the options distinct.
- **List numbering is presentation, not part of the pasted label.** The Hermes cap applies to the label after `1. ` through `8. ` is removed, but includes a supplied session prefix such as `17a.) `.

## Selection And Co-Invocation Semantics

- The user's selection is private, optional, and outside this skill's completion contract.
- If the user voluntarily reports a selection later, acknowledge it naturally if useful. Do not treat it as a state transition, require confirmation, update a file, or reopen completed work.
- If the user later asks for longer names, treat that as a fresh optional refinement and immediately emit a new set of eight reasonably longer, more detailed suggestions. Do not ask the user to choose a maximum. The original invocation remains complete and was never pending.
- When co-invoked with another skill or task, place the eight names at an appropriate point and continue the remaining work in the same turn.
- A later `session-summary` may mention a voluntarily shared selection when useful, but neither workflow waits for or requires it.

## Mid-Session Use

When invoked midway through a session, name only the work **completed so far** and briefly note that the name may evolve if the focus changes. Still emit exactly eight suggestions and complete without asking for a selection.

## Scope And Safety

- **Suggestion-only and read-only.** Produce chat output only. Do not rename the chat, claim it was renamed, create or rename a file, probe automatic-renaming support, or ask to investigate platform-side renaming.
- **Platform-neutral.** Recommend paste-ready labels without claiming mutation capability in Claude, Codex, zCode, Hermes, Antigravity, or any other host.
- **One-shot helper, not a mode.** Emit no Mode footer of its own and do not persist. Obey any footer required by an active host mode.

## Output Shape

Use a simple numbered list. The representative block below is a **non-Hermes, information-rich session**; it intentionally demonstrates natural length variation and the larger non-Hermes budget. With a supplied identifier, every pasted label carries the identical verbatim prefix:

```text
Eight session-name suggestions:

1. 42.) Finalize-Session Skill Built, Locally Validated, Synchronized Across Five Agent Platforms, and Released with Verified Byte Parity
2. 42.) Finalize-Session Orchestrator Connects Eight-Option Chat Naming with Durable ACTS Summaries While Preserving Independent Child Skills
3. 42.) Local-First Skill Implementation, Scenario Validation, Five-Platform Synchronization, and Recursive Parity Verification Complete
4. 42.) One Invocation Now Produces Eight Non-Blocking Session Names and a Durable Summary Without Renaming or Pausing the Actual Chat
5. 42.) From Prompt 13 to a Verified Global Skill: Thin Orchestration, Compulsory Identifier Routing, Duplicate-Safe Resume, and Five-Platform Parity
6. 42.) Finalize-Session Unifies Rich Session Naming and Durable Summary Creation Through Dependency Preflight, Safe Number Routing, and Same-Pass Completion
7. 42.) A Thin Wrapper Now Coordinates Two Independent Skills, Preserves Hermes-Specific Limits, Prevents Cross-Turn Duplication, and Ships Identically Everywhere
8. 42.) Combined Session Closure Delivered End to End with Adaptive Name Synthesis, ACTS Artifact Ownership, Local Validation, Global Sync, and Verified Handoff
```

The list ends there for `session-name`; do not append a selection request. Without a prefix, omit `42.) ` from every label. If a requested prefix lacked an identifier, add one brief note before or after the list: `Prefix omitted because no session identifier was supplied.` Then continue any co-invoked work.

## Behavior Scenarios

1. **No prefix preference stated:** emit eight unprefixed suggestions immediately; ask nothing.
2. **Explicit no-prefix:** emit eight unprefixed suggestions immediately.
3. **Prefix requested without an identifier:** emit eight unprefixed suggestions plus the brief omission note; do not stop.
4. **Parent identifier supplied:** `37` is used verbatim as `37.)` on all eight labels.
5. **Child identifier supplied:** `37b` is used verbatim as `37b.)` on all eight labels.
6. **No selection reported:** the invocation is complete after the eighth suggestion.
7. **Selection voluntarily reported later:** acknowledge naturally if useful; change no state and require no follow-up.
8. **Co-invoked work:** emit the eight labels at an appropriate point and continue the other requested work in the same turn.
9. **Hermes without a prefix:** verify all eight complete labels are at most 100 characters.
10. **Hermes with a prefix:** apply the verbatim prefix, then verify all eight complete labels are still at most 100 characters.
11. **Non-Hermes host, normal request:** keep each label at or below the 240-character default maximum excluding the optional prefix, with natural variation rather than artificial uniformity.
12. **Platform mutation boundary:** suggest labels only; never rename, claim a rename, probe capabilities, or ask to investigate renaming.
13. **Lowercase artifact identifier:** when option 2 would naturally lead with `session-name`, `npm`, `zCode`, or another lowercase identifier, begin with an uppercase descriptor such as `Session-Name Skill`, `Package Workflow with npm`, or `Global zCode Integration`; never emit a lowercase first descriptive word.
14. **Longer names requested initially outside Hermes:** provide eight reasonably expanded names, allow useful labels above 240 characters, and ask no character-count question.
15. **Longer names requested after the first eight outside Hermes:** immediately provide a fresh set of eight materially longer or more detailed names within good reason; the earlier invocation remains complete.
16. **Synthesis length and richness:** options 5-8 normally integrate more information and may be longer than options 1-4, but no mechanical length ordering or padding is required.

## Examples

### Known child identifier

> **User:** Run session-name; this is session 17a.
> **Agent:** Immediately emits eight `17a.)`-prefixed options. Options 1-4 lead with Outcome, Artifact/Tool, Method, and Headline Result; options 5-8 adaptively synthesize their strongest grounded material. The `a` suffix is preserved verbatim. No selection is requested.

### Prefix requested without an identifier

> **User:** Run session-name and use the number prefix.
> **Agent:** Emits eight unprefixed options plus `Prefix omitted because no session identifier was supplied.` It then continues any co-invoked work without asking or waiting.

### Co-invocation

> **User:** Name this session and write the requested wrap-up.
> **Agent:** Emits eight suggestions and then continues the explicitly requested wrap-up workflow in the same turn. The naming output is not a checkpoint.

### Voluntary later selection

> **User:** I used option 6.
> **Agent:** May respond, `Nice choice — option 6 captures the transition clearly.` No confirmation workflow, state change, or file update follows.

### Hermes

> **Context:** Current host is Hermes and the user supplied `37b`.
> **Agent:** Produces eight labels beginning `37b.) ` and verifies each complete label is at most 100 characters after the prefix is applied. It compresses wording naturally rather than truncating words.

### Longer non-Hermes refinement without a supplied maximum

> **User:** These are good, but give me longer session names.
> **Agent:** Immediately emits a fresh set of eight reasonably longer, more detailed suggestions without asking for a character limit. It may exceed the ordinary 240-character default where grounded detail benefits, preserves natural variation, and does not treat the earlier set as incomplete.

### Refusal: naming a plan file

> **User:** Use session-name to name my new plan file.
> **Agent:** Explains that `session-name` only suggests chat labels and routes plan-file naming to `plan-this`.

## Related Skills

- `finalize-session` — the convenience caller that runs `session-name` and `session-summary` in one pass, supplying the chat-session identifier as this skill's verbatim `N.)` prefix. It orchestrates only; every rule in this file still governs. Standalone invocation is unaffected.
- `session-summary` — the independent durable recap; it may follow `session-name`, but neither workflow depends on a reported selection.
- `plan-this`, `task-this`, `prompt-this`, `report-this`, and their finalizers — the durable-artifact family. `session-name` creates no artifact and needs no finalizer.

## Validation

When creating or updating this skill, validate the folder with `quick_validate.py` in Python UTF-8 mode. Exercise every Behavior Scenario; confirm exactly eight outputs with the required foundation/synthesis ordering; verify every first descriptive word starts uppercase even when option 2 represents a lowercase technical identifier; confirm normal non-Hermes names stay within the 240-character default maximum; confirm a plain request for longer names needs no user-supplied maximum and may reasonably exceed 240; confirm the set varies naturally in length and synthesis richness without padding; record final Hermes label lengths after prefixes are applied; confirm no blocking or rename language remains; and verify all coupled metadata agrees with this file.
