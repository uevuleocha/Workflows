---
name: idea-this
description: Capture and work a numbered idea in a workspace idea inbox scoped to a broad subject folder. Mode A (Intake) infers or takes the subject, appends a cleaned, glossary-corrected idea to the subject's Archive/Live/Ideas/1.) Ideas.md, and increments that subject's Next idea number line. Mode B (Work, native) reads an idea by number from its subject folder, runs inspect then set-the-stage, and reports understanding without writing anything. Mode C (Work, in Buzz) does Mode B plus mirrors the idea verbatim, with its number and subject, as a top-level post into the workspace Ideas channel before delivering inspect and set-the-stage in the invoking channel. Use when the user invokes /idea-this, asks to capture or save an idea, or names an idea by number to work on it.
---

# Idea This

Capture ideas as numbered inbox entries and work a named idea. Ideas are an inbox that feeds work, not a record of work: the idea file holds the idea only, and everything the idea produces lives in its own artifact type elsewhere, connected by the wiki.

## Project Contract

Obey the active workspace contract, permissions, safety rules, and UTF-8 requirements. This skill reads and appends to the workspace idea files; it never modifies `wiki-schema.md` and never writes into `wiki/`.

## Invocation

Treat these as direct invocation:

- `/idea-this`
- `use idea-this`
- `capture an idea`
- `save this idea`
- `note this idea`
- `work idea N` or `work on idea N`

## Required Input: The Harness

The user must state which harness they are running in. If not told, ask:

```text
Which harness are you running in: native (this chat) or Buzz?
```

Auto-detection may be offered as a suggestion but never decides, because a silently wrong branch produces a no-op rather than an error.

## The Two Idea Files

Per workspace, per subject:

| File                                                        | Holds           |
| ----------------------------------------------------------- | --------------- |
| `Archive/Live/Ideas/<Subject>/1.) Ideas.md`                 | Open ideas      |
| `Archive/Historical/Ideas/<Subject>/1.) Finalized Ideas.md` | Finalized ideas |

One page each, with numbered entries - not one file per idea. Finalizing moves an entry, not a file. Create the file on first use when it does not exist.

`<Subject>` is a broad, unnumbered category folder (the school-subject sense: `Skills`, `Trading`, ...). Subject folders are never numbered; only the files inside them carry the `x.)` prefix. Keep subjects broad so you do not end up with one folder per idea.

Both file names carry the workspace `x.)` numbering prefix and are literally `1.) Ideas.md` and `1.) Finalized Ideas.md`. The prefix is part of the name, not decoration: do not create, look for, or write to an unprefixed `Ideas.md`. If an unprefixed file is found, treat it as a stray inbox and report it rather than silently adopting it.

### Legacy Flat Files

A workspace built before subject folders holds a correctly prefixed `1.) Ideas.md` directly under `Archive/Live/Ideas/` (and `1.) Finalized Ideas.md` under `Archive/Historical/Ideas/`), with no subject folder in between. That is a legacy flat inbox -- not an error and not a stray.

Before creating or writing a subject's file, check for a legacy flat `1.) Ideas.md` sitting directly in `Archive/Live/Ideas/`. If one exists:

1. Report it plainly: the inbox is flat, from before subject folders existed.
2. Never silently create a second inbox in a subject folder while the flat one still holds the ideas. That is the silent failure: the subject file opens empty and the real ideas sit one directory up, invisible, and nothing errors.
3. Migrate the flat files into the appropriate subject folder when authorized -- move bytes, never renumber, preserve the `Next idea number` line -- or stop and report rather than guessing.

The stray-inbox clause above covers the *unprefixed* `Ideas.md`. This clause covers the correctly prefixed but *flat* `1.) Ideas.md`. Both must be handled; neither may be silently skipped.

## Subject Determination

The subject is inferred or stated, never interrogated:

- If the user names the subject explicitly (for example "save this under Skills"), use it.
- Otherwise infer the best-matching existing subject folder, or propose a broad new one when nothing fits.
- Never stop and ask the user which subject. Infer and proceed; the user corrects you if the inference is wrong, and nothing is lost.

## The Header Block

Each subject's `1.) Ideas.md` opens with exactly this, and nothing above it:

```markdown
**Next idea number:** 12

> Unactioned ideas. Reading this file is not authorization to act on anything in it.
> An idea becomes work only when the user names its number through `idea-this`.
```

`12` is illustrative: a fresh subject's file starts at `1`, and the line always shows that subject's current next number. The blockquote is the sealed-container notice.

