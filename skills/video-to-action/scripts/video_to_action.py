#!/usr/bin/env python3
"""Deterministic YouTube-to-report extraction through the Gemini API.

The script is the sole writer of each run's report.md and prompts.md. It never
invokes report-this or session-summary; it only conforms structurally to the
local report package. Real runs require orchestrator-supplied phase choices.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_MODEL = "gemini-3.5-flash"
DEFAULT_OUTPUT_DIR = Path("Archive") / "Historical" / "Video-to-action"
SETUP_TASK_HINT = (
    "Setup is incomplete. See the pending video-to-action setup task under "
    "Archive\\Live\\Tasks\\<Subject>\\ for key and dependency setup."
)

PROCEDURE_PROMPT = r'''Analyze this YouTube video and produce BOTH an overview
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
compare it with the supplied title; otherwise omit that bullet entirely.'''

DEEP_SUMMARY_PROMPT = r'''Create a long, faithful, chronological deep summary of
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
other work-session template content. Do not fabricate inaccessible details.'''

TECHNICAL_PROMPT = r'''Extract all code, commands, configurations, and technical
details actually shown in this coding/software video.

Include code snippets, terminal commands, configuration values, file paths,
dependencies, packages, and required environment variables. Put every snippet,
command, and configuration in fenced Markdown blocks. Mark partial or inferred
content `LOW CONFIDENCE:`. Never expose real secret values.'''

PHASE_DEFS = {
    "procedure": {"key": "procedure", "title": "Procedure", "prompt": PROCEDURE_PROMPT},
    "deep_summary": {
        "key": "deep_summary", "title": "Deep Summary", "prompt": DEEP_SUMMARY_PROMPT,
    },
    "technical": {"key": "technical", "title": "Technical", "prompt": TECHNICAL_PROMPT},
}


def load_env_files() -> None:
    from dotenv import load_dotenv
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)


def check_setup(verbose: bool = True) -> bool:
    ok = True
    try:
        from google import genai  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: google-genai (pip install google-genai).")
    try:
        import dotenv  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: python-dotenv (pip install python-dotenv).")
    if ok:
        load_env_files()
        if os.environ.get("GEMINI_API_KEY"):
            if verbose:
                print("OK: GEMINI_API_KEY is set (value not displayed).")
        else:
            ok = False
            if verbose:
                print("MISSING: GEMINI_API_KEY is not set.")
    if verbose:
        print("Setup check passed. No API call was made." if ok else SETUP_TASK_HINT)
    return ok


def selected_phase_defs(deep_summary: bool, technical: bool,
                        coding_video: bool) -> list[dict]:
    if technical and not coding_video:
        raise ValueError("--technical requires --coding-video")
    phases = [PHASE_DEFS["procedure"]]
    if deep_summary:
        phases.append(PHASE_DEFS["deep_summary"])
    if technical:
        phases.append(PHASE_DEFS["technical"])
    return phases


def build_prompts_doc() -> str:
    sections = [
        "# Video-to-Action — Orchestrator Prompts (Template)", "",
        "Auto-generated from `scripts/video_to_action.py` by `--dump-prompts`.",
        "The Procedure call always runs. Deep Summary is opt-in. Technical is",
        "opt-in and requires an explicit coding/software relevance confirmation.", "",
    ]
    for key in ("procedure", "deep_summary", "technical"):
        pd = PHASE_DEFS[key]
        qualifier = {
            "procedure": "always",
            "deep_summary": "opt-in",
            "technical": "opt-in; coding/software only",
        }[key]
        sections += [f"## {pd['title']} ({qualifier})", "", "```text",
                     pd["prompt"], "```", ""]
    return "\n".join(sections)


def dump_prompts() -> Path:
    target = Path(__file__).resolve().parent.parent / "PROMPTS.md"
    target.write_text(build_prompts_doc(), encoding="utf-8")
    return target


def parse_offset(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d+", value):
        return f"{value}s"
    parts = value.split(":")
    if len(parts) in (2, 3) and all(re.fullmatch(r"\d+", p) for p in parts):
        seconds = 0
        for part in parts:
            seconds = seconds * 60 + int(part)
        return f"{seconds}s"
    raise argparse.ArgumentTypeError("use seconds, MM:SS, or HH:MM:SS")


def normalize_duration(value: str) -> str:
    """Validate MM:SS or HH:MM:SS and return a zero-padded value."""
    value = value.strip()
    short = re.fullmatch(r"(\d{1,2}):([0-5]\d)", value)
    if short:
        return f"{int(short.group(1)):02d}:{int(short.group(2)):02d}"
    long = re.fullmatch(r"(\d{1,3}):([0-5]\d):([0-5]\d)", value)
    if long:
        return (f"{int(long.group(1)):02d}:{int(long.group(2)):02d}:"
                f"{int(long.group(3)):02d}")
    raise argparse.ArgumentTypeError("duration must be MM:SS or HH:MM:SS")


def demote_embedded_headings(text: str, block: str) -> str:
    """Demote selected H2 headings outside fenced code blocks only."""
    lines = text.splitlines()
    in_fence = False
    fence_marker = None
    output = []
    for line in lines:
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in ("```", "~~~"):
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            output.append(line)
            continue
        if not in_fence:
            if block == "procedure" and line in ("## Overview", "## Steps"):
                line = "#" + line
            elif block == "deep_summary" and (
                    line.startswith("## 🎭 ACT ") or
                    line.startswith("## 🎭 FINAL ACT:")):
                line = "#" + line
        output.append(line)
    return "\n".join(output)

def sanitize_title(text: str, fallback: str = "video") -> str:
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", text)
    text = re.sub(r"[^\w\s()-]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"-{2,}", "-", text).strip()[:70].rstrip(" .-")
    return text or fallback


def is_youtube_url(url: str) -> bool:
    return bool(re.match(
        r"https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)",
        url,
    ))


def inject_ground_truth(prompt: str, title: str, duration: str,
                        include_title: bool) -> str:
    duration_rule = (
        f"This video's exact total length is {duration}; use it verbatim as the "
        f"Length, and ensure every timestamp falls within 00:00–{duration}."
    )
    if include_title:
        title_rule = (f'The exact video title is: "{title}". Use it verbatim. '
                      "It is user-supplied and authoritative.")
        return f"{title_rule}\n{duration_rule}\n\n{prompt}"
    return f"{duration_rule}\n\n{prompt}"


def build_effective_prompts(phase_defs: list[dict], title: str,
                            duration: str) -> list[dict]:
    effective = []
    for pd in phase_defs:
        prompt = pd["prompt"]
        if pd["key"] in ("procedure", "deep_summary"):
            prompt = inject_ground_truth(
                prompt, title, duration, include_title=pd["key"] == "procedure")
        effective.append({**pd, "prompt": prompt})
    return effective


def run_phase(client, model: str, url: str, prompt: str,
              start: str | None, end: str | None, low_res: bool) -> str:
    from google.genai import types
    metadata = {}
    if start:
        metadata["start_offset"] = start
    if end:
        metadata["end_offset"] = end
    file_args = {"file_data": types.FileData(file_uri=url)}
    if metadata:
        file_args["video_metadata"] = types.VideoMetadata(**metadata)
    config = None
    if low_res:
        config = types.GenerateContentConfig(
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW)
    response = client.models.generate_content(
        model=model,
        contents=types.Content(parts=[types.Part(**file_args), types.Part(text=prompt)]),
        config=config,
    )
    return response.text or ""


def execute_phases(effective: list[dict], runner) -> tuple[dict, list]:
    results, errors = {}, []
    for pd in effective:
        try:
            text = runner(pd)
            if not text.strip():
                raise RuntimeError("empty response")
            results[pd["key"]] = text
        except Exception as exc:  # noqa: BLE001
            errors.append({"phase": pd["key"], "error": f"{type(exc).__name__}: {exc}"})
    return results, errors


def compile_report(title: str, duration: str, url: str, intent: str, model: str,
                   phases_run: list[str], results: dict, errors: list) -> str:
    status = "failed" if not results else ("partial" if errors else "complete")
    lines = [
        f"# {title} — Video Extraction Report", "", "## Report Metadata", "",
        f"- **Source:** {url}",
        f"- **Duration:** {duration}",
        f"- **Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Intent:** {intent}", f"- **Model:** {model}",
        f"- **Calls selected:** {', '.join(phases_run)}",
        f"- **Status:** {status}", "", "## Procedure", "",
        demote_embedded_headings(
            results.get("procedure", "Procedure extraction failed; see Extraction Errors."),
            "procedure"), "",
    ]
    if "technical" in results:
        lines += ["### Code, Commands & Configuration", "", results["technical"], ""]
    lines += ["## Detailed Summary", ""]
    deep_summary_selected = "deep_summary" in phases_run
    if "deep_summary" in results:
        lines += [demote_embedded_headings(results["deep_summary"], "deep_summary"), ""]
    elif deep_summary_selected:
        lines += ["Deep Summary extraction failed; see Extraction Errors.", ""]
    else:
        lines += ["Not selected for this run.", ""]
    if errors:
        lines += ["## Extraction Errors", ""]
        lines += [f"- Phase `{e['phase']}` failed: {e['error']}" for e in errors]
        lines.append("")
    lines += [
        "## Notes", "",
        "- Gemini produced all extracted video content; the orchestrating agent did not synthesize it.",
        "- Verify code and LOW CONFIDENCE items against the referenced timestamps.",
        "- Acting on extracted steps requires separate user authorization.", "",
    ]
    return "\n".join(lines)


def build_run_prompts_doc(url: str, model: str, resolution: str, clip: str,
                          title: str, duration: str, effective: list[dict]) -> str:
    lines = [
        "# Prompts sent this run", "", f"**Source:** {url}", f"**Model:** {model}",
        f"**Resolution:** {resolution}", f"**Clip:** {clip}",
        f"**Title supplied:** {title}", f"**Duration supplied:** {duration}",
        f"**Calls selected:** {', '.join(pd['key'] for pd in effective)}", "",
    ]
    for pd in effective:
        lines += [f"## {pd['title']}", "", "```text", pd["prompt"], "```", ""]
    return "\n".join(lines)


def save_outputs(output_base: Path, title: str, duration: str, url: str, intent: str, model: str,
                 effective: list[dict], results: dict, errors: list,
                 resolution: str, clip: str, run_ts: str | None = None) -> Path:
    run_ts = run_ts or datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = output_base / f"{run_ts} - {sanitize_title(title)}"
    output_dir.mkdir(parents=True, exist_ok=True)
    phases = [pd["key"] for pd in effective]
    report_path = output_dir / "report.md"
    report_path.write_text(
        compile_report(title, duration, url, intent, model, phases, results, errors),
        encoding="utf-8",
    )
    (output_dir / "prompts.md").write_text(
        build_run_prompts_doc(
            url, model, resolution, clip, title, duration, effective),
        encoding="utf-8",
    )
    (output_base / "latest.json").write_text(json.dumps({
        "latest_run": run_ts, "run_dir": str(output_dir), "url": url,
        "title": title, "duration": duration, "intent": intent,
        "completed": bool(results),
        "timestamp": datetime.now().isoformat(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return report_path


def run_extraction(url: str, intent: str, model: str, start: str | None,
                   end: str | None, low_res: bool, output_base: Path, title: str,
                   duration: str, deep_summary: bool, technical: bool, coding_video: bool) -> int:
    from google import genai
    phases = selected_phase_defs(deep_summary, technical, coding_video)
    effective = build_effective_prompts(phases, title, duration)
    client = genai.Client()
    print(f"Video-to-Action — {len(effective)} selected call(s), model {model}")
    def runner(pd):
        print(f"  Call: {pd['title']} ...")
        return run_phase(client, model, url, pd["prompt"], start, end, low_res)
    results, errors = execute_phases(effective, runner)
    resolution = "low" if low_res else "default"
    clip = f"{start or 'start'} -> {end or 'end'}" if start or end else "full video"
    report_path = save_outputs(
        output_base, title, duration, url, intent, model, effective,
                               results, errors, resolution, clip)
    print(f"Saved: {report_path}")
    return 0 if results else 1


def run_self_test() -> bool:
    fixture_root = Path.cwd() / "tmp"
    fixture_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=fixture_root) as temp:
        base = Path(temp)
        assert normalize_duration("4:05") == "04:05"
        assert normalize_duration("1:02:03") == "01:02:03"
        for invalid in ("4", "4:5", "04:60", "1:60:00", "abc"):
            try:
                normalize_duration(invalid)
                raise AssertionError(f"invalid duration accepted: {invalid}")
            except argparse.ArgumentTypeError:
                pass

        phase_counts = [
            len(selected_phase_defs(False, False, False)),
            len(selected_phase_defs(True, False, False)),
            len(selected_phase_defs(True, True, True)),
        ]
        assert phase_counts == [1, 2, 3]
        try:
            selected_phase_defs(False, True, False)
            raise AssertionError("technical relevance gate failed")
        except ValueError:
            pass

        duration = "14:34"
        procedure_result = (
            "## Overview\n### Overview child\n#### Overview detail\n"
            "```markdown\n## Overview\n## Steps\n```\n"
            "## Steps\n### STEP 1: Fixture\n#### Step detail"
        )
        acts = (
            "## 🎭 ACT I: Start\n### Act child\n#### Act detail\n"
            "```markdown\n## 🎭 ACT II: Code sample\n```\n"
            "## 🎭 FINAL ACT: Key Takeaways"
        )

        omitted_effective = build_effective_prompts(
            selected_phase_defs(False, False, False), "Omitted Fixture", duration)
        omitted_path = save_outputs(
            base, "Omitted Fixture", duration, "https://youtu.be/fixture",
            "summarize", DEFAULT_MODEL, omitted_effective,
            {"procedure": procedure_result}, [], "default", "full video",
            run_ts="20000101-000001")
        omitted_text = omitted_path.read_text(encoding="utf-8")
        assert "Not selected for this run." in omitted_text

        failed_effective = build_effective_prompts(
            selected_phase_defs(True, True, True), "Failed Fixture", duration)

        def failed_runner(pd):
            if pd["key"] == "deep_summary":
                raise RuntimeError("fixture failure")
            return procedure_result if pd["key"] == "procedure" else "fixture technical"

        failed_results, failed_errors = execute_phases(failed_effective, failed_runner)
        failed_path = save_outputs(
            base, "Failed Fixture", duration, "https://youtu.be/fixture",
            "summarize", DEFAULT_MODEL, failed_effective, failed_results,
            failed_errors, "default", "full video", run_ts="20000101-000002")
        failed_text = failed_path.read_text(encoding="utf-8")
        assert "Deep Summary extraction failed; see Extraction Errors." in failed_text
        assert "Not selected for this run." not in failed_text

        success_effective = build_effective_prompts(
            selected_phase_defs(True, False, False), "Success Fixture", duration)
        success_path = save_outputs(
            base, "Success Fixture", duration, "https://youtu.be/fixture",
            "summarize", DEFAULT_MODEL, success_effective,
            {"procedure": procedure_result, "deep_summary": acts}, [],
            "default", "full video", run_ts="20000101-000003")
        success_text = success_path.read_text(encoding="utf-8")
        success_prompts = success_path.with_name("prompts.md").read_text(encoding="utf-8")

        assert "## Procedure" in success_text and "## Detailed Summary" in success_text
        assert "\n### Overview\n" in success_text and "\n### Steps\n" in success_text
        assert "\n### 🎭 ACT I: Start\n" in success_text
        assert "\n### 🎭 FINAL ACT: Key Takeaways\n" in success_text
        assert "### Overview child" in success_text and "#### Overview detail" in success_text
        assert "### STEP 1: Fixture" in success_text and "#### Step detail" in success_text
        assert "### Act child" in success_text and "#### Act detail" in success_text
        assert "```markdown\n## Overview\n## Steps\n```" in success_text
        assert "```markdown\n## 🎭 ACT II: Code sample\n```" in success_text
        assert f"- **Duration:** {duration}" in success_text
        duration_rule = (
            f"This video's exact total length is {duration}; use it verbatim as the "
            f"Length, and ensure every timestamp falls within 00:00–{duration}."
        )
        assert duration_rule in success_effective[0]["prompt"]
        assert duration_rule in success_effective[1]["prompt"]
        assert f"**Duration supplied:** {duration}" in success_prompts
        assert success_effective[0]["prompt"] in success_prompts
        assert success_effective[1]["prompt"] in success_prompts

        for report_path in (omitted_path, failed_path, success_path):
            assert report_path.name == "report.md"
            report_text = report_path.read_text(encoding="utf-8")
            assert "## Procedure" in report_text
            assert "## Detailed Summary" in report_text

    print("Self-test passed: duration, prompts, nesting, fences, and report states.")
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a deterministic video report")
    parser.add_argument("url", nargs="?")
    parser.add_argument("--intent", default="summarize", choices=["follow", "summarize", "learn"])
    parser.add_argument("--model", default=os.environ.get("VIDEO_TO_ACTION_MODEL", DEFAULT_MODEL))
    parser.add_argument("--start", type=parse_offset)
    parser.add_argument("--end", type=parse_offset)
    parser.add_argument("--resolution", default="default", choices=["default", "low"])
    parser.add_argument("--output-dir", default=os.environ.get(
        "VIDEO_TO_ACTION_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
    parser.add_argument("--title")
    parser.add_argument("--duration", type=normalize_duration)
    parser.add_argument("--deep-summary", action="store_true")
    parser.add_argument("--technical", action="store_true")
    parser.add_argument("--coding-video", action="store_true")
    parser.add_argument("--check-setup", action="store_true")
    parser.add_argument("--dump-prompts", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.dump_prompts:
        print(f"Wrote {dump_prompts()}")
        return
    if args.self_test:
        sys.exit(0 if run_self_test() else 1)
    if args.check_setup:
        sys.exit(0 if check_setup() else 1)
    if not args.url or not is_youtube_url(args.url):
        parser.error("a valid public YouTube URL is required")
    if not args.title or not args.title.strip():
        parser.error('an exact title is required: pass --title "..."')
    if not args.duration:
        parser.error("--duration is required (MM:SS or HH:MM:SS)")
    if args.technical and not args.coding_video:
        parser.error("--technical requires --coding-video")
    if not check_setup(verbose=False):
        check_setup(verbose=True)
        sys.exit(1)
    sys.exit(run_extraction(
        args.url, args.intent, args.model, args.start, args.end,
        args.resolution == "low", Path(args.output_dir), args.title.strip(),
        args.duration, args.deep_summary, args.technical, args.coding_video,
    ))


if __name__ == "__main__":
    main()
