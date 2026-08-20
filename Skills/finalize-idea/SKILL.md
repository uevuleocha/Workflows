---
name: finalize-idea
description: Move a completed idea from the subject's Archive/Live/Ideas/1.) Ideas.md to its Archive/Historical/Ideas/1.) Finalized Ideas.md, keeping its number unchanged, cleaning the entry for readability if it was written by hand, and reconciling that subject's Next idea number counter upward when a hand-written entry has left it stale. In Buzz mode, also finds that idea's Ideas-channel message by its number and subject and marks it done with a fixed set of ten reactions, never by editing the message. Use when the user invokes /finalize-idea, asks to finalize an idea, or marks an idea complete by number.
---

# Finalize Idea

Move a completed idea from the open inbox to the finalized page, preserving its permanent number. Finalizing moves an entry, not a file, and on the way it cleans the entry if it was hand-written and reconciles that subject's `Next idea number` counter.

`finalize-idea` never creates ideas, and `idea-this` never finalizes. Same separation as `plan-this` and `finalize-plan`.

## Project Contract

Obey the active workspace contract, permissions, safety rules, and UTF-8 requirements. This skill reads and edits the workspace idea files; it never modifies `wiki-schema.md` and never writes into `wiki/`.

## Invocation

Treat these as direct invocation:

- `/finalize-idea`
- `use finalize-idea`
- `finalize idea N`
- `mark idea N done`
- `close out idea N`

## Required Input: The Harness

The user must state which harness they are running in, because step 3 applies in Buzz only. If not told, ask:

```text
Are you running in native (this chat) or Buzz?
```

Auto-detection may be offered as a suggestion but never decides.

## The Two Idea Files

Per workspace, per subject:

| File                                                        | Holds           |
| ----------------------------------------------------------- | --------------- |
| `Archive/Live/Ideas/<Subject>/1.) Ideas.md`                 | Open ideas      |
| `Archive/Historical/Ideas/<Subject>/1.) Finalized Ideas.md` | Finalized ideas |

One page each, with numbered entries. The `Next idea number` line lives only in that subject's `1.) Ideas.md`. Create the file on first use when it does not exist.

`<Subject>` is a broad, unnumbered category folder (the school-subject sense: `Skills`, `Trading`, ...). Subject folders are never numbered; only the files inside them carry the `x.)` prefix. Keep subjects broad so you do not end up with one folder per idea.

Both file names carry the workspace `x.)` numbering prefix and are literally `1.) Ideas.md` and `1.) Finalized Ideas.md`. The prefix is part of the name, not decoration: do not create, look for, or write to an unprefixed `Ideas.md`. If an unprefixed file is found, treat it as a stray inbox and report it rather than silently adopting it.

### Legacy Flat Files

A workspace built before subject folders holds a correctly prefixed `1.) Ideas.md` directly under `Archive/Live/Ideas/` (and `1.) Finalized Ideas.md` under `Archive/Historical/Ideas/`), with no subject folder in between. That is a legacy flat inbox -- not an error and not a stray.

Before creating or writing a subject's file, check for a legacy flat `1.) Ideas.md` sitting directly in `Archive/Live/Ideas/`. If one exists:

1. Report it plainly: the inbox is flat, from before subject folders existed.
2. Never silently create a second inbox in a subject folder while the flat one still holds the ideas. That is the silent failure: the subject file opens empty and the real ideas sit one directory up, invisible, and nothing errors.
3. Migrate the flat files into the appropriate subject folder when authorized -- move bytes, never renumber, preserve the `Next idea number` line -- or stop and report rather than guessing.

The stray-inbox clause above covers the *unprefixed* `Ideas.md`. This clause covers the correctly prefixed but *flat* `1.) Ideas.md`. Both must be handled; neither may be silently skipped.

Either the user or an agent may perform intake, which is `idea-this`'s job; `finalize-idea` only moves entries.

## Subject Determination

The subject is inferred or stated, never interrogated:

- If the user names the subject explicitly (for example "finalize idea 3 under Skills"), use it.
- Otherwise infer the best-matching existing subject folder.
- Never stop and ask the user which subject. Infer and proceed; the user corrects you if the inference is wrong, and nothing is lost.

