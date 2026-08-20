---
name: buzz-channel-description
description: Generate the paste-ready description text for a Buzz channel - the one line Buzz injects into every agent's [Context] block on every turn, and the only reliable routing signal tying a channel to a workspace on disk. Use when the user invokes /buzz-channel-description, asks to write, draft, or generate a description for a Buzz channel, asks what a channel description should contain, or wants to update an existing Buzz channel description. Produces one continuous line with a mandatory character count against the 500-character cap. Never calls the Buzz CLI, never edits channel settings, needs no network or running Buzz.
---

# Buzz Channel Description

Generate the description text for a Buzz channel - the one line Buzz injects verbatim into every agent's [Context] block on every turn. Agents cannot see sidebar sections or channel grouping; the channel description is the entire routing mechanism between a Buzz channel and a workspace on disk. This skill produces that text for the user to paste into Buzz's channel settings. It does not call the Buzz CLI, does not edit channel settings, and does not require Buzz to be running.

## Mechanics the description must respect

Buzz caps descriptions at 500 characters and silently truncates anything longer. Newlines are collapsed to single spaces - a deliberate anti-spoofing measure, because a description containing a line break could forge a [Context] field. Never rely on line breaks for structure, and never try to work around the collapse. The description is injected on every turn of every conversation in the channel, so every character is a recurring token cost: brevity is not cosmetic.

Channel names collide (several workspaces can each have a `1.) Ideas`), so the description must disambiguate - never the name.

## Invocation

Treat these as direct invocation:

- `/buzz-channel-description`
- `use buzz-channel-description`
- `use the buzz-channel-description skill`

Natural triggers:

- "write a description for this channel"
- "generate a channel description"
- "what should this channel's description say"
- clear equivalents asking for Buzz channel description text

## Required Inputs

Ask only for what is missing and cannot be inferred:

1. which workspace this channel maps to (absolute path) - infer it rather than asking when the user is already working inside the target workspace;
2. the channel's purpose or name;
3. the sibling Ideas channel UUID, when this channel is not itself the Ideas channel - ask for it or omit the pointer; never invent a UUID.

## Structure - two parts, one continuous line

**Part 1 - the generic block.** Identical for every channel in the same workspace. Carries:

1. the absolute path of the workspace this channel belongs to;
2. an instruction to read that workspace's `AGENTS.md` and `CLAUDE.md` before acting;
3. where durable artifacts for this workspace belong;
4. the UUID of the sibling Ideas channel for this workspace, when one exists.

**Part 2 - the channel-specific block.** What this particular channel is for, and any behaviour unique to it.

Keep Part 1 byte-identical across channels in the same workspace - consistency is what lets the user diff descriptions later and spot drift.

### The staple is versioned, not permanent

Part 1's four elements are the **current** staple, not a law. They were arrived at by asking what an agent cannot obtain any other way, and that answer will change as Buzz changes and as the user's setup grows. This skill file is the single place where that revision happens: when the user decides a new line belongs in every channel description, they update this skill and regenerate - they do not hand-edit descriptions one by one and let them drift apart. No version-negotiation mechanism, no changelog inside generated descriptions, no migration routine - just this honest acknowledgment.

## Generation procedure

1. Resolve the three inputs above; infer the workspace path when operating inside the target workspace.
2. Emit Part 1 from the current staple.
3. Emit Part 2 from the channel's actual purpose. If the purpose is not yet decided, emit a short description naming only the workspace and say the remaining budget is deliberately unused - a short correct answer beats an invented one. Never fill space.
4. Count the characters of the full line and report the count against the 500 cap. Do not estimate - count.
5. If the draft exceeds 500, tighten Part 2 and re-count. Never truncate Part 1 - the routing information is the point. Refuse to emit over-length text.
6. Emit the final text as one continuous line in a copyable code block, since the user pastes it into a GUI field by hand. Prefer ASCII throughout - wide glyphs consume budget unpredictably.

### The budget is a ceiling, never a target

Do not pad, elaborate, or invent detail to approach 500. A description that says everything necessary in 200 characters is better than one that says the same thing in 480, because every character is re-sent on every turn forever. Unused budget is correct, not a shortfall.

### The every-turn test

Apply this to any candidate content: does this need to be true on *every* turn in this channel, regardless of what is being done? If it only matters during a specific workflow, it belongs in that workflow's skill, where it is in context exactly when it matters - not in a description re-sent on every turn of every unrelated conversation. When asked to add such a rule, decline and direct it to the owning skill, citing this test.

## Worked examples

Work channel for the Workflows workspace - 316 of 500 characters (UUID here is a 36-character placeholder; counts are computed with it):

```
Workspace: C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows. Read its AGENTS.md and CLAUDE.md before acting. Durable artifacts go under that workspace's Archive/. Ideas channel for this workspace: 12345678-1234-1234-1234-123456789012. This is the Work channel: execute Workflows workspace implementations here.
```

Ideas channel for the same workspace - 318 of 500 characters. Part 1 is byte-identical to the Work example; only Part 2 differs:

```
Workspace: C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows. Read its AGENTS.md and CLAUDE.md before acting. Durable artifacts go under that workspace's Archive/. Ideas channel for this workspace: 12345678-1234-1234-1234-123456789012. This is the Ideas channel: propose and discuss Workflows workspace work here.
```

Over-length handling, worked: a deliberately verbose Operations purpose ("...scheduled maintenance sweeps, routine skill audits, dependency updates, deprecation cleanups, monthly archival of stale artifacts, and the weekly coordination roundup with all agents across every workspace in the universe") produced a 572-character draft. Tightening Part 2 to "run day-to-day Workflows workspace maintenance and coordination" brought the final line to 337 of 500, verified by re-count. Part 1 was untouched.

Undecided purpose, worked: with no purpose yet decided, the correct output is the workspace-only line - 168 of 500 characters - stated as complete, with the remaining budget deliberately unused rather than filled with an invented purpose:

```
Workspace: C:\Users\Admin\Uzzys Universe\MilkyWay\Tools\Workflows. Read its AGENTS.md and CLAUDE.md before acting. Durable artifacts go under that workspace's Archive/.
```

## Boundaries

Do:

- count the final line's characters and report the count against the 500 cap on every output
- keep Part 1 byte-identical across channels in the same workspace
- emit exactly one continuous line, in a copyable code block
- prefer ASCII; wide glyphs consume budget unpredictably
- ask for, or omit, the Ideas channel UUID - never fabricate one

Do not:

- emit over-length text, or any text without its reported count
- pad a description with invented or restated content to approach the cap
- write a workflow-specific behavioural rule into a description - direct it to the owning skill
- reference sidebar sections as a routing mechanism - agents cannot see them; decline and explain
- restate workspace contract content - point at `AGENTS.md`; never paraphrase it
- write, edit, or publish anything to Buzz; call the Buzz CLI; or require a network connection or a running Buzz instance

## Validation

- every generated line is exactly one line, at or under 500 characters, with its count reported
- Part 1 is byte-identical across same-workspace outputs
- over-length drafts tighten Part 2 and re-count; Part 1 is never truncated
- undecided purposes yield short workspace-only lines with unused budget declared as deliberate
- no UUID is ever invented; sidebar sections never appear
- no Buzz CLI command is issued and no network call is made
- when creating or updating this skill: validate with `quick_validate.py` run under `python -X utf8`

Governance record: this skill writes no Markdown tables anywhere and creates no first-party durable artifacts. The Markdown Table Alignment section and the provenance / exact-model attribution requirements are therefore intentionally exempt here - a deliberate design decision recorded at creation, not an omission. This exemption does not extend to any future edit that adds tables or artifact writes.
