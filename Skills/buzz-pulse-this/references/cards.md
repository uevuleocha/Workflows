# Pulse Card Catalogue

This file is the card catalogue owned by the `buzz-pulse-this` skill. A "card" is a named post shape. Buzz doc 3 points at the skill rather than holding these shapes.

Card index:

- Card 0 -- Free-form -- the default
- Card 1 -- Work-log card -- task posts only

## Card 0 -- Free-form (the default)

Card 0 has no fixed shape at all: the agent writes the post however suits the content -- a paragraph, an observation, a finding, a link, a one-liner. Card 0 is what an agent reaches for unless the post is specifically a task work-log.

Use it for thoughts, observations, findings, links, one-liners, and anything the owner asks to be posted that is not a task work-log. "Post a note about that bug you saw" is a Card 0 post; "post what you're about to do to Pulse and update it when you're done" is a Card 1 post.

**Card 0 is not a "fallback".** It is the normal choice. Most posts are not tasks: "post what you found about X" has no owner, no deliverable, and nothing to wait on, and filling seven fields with `n/a` produces a worse post than a sentence. Do not force unrelated content into a card.

A scheduled workflow that posts to Pulse is not bound by any card either. Cards are a convention for the roster's own work log, not a schema the feed enforces -- nothing in Buzz validates a Pulse note's shape, because a Pulse note is just a `kind:1` text note.

## Card 1 -- The Work-Log Card (task posts only)

The seven-field template, moved verbatim from Buzz doc 3. Do not redesign it:

```text
Owner: {Working Agent} (via {Dispatching Agent or Uzo})
Asked: one line stating what was requested
Deliverable(s): in-chat answer, durable artifact, or both
Links: workspace-relative paths and/or URLs
Dates: Started YYYY-MM-DD
Current: what state the task is in right now
Waiting on: the agent or person the task is blocked on, or "nobody"
```

Use it only when the post is about a task the agent has been given -- starting one, updating one, finishing one.

Field notes:

1. **Owner** -- the agent doing the work, then in brackets whoever dispatched it. `Uzo` when the user assigned it directly. This mirrors the delegation chain, so the feed reads as an org chart in motion.
2. **Links** -- **workspace-relative paths, never absolute**. An absolute path publishes the Windows account name into a relay-hosted feed, and it does not resolve for a reader on another machine. Plain URLs are fine.
3. **No `Last update` field.** Each reply carries its own relay timestamp, so threading supplies it for free. A hand-maintained field would only go stale.

Nothing else belongs on the card. It is a status marker, not a report.

Threading: post the card once as a top-level note, then post every subsequent update as a `--reply-to` on that note's event id. Replies are open to any identity, so a second agent can add to another agent's task thread.

## Adding Card 2 And Beyond

If the owner likes a shape an agent improvised under Card 0, adopt it as a new numbered card. This is a documented edit to this file, not a restructure:

1. Confirm with the owner that the shape should be adopted, and take its number (next in sequence).
2. Add a `## Card N -- Name (when to use it)` section below Card 1, carrying the shape as a copyable block, when to use it, when not to, and any field notes.
3. Add the card to the index list at the top of this file.
4. If the new card warrants deterministic checks, extend `scripts/check_content.py` with a matching flag rather than inventing a second checker.

`SKILL.md` describes the catalogue as "Card 0 free-form default, Card 1 task work-logs, extensible" and does not enumerate future cards, so adding a card does not touch it. The one exception: if a new card ever changes the default rule itself -- which card is the normal choice -- update `SKILL.md` in the same pass, because the no-inverted-default rule lives there.
