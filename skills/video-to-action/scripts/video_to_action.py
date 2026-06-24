#!/usr/bin/env python3
"""
Video-to-Action - YouTube tutorial extraction via the Gemini API (Uzzy adaptation).

Sends a public YouTube URL to Gemini video understanding and runs structured
extraction phases (overview, step-by-step, technical), then compiles the results
into a procedure document. The script only extracts; acting on extracted steps
is the orchestrating agent's job and requires separate user authorization.

Requires: Python 3.10+, `google-genai`, `python-dotenv`, and GEMINI_API_KEY.
Run `video_to_action.py --check-setup` to verify prerequisites without any API call.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "gemini-3.5-flash"
DEFAULT_OUTPUT_DIR = Path("Archive") / "Video-to-action"

SETUP_TASK_HINT = (
    "Setup is incomplete. See the pending video-to-action setup/learning task in "
    "your workspace (Archive\\Tasks\\) for API key creation, safe storage, and "
    "dependency installation steps."
)

OVERVIEW_PROMPT = """\
Analyze this YouTube video and provide a structured breakdown.

Begin your response with exactly this line, followed by a blank line:

Here is a structured breakdown of the video:

Then output the following five sections, each with its heading in this exact form \
and order — keep the "N.)" numbering and the heading text verbatim:

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

Title rule: the exact VIDEO TITLE is provided to you in the instruction above. Use \
it verbatim and do not infer, alter, or add any marker. Separately, and ONLY if you \
can actually read the real title from the video's metadata, add one extra bullet \
immediately under the Approximate Length line: `* **Metadata title (from video \
metadata):** "..."` and note whether it matches the supplied title. If you cannot \
access the video's metadata (the current expected behaviour), omit that bullet \
entirely — do not state that metadata is unavailable.

Be specific and concrete. Don't say "the presenter shows techniques" — say what the \
techniques are.\
"""

STEPS_PROMPT = """\
Extract detailed step-by-step instructions from this video.

Format every step as a Markdown section using this exact shape, separated from the \
next step by a horizontal rule (`---`):

### STEP {n}: {short title}
* **TIMESTAMP:** {MM:SS}-{MM:SS} (the approximate start-to-end range for this step)
* **ACTION:** {what to do, in imperative form, e.g. "Click File > New" or "Set the value to 0.5"}
* **DETAILS:** {specific values, settings, parameters shown; if the presenter says \
"adjust to taste" or similar, record the value they actually used in the demo}
* **VISUAL REFERENCE:** {what the screen/result should look like after this step}
* **COMMON MISTAKES:** {a pitfall for this step — include one when the presenter \
states it, or when a practitioner would clearly recognize a well-founded pitfall for \
this step. Mark inferred pitfalls "(inferred)". Write "None notable" only when nothing \
meaningful applies.}

Be extremely specific about values, menu paths, and settings. When a step shows code, \
commands, or JSON, reproduce it inside a fenced Markdown code block (triple backticks), \
never inline.

If a step relies on a subtle visual technique that may not be fully captured (precise \
mouse movements, brush strokes, gestures), prefix that step's ACTION with \
"LOW CONFIDENCE:" and describe it as best you can.\
"""

TECHNICAL_PROMPT = """\
Extract all code, commands, configurations, and technical details from this video.

Extract:
1. All CODE SNIPPETS shown (reconstruct from what's visible on screen)
2. All TERMINAL COMMANDS run
3. All CONFIGURATION values or settings changed
4. All FILE PATHS referenced
5. All DEPENDENCIES or PACKAGES installed
6. Any API keys, environment variables, or config needed (note if they're \
placeholder values)

Reproduce every code snippet, command, and configuration inside a fenced Markdown \
code block (triple backticks), never inline. For code: provide the complete snippet, \
not fragments. If code is partially visible, note what's inferred and mark it \
"LOW CONFIDENCE:". For commands: provide the exact command, including flags and \
arguments.\
"""

PHASE_DEFS = [
    {"key": "overview", "title": "Overview extraction", "prompt": OVERVIEW_PROMPT},
    {"key": "steps", "title": "Step-by-step extraction", "prompt": STEPS_PROMPT},
    {"key": "technical", "title": "Technical extraction", "prompt": TECHNICAL_PROMPT},
]


