---
name: video-to-action
description: Extract actionable procedures from public YouTube videos via the Gemini API video-understanding route using a bundled Python script, then summarize, save, or (with separate authorization) act on the extracted steps. Setup-gated; requires a Gemini API key. Use only when the user explicitly invokes /video-to-action.
---

# Video-to-Action

Extract what a YouTube video teaches into structured, actionable form. The bundled `scripts\video_to_action.py` sends a public YouTube URL to Gemini video understanding and runs structured extraction phases — overview, step-by-step, and (for technical content) code/commands/configuration — then compiles a procedure document. The orchestrating agent presents or acts on the extraction according to the user's intent and the host project's rules.

**The video analysis runs on the Gemini API.** The orchestrating agent that launches the script may be Claude, Codex, or Antigravity — none of which can watch video natively. Do not assume any agent platform ingests YouTube video itself; the script and a `GEMINI_API_KEY` are the only supported route.

## Project Contract

Follow the host project's canonical contract, such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Its safety rules, approval gates, path limits, and product-code workflow remain unchanged.

Extraction is free-standing; **acting on extracted steps is not**. Invoking this skill never authorizes executing tutorial instructions, editing files, installing software, or generating product code. Those require the user's separate, explicit authorization under the host contract.

## Invocation

Run this workflow only when the user explicitly invokes:

- `/video-to-action`

Do not activate from phrases such as "watch this video", "learn from this tutorial", "extract steps from video", or similar natural language unless the slash command is present.

## Prerequisites And Setup Gate

Before any real run, the orchestrating agent must verify:

1. `scripts\video_to_action.py` exists in this skill folder.
2. Python 3.10+ is available.
3. The `google-genai` and `python-dotenv` packages are installed.
4. `GEMINI_API_KEY` is available via the environment or a `.env` file (created through Google AI Studio). Never display, echo, or save the key value.

Run the harmless preflight (no API call, no cost):

```text
python scripts\video_to_action.py --check-setup
```

If any prerequisite is missing, **stop**. Do not attempt the extraction. Route the user to a setup task under the host workspace's configured task directory. Common default: `<project root>\Archive\Tasks\` on Windows or `<project root>/Archive/Tasks/` on macOS/Linux. If the workspace has no task convention, ask the user where setup tasks should live.

## Hard Limits (Per Google's Documentation)

State these honestly; do not promise around them:

- **Public videos only.** Private and unlisted videos are not supported. Suggest a transcript instead.
- **Free tier: 8 hours of YouTube video per day.** Paid tier: no daily duration limit.
- **Token cost: ~300 tokens per second of video** at default resolution, ~100 at low resolution. A 30-minute video is roughly 540K input tokens per phase at default resolution.
- **Length caps: ~1 hour at default resolution, ~3 hours at low resolution** on 1M-context models. For longer videos, use clipping to analyze segments.
- Verify current model availability and pricing against Google's live documentation; model generations retire (the Gemini 2.0 models shut down 2026-06-01).

## Cost Guidance

Each run makes 2-3 API calls, each re-sending the video. Cost levers, biggest first:

1. **Clip** with `--start`/`--end` when the user only cares about a section.
2. **Low resolution** (`--resolution low`) cuts video tokens ~3x; fine for talking-head and screen-recording tutorials, weaker for fine visual detail.
3. **Two phases instead of three** when the video is not technical.
4. The free tier's 8h/day allowance means small extractions are often $0 — but confirm tier status before assuming.

Confirm the configured run with the user before launching a paid extraction.

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `url` | required | Public YouTube video URL (positional) |
| `--intent` | `summarize` | `follow`, `summarize`, or `learn` — recorded in the output; `follow` still only extracts |
| `--phases` | `2` | `2` for general content; `3` adds the technical pass for coding/software videos |
| `--model` | `gemini-3.5-flash` | Gemini model id; also via `VIDEO_TO_ACTION_MODEL` env var. Override per run, e.g. `--model gemini-3.1-pro` for hard videos |
| `--start` / `--end` | none | Clip offsets (seconds, MM:SS, or HH:MM:SS) — analyze only that segment |
| `--resolution` | `default` | `low` cuts token cost ~3x and extends the length cap |
| `--output-dir` | `Archive\Video-to-action` | Base output directory; also via `VIDEO_TO_ACTION_OUTPUT_DIR` env var |
| `--title` | **required** | Exact video title, supplied by the orchestrating agent from user input. Used verbatim in `procedure.md`; sanitized for the run-folder name. An extraction run errors without it — the skill no longer infers titles |
| `--check-setup` | off | Verify dependencies and key presence with no API call, then exit |
| `--dump-prompts` | off | Regenerate `PROMPTS.md` (the canonical template) from the in-code prompt constants with no API call, then exit |

The default model is a stable GA model. Do not hardcode preview models as defaults; pass them per run with `--model` when a specific video needs deeper reasoning.

## Extraction Phases

The script preserves the original three-phase prompt contracts:

