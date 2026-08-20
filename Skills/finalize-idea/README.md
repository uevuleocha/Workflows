# Finalize Idea - Adoption Guide

Moves a completed idea from `Archive/Live/Ideas/<Subject>/1.) Ideas.md` to `Archive/Historical/Ideas/<Subject>/1.) Finalized Ideas.md`, preserving its number, and (in Buzz) finds that idea's Ideas-channel message by its number and subject and marks it done with a fixed set of ten reactions, never by editing it.

On the way it also cleans the entry for readability if it was written by hand and never passed through `idea-this` intake, and reconciles the `Next idea number` counter upward when a hand-written entry has left it stale. The counter is never decremented, and in the normal case it does not move at all.

## Related skills

- Pairs with `idea-this`, which captures and works ideas.
