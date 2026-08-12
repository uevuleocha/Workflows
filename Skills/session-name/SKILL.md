---
name: session-name
description: Suggest exactly eight descriptive, naturally varied chat-session names grounded in the current session. Use when the user invokes /session-name, use session-name, asks to name the chat, requests eight session names, or asks for longer names. Options 1-4 lead with Outcome, Artifact/Tool, Method, and Headline Result; options 5-8 adaptively synthesize their strongest material. Every label begins with an uppercase display word. Selection and opt-in N.) prefix are optional. Establish the host cap before drafting, then mechanically count every complete label before emitting. Antigravity/Gemini caps at 70 characters including any prefix; Hermes at 100 including any prefix. Both caps are absolute and the full budget is usable — exactly at the cap passes, one over fails. On capped hosts, options 5-8 integrate more densely, never more lengthily. Other hosts (Claude, Codex, zCode) default to 240 excluding prefix. Suggestion-only — never renames a chat or creates a file.
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

1. **Establish the host and the governing budget before drafting anything.** Name the current host and state its cap explicitly to yourself — `Antigravity/Gemini: 70 including prefix`, `Hermes: 100 including prefix`, or `Claude/Codex/zCode: 240 excluding prefix (default)`. Use only known host context; never probe or investigate the host. On a capped host, the entire budget is usable: a label at exactly 70 or exactly 100 is fully valid. Do not reserve a safety margin, do not aim below the cap, and do not compress a label that already fits. The cap is a wall, not a target to stay clear of. If the host is genuinely unknown, apply the most restrictive relevant cap and say which one you assumed.
2. **Read the session.** Review what this conversation actually did so far — work performed, decisions made, problems solved, artifacts handled, and outcomes reached. Use only grounded session content; never invent a generic angle.
3. **Resolve the optional prefix without asking a preliminary question.** The `N.)` session-identifier prefix is opt-in and identifiers are never guessed.
   - If the user supplies an identifier or clearly says "this is session 20," use that identifier **verbatim** on all eight options. Preserve lowercase child suffixes: `17a` becomes `17a.)`, never `17.)`.
   - If the user explicitly declines a prefix, omit it.
   - If the user says nothing about a prefix, treat the opt-in as not exercised and produce eight unprefixed suggestions without asking.
   - If the user explicitly requests a prefix but supplies no identifier, produce eight unprefixed suggestions, briefly note that the prefix was omitted because no identifier was supplied, and continue. Never stop, ask, wait, infer, or guess.
4. **Draft options 1-4 as the foundation set.** Each option may combine any applicable facets, but it must lead with its assigned facet and remain meaningfully distinct:
   1. **Outcome-led** — lead with what the session accomplished.
   2. **Artifact/Tool-led** — lead with the principal artifact, system, or tool while still beginning with an uppercase display word. If the canonical identifier is lowercase, rewrite the lead naturally rather than placing that identifier first; for example, use `Session-Name Skill Upgraded ...`, not `session-name Upgraded ...`.
   3. **Method-led** — lead with the approach, workflow, or technique.
   4. **Headline Result-led** — lead with the strongest newsworthy result.
