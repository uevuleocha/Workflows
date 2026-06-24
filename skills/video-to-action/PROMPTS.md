# Video-to-Action — Orchestrator Prompts (Template)

Auto-generated from the prompt constants in `scripts/video_to_action.py` by
running `python scripts/video_to_action.py --dump-prompts`. Do not edit by
hand — regenerate after changing the prompts. This is the canonical TEMPLATE;
each run also writes a per-run lowercase `prompts.md` into its run folder
capturing the actual prompts sent (which may include a user-supplied title
injected into Phase 1). Each phase below is sent to the Gemini model verbatim
as the text part of the request, alongside the YouTube video. Phase 3 runs
only with `--phases 3`.

## Phase 1 — Overview extraction

```text
Analyze this YouTube video and provide a structured breakdown.

Begin your response with exactly this line, followed by a blank line:

Here is a structured breakdown of the video:

Then output the following five sections, each with its heading in this exact form and order — keep the "N.)" numbering and the heading text verbatim:

### 1.) Video Title and Length
* **Video Title:** {title — see the title rule below}
* **Approximate Length:** {approximate duration}

### 2.) Summary
{2-3 sentences on what the video teaches}

### 3.) Prerequisites
{tools, software, or knowledge needed before starting, as bullet points}

### 4.) Main Sections
{the major sections/chapters with approximate timestamp ranges, as bullet points}

### 5.) Key Outcomes
{what the viewer can do after watching, as bullet points}

Title rule: the exact VIDEO TITLE is provided to you in the instruction above. Use it verbatim and do not infer, alter, or add any marker. Separately, and ONLY if you can actually read the real title from the video's metadata, add one extra bullet immediately under the Approximate Length line: `* **Metadata title (from video metadata):** "..."` and note whether it matches the supplied title. If you cannot access the video's metadata (the current expected behaviour), omit that bullet entirely — do not state that metadata is unavailable.

Be specific and concrete. Don't say "the presenter shows techniques" — say what the techniques are.
```

## Phase 2 — Step-by-step extraction

```text
Extract detailed step-by-step instructions from this video.

Format every step as a Markdown section using this exact shape, separated from the next step by a horizontal rule (`---`):

### STEP {n}: {short title}
* **TIMESTAMP:** {MM:SS}-{MM:SS} (the approximate start-to-end range for this step)
* **ACTION:** {what to do, in imperative form, e.g. "Click File > New" or "Set the value to 0.5"}
* **DETAILS:** {specific values, settings, parameters shown; if the presenter says "adjust to taste" or similar, record the value they actually used in the demo}
* **VISUAL REFERENCE:** {what the screen/result should look like after this step}
* **COMMON MISTAKES:** {a pitfall for this step — include one when the presenter states it, or when a practitioner would clearly recognize a well-founded pitfall for this step. Mark inferred pitfalls "(inferred)". Write "None notable" only when nothing meaningful applies.}

Be extremely specific about values, menu paths, and settings. When a step shows code, commands, or JSON, reproduce it inside a fenced Markdown code block (triple backticks), never inline.

If a step relies on a subtle visual technique that may not be fully captured (precise mouse movements, brush strokes, gestures), prefix that step's ACTION with "LOW CONFIDENCE:" and describe it as best you can.
```

## Phase 3 — Technical extraction (only with --phases 3)

```text
Extract all code, commands, configurations, and technical details from this video.

Extract:
1. All CODE SNIPPETS shown (reconstruct from what's visible on screen)
2. All TERMINAL COMMANDS run
3. All CONFIGURATION values or settings changed
4. All FILE PATHS referenced
5. All DEPENDENCIES or PACKAGES installed
6. Any API keys, environment variables, or config needed (note if they're placeholder values)

Reproduce every code snippet, command, and configuration inside a fenced Markdown code block (triple backticks), never inline. For code: provide the complete snippet, not fragments. If code is partially visible, note what's inferred and mark it "LOW CONFIDENCE:". For commands: provide the exact command, including flags and arguments.
```
