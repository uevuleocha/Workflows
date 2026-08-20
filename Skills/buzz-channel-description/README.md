# Buzz Channel Description — Adoption Guide

Generates the paste-ready description text for a Buzz channel - the one line Buzz injects into every agent's [Context] block on every turn, tying the channel to its workspace on disk. Emits one continuous line (workspace routing block + channel purpose) with a mandatory character count against the 500-character cap. Never calls the Buzz CLI, never edits channel settings, needs no network.

Invoke with `/buzz-channel-description` or "write a description for this channel".

## Related skills

- None — this skill is deliberately standalone: no scripts, no network, no Buzz CLI, no dependencies.
