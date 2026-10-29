# Video-to-Action — Orchestrator Prompts (Template)

Auto-generated from `scripts/video_to_action.py` by `--dump-prompts`.
Free tier is the non-blocking default. The primary model is
`gemini-3.8-flash` and the one-attempt fallback after three recognized
transient primary failures is `gemini-3.6-flash`.

The Procedure call always runs. Deep Summary is default-on. Technical is
opt-in and requires an explicit coding/software relevance confirmation.
Choices already present in the request are reused without reconfirmation.
Per-run prompts.md stores each exact selected prompt once and associates
all sanitized model-attempt provenance with that prompt.

Every selected phase uses static video processing by default.
--processing agentic opts into agentic processing; a failed agentic phase
recovers through static processing with the same prompt. An explicit optional
--custom-request supplements the Procedure prompt in the same call and
requires a Your Specific Request answer section. Empty requests add nothing.

## Procedure (always)

```text
Analyze this YouTube video and produce BOTH an overview
and detailed steps in one response. Use this exact order.

## Overview

Begin with exactly: Here is a structured breakdown of the video:

### 1.) Video Title and Length
* **Video Title:** {use the exact supplied title; never infer or alter it}
* **Length:** {use the exact supplied duration verbatim}

### 2.) Summary
{2-3 concrete sentences describing what the video teaches}

### 3.) Prerequisites
{tools, software, or knowledge needed, as bullets}

### 4.) Main Sections
{chronological chapters with approximate timestamp ranges, as bullets}

### 5.) Key Outcomes
{what the viewer can do after watching, as bullets}

## Steps

Format every step as follows and separate steps with `---`:

### STEP {n}: {short title}
* **TIMESTAMP:** {MM:SS-MM:SS}
* **ACTION:** {specific imperative action}
* **DETAILS:** {exact values, settings, and demonstrated choices}
* **VISUAL REFERENCE:** {expected screen or result}
* **COMMON MISTAKES:** {stated pitfall, well-founded `(inferred)` pitfall, or
  `None notable` only when nothing meaningful applies}

Put code, commands, or JSON in fenced Markdown blocks. Prefix uncertain subtle
visual actions with `LOW CONFIDENCE:` and direct the reader to the timestamp.
If and only if video metadata exposes a title, add a metadata-title bullet and
compare it with the supplied title; otherwise omit that bullet entirely.
```

## Deep Summary (default-on; --no-deep-summary opts out)

```text
Create a long, faithful, chronological deep summary of
this YouTube video. Only summarize content actually present in the video. Map
acts to timestamped chapters or meaningful chronological beats.

Return ONLY ACT sections using this exact heading contract:

## 🎭 ACT I: {specific chronological title}
**Timestamp:** {approximate range}
{Detailed faithful narrative of what happens, what is explained, and why it
matters. Clearly label any inference.}

Continue with `## 🎭 ACT II:`, `## 🎭 ACT III:`, and as many sequential acts as
needed. End exactly with:

## 🎭 FINAL ACT: Key Takeaways
{Thorough synthesis of the video's conclusions, lessons, and cautions.}

Do not include session pickup, active-plan status, next-session context, or any
other work-session template content. Do not fabricate inaccessible details.
```

## Technical (opt-in; coding/software only)

```text
Extract all code, commands, configurations, and technical
details actually shown in this coding/software video.

Include code snippets, terminal commands, configuration values, file paths,
dependencies, packages, and required environment variables. Put every snippet,
command, and configuration in fenced Markdown blocks. Mark partial or inferred
content `LOW CONFIDENCE:`. Never expose real secret values.
```