# ── Preflight ────────────────────────────────────────────────────────────────

def load_env_files() -> None:
    """Load .env from the current working directory, then the script's folder.

    Values already present in the environment are never overwritten.
    """
    from dotenv import load_dotenv

    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        load_dotenv(cwd_env)
    script_env = Path(__file__).resolve().parent / ".env"
    if script_env.is_file():
        load_dotenv(script_env)


def check_setup(verbose: bool = True) -> bool:
    """Verify dependencies and API key without making any API call.

    Never prints the key itself - only whether it is present.
    """
    ok = True

    try:
        from google import genai  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: the 'google-genai' package is not installed "
                  "(pip install google-genai).")

    try:
        import dotenv  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: the 'python-dotenv' package is not installed "
                  "(pip install python-dotenv).")

    if ok:
        load_env_files()
        if os.environ.get("GEMINI_API_KEY"):
            if verbose:
                print("OK: GEMINI_API_KEY is set (value not displayed).")
        else:
            ok = False
            if verbose:
                print("MISSING: GEMINI_API_KEY is not set in the environment "
                      "or a discoverable .env file.")

    if verbose:
        if ok:
            print("Setup check passed. No API call was made.")
        else:
            print(SETUP_TASK_HINT)
    return ok


# ── Prompt documentation ─────────────────────────────────────────────────────

def build_prompts_doc() -> str:
    """Build prompts.md content from the live prompt constants.

    Generating the doc from the constants (rather than hand-maintaining it)
    guarantees prompts.md can never drift from what Gemini actually receives.
    """
    sections = [
        "# Video-to-Action — Orchestrator Prompts (Template)",
        "",
        "Auto-generated from the prompt constants in `scripts/video_to_action.py` by",
        "running `python scripts/video_to_action.py --dump-prompts`. Do not edit by",
        "hand — regenerate after changing the prompts. This is the canonical TEMPLATE;",
        "each run also writes a per-run lowercase `prompts.md` into its run folder",
        "capturing the actual prompts sent (which may include a user-supplied title",
        "injected into Phase 1). Each phase below is sent to the Gemini model verbatim",
        "as the text part of the request, alongside the YouTube video. Phase 3 runs",
        "only with `--phases 3`.",
        "",
        "## Phase 1 — Overview extraction",
        "",
        "```text",
        OVERVIEW_PROMPT,
        "```",
        "",
        "## Phase 2 — Step-by-step extraction",
        "",
        "```text",
        STEPS_PROMPT,
        "```",
        "",
        "## Phase 3 — Technical extraction (only with --phases 3)",
        "",
        "```text",
        TECHNICAL_PROMPT,
        "```",
        "",
    ]
    return "\n".join(sections)


def dump_prompts() -> Path:
    """Write PROMPTS.md (the canonical template) next to SKILL.md. No API call."""
    target = Path(__file__).resolve().parent.parent / "PROMPTS.md"
    target.write_text(build_prompts_doc(), encoding="utf-8")
    return target


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_offset(value: str) -> str:
    """Accept seconds ('90'), MM:SS ('1:30'), or HH:MM:SS and return 'Ns' form."""
    value = value.strip()
    if re.fullmatch(r"\d+", value):
        return f"{value}s"
    parts = value.split(":")
    if len(parts) in (2, 3) and all(re.fullmatch(r"\d+", p) for p in parts):
        seconds = 0
        for p in parts:
            seconds = seconds * 60 + int(p)
        return f"{seconds}s"
    raise argparse.ArgumentTypeError(
        f"invalid time offset '{value}' (use seconds, MM:SS, or HH:MM:SS)")