1. **Overview** — a fixed structure: an intro line then five headings, `### 1.) Video Title and Length` (bold-label bullets) / `### 2.) Summary` / `### 3.) Prerequisites` / `### 4.) Main Sections` (timestamp ranges) / `### 5.) Key Outcomes`. The title is **always** the user-supplied `--title`, used verbatim with no marker — the skill no longer infers titles. **Metadata canary:** Gemini is additionally told that *if and only if* it can read the real title from the video's metadata, it adds a `Metadata title (from video metadata):` bullet; today it cannot, so that bullet never appears. If it ever does, that is the signal that Google enabled metadata access and the skill can be upgraded (and it doubles as a cross-check against the supplied title).
2. **Step-by-step** — each step as a `### STEP n:` section separated by `---` dividers, with: timestamp range (MM:SS-MM:SS), imperative action, exact values/settings, visual reference (what the screen should look like after), and a common-mistakes line. Demo values recorded even when the presenter says "adjust to taste". Code/commands/JSON are reproduced in fenced code blocks, never inline. Subtle visual techniques are marked `LOW CONFIDENCE:`. The common-mistakes line allows **labeled inference**: it surfaces a pitfall when the presenter states one *or* when a practitioner would clearly recognize a well-founded one, marking inferred pitfalls `(inferred)`, and reads "None notable" only when nothing meaningful applies.
3. **Technical** (phase 3, for coding/software content) — all code snippets reconstructed from screen, exact terminal commands with flags, configuration values, file paths, dependencies/packages, and required keys/env vars (noting placeholders). Partially visible code is marked `LOW CONFIDENCE:`.

Each phase is failure-isolated: one failed phase is logged into the run's `errors` list and the remaining phases continue. The run fails only when every phase fails.

## Prompt Documentation

Prompts are documented at two levels:

- **`PROMPTS.md`** (skill root, caps to match `SKILL.md`) — the canonical **template**, generated from the script's prompt constants, never hand-edited, via `python scripts\video_to_action.py --dump-prompts`. It cannot drift from the live prompts; regenerate it whenever the constants change.
- **`prompts.md`** (lowercase, inside each run folder) — the **actual** prompts sent to Gemini for that specific run, including the title injected via `--title` and the run's model/resolution/clip context. This is the faithful per-run record of what the model received.

## Title Acquisition

The title is **mandatory** — the skill no longer infers titles, and the script errors without `--title`. The orchestrating agent must obtain the real title from the user and pass it via `--title "..."`. Acquire it in this order of preference, kept **agent-agnostic** — do not hard-code any one agent's mechanism:

1. **User-supplied up front** — if the user already typed the title (e.g. after the link) or pasted a screenshot showing it, read it and pass it via `--title`. No prompt needed.
2. **Runtime pop-up** — if the agent has an in-turn interactive-question capability (for Claude, that is the `AskUserQuestion` tool; other agents use their own equivalent), ask the user for the title at runtime. Design it so the title is captured as **free text**: instruct the user to **type or paste the exact title into the "Other" free-text field and submit** — not click a placeholder option, which captures no text. Proceed within the same turn with the title.
3. **Stop-and-ask fallback** — if the agent has no in-turn pop-up, or is unsure it can invoke one, it must **stop and ask the user in chat** for the title (or a screenshot), then resume on the next turn. Never fake a pop-up, and never proceed without a title.

**Illegal characters in the title.** The run folder is named `<timestamp> - <title>`, so a title containing characters illegal in a Windows folder name (`< > : " / \ | ? *`) is sanitized for the folder only — the script replaces them with hyphens and the verbatim title is still written inside `procedure.md`. When the agent notices such characters, it may either proceed with the sanitized name and tell the user, or ask the user how to handle them (substitute, drop, or supply a cleaner title) — the user's call.

## Intent Routing

Based on the user's stated intent:

- **"What does this video show?"** (`summarize`) — present the overview and step list. Execute nothing. Offer further action.
- **"Learn this technique"** (`learn`) — treat `procedure.md` as a reusable procedure; with the user's approval, generalize it and save a copy to a user-chosen permanent location.
- **"Follow this tutorial"** (`follow`) — present the extracted procedure and **stop**. Walking through the steps, adapting them to the user's environment, or executing anything requires the user's separate explicit authorization under the host contract. Steps needing visual verification are flagged for the user to confirm manually.

## Output Files

**Archive folder rule.** Extraction runs always live under `Archive/` (in `Archive/Video-to-action/`, the `--output-dir` default). If the `Archive/` folder does not yet exist in the workspace, create it — along with the needed `Video-to-action/` subfolder — when file creation is allowed. Never redirect a run into any other folder (such as `Documentation/`) as a fallback. The run folder always nests inside `Archive/`.

