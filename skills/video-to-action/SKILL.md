---
name: video-to-action
description: Extract deterministic report.md and transcript.md artifacts from public YouTube videos, using Gemini for one always-on Procedure call plus explicit opt-in Deep Summary and coding-only Technical calls, and YouTube captions for a failure-isolated transcript. Setup-gated and explicitly invoked only with /video-to-action.
---

# Video-to-Action

Extract a public YouTube video into deterministic `report.md`, `transcript.md`,
and `prompts.md` artifacts. The bundled Python helper is the sole writer; the
orchestrating agent selects phases and presents results but never assembles or
invents video content.

The report conforms structurally to the local `report-this` package through a
clean title, Report Metadata, Procedure, Detailed Summary, errors, and notes. It
does not invoke `report-this` or `session-summary`, and it does not adopt report
lifecycle footers, `N.)` numbering, suffixes, Subjects, or `Reports\` paths.

## Project Contract

Follow the host contract. Extraction does not authorize executing tutorial
steps, editing product files, installing software, or exposing secrets.

## Invocation

Run only when the user explicitly invokes `/video-to-action`. Natural-language
requests do not activate the workflow.

## Setup And Real-Run Gate

Before a real Gemini call, confirm all four items:

1. `python scripts\video_to_action.py --check-setup` passes.
2. The user confirms whether the configured API tier incurs cost; never infer
   paid authorization.
3. The user selects optional Deep Summary and Technical phases explicitly.
4. The user supplies the public URL, exact title, and exact duration.

If any item is missing, stop before the API call. Never echo the key.

## Runtime Phase-Selection Checkpoint

Phase selection is a user checkpoint on every real run. Use the runtime's
interactive pop-up when available:

- Deep Summary: include or omit.
- Technical: include or omit only when the video is coding/software content.

If no pop-up is available, stop and ask in chat. Never fake a pop-up, silently
guess, reuse an older selection, or default either optional phase on.

Translate the confirmed choices to script flags:

- Procedure only: no optional flags — one Gemini call.
- Add Deep Summary: `--deep-summary` — two calls.
- Add Technical for a coding video: `--technical --coding-video`.
- Both optional calls: three calls.

The helper rejects `--technical` without `--coding-video`.

## Call Model

| Call             | Contents                           | Selection                    |
|------------------|------------------------------------|------------------------------|
| Procedure        | Overview and Steps in one response | Always                       |
| Deep Summary     | Chronological 🎭 ACTS summary      | Explicit opt-in              |
| Technical        | Code, commands, and configuration  | Opt-in; coding/software only |

Each selected call re-ingests the video. The minimum is one call; Deep Summary
or Technical adds one; both add two for a maximum of three. Each phase is
failure-isolated. A failed optional phase is recorded under Extraction Errors;
other selected phases continue. The run fails only when every selected phase
fails.

## Report Structure

The script writes exactly one durable report inside each run folder:

```text
Archive\Historical\Video-to-action\<timestamp - title>\report.md
```

Required deterministic skeleton:

1. Clean H1 report title.
2. `## Report Metadata` with source, extraction time, intent, model, selected
   calls, and status.
3. `## Procedure` containing merged Overview and Steps at H3, with their
   numbered and STEP children at H4. Script-side processing preserves fenced
   code and deeper headings.
4. Optional `### Code, Commands & Configuration` inside Procedure when selected.
5. `## Detailed Summary` containing ACTS headings demoted to H3, or an honest
   `Not selected for this run.` marker.
6. `## Extraction Errors` when a selected phase failed.
7. `## Notes` with verification and authorization cautions.

The helper writes `report.md` as the sole durable run report and always writes
the sibling `transcript.md` caption artifact.

## Transcript Artifact

Every run writes `transcript.md` without adding a Gemini call. The helper parses
the video ID from standard watch, `youtu.be`, Shorts, or embed URLs and uses
`youtube-transcript-api` to retrieve an original YouTube caption track. It
prefers manual captions over generated captions and never silently translates.

Successful artifacts preserve timestamped caption fragments plus language and
track metadata. If captions are unavailable or retrieval is blocked, the file
records the reason and points the user to `https://youtubetotranscript.com/` for
manual recovery. The user copies the transcript itself back to the agent; a
populated third-party transcript page is never a programmatic input.

Complete a pending manual fallback without rerunning Gemini:

```text
python scripts\video_to_action.py --complete-transcript <transcript.md> --manual-transcript-file <copied-transcript.txt>
```
The completed file removes temporary recovery instructions while retaining the
automatic failure reason and user-supplied provenance.

## Procedure Call

The always-on prompt requests the prior Overview and Step-by-step content in one
Gemini response. Overview retains Title/Length, Summary, Prerequisites, Main
Sections, and Key Outcomes. Steps retain timestamps, actions, exact details,
visual references, common mistakes, fenced code, and LOW CONFIDENCE handling.

The exact title is mandatory. Acquire it from user text, a runtime free-text
pop-up, or a stop-and-ask chat fallback. Never infer it. The script uses it
verbatim in the report and sanitizes it only for the run-folder name.