## Unnumbered Entries

An entry with no recognisable number is not a malformed entry to skip, and not an
entry to act on. Handle it exactly like this:

1. Assign it the next number using the recompute rule - one above the highest
   number found across both of that subject's idea files. This is not renumbering:
   there was no number to preserve.
2. Report the number that was assigned, and quote enough of the entry that the
   user can confirm it is the one they meant.
3. Increment `Next idea number` as with any intake.
4. Never act on it. Numbering an entry identifies it; it does not authorize it.
   The sealed-container notice still applies, and the user must name the new
   number before any work begins.

Never silently skip an unnumbered entry, and never treat its description as a
substitute for a number.

## Steps

1. Determine the subject (see Subject Determination).
2. Clean the entry for readability if it has not already been cleaned. See Cleaning On Move below.
3. Move the entry from that subject's `1.) Ideas.md` to that subject's `1.) Finalized Ideas.md`, keeping its number unchanged.
4. Reconcile that subject's `Next idea number` line. See Reconciling The Counter below.
5. In Buzz mode only: find the idea's message in the Ideas channel by its number and subject and mark it done with reactions. See Marking Done In Buzz below.
6. Report what moved, where, whether cleaning was applied, and whether the counter was corrected.

Never decrement the `Next idea number` line. Numbers are permanent identifiers, not slots.

## Leaving The Source File Clean

Removing an entry must not leave its scaffolding behind. Entries in `1.) Ideas.md` are separated by `---` rules, so lifting one out can strand a separator that belongs to nothing.

Two cases, both of which must be handled:

- **The last open idea is removed.** The file is left holding the `Next idea number` line and the sealed-container notice, and nothing else. No trailing `---`. An empty inbox that ends in a separator reads as a truncated or half-deleted entry, which is exactly the wrong signal for a file whose whole job is to show what is still open.
- **A middle entry is removed.** The entries above and below it end up adjacent, separated by exactly one `---`. Never two in a row, and never none.

The same applies to `1.) Finalized Ideas.md` on the receiving side: one separator between consecutive entries, none dangling at either end.

Read the file back after the write and confirm this, rather than assuming the edit landed cleanly. A stray separator is invisible in a diff of the moved entry and only shows up in the file itself.

## Cleaning On Move

An entry may reach this skill uncleaned, because the user writes ideas by hand -- in Obsidian, in a text editor, or by dictating straight into the file -- and hand-written entries never pass through `idea-this` Mode A, which is where cleaning normally happens. Finalizing is the last point at which the entry can be tidied, so it happens here.

Apply the same voice rule `idea-this` uses for intake:

> Clean for readability only: fix run-ons, remove filler, add paragraph breaks, and apply the workspace Voice-to-Text Glossary corrections. Do **not** rewrite, paraphrase, restructure, or improve. Swearing stays. Frustration stays. Half-formed thoughts get tightened, not polished. It must still sound like the user.

Rules:

- Clean only entries that need it. An entry captured through `idea-this` Mode A is already clean; passing it through a second time risks drift, so leave it alone.
- Never change the number, and never change what the idea is asking for. Cleaning is a readability pass, not an editorial one.
- Preserve embedded content exactly: file paths, URLs, code, image embeds such as `![[Pasted image ...]]`, quoted material, and screenshot references.
- Report that cleaning was applied, so the user can check the result against what they wrote.

## Reconciling The Counter

`Next idea number` lives only in that subject's `1.) Ideas.md` and is the number the next new idea in that subject will take. A hand-written entry does not update it, so it goes stale the moment the user adds an idea directly to the file -- and a stale counter is how a number gets reused.

After moving the entry, recompute the counter as one above the highest number found across **both** of that subject's idea files, and write that value.

| Situation                                 | Effect on the line |
| ----------------------------------------- | ------------------ |
| Counter already correct (the normal case) | Unchanged          |
| Counter stale after a hand-written entry  | Corrected upward   |
| Any situation whatsoever                  | Never decremented  |

The normal case leaves the line exactly where it was, because the highest number across that subject's two files does not change when an entry merely moves between them. The line moves only when it was already wrong.