Each run saves to a folder named `<output-dir>\<YYYYMMDD-HHMMSS> - <sanitized-title>\` — timestamp first (so runs still sort chronologically) followed by the readable, sanitized title:

| File | Description |
|------|-------------|
| `procedure.md` | The complete run record. Header carries the run metadata (source URL, extracted timestamp, intent, model, phases run, status), followed by Overview / Steps / Code, Commands & Configuration / Extraction Errors / Notes. The verbatim (unsanitized) title appears here |
| `prompts.md` | The exact prompts sent to Gemini for this run (with the injected title and the run's model/resolution/clip context) — the faithful per-run counterpart to the `PROMPTS.md` template |

`procedure.md` carries everything the run extracted; `prompts.md` records exactly what was asked. Both are markdown — humans and AI agents read it more naturally than escaped JSON, and no downstream program consumes the run programmatically, so no structured log is kept.

`<output-dir>\latest.json` is a Windows-safe pointer (plain JSON metadata, not a symlink) recording the latest run folder, URL, title, intent, and timestamp. Previous runs are preserved. All files are written with explicit UTF-8 encoding.

## Extraction Honesty

Be transparent about what video extraction can and cannot capture:

- **Can extract:** spoken instructions, on-screen text, code shown on screen, UI interactions described verbally, settings and values mentioned.
- **Partially reliable:** code that's partially visible, fast-scrolling content, background details — these arrive marked `LOW CONFIDENCE:`.
- **Cannot extract:** subtle visual techniques (brush strokes, precise mouse movements), audio-only cues with no verbal description.

When a step carries a `LOW CONFIDENCE:` marker, recommend the user watch the referenced timestamp directly rather than trusting the extraction.

## Multi-Video Learning

For topics spanning multiple videos:

1. Run the extraction separately per video (each gets its own run folder).
2. Merge into a single procedure, resolving conflicts — later videos override earlier ones.
3. De-duplicate steps that appear in multiple videos.
4. Note where videos disagree on approach.

## Orchestrating Agent Workflow

1. Confirm explicit `/video-to-action` invocation; extract the URL, intent, scope (full video or a section), and any model/resolution preferences.
2. Run `--check-setup`; if it fails, stop and route to the setup task.
3. Acquire the **mandatory** title per **Title Acquisition** above (user-supplied / runtime pop-up / stop-and-ask) and pass it via `--title`; never proceed without one.
4. Confirm the configured run and its rough cost with the user (free-tier status, phases, clipping, resolution).
5. Run the script from the host workspace root so outputs land inside the workspace.
6. Present results per the intent routing above; surface `LOW CONFIDENCE` flags and any failed phases honestly.
7. Do not act on extracted steps without the user's separate authorization.

## Boundaries

Do:

- require the exact `/video-to-action` slash command
- preflight setup before every real run and route to the setup task on failure
- state the public-only, daily-quota, and length limits honestly
- keep API keys out of chat, logs, and saved artifacts
- preserve `LOW CONFIDENCE` markers and failed-phase reports in what you present

Do not:

- auto-trigger this skill from natural language
- rely on any MCP server or agent-native video ingestion for the video analysis
- execute extracted tutorial steps without separate explicit authorization
- expose, echo, or persist the API key
- hard-code course-machine paths, preview-model defaults, or symlinks
- claim support for private or unlisted videos

## Edge Cases

- **Missing key or packages:** preflight fails; stop and route to the pending setup task.
- **Private/unlisted/unavailable video:** the API call fails; report it and suggest the user provide a transcript instead.
- **Video is not a tutorial:** still extract what's useful — key claims, demonstrated results, referenced tools — and note it isn't step-by-step content.
- **Very long video (1hr+):** ask which section matters and clip with `--start`/`--end`, or use `--resolution low`; analyze in segments for full coverage.
- **Non-English video:** Gemini handles many languages; note the language and potential translation artifacts.
- **Extracted code doesn't work:** common — screen code is often partial or has typos. The procedure's Notes section says to verify before use; repeat that warning when presenting.
- **Daily quota exhausted (free tier):** the API rejects the call; report it and suggest waiting for the quota reset or upgrading tier.
- **Dead or invalid model id:** every phase fails fast with the API error; verify the id against current Google docs and pass `--model`.

## Validation

After creating or updating this skill:

- confirm only `/video-to-action` activates it
- confirm the setup gate stops the workflow when prerequisites are missing
- confirm the hard limits, cost guidance, and key-safety rules are present
- confirm the three extraction prompt contracts, intent routing, and LOW CONFIDENCE handling remain intact
- confirm the common-mistakes line allows labeled inference (`(inferred)`), not forced to "None"
- confirm the title-acquisition workflow is mandatory and agent-agnostic with an explicit stop-and-ask fallback
- confirm `--title` is required (extraction errors without it), used verbatim in `procedure.md`, and sanitized into the `<timestamp> - <title>` run-folder name
- confirm the title infer path is gone and the metadata canary stays silent unless metadata is actually readable
- confirm `sanitize_title` produces Windows-safe folder names (no `< > : " / \ | ? *`, no trailing dot/space, length-capped)
- confirm each run writes a per-run `prompts.md`
- confirm no MCP dependency, course paths, broad triggers, or symlinks remain
- confirm all file writes in the script specify UTF-8 explicitly
- run `python scripts\video_to_action.py --check-setup` as a harmless smoke test (no API call)
- run `python scripts\video_to_action.py --dump-prompts` and confirm `PROMPTS.md` is unchanged (the template matches the live prompt constants)
- validate the folder with the installed `quick_validate.py` in UTF-8 mode (`-X utf8`)