5. **Draft options 5-8 as adaptive syntheses.** Write these only after considering options 1-4. For each synthesis, identify complementary strengths, facts, phrases, and emphasis from the foundation set, then rewrite them into one cohesive, natural name that usually communicates a richer integration than any single foundation angle. Reorganize, expand, compress, sharpen, or newly phrase grounded material when useful. Because a synthesis may carry more integrated information, it may naturally be longer than options 1-4 **on uncapped hosts only (Claude, Codex, zCode)**, and even there literal extra length is never mandatory. **On a capped host (Antigravity/Gemini or Hermes), richness is expressed through density, never through extent.** A synthesis proves itself by carrying more meaning per character, not by occupying more characters — use a compound term in place of a clause, one precise verb in place of a weak verb plus adverb, and cut scaffolding words that carry no session-specific information. Never let synthesis ambition push a label toward or past the cap; a synthesis that will not fit is compressed, never truncated and never allowed to overflow. It must not mechanically concatenate fragments, repeat a foundation option, pad wording, inflate the outcome, or introduce ungrounded claims. Options 5-8 must differ materially from one another.
6. **Apply the host length and user-preference rules to each complete label.** Include any visible list number and optional session prefix only as specified below. Do not compress every option into a uniform length band; let the session substance, foundation angle, synthesis depth, host, and any explicit request for longer names determine natural variation.
7. **Measure every complete label before emitting — a hard gate, not a review.** On a capped host (Antigravity/Gemini or Hermes) this step is compulsory and blocking. Count each complete label exactly as it will be pasted: the optional `N.) ` prefix, every space, and every punctuation mark, with only the presentation list number (`1. ` through `8. `) excluded. **Count mechanically, never by eye** — run a one-line script or equivalent deterministic count. Visual length estimation is unreliable in the 60-110 character range, which is precisely where these caps sit and precisely where the failure occurs. Any label over budget is **invalid**: rewrite it by the density rules below, re-count it, and repeat until it fits. Do not emit any suggestion until all eight have been counted and all eight pass. On uncapped hosts, confirm the 240-character default is respected unless the user asked for longer names.
8. **Emit all eight suggestions and continue.** Delivering the eight valid suggestions is terminal success for `session-name`. Never ask the user to choose, promise later confirmation, wait for a response, or leave any turn, task, workflow, delegation, goal, or co-invoked skill pending because no selection was reported. Continue all co-invoked work in the same turn.

## Naming Style And Length Rules

- **Exactly eight.** Options 1-4 are the four foundation angles; options 5-8 are four adaptive syntheses. No more and no fewer.
- **Uppercase display start.** After any optional `N.)` prefix, the first descriptive word of every option must begin with an uppercase letter. This applies especially to Artifact/Tool-led option 2. Preserve the canonical casing of intentionally lowercase technical identifiers such as `session-name`, `npm`, or `zCode` when they appear later in the label; if one would otherwise lead, prepend or rewrite with an uppercase natural descriptor instead of altering the identifier or allowing a lowercase start.
- **Grounded and distinct.** Every option must accurately reflect the current session and provide a useful alternative emphasis.
- **Natural rather than stitched.** Options 5-8 must read as newly composed names, not joined clauses copied from options 1-4.
- **Natural length variation.** Do not force all eight names toward the same length. Foundation options may stay focused; synthesis options may use more space when their richer integration earns it. Semantic richness matters more than character count, so options 5-8 do not have to be longer and no option may be padded merely to create a length difference. **On a capped host, eight labels all clustered within a few characters of the cap is a warning sign** — it indicates the set was drafted by eye toward the ceiling rather than measured, which is the exact pattern that precedes an overflow.
- **The full budget is usable; the cap is absolute.** On capped hosts, every character up to and including the cap is available — 70 on Antigravity/Gemini and 100 on Hermes are valid lengths, not near-misses. Do not hold back a safety margin, do not target a lower band, and do not shorten a label that already fits. Equally, there is no tolerance above the line: one character over is a failure.
- **On Antigravity / Gemini: 70-character hard cap for the complete paste-ready option, including any `N.)` prefix, spaces, and punctuation.** Use only known host context; do not probe or investigate Antigravity or Gemini. Measure after applying the prefix. Compress intelligently until every option fits cleanly without cutting words, truncating UI text, or removing the facts that make the options distinct.
- **On Hermes: 100-character hard cap for the complete paste-ready option, including any `N.)` prefix, spaces, and punctuation.** Use only known host context; do not probe or investigate Hermes. Measure after applying the prefix. Compress intelligently until every option fits without cutting words or removing the facts that make the options distinct.
- **On other hosts (Claude, Codex, zCode): 240-character default maximum excluding the optional session prefix.** Stay at or below 240 characters by default. This is a maximum, not a quota: a thin session still deserves shorter names, while a substantial session should not be compressed merely to keep every option inside an Antigravity/Hermes-like range.
- **On other hosts (Claude, Codex, zCode), an explicit request for longer names overrides the default maximum when useful.** The user may ask for longer, richer, more detailed, or expanded names either in the original invocation or after receiving the first eight. The user does not need to specify a character count or replacement maximum, and the agent must not ask for one. Produce eight reasonably expanded, still useful names; they may exceed 240 characters when the added grounded detail earns it, but never become rambling, padded, or unreasonable.
- **List numbering is presentation, not part of the pasted label.** The Antigravity (70-char) and Hermes (100-char) caps apply to the label after `1. ` through `8. ` is removed, but include a supplied session prefix such as `17a.) `.

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

