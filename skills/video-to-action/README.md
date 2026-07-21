# Video-to-Action Setup Guide

`video-to-action` deterministically writes `report.md`, `transcript.md`, and
per-run `prompts.md` under `Archive\Historical\Video-to-action\<run>\`. Gemini
produces the report phases; YouTube captions provide the transcript without an
extra model call. The helper—not the orchestrating agent—is the sole writer.

## Setup

Run the no-cost preflight:

```text
python scripts\video_to_action.py --check-setup
```

It requires Python 3.10+, `google-genai`, `python-dotenv`,
`youtube-transcript-api`, and a safely provided `GEMINI_API_KEY`. Never print or
save the key.

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
It demotes embedded Overview and Steps to H3 and their numbered and STEP
children to H4 while preserving deeper headings and fenced code blocks. ACTS
headings are demoted separately to H3.

Every run also writes `transcript.md`. When YouTube captions cannot be fetched,
the artifact records the reason and offers a manual copy/paste recovery through
`https://youtubetotranscript.com/`; the generated third-party page itself is
never used as a machine input. Manual completion preserves the automatic failure
provenance and does not rerun Gemini.

Use `--self-test` for deterministic no-API fixtures and `--dump-prompts` to
regenerate the canonical `PROMPTS.md` from live constants.