Report the correction when one is made, and say what the value was and what it became. A silently corrected counter looks identical to a counter that was never wrong, and the user needs to know a hand-written entry slipped past the counter.

## Marking Done In Buzz

Buzz mode only. This runs after the entry has already been moved and the counter reconciled.

### Finding the message

The user names the idea by number -- one number, or several when finalizing a batch -- and the subject (stated or inferred). Use that number and subject to locate the message in the workspace's Ideas channel.

Each mirrored idea was posted with its `## N.` heading as its first line and a `Subject: <Subject>` line as its second, so both the number and the subject are carried in the message itself. Match on both. `buzz messages get` on the channel, or `buzz messages search`, both work.

Take the Ideas channel UUID from the current channel's description, never from memory and never invented.

Rules:

- Match the number exactly. `## 4.` is not `## 43.`; anchor the match to the whole number, not a prefix.
- Match the subject too. `Subject: Skills` is not `Subject: Trading`. A number alone may repeat across subject folders; the number plus the subject is what resolves to one idea.
- If no message carries that number and subject, stop and report it. Do not mark a different message, and do not post a replacement.
- If more than one message carries it, stop and report that too. Duplicates mean something upstream went wrong and picking one hides it.
- Re-read the channel before concluding it is empty -- see the private-channel warning in `idea-this`, because `[]` can mean no access rather than no messages.

### Legacy mirrors (pre-subject format)

A mirror posted before the subject-folder change carries its `## N.` heading (or a bare `N.)` number) but no `Subject:` line. That is a legacy mirror, not an error and not a duplicate.

When finalizing an idea whose mirror has no `Subject:` line:

1. Match it on number alone, using the exact-number anchoring above.
2. Report plainly that the match was number-only, because the mirror predates the subject-folder format.
3. Still stop on duplicates: if more than one message carries that number, do not pick one -- report it. A number-only match is safe only when exactly one such message exists.

This clause mirrors the Legacy Flat Files rule for files: the old shape still exists in the wild, and matching it by number alone is the right resolution -- but only when unambiguous.

### Marking it done

Add reactions to that message. **All ten, every time**, not a selection:

1. ✔️
2. ✅
3. ☑️
4. 🤲🏿
5. 👍🏿
6. 🤞🏿
7. 🙏🏿
8. 👏🏿
9. 🙂
10. 😉

One call per emoji: `buzz reactions add --event <event-id> --emoji <emoji>`.

The full set is the marker. A fixed, complete set means "finalized" is a single unambiguous check -- ten reactions present or not -- whereas a random or partial selection would force a reader to know every possible emoji before recognising a finalize. Report how many reactions were accepted, and name any that failed.

**Never edit the message to mark it done.** `buzz messages edit` replaces the entire body, so an edit that writes a done notice destroys the verbatim mirror. The mirror is byte-identical to the idea file by design; reactions leave it untouched. If a marker somehow cannot be applied by reaction, stop and report rather than falling back to an edit.

The emoji list is configuration, not doctrine -- the user may change it. Keep it as the single list above so there is one place to edit.

## Boundaries

- Never modify `wiki-schema.md` or write into `wiki/`.
- Never renumber an existing idea.
- Never create an idea (that is `idea-this`'s job).
- Never decrement the `Next idea number` line, and never change it other than the upward reconcile described above.
- Never rewrite, paraphrase, or improve an idea while cleaning it, and never clean an entry that is already clean.
- Never invent a channel UUID; take it from the current channel's description or ask.
- Never edit a mirrored idea message; mark it done with reactions only.
- Never mark a message whose number and subject do not match exactly, and never guess between duplicates -- except a legacy mirror carrying no `Subject:` line, resolved by number alone when exactly one such message exists.
- Never resolve a number-only match to a legacy mirror when more than one message carries that number.
- Never leave a dangling or doubled `---` separator in either idea file after a move.
- Never number a subject folder; only the files inside it carry the `x.)` prefix.
- Never stop and ask the user which subject - infer it or take it when stated.

## Validation

When creating or updating this skill itself, validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`).