### Capped-host worked example (Hermes, 100 including prefix)

The block above is deliberately long because it demonstrates the uncapped 240-character budget. **Do not anchor on it when the host is capped.** The measured Hermes set below is the reference for that case. Foundation options stay focused, syntheses integrate more densely rather than more lengthily, and every complete label was counted mechanically with the `42.) ` prefix applied:

```text
1. 42.) Finalize-Session Skill Built, Synced to Five Platforms, Parity Verified          (76)
2. 42.) Finalize-Session Orchestrator Links Chat Naming to Durable ACTS Summaries        (78)
3. 42.) Local-First Build, Scenario Validation, Five-Platform Sync, Parity Check         (77)
4. 42.) One Invocation Now Names a Session and Writes Its Summary, Renaming Nothing      (80)
5. 42.) From Prompt 13 to a Verified Global Skill: Thin Orchestration, Duplicate-Safe Resume  (89)
6. 42.) Finalize-Session Unifies Rich Naming and Durable Summaries Behind One Preflighted Call  (91)
7. 42.) A Thin Wrapper Drives Two Independent Skills, Preserves Host Caps, Ships Fleet-Wide  (88)
8. 42.) Combined Session Closure End to End: Adaptive Naming, ACTS Artifact, Verified Handoff  (90)
```

The parenthetical counts are working notes for the measurement gate, not part of the emitted output — strip them before showing the user. The Antigravity/Gemini equivalent follows the same discipline against a 70-character budget.

**Compression worked example.** A synthesis that overruns is made denser, never truncated and never shipped over. A real Hermes breach ran 102 characters unprefixed, 106 with the prefix:

```text
3.) LTNEY Read Permission Hardened, Transitive Reads Codified, and Language Policy Strengthened Fleet-Wide   (106 - FAIL)
3.) LTNEY Reads Made Absolute and Transitive, Fleet-Wide Language Policy                                    (70 - PASS)
```

`Read Permission Hardened` becomes `Reads Made Absolute`; `Codified` is dropped because a list of changes already implies it; `Language Policy Strengthened Fleet-Wide` becomes `Fleet-Wide Language Policy`. All three facts survive — the label got denser, not thinner.

## Failure Conditions

Any of the following is a failure of this skill, regardless of how good the names otherwise are:

- **Emitting any label that exceeds the host cap.** Over 70 on Antigravity/Gemini or over 100 on Hermes, measured with the prefix applied, is a failure even by one character and even when the excess carried genuine grounded richness. Silent sidebar truncation is the harm the cap exists to prevent.
- **Emitting on a capped host without having counted mechanically.** An uncounted set is a failure even when it happens to fit; correctness by luck is not correctness.
- **Estimating length visually on a capped host** instead of running a deterministic count.
- **Anchoring on the uncapped 240-character example while on a capped host.**
- **Truncating or dropping a grounded fact to fit** when denser phrasing would have preserved it.
- **Artificially shortening a label that already fits** in order to hold a margin below the cap.
- Emitting other than exactly eight options, a lowercase first descriptive word, a guessed or altered session identifier, or any claim that the chat was renamed.

## Behavior Scenarios