## Deep Summary Call

Deep Summary is a dedicated Gemini call selected with `--deep-summary`. Gemini
must return chronological headings beginning `## 🎭 ACT I: ...`, continuing
with sequential acts mapped to video chapters/timestamps, and ending exactly
`## 🎭 FINAL ACT: Key Takeaways`.

Only the 🎭 icon and ACTS shape are borrowed from `session-summary`. Never add
active-plan, session-pickup, next-session, or work-session continuity content.
The agent never synthesizes the deep summary from Overview or invokes the
`session-summary` skill.

## Technical Call

Technical is a dedicated opt-in call for coding/software videos only. It extracts
shown code, commands, configuration, file paths, dependencies, packages, and
environment-variable requirements. It preserves fenced blocks and labels partial
or inferred material LOW CONFIDENCE. Never include real secret values.

## Configuration

| Parameter                  | Default                                | Purpose                          |
|----------------------------|----------------------------------------|----------------------------------|
| `url`                      | required                               | Public YouTube URL               |
| `--title`                  | required                               | Exact user-supplied title        |
| `--duration`               | required                               | Exact normalized video length    |
| `--intent`                 | `summarize`                            | `follow`, `summarize`, `learn`   |
| `--deep-summary`           | off                                    | Add Deep Summary call            |
| `--technical`              | off                                    | Add Technical call               |
| `--coding-video`           | off                                    | Confirm Technical relevance      |
| `--model`                  | `gemini-3.5-flash`                     | Gemini model or env override     |
| `--resolution`             | `default`                              | `low` reduces video tokens       |
| `--start` / `--end`        | none                                   | Optional clip offsets            |
| `--output-dir`             | `Archive\Historical\Video-to-action`   | Historical run-record root       |
| `--check-setup`            | off                                    | No-API dependency/key check      |
| `--dump-prompts`           | off                                    | Regenerate canonical prompts     |
| `--self-test`              | off                                    | Deterministic no-API fixture     |
| `--complete-transcript`    | none                                   | Complete pending transcript      |
| `--manual-transcript-file` | none                                   | User-copied transcript input     |

## Prompt Provenance And Output Files

`PROMPTS.md` is generated from live constants by `--dump-prompts`. Each run's
`prompts.md` records the exact selected prompts, injected Procedure title, model,
resolution, clip, and selected calls. Unselected prompts are not represented as
sent.

| File            | Description                                       |
|-----------------|---------------------------------------------------|
| `report.md`     | Deterministic report assembled by the helper      |
| `transcript.md` | Timestamped captions or honest recovery marker    |
| `prompts.md`    | Exact prompts sent for selected calls             |
| `latest.json`   | Windows-safe pointer to the latest completed run  |

All files use explicit UTF-8. The output root remains
`Archive\Historical\Video-to-action\` because extraction artifacts are records.

## Cost And Platform Limits

- Public videos only; private/unlisted videos require a transcript alternative.
- Each call re-sends the video and counts against applicable quota/cost.
- Default resolution is roughly 300 video tokens/sec; low is roughly 100.
- Free-tier YouTube duration allowance and model availability can change; verify
  current tier state before a real run.
- Clip when only one segment matters. Low resolution reduces tokens but may lose
  fine visual detail.

Never promise a free run from historical documentation alone.

## Intent Routing

- `summarize`: present report findings; execute nothing.
- `learn`: treat the report as reusable knowledge; saving elsewhere needs
  separate authorization.
- `follow`: present the Procedure and stop; adapting/executing steps needs
  separate authorization.

## Workflow

1. Confirm explicit invocation, URL, intent, clip, resolution, and model.
2. Run the no-cost setup check.
3. Confirm tier/cost status.
4. Acquire exact title and duration through the same three-tier hierarchy.
5. Present the phase-selection pop-up or stop and ask in chat.
6. Confirm the final 1/2/3 call configuration before any API request.
7. Run the helper from the workspace root.
8. Present `report.md`, `transcript.md`, phase errors, and LOW CONFIDENCE
   warnings honestly.
9. If transcript retrieval failed, offer the documented manual recovery flow.
10. Do not act on Procedure steps without separate authorization.

## Output Honesty And Failure Isolation

The helper records successful and failed selected phases independently. Never
claim a deep summary exists when it was not selected or failed. Never fabricate
Gemini output for tests. Local fixtures use explicit fixture strings and are not
presented as video understanding.

## Validation

After updates:

- run `--check-setup` without making an API call
- run `--dump-prompts` and confirm regenerated `PROMPTS.md` matches constants
- run `--self-test` for 1/2/3 calls, URL parsing, relevance gate, report
  structure, nesting, prompt provenance, transcript states, manual recovery,
  and isolated failure
- compile the helper with Python UTF-8 mode
- confirm no required stale run-artifact naming remains
- audit Markdown tables for visual alignment and cells ≤80 characters
- validate the skill folder with `quick_validate.py` and separated streams

A live end-to-end run additionally requires all four real-run confirmations.