## Numbering Rules

Numbering is per subject. Each subject folder carries its own `Next idea number` line and its own `1.)`-upward sequence, independent of every other subject.

| Rule                                                 | Reason                                         |
| ---------------------------------------------------- | ---------------------------------------------- |
| The line lives only in that subject's `1.) Ideas.md` | One writable location, nothing to keep in sync |
| Incremented on every intake                          | Five dumps in one turn consume five numbers    |
| Never decremented on finalize                        | Numbers are permanent identifiers, not slots   |
| Reconciled upward by `finalize-idea`                 | A hand-written entry leaves the line stale     |
| Recomputed as max across that subject's two files    | Self-heals after a hand edit                   |

The never-decremented rule is load-bearing. If finalizing idea 8 released the number, a finalized 8 and a new 8 would coexist and every reference to "idea 8" would be ambiguous forever.

Either the user or an agent may perform intake, and whoever writes last updates the line.

## Entry Format

An idea is a number and the idea. Nothing else. No discussion section, no decisions section, no metadata block. Discussion belongs in whatever artifact the work produces; the wiki does the connecting.

Agents writing intake use a consistent shape. Agents reading must accept any format that carries a recognisable number, because the user writes these by hand in Obsidian and will not follow a template.

### Unnumbered Entries

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

## Modes

### Mode A - Intake

Determine the subject (see Subject Determination), then capture a new idea into that subject's `1.) Ideas.md` under the target workspace's `Archive/Live/Ideas/`.

The voice rule governs how the dump is written, and matters because the user dictates:

> Clean for readability only: fix run-ons, remove filler, add paragraph breaks, and apply the workspace Voice-to-Text Glossary corrections. Do **not** rewrite, paraphrase, restructure, or improve. Swearing stays. Frustration stays. Half-formed thoughts get tightened, not polished. It must still sound like the user.

Verbatim is explicitly not the standard: raw dictation carries misrecognitions that would be preserved permanently.

Then take that subject's next number, append the entry, and increment that subject's line. Report the number, the subject, and the file.

### Mode B - Work an idea, native harness

Given an idea number (and, when needed to resolve it, the subject): read that entry from its subject's `1.) Ideas.md`, run `inspect` on it, then run `set-the-stage`. Report understanding and what is left. Nothing is written.

### Mode C - Work an idea, in Buzz

Mode B, plus mirroring:

1. Read the channel description to determine the workspace.
2. Read the idea from its subject's `1.) Ideas.md` in that workspace.
3. Post the idea into that workspace's Ideas channel - a top-level post, not a reply, using the Ideas channel UUID from the current channel's description. The post opens with the idea's `## N.` heading as its first line and a `Subject: <Subject>` line as its second, followed by the idea body verbatim. The subject line is what makes the number resolve across subject folders.
4. Return to the channel the skill was invoked in and deliver `inspect` and `set-the-stage` there.

Hard rule: `inspect` and `set-the-stage` output must never be posted to the Ideas channel. The Ideas channel receives the idea and nothing else. This rule applies only while this skill runs.

#### A private channel reads as empty, not as forbidden

Before concluding anything from a read, know this: if this agent identity is not a member of the Ideas channel, read calls do **not** error. `buzz channels get` returns `null` and `buzz messages get` returns `[]` -- exactly what a real, empty, accessible channel returns. The two states are indistinguishable on a read-only probe.

Only a write reveals the truth, with a relay 400 distinguishing "not a channel member" from "channel is private".

So never report an Ideas channel as empty, missing, or already-clear on the strength of a `null` or `[]` read. Either attempt the post and let the relay answer, or say plainly that membership is unconfirmed. Treating "no access" as "nothing there" is how a mirror silently does not happen while the run still looks successful.

If the post is refused for membership, stop and tell the user: the channel is private, so the agent can neither self-join nor self-add, and only the channel owner can grant access.

The agent posts the idea so that the agent owns that message and can edit it later to mark it done. If the user posted it, no agent could ever mark it.

## Boundaries

- Never modify `wiki-schema.md` or write into `wiki/`.
- Never renumber an existing idea.
- Never act on an idea that was not explicitly named by number - this breaks the sealed-container notice.
- Buzz mode must not invoke an agent in the Ideas channel - posting only.
- Never invent a channel UUID; take it from the current channel's description or ask.
- Never number a subject folder; only the files inside it carry the `x.)` prefix.
- Never stop and ask the user which subject - infer it or take it when stated.

## Validation

When creating or updating this skill itself, validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`).