def sanitize_title(text: str, fallback: str = "video") -> str:
    """Make a readable, Windows-safe folder name from a title.

    Preserves letters, digits, spaces, parentheses and hyphens. Replaces each
    Windows-illegal character (< > : " / \\ | ? * and control chars) with a hyphen,
    drops other punctuation, collapses repeated separators, trims trailing dots and
    spaces (illegal at the end of a Windows name), and caps the length so the run
    path stays well under the ~260-char limit.
    """
    # Windows-illegal characters and control chars become hyphens (not dropped, so
    # word boundaries survive, e.g. "How to: Build" -> "How to- Build").
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", text)
    # Drop remaining punctuation that isn't a word char, space, parenthesis or hyphen.
    text = re.sub(r"[^\w\s()-]", "", text)
    # Collapse whitespace and repeated hyphens.
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"-{2,}", "-", text).strip()
    # Cap length, then trim trailing space/dot/hyphen (dots/spaces are illegal at end).
    text = text[:70].rstrip(" .-")
    return text or fallback


def is_youtube_url(url: str) -> bool:
    return bool(re.match(
        r"https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)",
        url))


# ── Core ─────────────────────────────────────────────────────────────────────

def run_phase(client, model: str, url: str, prompt: str,
              start: str | None, end: str | None, low_res: bool) -> str:
    """Run one extraction phase against the video. Returns the response text."""
    from google.genai import types

    metadata_kwargs = {}
    if start:
        metadata_kwargs["start_offset"] = start
    if end:
        metadata_kwargs["end_offset"] = end

    file_part_kwargs = {
        "file_data": types.FileData(file_uri=url),
    }
    if metadata_kwargs:
        file_part_kwargs["video_metadata"] = types.VideoMetadata(**metadata_kwargs)

    config = None
    if low_res:
        config = types.GenerateContentConfig(
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
        )

    response = client.models.generate_content(
        model=model,
        contents=types.Content(parts=[
            types.Part(**file_part_kwargs),
            types.Part(text=prompt),
        ]),
        config=config,
    )
    return response.text or ""


