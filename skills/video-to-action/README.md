# Video-to-Action Setup Guide

`video-to-action` deterministically writes `report.md` and per-run `prompts.md`
under `Archive\Historical\Video-to-action\<run>\` through the bundled Gemini
helper. The helper—not the orchestrating agent—is the sole report writer.

## Setup

Run the no-cost preflight:

```text
python scripts\video_to_action.py --check-setup
```

It requires Python 3.10+, `google-genai`, `python-dotenv`, and a safely provided
`GEMINI_API_KEY`. Never print or save the key.

## Real-Run Checkpoint

Before any API call, confirm setup, whether the configured tier incurs cost,
the exact video URL/title/duration, and explicit optional-phase choices. The orchestrator
must present a runtime pop-up for Deep Summary and coding-only Technical choices;
without pop-up support it stops and asks in chat. It never guesses.

The baseline Procedure call always runs. `--deep-summary` adds the ACTS summary.
`--technical --coding-video` adds technical extraction for coding/software video.
This preserves one, two, or three selected Gemini calls.

Duration is required as `--duration MM:SS|HH:MM:SS`. Acquire it exactly like
title: user value, runtime free-text pop-up, or stop and ask in chat. The helper
normalizes it, records it, and injects it into Procedure and Deep Summary prompts.
It also demotes embedded Overview, Steps, and ACTS H2 headings script-side while
preserving deeper children and headings inside fenced code blocks.

Use `--self-test` for deterministic no-API fixtures and `--dump-prompts` to
regenerate the canonical `PROMPTS.md` from live constants.