1. **No prefix preference stated:** emit eight unprefixed suggestions immediately; ask nothing.
2. **Explicit no-prefix:** emit eight unprefixed suggestions immediately.
3. **Prefix requested without an identifier:** emit eight unprefixed suggestions plus the brief omission note; do not stop.
4. **Parent identifier supplied:** `37` is used verbatim as `37.)` on all eight labels.
5. **Child identifier supplied:** `37b` is used verbatim as `37b.)` on all eight labels.
6. **No selection reported:** the invocation is complete after the eighth suggestion.
7. **Selection voluntarily reported later:** acknowledge naturally if useful; change no state and require no follow-up.
8. **Co-invoked work:** emit the eight labels at an appropriate point and continue the other requested work in the same turn.
9. **Antigravity / Gemini without a prefix:** verify all eight complete labels are at most 70 characters to prevent silent UI truncation.
10. **Antigravity / Gemini with a prefix:** apply the verbatim prefix, then verify all eight complete labels are still at most 70 characters.
11. **Hermes without a prefix:** verify all eight complete labels are at most 100 characters.
12. **Hermes with a prefix:** apply the verbatim prefix, then verify all eight complete labels are still at most 100 characters.
13. **Other hosts (Claude, Codex, zCode), normal request:** keep each label at or below the 240-character default maximum excluding the optional prefix, with natural variation rather than artificial uniformity.
14. **Platform mutation boundary:** suggest labels only; never rename, claim a rename, probe capabilities, or ask to investigate renaming.
15. **Lowercase artifact identifier:** when option 2 would naturally lead with `session-name`, `npm`, `zCode`, or another lowercase identifier, begin with an uppercase descriptor such as `Session-Name Skill`, `Package Workflow with npm`, or `Global zCode Integration`; never emit a lowercase first descriptive word.
16. **Longer names requested initially outside Antigravity/Hermes:** provide eight reasonably expanded names, allow useful labels above 240 characters, and ask no character-count question.
17. **Longer names requested after the first eight outside Antigravity/Hermes:** immediately provide a fresh set of eight materially longer or more detailed names within good reason; the earlier invocation remains complete.
18. **Synthesis length and richness on uncapped hosts:** options 5-8 normally integrate more information and may be longer than options 1-4, but no mechanical length ordering or padding is required. This allowance applies only to Claude, Codex, and zCode.
19. **Synthesis length and richness on capped hosts:** on Antigravity/Gemini and Hermes, options 5-8 integrate more densely rather than more lengthily; the "may be longer" allowance in Scenario 18 does not apply, and exceeding the cap is a failure regardless of how much grounded richness the extra characters carried.
20. **Capped-host measurement:** every complete label is counted mechanically, including the prefix, before any suggestion is emitted; an over-budget label is rewritten and re-counted rather than emitted with an apology.
21. **Label at exactly the cap:** a 70-character Antigravity label or a 100-character Hermes label passes; do not shorten it to create margin.

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

### Antigravity / Gemini

> **Context:** Current host is Antigravity (Gemini) and the user supplied `37b`.
> **Agent:** Produces eight labels beginning `37b.) ` and verifies each complete label is at most 70 characters after the prefix is applied. It compresses wording naturally so no title is silently cut off in the sidebar UI.

### Hermes

> **Context:** Current host is Hermes and the user supplied `37b`.
> **Agent:** Produces eight labels beginning `37b.) ` and verifies each complete label is at most 100 characters after the prefix is applied. It compresses wording naturally rather than truncating words.

### Longer refinement outside Antigravity/Hermes without a supplied maximum

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

When creating or updating this skill, validate the folder with `quick_validate.py` in Python UTF-8 mode. Exercise every Behavior Scenario; confirm exactly eight outputs with the required foundation/synthesis ordering; verify every first descriptive word starts uppercase even when option 2 represents a lowercase technical identifier; confirm normal names on other hosts (Claude, Codex, zCode) stay within the 240-character default maximum; confirm a plain request for longer names on other hosts needs no user-supplied maximum and may reasonably exceed 240; confirm the set varies naturally in length and synthesis richness without padding; record final Antigravity (70-char) and Hermes (100-char) label lengths after prefixes are applied; confirm no blocking or rename language remains; and verify all coupled metadata agrees with this file.

Additionally, exercise the capped-host hardening explicitly:

- confirm Workflow step 1 establishes the host and its governing budget before any drafting occurs;
- confirm Workflow step 7 blocks emission until all eight complete labels have been counted, and that the count is described as mechanical rather than visual;
- simulate a Hermes run with a supplied prefix and verify all eight complete labels measure at most 100 characters with the prefix applied;
- simulate an Antigravity/Gemini run with a supplied prefix and verify all eight measure at most 70;
- confirm a label sitting exactly at 70 or exactly 100 is accepted without being shortened for margin;
- confirm an over-budget synthesis is resolved by denser phrasing that preserves every grounded fact, not by truncation or fact removal;
- confirm the "syntheses may be longer" allowance is scoped to uncapped hosts only and that the Failure Conditions section names cap overflow as a failure;
- confirm the capped-host worked example is present alongside the uncapped one, so a capped-host run has a correctly sized exemplar to anchor on; and
- confirm the uncapped path (Claude, Codex, zCode - 240 default, longer on request) is unchanged by the capped-host hardening.