def compile_procedure(url: str, intent: str, model: str,
                      phases_run: list, results: dict, errors: list) -> str:
    """Compile phase results into the procedure markdown document.

    This document is the single human-readable run record. It carries the run
    metadata (source, timestamp, intent, model, phases run, status) in its
    header, then the extracted content, errors, and notes.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not results:
        status = "failed (no phases succeeded)"
    elif errors:
        status = f"partial ({len(errors)} phase error(s))"
    else:
        status = "complete"
    lines = [
        "# Extracted Procedure",
        "",
        f"**Source**: {url}",
        f"**Extracted**: {now}",
        f"**Intent**: {intent}",
        f"**Model**: {model}",
        f"**Phases run**: {', '.join(phases_run) if phases_run else 'none'}",
        f"**Status**: {status}",
        "",
    ]
    if "overview" in results:
        lines += ["## Overview", "", results["overview"], ""]
    if "steps" in results:
        lines += ["## Steps", "", results["steps"], ""]
    if "technical" in results:
        lines += ["## Code, Commands & Configuration", "", results["technical"], ""]
    if errors:
        lines += ["## Extraction Errors", ""]
        for e in errors:
            lines.append(f"- Phase `{e['phase']}` failed: {e['error']}")
        lines.append("")
    lines += [
        "## Notes",
        "",
        "- Extracted by Gemini video understanding. Code shown on screen may be "
        "partially visible or contain typos; verify before use.",
        "- Items marked LOW CONFIDENCE involve visual techniques that may not be "
        "fully captured. Watch the referenced timestamp directly for those steps.",
        "- Acting on these steps requires separate user authorization; this "
        "document is an extraction, not an instruction to execute.",
        "",
    ]
    return "\n".join(lines)


def build_effective_prompts(phase_defs: list, title: str | None) -> list:
    """Return the phase prompts actually used this run, injecting a user-supplied
    title into the overview phase when one is given."""
    effective = []
    for pd in phase_defs:
        prompt = pd["prompt"]
        if pd["key"] == "overview" and title:
            prompt = (
                f'The exact title of this video is: "{title}". Use it verbatim as '
                f'the `### 1.) Video Title and Length` value; it is user-supplied and '
                f'authoritative — do not infer or alter it and do not add any marker. '
                f'(You may still perform the separate metadata check described '
                f'below.)\n\n' + prompt
            )
        effective.append({"key": pd["key"], "title": pd["title"], "prompt": prompt})
    return effective


def build_run_prompts_doc(url: str, model: str, resolution: str, clip: str,
                          title: str | None, effective: list) -> str:
    """Build the per-run prompts.md: the exact prompts sent to Gemini this run."""
    lines = [
        "# Prompts sent this run",
        "",
        f"**Source**: {url}",
        f"**Model**: {model}",
        f"**Resolution**: {resolution}",
        f"**Clip**: {clip}",
        f"**Title supplied**: {title if title else '(none — model infers the title)'}",
        "",
        "The exact phase prompts sent to Gemini for THIS run. The canonical template",
        "lives in `PROMPTS.md` at the skill root; this file reflects any per-run",
        "changes, such as an injected title.",
        "",
    ]
    headings = {
        "overview": "Phase 1 — Overview extraction",
        "steps": "Phase 2 — Step-by-step extraction",
        "technical": "Phase 3 — Technical extraction",
    }
    for pd in effective:
        lines += [f"## {headings.get(pd['key'], pd['key'])}", "",
                  "```text", pd["prompt"], "```", ""]
    return "\n".join(lines)


def save_outputs(output_base: Path, url: str, intent: str, model: str,
                 phases_run: list, results: dict, errors: list,
                 effective: list, resolution: str, clip: str,
                 title: str | None) -> Path:
    """Save procedure.md, the per-run prompts.md, and the latest-run pointer.

    procedure.md is the single human-readable record; prompts.md captures the exact
    prompts sent this run; latest.json is a small pointer for quick lookups.
    """
    run_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = f"{run_ts} - {sanitize_title(title)}" if title else run_ts
    output_dir = output_base / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    proc_path = output_dir / "procedure.md"
    proc_path.write_text(
        compile_procedure(url, intent, model, phases_run, results, errors),
        encoding="utf-8")

    prompts_path = output_dir / "prompts.md"
    prompts_path.write_text(
        build_run_prompts_doc(url, model, resolution, clip, title, effective),
        encoding="utf-8")

    # Windows-safe latest-run pointer (JSON metadata file, not a symlink)
    latest_path = output_base / "latest.json"
    latest_path.write_text(
        json.dumps(
            {
                "latest_run": run_ts,
                "run_dir": str(output_dir),
                "url": url,
                "title": title,
                "intent": intent,
                "completed": bool(results),
                "timestamp": datetime.now().isoformat(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return proc_path


def run_extraction(url: str, intent: str, phases: int, model: str,
                   start: str | None, end: str | None, low_res: bool,
                   output_base: Path, title: str | None = None) -> int:
    """Run the extraction phases and save outputs. Returns an exit code."""
    from google import genai

    client = genai.Client()

    phase_defs = PHASE_DEFS[:phases]
    effective = build_effective_prompts(phase_defs, title)
    resolution = "low" if low_res else "default"
    clip = f"{start or 'start'} -> {end or 'end'}" if (start or end) else "full video"
    results: dict = {}
    errors: list = []

    print(f"Video-to-Action — {len(phase_defs)} phases, model {model}")
    print(f"  URL: {url}")
    if start or end:
        print(f"  Clip: {start or 'start'} -> {end or 'end'}")
    if low_res:
        print("  Resolution: low (~100 tokens/sec of video)")
    else:
        print("  Resolution: default (~300 tokens/sec of video)")
    if title:
        print(f'  Title: supplied by user ("{title}")')
    else:
        print("  Title: model will infer")
    print()

    for pd in effective:
        print(f"  Phase: {pd['title']} ...")
        try:
            text = run_phase(client, model, url, pd["prompt"], start, end, low_res)
            if not text.strip():
                raise RuntimeError("empty response from the API")
            results[pd["key"]] = text
            print(f"    OK ({len(text)} chars)")
        except Exception as exc:  # noqa: BLE001
            errors.append({
                "phase": pd["key"],
                "error": f"{type(exc).__name__}: {exc}",
                "timestamp": datetime.now().isoformat(),
            })
            print(f"    FAILED: {type(exc).__name__}: {exc}")

    if not results:
        print("\nAll phases failed. Nothing to compile. Common causes: private or "
              "unlisted video, invalid model id, exhausted daily quota, or an "
              "authentication problem.")
        save_outputs(output_base, url, intent, model,
                     [p["key"] for p in effective], results, errors,
                     effective, resolution, clip, title)
        return 1

    proc_path = save_outputs(
        output_base, url, intent, model,
        [p["key"] for p in effective], results, errors,
        effective, resolution, clip, title)

    print(f"\nSaved: {proc_path}")
    if errors:
        print(f"Completed with {len(errors)} failed phase(s); see Extraction "
              "Errors in the procedure document.")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Video-to-Action — extract procedures from public YouTube "
                    "videos via the Gemini API")
    parser.add_argument("url", nargs="?", default=None,
                        help="Public YouTube video URL")
    parser.add_argument("--intent", default="summarize",
                        choices=["follow", "summarize", "learn"],
                        help="What the extraction is for (default: summarize). "
                             "Note: 'follow' still only extracts; execution needs "
                             "separate authorization.")
    parser.add_argument("--phases", type=int, default=2, choices=[2, 3],
                        help="Extraction passes: 2 for general content, 3 to add "
                             "the technical pass for coding/software videos "
                             "(default: 2)")
    parser.add_argument("--model", default=os.environ.get(
                            "VIDEO_TO_ACTION_MODEL", DEFAULT_MODEL),
                        help=f"Gemini model id (default: {DEFAULT_MODEL}, or "
                             "VIDEO_TO_ACTION_MODEL env var)")
    parser.add_argument("--start", type=parse_offset, default=None,
                        help="Analyze from this offset (seconds, MM:SS, or HH:MM:SS)")
    parser.add_argument("--end", type=parse_offset, default=None,
                        help="Analyze up to this offset (seconds, MM:SS, or HH:MM:SS)")
    parser.add_argument("--resolution", default="default",
                        choices=["default", "low"],
                        help="Media resolution: 'low' cuts video token cost ~3x "
                             "and extends the length cap (default: default)")
    parser.add_argument("--output-dir", default=os.environ.get(
                            "VIDEO_TO_ACTION_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)),
                        help="Base directory for run outputs (default: "
                             "Archive\\Video-to-action under the current directory, "
                             "or VIDEO_TO_ACTION_OUTPUT_DIR env var)")
    parser.add_argument("--check-setup", action="store_true",
                        help="Verify dependencies and API key, make no API call, "
                             "then exit")
    parser.add_argument("--dump-prompts", action="store_true",
                        help="Regenerate PROMPTS.md (the canonical prompt template) "
                             "next to SKILL.md and exit; makes no API call")
    parser.add_argument("--title", default=None,
                        help="Exact video title (REQUIRED for an extraction run). "
                             "Supplied by the orchestrating agent from user input "
                             "(typed, pasted, or read from a screenshot). Used verbatim "
                             "in procedure.md and, sanitized, in the run folder name.")
    args = parser.parse_args()

    if args.dump_prompts:
        target = dump_prompts()
        print(f"Wrote {target}")
        sys.exit(0)

    if args.check_setup:
        sys.exit(0 if check_setup(verbose=True) else 1)

    if not args.url:
        parser.error("a YouTube URL is required (or use --check-setup)")
    if not is_youtube_url(args.url):
        parser.error("the URL does not look like a YouTube video URL "
                     "(youtube.com/watch, youtu.be, or youtube.com/shorts)")
    if not args.title or not args.title.strip():
        parser.error('a title is required: pass --title "..." (the orchestrating '
                     "agent supplies it from user input; this skill no longer "
                     "infers titles)")

    if not check_setup(verbose=False):
        check_setup(verbose=True)
        sys.exit(1)

    try:
        sys.exit(run_extraction(
            url=args.url,
            intent=args.intent,
            phases=args.phases,
            model=args.model,
            start=args.start,
            end=args.end,
            low_res=(args.resolution == "low"),
            output_base=Path(args.output_dir),
            title=args.title,
        ))
    except KeyboardInterrupt:
        print("\nExtraction cancelled by user. No further API calls will be made.")
        sys.exit(130)


if __name__ == "__main__":
    main()
