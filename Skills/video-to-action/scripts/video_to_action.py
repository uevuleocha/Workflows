#!/usr/bin/env python3
"""Deterministic YouTube report and transcript extraction.

The script is the sole writer of each run's report.md, transcript.md, and
prompts.md. It never invokes report-this or session-summary; it only conforms
structurally to the local report package. Real runs require
orchestrator-supplied phase choices.
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from importlib.metadata import version, PackageNotFoundError
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from subject_outputs import subject_path, publish_pointers, repair_pointers, atomic_json

DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_FALLBACK_MODEL = "gemini-3.6-flash"
DEFAULT_TIER = "free"
FREE_TIER_MODELS = frozenset({
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
})
# Google deprecated these IDs on 2026-10-08 and serves them with the routed model.
MODEL_ALIASES = {
    "gemini-3.7-flash": "gemini-3.8-flash",
    "gemini-3.5-flash": "gemini-3.6-flash",
}
PROCESSING_MODES = ("static", "agentic")
DEFAULT_PROCESSING = "static"
AGENTIC_STATUS_FILE = "agentic-status.json"
PROBE_HISTORY_LIMIT = 20
PROBE_RECOVERY_THRESHOLD = 3
PROBE_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
PROBE_PROMPT = ("The exact video title is \"Me at the zoo\" and its length is 00:19. "
                "Describe what happens in this video in two sentences.")
PRIMARY_ATTEMPTS = 3
PRIMARY_BACKOFF_SECONDS = (1.0, 3.0)
MIN_GENAI_VERSION = (2, 29, 0)
CUSTOM_HEADING = "## Your Specific Request"
DEFAULT_OUTPUT_DIR = Path("Archive") / "Historical" / "Video-to-action"
MANUAL_TRANSCRIPT_URL = "https://youtubetotranscript.com/"
MANUAL_RECOVERY_START = "<!-- MANUAL_RECOVERY_START -->"
MANUAL_RECOVERY_END = "<!-- MANUAL_RECOVERY_END -->"
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


def env_file_candidates() -> tuple[Path, Path]:
    """Return the two .env paths in their established lookup order."""
    return Path.cwd() / ".env", Path(__file__).resolve().parent / ".env"


def load_env_files() -> dict:
    """Load discovered .env files and return secret-free discovery details."""
    from dotenv import load_dotenv
    searched = env_file_candidates()
    found = []
    loaded = []
    for candidate in searched:
        if candidate.is_file():
            found.append(candidate)
            if load_dotenv(candidate):
                loaded.append(candidate)
    return {"searched": searched, "found": tuple(found), "loaded": tuple(loaded)}


def describe_env_search(discovery: dict) -> list[str]:
    """Render secret-free .env discovery lines for setup diagnostics."""
    found = set(discovery["found"])
    lines = [
        f"ENV SEARCH {index}: {candidate} (found: {'yes' if candidate in found else 'no'})"
        for index, candidate in enumerate(discovery["searched"], start=1)
    ]
    if discovery["loaded"]:
        lines.append(
            "ENV LOADED: " + ", ".join(str(path) for path in discovery["loaded"])
        )
    else:
        lines.append("ENV LOADED: none")
    return lines


def api_key_name(tier: str) -> str:
    return "GEMINI_API_KEY_PAID" if tier == "paid" else "GEMINI_API_KEY"


def resolve_model_policy(tier: str, requested_primary: str,
                         requested_fallback: str) -> dict:
    """Resolve deterministic free/paid model policy without making an API call."""
    if tier not in ("free", "paid"):
        raise ValueError("tier must be free or paid")
    primary = requested_primary
    fallback = requested_fallback
    overrides = []
    for role, current in (("Primary", primary), ("Fallback", fallback)):
        if current in MODEL_ALIASES:
            overrides.append(
                f"{role} `{current}` is deprecated and served by "
                f"`{MODEL_ALIASES[current]}`; using `{MODEL_ALIASES[current]}`."
            )
    primary = MODEL_ALIASES.get(primary, primary)
    fallback = MODEL_ALIASES.get(fallback, fallback)
    if tier == "free":
        if primary not in FREE_TIER_MODELS:
            overrides.append(
                f"Primary `{primary}` is not approved for free mode; "
                f"using `{DEFAULT_MODEL}`."
            )
            primary = DEFAULT_MODEL
        if fallback not in FREE_TIER_MODELS:
            overrides.append(
                f"Fallback `{fallback}` is not approved for free mode; "
                f"using `{DEFAULT_FALLBACK_MODEL}`."
            )
            fallback = DEFAULT_FALLBACK_MODEL
    if fallback == primary:
        replacement = (
            DEFAULT_FALLBACK_MODEL
            if primary != DEFAULT_FALLBACK_MODEL else DEFAULT_MODEL
        )
        if tier == "paid" or replacement in FREE_TIER_MODELS:
            overrides.append(
                f"Fallback matched primary; using distinct `{replacement}`."
            )
            fallback = replacement
    return {
        "tier": tier,
        "requested_primary": requested_primary,
        "requested_fallback": requested_fallback,
        "primary": primary,
        "fallback": fallback,
        "overrides": overrides,
    }


def check_setup(tier: str = DEFAULT_TIER, verbose: bool = True) -> bool:
    ok = True
    dotenv_available = True
    try:
        from google import genai  # noqa: F401
        installed = tuple(int(n) for n in version("google-genai").split(".")[:3])
        if installed < MIN_GENAI_VERSION:
            raise ImportError("agentic Interactions API requires google-genai>=2.29.0")
    except (ImportError, PackageNotFoundError, ValueError):
        ok = False
        if verbose:
            print('MISSING/OUTDATED: google-genai>=2.29.0 '
                  '(install with: python -m pip install "google-genai>=2.29.0").')
    try:
        import dotenv  # noqa: F401
    except ImportError:
        dotenv_available = False
        ok = False
        if verbose:
            print("MISSING: python-dotenv "
                  "(install with: python -m pip install python-dotenv).")
    try:
        import youtube_transcript_api  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print(
                "MISSING: youtube-transcript-api "
                "(install with: python -m pip install youtube-transcript-api)."
            )
    discovery = {
        "searched": env_file_candidates(),
        "found": tuple(path for path in env_file_candidates() if path.is_file()),
        "loaded": (),
    }
    if dotenv_available:
        discovery = load_env_files()
    if verbose:
        for line in describe_env_search(discovery):
            print(line)
    if dotenv_available:
        key_name = api_key_name(tier)
        if os.environ.get(key_name):
            if verbose:
                print(f"OK: {key_name} is set (value not displayed).")
        else:
            ok = False
            if verbose:
                print(
                    f"MISSING: {key_name} is not set after searching both .env paths."
                )
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
        "Free tier is the non-blocking default. The primary model is",
        f"`{DEFAULT_MODEL}` and the one-attempt fallback after three recognized",
        f"transient primary failures is `{DEFAULT_FALLBACK_MODEL}`.", "",
        "The Procedure call always runs. Deep Summary is default-on. Technical is",
        "opt-in and requires an explicit coding/software relevance confirmation.",
        "Choices already present in the request are reused without reconfirmation.",
        "Per-run prompts.md stores each exact selected prompt once and associates",
        "all sanitized model-attempt provenance with that prompt.", "",
        "Every selected phase uses static video processing by default.",
        "--processing agentic opts into agentic processing; a failed agentic phase",
        "recovers through static processing with the same prompt. An explicit optional",
        "--custom-request supplements the Procedure prompt in the same call and",
        "requires a Your Specific Request answer section. Empty requests add nothing.", "",
    ]
    for key in ("procedure", "deep_summary", "technical"):
        pd = PHASE_DEFS[key]
        qualifier = {
            "procedure": "always",
            "deep_summary": "default-on; --no-deep-summary opts out",
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
            elif block == "procedure" and (
                    re.match(r"^### \d+(?:\.\)|\)) ", line) or
                    line.startswith("### STEP ")):
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


def parse_youtube_video_id(url: str) -> str:
    """Return a validated video ID from supported public YouTube URL forms."""
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]

    video_id = ""
    parts = [part for part in parsed.path.split("/") if part]
    if host == "youtu.be" and parts:
        video_id = parts[0]
    elif host in ("youtube.com", "music.youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif len(parts) >= 2 and parts[0] in ("shorts", "embed"):
            video_id = parts[1]

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(
            "a supported public YouTube URL with a valid video ID is required"
        )
    return video_id


def is_youtube_url(url: str) -> bool:
    try:
        parse_youtube_video_id(url)
        return True
    except ValueError:
        return False


def select_transcript_track(transcripts) -> object:
    """Prefer original manual tracks, then original generated tracks."""
    tracks = list(transcripts)
    if not tracks:
        raise LookupError("no caption tracks are available")

    def is_english(track) -> bool:
        return str(getattr(track, "language_code", "")).lower().startswith("en")

    groups = (
        [track for track in tracks if not track.is_generated and is_english(track)],
        [track for track in tracks if not track.is_generated and not is_english(track)],
        [track for track in tracks if track.is_generated and is_english(track)],
        [track for track in tracks if track.is_generated and not is_english(track)],
    )
    return next(group[0] for group in groups if group)


def resolve_ytdlp_executable() -> Path | None:
    """Resolve optional yt-dlp from PATH or its bounded WinGet package roots."""
    resolved = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if resolved:
        return Path(resolved)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None
    packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
    if not packages.is_dir():
        return None
    candidates = sorted(
        packages.glob("yt-dlp.yt-dlp_Microsoft.Winget.Source_*\\yt-dlp.exe")
    )
    return candidates[-1] if candidates else None


def parse_vtt_timestamp(value: str) -> float:
    """Convert a WebVTT timestamp into seconds."""
    parts = value.strip().replace(",", ".").split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"invalid WebVTT timestamp: {value}")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _normalized_vtt_token(token: str) -> str:
    return re.sub(r"[^\w]+", "", token, flags=re.UNICODE).casefold()


def parse_vtt_captions(vtt_text: str) -> list[dict]:
    """Strip WebVTT markup and collapse rolling-window caption duplication."""
    lines = vtt_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cues = []
    index = 0
    while index < len(lines):
        line = lines[index].strip().lstrip("\ufeff")
        if "-->" not in line:
            index += 1
            continue
        start_text, remainder = line.split("-->", 1)
        end_text = remainder.strip().split()[0]
        start = parse_vtt_timestamp(start_text)
        end = parse_vtt_timestamp(end_text)
        index += 1
        payload = []
        while index < len(lines) and lines[index].strip():
            cleaned = html.unescape(re.sub(r"<[^>]+>", "", lines[index])).strip()
            if cleaned and cleaned not in payload:
                payload.append(cleaned)
            index += 1
        text = re.sub(r"\s+", " ", " ".join(payload)).strip()
        if text:
            cues.append((start, max(0.0, end - start), text))

    accumulated = []
    snippets = []
    for start, duration, text in cues:
        original = text.split()
        normalized = [_normalized_vtt_token(token) for token in original]
        pairs = [(raw, norm) for raw, norm in zip(original, normalized) if norm]
        if not pairs:
            continue
        original = [raw for raw, _ in pairs]
        normalized = [norm for _, norm in pairs]
        overlap = 0
        maximum = min(len(accumulated), len(normalized))
        for size in range(maximum, 0, -1):
            if accumulated[-size:] == normalized[:size]:
                overlap = size
                break
        novel_original = original[overlap:]
        novel_normalized = normalized[overlap:]
        if not novel_original:
            continue
        snippets.append({
            "text": " ".join(novel_original),
            "start": start,
            "duration": duration,
        })
        accumulated.extend(novel_normalized)
    return snippets


def fetch_transcript_with_ytdlp(url: str, video_id: str, executable=None,
                                runner=None) -> dict:
    """Use optional yt-dlp, preferring manual English captions before auto."""
    executable = Path(executable) if executable else resolve_ytdlp_executable()
    if executable is None:
        return {
            "status": "failed", "video_id": video_id,
            "reason": "yt-dlp executable was not found on PATH or in WinGet packages",
            "snippets": [],
        }
    runner = runner or subprocess.run
    fixture_root = Path.cwd() / "tmp"
    fixture_root.mkdir(parents=True, exist_ok=True)
    failures = []
    with tempfile.TemporaryDirectory(
            prefix="video-to-action-ytdlp-", dir=fixture_root) as temp:
        output_dir = Path(temp)
        for caption_kind, flag in (("manual", "--write-sub"),
                                   ("auto-generated", "--write-auto-sub")):
            command = [
                str(executable), flag, "--skip-download", "--sub-lang", "en",
                "--sub-format", "vtt", "--paths", str(output_dir),
                "-o", "%(id)s.%(ext)s", url,
            ]
            completed = runner(
                command, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=120, check=False,
            )
            vtt_files = sorted(output_dir.glob("*.vtt"))
            if completed.returncode == 0 and vtt_files:
                snippets = parse_vtt_captions(
                    vtt_files[0].read_text(encoding="utf-8")
                )
                if snippets:
                    return {
                        "status": "complete", "video_id": video_id,
                        "language": "English", "language_code": "en",
                        "is_generated": caption_kind == "auto-generated",
                        "caption_kind": caption_kind,
                        "retrieval_path": "yt-dlp",
                        "snippets": snippets,
                    }
                failures.append(f"{caption_kind} VTT contained no usable captions")
            else:
                detail = re.sub(
                    r"\s+", " ", (completed.stderr or completed.stdout or "").strip()
                )[:300]
                failures.append(
                    f"{caption_kind} captions unavailable"
                    + (f": {detail}" if detail else "")
                )
            for vtt_file in vtt_files:
                vtt_file.unlink()
    return {
        "status": "failed", "video_id": video_id,
        "reason": "; ".join(failures) or "yt-dlp produced no captions",
        "snippets": [],
    }


def fetch_transcript(url: str, api_factory=None, ytdlp_fetcher=None) -> dict:
    """Fetch captions through the primary API, then optional yt-dlp fallback."""
    video_id = parse_youtube_video_id(url)
    try:
        if api_factory is None:
            from youtube_transcript_api import YouTubeTranscriptApi
            api_factory = YouTubeTranscriptApi
        api = api_factory()
        track = select_transcript_track(api.list(video_id))
        fetched = track.fetch()
        snippets = [
            {
                "text": snippet.text,
                "start": float(snippet.start),
                "duration": float(snippet.duration),
            }
            for snippet in fetched
        ]
        if not snippets:
            raise LookupError("the selected caption track is empty")
        return {
            "status": "complete",
            "video_id": video_id,
            "language": track.language,
            "language_code": track.language_code,
            "is_generated": bool(track.is_generated),
            "caption_kind": (
                "auto-generated" if bool(track.is_generated) else "manual"
            ),
            "retrieval_path": "youtube-transcript-api",
            "snippets": snippets,
        }
    except Exception as exc:  # noqa: BLE001 - every caption failure is isolated
        unavailable = {
            "NoTranscriptFound", "TranscriptsDisabled", "VideoUnavailable",
            "NoTranscriptAvailable", "LookupError",
        }
        status = "unavailable" if type(exc).__name__ in unavailable else "failed"
        primary_reason = f"{type(exc).__name__}: {exc}"
        ytdlp_fetcher = ytdlp_fetcher or fetch_transcript_with_ytdlp
        try:
            fallback = ytdlp_fetcher(url, video_id)
        except Exception as fallback_exc:  # noqa: BLE001 - fallback is non-fatal
            fallback = {
                "status": "failed", "video_id": video_id,
                "reason": f"{type(fallback_exc).__name__}: {fallback_exc}",
                "snippets": [],
            }
        if fallback["status"] == "complete":
            fallback["primary_failure_reason"] = primary_reason
            return fallback
        return {
            "status": status,
            "video_id": video_id,
            "reason": (
                f"youtube-transcript-api: {primary_reason}; "
                f"yt-dlp fallback: {fallback.get('reason', 'no result')}"
            ),
            "primary_failure_reason": primary_reason,
            "fallback_failure_reason": fallback.get("reason", "no result"),
            "snippets": [],
        }


def format_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def build_transcript_doc(title: str, url: str, result: dict) -> str:
    """Render an automatic transcript or an honest manual-recovery artifact."""
    status = result["status"]
    lines = [
        f"# {title} — Video Transcript", "", "## Transcript Metadata", "",
        f"- **Source:** {url}",
        f"- **Video ID:** {result['video_id']}",
    ]
    if status == "complete":
        track_type = (
            "Automatically generated" if result["is_generated"] else "Manual"
        )
        lines += [
            "- **Status:** Complete via automatic retrieval",
            "- **Automatic retrieval:** Complete",
            f"- **Retrieval path:** {result['retrieval_path']}",
            f"- **Language:** {result['language']} ({result['language_code']})",
            f"- **Caption track:** {track_type}",
            "- **Manual source:** Not used", "",
            "## Accuracy Note", "",
            "This is the available YouTube caption track, not a human-verified",
            "transcription of the audio. Automatic captions may contain recognition",
            "errors, missing punctuation, absent speaker labels, and awkward breaks.",
            "", "## Transcript", "",
        ]
        if result.get("primary_failure_reason"):
            lines.insert(
                10,
                f"- **Primary retrieval failure:** {result['primary_failure_reason']}",
            )
        for snippet in result["snippets"]:
            end = snippet["start"] + snippet["duration"]
            lines.append(
                f"[{format_timestamp(snippet['start'])}–{format_timestamp(end)}] "
                f"{snippet['text']}"
            )
    else:
        automatic_label = "Unavailable" if status == "unavailable" else "Failed"
        lines += [
            "- **Status:** Manual recovery required",
            f"- **Automatic retrieval:** {automatic_label}",
            f"- **Automatic failure reason:** {result['reason']}",
            "- **Manual source:** Not yet supplied", "",
            MANUAL_RECOVERY_START,
            "## Manual Recovery", "",
            "Automatic caption retrieval did not complete. To recover manually:", "",
            f"1. Open {MANUAL_TRANSCRIPT_URL}",
            "2. Paste the original YouTube URL and generate the transcript.",
            "3. Copy the transcript itself; do not provide only the generated page URL.",
            "4. Give the copied transcript to the agent for this run.",
            "5. The helper will replace these instructions while preserving the",
            "   automatic-failure provenance above.", "",
            "Manual transcript pending.",
            MANUAL_RECOVERY_END,
        ]
    return "\n".join(lines) + "\n"


def complete_manual_transcript(transcript_path: Path, manual_path: Path) -> Path:
    """Complete a failed transcript artifact without rerunning Gemini."""
    existing = transcript_path.read_text(encoding="utf-8")
    manual_text = manual_path.read_text(encoding="utf-8").strip()
    if not manual_text:
        raise ValueError("manual transcript file is empty")
    pattern = re.compile(
        rf"{re.escape(MANUAL_RECOVERY_START)}.*?{re.escape(MANUAL_RECOVERY_END)}",
        re.DOTALL,
    )
    if not pattern.search(existing):
        raise ValueError(
            "transcript does not contain a pending manual-recovery block"
        )
    completed = existing.replace(
        "- **Status:** Manual recovery required",
        "- **Status:** Complete via manual fallback",
        1,
    ).replace(
        "- **Manual source:** Not yet supplied",
        f"- **Manual source:** User-supplied copy from {MANUAL_TRANSCRIPT_URL}",
        1,
    )
    completed = pattern.sub(
        "## Accuracy Note\n\n"
        "This transcript was supplied by the user from a third-party caption "
        "tool and is preserved as supplied. The automatic retrieval result "
        "remains recorded above.\n\n## Transcript\n\n" + manual_text,
        completed,
        count=1,
    )
    transcript_path.write_text(completed.rstrip() + "\n", encoding="utf-8")
    return transcript_path


def transcript_result_messages(result: dict, transcript_path: Path) -> list[str]:
    """Return explicit terminal/chat handoff lines for transcript status."""
    if result["status"] == "complete":
        return [
            "Transcript: complete via "
            f"{result['retrieval_path']} ({result['caption_kind']} captions)."
        ]
    command = (
        f'python "{Path(__file__).resolve()}" --complete-transcript '
        f'"{transcript_path}" --manual-transcript-file '
        '"<copied-transcript.txt>"'
    )
    return [
        f"TRANSCRIPT FAILURE: {result['reason']}",
        f"Retroactive completion command: {command}",
    ]


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
                            duration: str, custom_request: str = "") -> list[dict]:
    effective = []
    for pd in phase_defs:
        prompt = pd["prompt"]
        if pd["key"] in ("procedure", "deep_summary"):
            prompt = inject_ground_truth(
                prompt, title, duration, include_title=pd["key"] == "procedure")
        request = custom_request if custom_request.strip() else ""
        if pd["key"] == "procedure" and request:
            prompt += (
                "\n\nAdditional user request (supplements all normal work above):\n"
                + request
                + "\n\nAfter the normal report content, answer the additional request "
                "under the exact heading '## Your Specific Request'. If the video "
                "does not provide enough evidence, say so explicitly. Do not omit "
                "normal report content or invent inaccessible details."
            )
        effective.append({**pd, "prompt": prompt,
                          "custom_request": request if pd["key"] == "procedure" else ""})
    return effective


class PhaseText(str):
    """Final text with a small allowlisted processing-evidence payload."""

    def __new__(cls, text, evidence):
        instance = super().__new__(cls, text)
        instance.evidence = evidence
        return instance


def field(value, name, default=None):
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


class InteractionError(RuntimeError):
    """A submitted interaction failure with bounded, secret-safe diagnostics."""

    def __init__(self, message, evidence, retryable_capacity=False):
        super().__init__(message)
        self.evidence = evidence
        self.retryable_capacity = retryable_capacity


AgenticInteractionError = InteractionError  # historical name kept for callers and tests

QUOTA_CODES = frozenset({"429", "RESOURCE_EXHAUSTED"})


def interaction_diagnostics(response, interaction_id, counts, processing="agentic"):
    """Retain only identity, state and provider errors, never the raw response."""
    return {
        "processing": processing, **counts,
        "interaction_id": sanitize_detail(interaction_id or "unavailable"),
        "interaction_status": sanitize_detail(field(response, "status") or "unknown"),
        "errors": [
            {key: sanitize_detail(field(error, key) or "") for key in ("code", "message")}
            for error in (field(response, "errors", []) or [])[:10]
        ],
    }


def validate_agentic_options(start, end):
    if start is not None or end is not None:
        raise ValueError("Interactions video processing does not support hard --start/--end "
                         "clipping. Omit these flags; a --custom-request may focus on "
                         "timestamps but does not restrict the video input.")


def run_phase(client, model: str, url: str, prompt: str,
              start: str | None, end: str | None, low_res: bool,
              *, processing=DEFAULT_PROCESSING, sleeper=time.sleep, max_polls=120) -> str:
    validate_agentic_options(start, end)
    if processing not in PROCESSING_MODES:
        raise ValueError(f"processing must be one of {PROCESSING_MODES}")
    video = {"type": "video", "uri": url, "processing": processing}
    if low_res:
        video["resolution"] = "low"
    response = client.interactions.create(
        model=model, input=[video, {"type": "text", "text": prompt}],
        background=True, timeout=30,
    )
    interaction_id = field(response, "id")
    counts = {"processing_call": 0, "processing_result": 0}
    poll_failures = []
    retry_delays = (2, 5, 10)
    next_delay = 5

    def diagnostics():
        return {**interaction_diagnostics(response, interaction_id, counts, processing),
                "poll_failures": poll_failures}

    def capture(item):
        steps = field(item, "steps", []) or []
        for name in counts:
            counts[name] = max(counts[name], sum(field(s, "type") == name for s in steps))

    capture(response)
    try:
        for _ in range(max_polls):
            if field(response, "status") != "in_progress":
                break
            if not interaction_id:
                raise RuntimeError("in-progress interaction missing its ID")
            sleeper(next_delay)
            try:
                response = client.interactions.get(interaction_id, timeout=30)
            except Exception as exc:
                retry = (is_transient_poll_error(exc)
                         and len(poll_failures) < len(retry_delays)
                         and _ + 1 < max_polls)
                delay = retry_delays[len(poll_failures)] if retry else None
                poll_failures.append({"error": sanitize_error(exc),
                                      "retry_delay_seconds": delay})
                if not retry:
                    raise
                next_delay = delay
                continue
            next_delay = 5
            capture(response)
        if field(response, "status") == "in_progress":
            raise TimeoutError(f"{processing} inspection exceeded bounded polling budget")
    except Exception as exc:
        # A submitted job might still be running. Never retry creation for poll errors.
        cancelled = False
        if interaction_id:
            try:
                client.interactions.cancel(interaction_id, timeout=30)
                cancelled = True
            except Exception:
                pass
        evidence = diagnostics()
        evidence["poll_error"] = sanitize_error(exc)
        evidence["cancellation"] = "requested" if cancelled else "unconfirmed"
        raise AgenticInteractionError(
            f"{processing.capitalize()} polling stopped ({type(exc).__name__}); "
            f"cancellation {'requested' if cancelled else 'unconfirmed'}; "
            "no automatic resubmission.", evidence
        ) from None
    status = field(response, "status")
    evidence = diagnostics()
    if status != "completed":
        codes = [error["code"].rstrip("/").rsplit("/", 1)[-1].upper()
                 for error in evidence["errors"]]
        retryable = status == "failed" and bool(codes) and all(
            code in ("503", "UNAVAILABLE") for code in codes)
        quota_hint = (
            " Provider reported a quota or rate limit (RESOURCE_EXHAUSTED); free-tier "
            "daily request limits are per model, so retry after the daily reset or use "
            "another model." if codes and all(code in QUOTA_CODES for code in codes) else "")
        raise AgenticInteractionError(
            f"{processing.capitalize()} interaction ended with status {status!r}; "
            f"no final result.{quota_hint}", evidence, retryable)
    text = field(response, "output_text", "") or ""
    if not text.strip():
        raise AgenticInteractionError(f"empty {processing} response", evidence)
    if processing == "agentic" and not all(counts.values()):
        raise AgenticInteractionError("Agentic processing requested but processing evidence is missing.", evidence)
    usage = field(response, "usage")
    for name in ("total_input_tokens", "total_output_tokens", "total_thought_tokens",
                 "total_tool_use_tokens", "total_tokens"):
        value = field(usage, name)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            evidence[name] = value
    return PhaseText(text, evidence)


def structured_error_code(exc: Exception) -> int | None:
    """Return a structured HTTP-style status code when the SDK exposes one."""
    for attribute in ("status_code", "code"):
        value = getattr(exc, attribute, None)
        if callable(value):
            continue
        value = getattr(value, "value", value)
        if isinstance(value, int):
            return value
        match = re.fullmatch(r"\s*(\d{3})\s*", str(value or ""))
        if match:
            return int(match.group(1))
    return None


def is_transient_poll_error(exc: Exception) -> bool:
    """Retry read-only status requests, never authentication or invalid input."""
    code = structured_error_code(exc)
    if code is not None:
        return code in (408, 500, 502, 503, 504)
    import httpx
    return isinstance(exc, (TimeoutError, ConnectionError, httpx.TransportError)) or is_transient_capacity_error(exc)


def sanitize_error(exc: Exception) -> str:
    """Bound error provenance and redact credential-shaped or configured values."""
    return sanitize_detail(f"{type(exc).__name__}: {exc}")


def sanitize_detail(value) -> str:
    """Sanitize each allowlisted diagnostic before persistence."""
    message = str(value)
    for key_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_PAID"):
        value = os.environ.get(key_name)
        if value:
            message = message.replace(value, "[REDACTED]")
    message = re.sub(r"AIza[A-Za-z0-9_-]{20,}", "[REDACTED]", message)
    message = re.sub(r"(?i)(Bearer\s+)[^\s,;]+", r"\1[REDACTED]", message)
    message = re.sub(
        r"([?&](?:key|api_key)=)[^&\s]+", r"\1[REDACTED]", message,
        flags=re.IGNORECASE,
    )
    return message.replace("\r", " ").replace("\n", " ")[:500]


def is_transient_capacity_error(exc: Exception) -> bool:
    """Retry only recognized temporary capacity failures; never generic 429s."""
    if isinstance(exc, AgenticInteractionError):
        return exc.retryable_capacity
    code = structured_error_code(exc)
    status = str(getattr(exc, "status", "") or "").upper()
    if code == 503 or status == "UNAVAILABLE":
        return True
    if code is not None:
        return False
    message = str(exc)
    return bool(
        re.search(r"\b503\b", message)
        and re.search(
            r"UNAVAILABLE|high demand|overload|temporar(?:y|ily)",
            message,
            flags=re.IGNORECASE,
        )
    )


def execute_phase_with_recovery(pd: dict, runner, policy: dict,
                                sleeper=time.sleep) -> tuple[str | None, list]:
    """Run one phase with three primary attempts and one bounded fallback."""
    attempts = []
    primary_exhausted_transiently = False
    for attempt_number in range(1, PRIMARY_ATTEMPTS + 1):
        try:
            text = runner(pd, policy["primary"])
            if not text.strip():
                raise RuntimeError("empty response")
            validate_custom_answer(pd, text)
            attempts.append({
                "phase": pd["key"], "role": "primary",
                "attempt": attempt_number, "attempt_limit": PRIMARY_ATTEMPTS,
                "model": policy["primary"], "status": "success",
                "evidence": getattr(text, "evidence", {}),
            })
            return text, attempts
        except Exception as exc:  # noqa: BLE001
            transient = is_transient_capacity_error(exc)
            attempts.append({
                "phase": pd["key"], "role": "primary",
                "attempt": attempt_number, "attempt_limit": PRIMARY_ATTEMPTS,
                "model": policy["primary"], "status": "failed",
                "transient": transient, "error": sanitize_error(exc),
                "evidence": getattr(exc, "evidence", {}),
            })
            if not transient:
                return None, attempts
            if attempt_number < PRIMARY_ATTEMPTS:
                sleeper(PRIMARY_BACKOFF_SECONDS[attempt_number - 1])
            else:
                primary_exhausted_transiently = True

    if primary_exhausted_transiently:
        try:
            text = runner(pd, policy["fallback"])
            if not text.strip():
                raise RuntimeError("empty response")
            validate_custom_answer(pd, text)
            attempts.append({
                "phase": pd["key"], "role": "fallback",
                "attempt": 1, "attempt_limit": 1,
                "model": policy["fallback"], "status": "success",
                "evidence": getattr(text, "evidence", {}),
            })
            return text, attempts
        except Exception as exc:  # noqa: BLE001
            attempts.append({
                "phase": pd["key"], "role": "fallback",
                "attempt": 1, "attempt_limit": 1,
                "model": policy["fallback"], "status": "failed",
                "transient": is_transient_capacity_error(exc),
                "error": sanitize_error(exc),
                "evidence": getattr(exc, "evidence", {}),
            })
    return None, attempts


def validate_custom_answer(pd, text):
    if pd.get("custom_request", "").strip():
        parts = re.split(r"(?m)^## Your Specific Request\s*$", text, maxsplit=1)
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            raise AgenticInteractionError("Missing normal report or nonempty Your Specific Request answer.",
                                          getattr(text, "evidence", {}))


def execute_phase_with_processing(pd: dict, runner, policy: dict, processing: str,
                                  sleeper=time.sleep) -> tuple[str | None, list]:
    """Run a phase in the selected mode; a failed agentic phase recovers through static."""
    def bind(mode):
        return lambda phase, model: runner(phase, model, mode)

    text, attempts = execute_phase_with_recovery(pd, bind(processing), policy, sleeper)
    for item in attempts:
        item["processing"] = processing
    if text is not None or processing == "static":
        return text, attempts
    static_text, static_attempts = execute_phase_with_recovery(
        pd, bind("static"), policy, sleeper)
    for item in static_attempts:
        item["processing"] = "static"
        item["recovery"] = "agentic-to-static"
    return static_text, attempts + static_attempts


def execute_phases(effective: list[dict], runner, policy: dict,
                   sleeper=time.sleep, processing: str | None = None
                   ) -> tuple[dict, list, list, dict]:
    """Run every phase. With processing set, runner takes (pd, model, processing)."""
    results, errors, attempts, successful_models = {}, [], [], {}
    for pd in effective:
        if processing is None:
            text, phase_attempts = execute_phase_with_recovery(
                pd, runner, policy, sleeper=sleeper
            )
        else:
            text, phase_attempts = execute_phase_with_processing(
                pd, runner, policy, processing, sleeper=sleeper
            )
        attempts.extend(phase_attempts)
        if text is not None:
            results[pd["key"]] = text
            successful_models[pd["key"]] = phase_attempts[-1]["model"]
        else:
            final_attempt = phase_attempts[-1]
            errors.append({
                "phase": pd["key"],
                "error": final_attempt.get("error", "phase failed"),
            })
    return results, errors, attempts, successful_models


def build_attempt_provenance(attempts: list[dict]) -> list[str]:
    lines = []
    for item in attempts:
        label = (
            f"{item['role']} {item['attempt']}/{item['attempt_limit']}"
        )
        if item.get("processing"):
            label = f"{item['processing']} {label}"
        if item.get("recovery"):
            label += f" ({item['recovery']} recovery)"
        if item["status"] == "success":
            outcome = "success"
        else:
            classification = (
                "transient capacity" if item.get("transient")
                else "non-retryable"
            )
            outcome = f"{classification} failure — {item['error']}"
        lines.append(
            f"- `{item['phase']}` — {label} — `{item['model']}` — {outcome}"
        )
        if item.get("evidence"):
            lines.append("  - Processing evidence: " + json.dumps(item["evidence"], sort_keys=True))
    return lines


def load_agentic_status(output_base: Path) -> dict | None:
    """Read the probe status file; a missing or unreadable file means never probed."""
    try:
        data = json.loads((output_base / AGENTIC_STATUS_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and data.get("last_checked") else None


PROBE_VERDICTS = {"working": "WORKING", "broken": "STILL BROKEN",
                  "inconclusive": "INCONCLUSIVE (quota or rate limit)"}


def describe_agentic_status(status: dict | None) -> str:
    if not status:
        return "never probed (run --agentic-probe)"
    verdict = PROBE_VERDICTS.get(status.get("last_result"), "STILL BROKEN")
    return (f"{verdict} at last probe {status['last_checked']} "
            f"({status.get('consecutive_successes', 0)} consecutive successes; "
            f"{PROBE_RECOVERY_THRESHOLD} needed before treating agentic as recovered)")


def record_probe_result(output_base: Path, result: str, model: str,
                        detail: str, checked: str | None = None) -> dict:
    """Atomically update agentic-status.json with a bounded history.

    An inconclusive (quota) probe says nothing about agentic health, so it keeps
    the consecutive-success count instead of resetting it.
    """
    if result not in PROBE_VERDICTS:
        raise ValueError(f"probe result must be one of {tuple(PROBE_VERDICTS)}")
    previous = load_agentic_status(output_base) or {}
    checked = checked or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"checked": checked, "result": result,
             "model": model, "detail": sanitize_detail(detail)}
    history = (previous.get("history") or []) + [entry]
    streak = previous.get("consecutive_successes", 0)
    streak = {"working": streak + 1, "broken": 0, "inconclusive": streak}[result]
    status = {
        "last_checked": checked, "last_result": result, "model": model,
        "last_detail": entry["detail"],
        "consecutive_successes": streak,
        "history": history[-PROBE_HISTORY_LIMIT:],
    }
    output_base.mkdir(parents=True, exist_ok=True)
    atomic_json(output_base / AGENTIC_STATUS_FILE, status)
    return status


def run_agentic_probe(output_base: Path, tier: str, requested_model: str,
                      requested_fallback_model: str, *, client=None) -> int:
    """One agentic call on a fixed short video; records the verdict, creates no run."""
    policy = resolve_model_policy(tier, requested_model, requested_fallback_model)
    model = policy["primary"]
    owns_client = client is None
    if owns_client:
        load_env_files()
        client = create_client(os.environ[api_key_name(tier)])
    print(f"Agentic probe — model {model}; one agentic call on {PROBE_URL}")
    try:
        text = run_phase(client, model, PROBE_URL, PROBE_PROMPT, None, None, False,
                         processing="agentic")
        result, detail = "working", " ".join(str(text).split())[:200]
    except Exception as exc:  # noqa: BLE001
        detail = sanitize_error(exc)
        evidence = getattr(exc, "evidence", {}) or {}
        codes = [str(error.get("code", "")).rstrip("/").rsplit("/", 1)[-1].upper()
                 for error in evidence.get("errors", [])]
        if structured_error_code(exc) is not None:
            codes.append(str(structured_error_code(exc)))
        codes = [code for code in codes if code]
        if codes:
            detail += " | provider codes: " + ", ".join(codes)
        result = "inconclusive" if codes and all(c in QUOTA_CODES for c in codes) else "broken"
    finally:
        if owns_client:
            client.close()
    status = record_probe_result(output_base, result, model, detail)
    print(f"AGENTIC PROBE: {PROBE_VERDICTS[result]} — {detail}")
    if result == "inconclusive":
        print("The free-tier quota was hit, so this says nothing about agentic health; "
              "wait a few minutes and probe again.")
    print(f"Agentic status: {describe_agentic_status(status)}")
    print(f"Status file: {output_base / AGENTIC_STATUS_FILE}")
    return {"working": 0, "broken": 1, "inconclusive": 2}[result]


def compile_report(title: str, duration: str, url: str, intent: str,
                   policy: dict, phases_run: list[str], results: dict,
                   errors: list, attempts: list[dict],
                   successful_models: dict, custom_request: str = "",
                   processing: str = DEFAULT_PROCESSING,
                   agentic_status: str = "never probed (run --agentic-probe)") -> str:
    status = "failed" if not results else ("partial" if errors else "complete")
    success_text = ", ".join(
        f"{phase}={model}" for phase, model in successful_models.items()
    ) or "none"
    lines = [
        f"# {title} — Video Extraction Report", "", "## Report Metadata", "",
        f"- **Source:** {url}",
        f"- **Duration:** {duration}",
        f"- **Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Intent:** {intent}",
        f"- **API tier policy:** {policy['tier']}",
        f"- **Processing:** {processing}",
        f"- **Primary model:** {policy['primary']}",
        f"- **Fallback model:** {policy['fallback']}",
        f"- **Successful models:** {success_text}",
        f"- **Calls selected:** {', '.join(phases_run)}",
        f"- **Agentic status:** {agentic_status}",
        f"- **Status:** {status}", "",
    ]
    if policy["overrides"]:
        lines += ["## Preflight Policy Overrides", ""]
        lines += [f"- {item}" for item in policy["overrides"]]
        lines.append("")
    lines += ["## Model Attempt Provenance", ""]
    lines += build_attempt_provenance(attempts)
    procedure = results.get("procedure", "Procedure extraction failed; see Extraction Errors.")
    custom_answer = ""
    if custom_request.strip():
        parts = re.split(r"(?m)^## Your Specific Request\s*$", procedure, maxsplit=1)
        procedure = parts[0]
        custom_answer = parts[1].strip() if len(parts) == 2 else "Unavailable; procedure extraction did not return the requested answer."
    lines += ["", "## Procedure", "",
        demote_embedded_headings(
            procedure,
            "procedure"), "",
    ]
    if "technical" in results:
        lines += ["### Code, Commands & Configuration", "", results["technical"], ""]
    if custom_request.strip():
        lines += [CUSTOM_HEADING, "", custom_answer, ""]
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
        "- Primary retries and fallback attempts reuse the exact phase prompt shown in prompts.md.",
        "- Verify code and LOW CONFIDENCE items against the referenced timestamps.",
        "- Acting on extracted steps requires separate user authorization.", "",
    ]
    return "\n".join(lines)


def build_run_prompts_doc(url: str, policy: dict, resolution: str, clip: str,
                          title: str, duration: str, effective: list[dict],
                          attempts: list[dict], successful_models: dict,
                          processing: str = DEFAULT_PROCESSING,
                          agentic_status: str = "never probed (run --agentic-probe)") -> str:
    success_text = ", ".join(
        f"{phase}={model}" for phase, model in successful_models.items()
    ) or "none"
    lines = [
        "# Prompts sent this run", "", f"**Source:** {url}",
        f"**API tier policy:** {policy['tier']}",
        f"**Processing:** {processing}",
        f"**Agentic status:** {agentic_status}",
        f"**Requested primary model:** {policy['requested_primary']}",
        f"**Primary model used:** {policy['primary']}",
        f"**Requested fallback model:** {policy['requested_fallback']}",
        f"**Fallback model used:** {policy['fallback']}",
        f"**Successful models:** {success_text}",
        f"**Resolution:** {resolution}", f"**Clip:** {clip}",
        f"**Title supplied:** {title}", f"**Duration supplied:** {duration}",
        f"**Calls selected:** {', '.join(pd['key'] for pd in effective)}", "",
        "## Model Attempt Provenance", "",
    ]
    lines += build_attempt_provenance(attempts)
    if policy["overrides"]:
        lines += ["", "## Preflight Policy Overrides", ""]
        lines += [f"- {item}" for item in policy["overrides"]]
    lines.append("")
    for pd in effective:
        lines += [f"## {pd['title']}", "", "```text", pd["prompt"], "```", ""]
    return "\n".join(lines)

def save_outputs(output_base: Path, title: str, duration: str, url: str,
                 intent: str, policy: dict, effective: list[dict],
                 results: dict, errors: list, attempts: list[dict],
                 successful_models: dict, transcript_result: dict,
                 resolution: str, clip: str, run_ts: str | None = None,
                 *, subject: str, processing: str = DEFAULT_PROCESSING) -> Path:
    subject_dir = subject_path(output_base, subject)
    run_ts = run_ts or datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output_dir = subject_dir / f"{run_ts} - {sanitize_title(title)}"
    output_dir.mkdir(parents=True, exist_ok=False)
    phases = [pd["key"] for pd in effective]
    agentic_status = describe_agentic_status(load_agentic_status(output_base))
    report_path = output_dir / "report.md"
    report_path.write_text(
        compile_report(
            title, duration, url, intent, policy, phases, results, errors,
            attempts, successful_models,
            next((pd.get("custom_request", "") for pd in effective if pd["key"] == "procedure"), ""),
            processing, agentic_status,
        ),
        encoding="utf-8",
    )
    (output_dir / "prompts.md").write_text(
        build_run_prompts_doc(
            url, policy, resolution, clip, title, duration, effective,
            attempts, successful_models, processing, agentic_status,
        ),
        encoding="utf-8",
    )
    (output_dir / "transcript.md").write_text(
        build_transcript_doc(title, url, transcript_result), encoding="utf-8"
    )
    metadata = {
        "latest_run": run_ts, "run_dir": str(output_dir), "url": url,
        "title": title, "duration": duration, "intent": intent,
        "tier": policy["tier"], "primary_model": policy["primary"],
        "fallback_model": policy["fallback"],
        "successful_models": successful_models,
        "completed": bool(results),
        "timestamp": datetime.now().isoformat(),
    }
    try:
        publish_pointers(output_base, subject_dir.name, metadata)
    except (OSError, ValueError) as exc:
        print(f"POINTER FAILURE ({type(exc).__name__}): run preserved at {report_path}.")
        print("If a pending journal exists, use --repair-pointers --output-dir "
              f'"{output_base}" from this workspace. Otherwise reconstruct pointers '
              'from the saved report metadata; do not rerun extraction.')
        raise
    return report_path


def create_client(api_key):
    from google import genai
    client = genai.Client(api_key=api_key, http_options={
        "timeout": 30000, "retry_options": {"attempts": 0}})
    # SDK 2.29 normalizes zero to one in the legacy client, then Interactions
    # interprets that one as a retry count. Apply zero to its generated config
    # after construction; fail closed if a future SDK changes this adapter.
    try:
        config = client.interactions.sdk_configuration.retry_config
        if config.strategy != "attempt-count-backoff":
            raise RuntimeError("unsupported Interactions retry strategy")
        config.max_retries = 0
        config.retry_connection_errors = False
    except (AttributeError, RuntimeError):
        client.close()
        raise RuntimeError("Cannot disable Interactions SDK retries; use the tested "
                           "google-genai 2.29.0 runtime or update the adapter.") from None
    return client


def run_extraction(url: str, intent: str, requested_model: str,
                   requested_fallback_model: str, tier: str,
                   start: str | None, end: str | None, low_res: bool,
                   output_base: Path, title: str, duration: str,
                   deep_summary: bool, technical: bool,
                   coding_video: bool, subject: str, custom_request: str = "",
                   processing: str = DEFAULT_PROCESSING) -> int:
    validate_agentic_options(start, end)
    if processing not in PROCESSING_MODES:
        raise ValueError(f"processing must be one of {PROCESSING_MODES}")
    subject_path(output_base, subject)
    policy = resolve_model_policy(
        tier, requested_model, requested_fallback_model
    )
    phases = selected_phase_defs(deep_summary, technical, coding_video)
    effective = build_effective_prompts(phases, title, duration, custom_request)
    load_env_files()
    key_name = api_key_name(tier)
    client = create_client(os.environ[key_name])
    print(
        f"Video-to-Action — {len(effective)} selected phase(s); "
        f"{tier}-tier policy; {processing} processing; primary {policy['primary']}; "
        f"fallback {policy['fallback']}"
    )
    if tier == "free":
        print("Preflight: free tier is the non-blocking default for this run.")
    for override in policy["overrides"]:
        print(f"Preflight override: {override}")

    def runner(pd, selected_model, mode):
        print(f"  Phase: {pd['title']} — {mode} — model {selected_model} ...")
        return run_phase(
            client, selected_model, url, pd["prompt"], start, end, low_res,
            processing=mode,
        )

    try:
        results, errors, attempts, successful_models = execute_phases(
            effective, runner, policy, processing=processing
        )
    finally:
        client.close()
    transcript_result = fetch_transcript(url)
    resolution = "low" if low_res else "default"
    clip = f"{start or 'start'} -> {end or 'end'}" if start or end else "full video"
    report_path = save_outputs(
        output_base, title, duration, url, intent, policy, effective,
        results, errors, attempts, successful_models, transcript_result,
        resolution, clip, subject=subject, processing=processing,
    )
    print(f"Saved: {report_path}")
    print(f"Agentic status: {describe_agentic_status(load_agentic_status(output_base))}")
    for message in transcript_result_messages(
            transcript_result, report_path.with_name("transcript.md")):
        print(message)
    return 0 if results else 1

def run_self_test() -> bool:
    fixture_root = Path.cwd() / "tmp"
    fixture_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=fixture_root) as temp:
        base = Path(temp)
        assert DEFAULT_MODEL == "gemini-3.8-flash"
        assert DEFAULT_FALLBACK_MODEL == "gemini-3.6-flash"
        assert DEFAULT_PROCESSING == "static"
        env_a, env_b = base / "workspace.env", base / "skill.env"
        env_lines = describe_env_search({
            "searched": (env_a, env_b), "found": (env_a,), "loaded": (env_a,),
        })
        assert str(env_a) in env_lines[0] and "found: yes" in env_lines[0]
        assert str(env_b) in env_lines[1] and "found: no" in env_lines[1]
        assert str(env_a) in env_lines[2] and "ENV LOADED" in env_lines[2]
        assert normalize_duration("4:05") == "04:05"
        assert normalize_duration("1:02:03") == "01:02:03"
        for invalid in ("4", "4:5", "04:60", "1:60:00", "abc"):
            try:
                normalize_duration(invalid)
                raise AssertionError(f"invalid duration accepted: {invalid}")
            except argparse.ArgumentTypeError:
                pass

        expected_id = "0-QDPnEIkvw"
        url_forms = (
            f"https://www.youtube.com/watch?v={expected_id}",
            f"https://youtu.be/{expected_id}",
            f"https://youtube.com/shorts/{expected_id}",
            f"https://youtube.com/embed/{expected_id}",
        )
        assert all(parse_youtube_video_id(url) == expected_id for url in url_forms)
        for invalid_url in ("https://example.com/watch?v=0-QDPnEIkvw", "bad"):
            try:
                parse_youtube_video_id(invalid_url)
                raise AssertionError(f"invalid YouTube URL accepted: {invalid_url}")
            except ValueError:
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

        free_policy = resolve_model_policy(
            "free", DEFAULT_MODEL, DEFAULT_FALLBACK_MODEL
        )
        assert free_policy["primary"] == "gemini-3.8-flash"
        assert free_policy["fallback"] == "gemini-3.6-flash"
        alias_policy = resolve_model_policy("free", "gemini-3.7-flash", "gemini-3.5-flash")
        assert alias_policy["primary"] == "gemini-3.8-flash"
        assert alias_policy["fallback"] == "gemini-3.6-flash"
        assert len(alias_policy["overrides"]) == 2
        free_override = resolve_model_policy(
            "free", "gemini-paid-only", "gemini-other-paid"
        )
        assert free_override["primary"] == DEFAULT_MODEL
        assert free_override["fallback"] == DEFAULT_FALLBACK_MODEL
        assert len(free_override["overrides"]) == 2
        paid_policy = resolve_model_policy(
            "paid", "gemini-paid-only", "gemini-paid-fallback"
        )
        assert paid_policy["primary"] == "gemini-paid-only"
        assert paid_policy["fallback"] == "gemini-paid-fallback"

        class FakeSdkError(Exception):
            def __init__(self, message, code, status=""):
                super().__init__(message)
                self.code = code
                self.status = status

        procedure_def = PHASE_DEFS["procedure"]
        retry_models, retry_sleeps = [], []
        retry_outcomes = [
            FakeSdkError("high demand", 503, "UNAVAILABLE"),
            FakeSdkError("high demand", 503, "UNAVAILABLE"),
            "primary success",
        ]

        def retry_runner(pd, model):
            retry_models.append(model)
            outcome = retry_outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        retry_text, retry_attempts = execute_phase_with_recovery(
            procedure_def, retry_runner, free_policy,
            sleeper=retry_sleeps.append,
        )
        assert retry_text == "primary success"
        assert retry_models == [DEFAULT_MODEL] * 3
        assert retry_sleeps == list(PRIMARY_BACKOFF_SECONDS)
        assert len(retry_attempts) == 3

        fallback_models = []
        fallback_outcomes = [
            FakeSdkError("high demand", 503, "UNAVAILABLE"),
            FakeSdkError("high demand", 503, "UNAVAILABLE"),
            FakeSdkError("high demand", 503, "UNAVAILABLE"),
            "fallback success",
        ]

        def fallback_runner(pd, model):
            fallback_models.append(model)
            outcome = fallback_outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        fallback_text, fallback_attempts = execute_phase_with_recovery(
            procedure_def, fallback_runner, free_policy, sleeper=lambda _: None
        )
        assert fallback_text == "fallback success"
        assert fallback_models == [DEFAULT_MODEL] * 3 + [DEFAULT_FALLBACK_MODEL]
        assert len(fallback_attempts) == 4
        assert fallback_attempts[-1]["role"] == "fallback"

        exhausted_outcomes = [
            FakeSdkError("primary unavailable", 503, "UNAVAILABLE"),
            FakeSdkError("primary unavailable", 503, "UNAVAILABLE"),
            FakeSdkError("primary unavailable", 503, "UNAVAILABLE"),
            FakeSdkError("fallback unavailable", 503, "UNAVAILABLE"),
        ]

        def exhausted_runner(pd, model):
            raise exhausted_outcomes.pop(0)

        exhausted_text, exhausted_attempts = execute_phase_with_recovery(
            procedure_def, exhausted_runner, free_policy, sleeper=lambda _: None
        )
        assert exhausted_text is None
        assert len(exhausted_attempts) == 4
        assert exhausted_attempts[-1]["role"] == "fallback"
        assert exhausted_attempts[-1]["status"] == "failed"

        for code in (401, 429):
            nonretry_models = []

            def nonretry_runner(pd, model, error_code=code):
                nonretry_models.append(model)
                raise FakeSdkError("not retryable", error_code)

            text_result, attempt_result = execute_phase_with_recovery(
                procedure_def, nonretry_runner, free_policy,
                sleeper=lambda _: None,
            )
            assert text_result is None
            assert len(nonretry_models) == 1
            assert len(attempt_result) == 1
            assert not attempt_result[0]["transient"]

        configured_secret = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = "AIzaFixtureSecretValueThatMustNeverAppear"
            redacted = sanitize_error(FakeSdkError(
                "key=AIzaFixtureSecretValueThatMustNeverAppear", 503
            ))
            assert "FixtureSecret" not in redacted
            assert "[REDACTED]" in redacted
        finally:
            if configured_secret is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = configured_secret

        class Snippet:
            def __init__(self, text, start, duration):
                self.text, self.start, self.duration = text, start, duration

        class Track:
            def __init__(self, language, code, generated, snippets):
                self.language = language
                self.language_code = code
                self.is_generated = generated
                self._snippets = snippets

            def fetch(self):
                return self._snippets

        manual_spanish = Track(
            "Spanish", "es", False, [Snippet("Hola", 0.08, 1.5)]
        )
        generated_english = Track(
            "English", "en", True, [Snippet("Hello", 0.08, 1.5)]
        )

        class FakeApi:
            def list(self, video_id):
                assert video_id == expected_id
                return [generated_english, manual_spanish]

        successful_transcript = fetch_transcript(url_forms[0], FakeApi)
        assert successful_transcript["status"] == "complete"
        assert successful_transcript["language_code"] == "es"
        assert not successful_transcript["is_generated"]
        assert successful_transcript["retrieval_path"] == "youtube-transcript-api"
        assert successful_transcript["caption_kind"] == "manual"

        class TranscriptsDisabled(Exception):
            pass

        class DisabledApi:
            def list(self, video_id):
                raise TranscriptsDisabled("captions disabled")

        def absent_ytdlp(url, video_id):
            return {
                "status": "failed", "video_id": video_id,
                "reason": "yt-dlp fixture absent", "snippets": [],
            }

        unavailable_transcript = fetch_transcript(
            url_forms[0], DisabledApi, absent_ytdlp
        )
        assert unavailable_transcript["status"] == "unavailable"
        assert "yt-dlp fixture absent" in unavailable_transcript["reason"]

        class RequestBlocked(Exception):
            pass

        class BlockedApi:
            def list(self, video_id):
                raise RequestBlocked("request blocked")

        blocked_transcript = fetch_transcript(
            url_forms[0], BlockedApi, absent_ytdlp
        )
        assert blocked_transcript["status"] == "failed"

        rolling_vtt = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:01.000 align:start position:0%
<c>Hello</c>

00:00:01.000 --> 00:00:02.000 align:start position:0%
Hello world

00:00:02.000 --> 00:00:03.000 align:start position:0%
world again
"""
        parsed_rolling = parse_vtt_captions(rolling_vtt)
        assert " ".join(item["text"] for item in parsed_rolling) == "Hello world again"

        class FakeYtDlpResult:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        ytdlp_flags = []

        def fake_ytdlp_runner(command, **kwargs):
            del kwargs
            flag = "--write-sub" if "--write-sub" in command else "--write-auto-sub"
            ytdlp_flags.append(flag)
            if flag == "--write-auto-sub":
                target_dir = Path(command[command.index("--paths") + 1])
                (target_dir / f"{expected_id}.en.vtt").write_text(
                    rolling_vtt, encoding="utf-8"
                )
            return FakeYtDlpResult()

        fallback_transcript = fetch_transcript(
            url_forms[0], DisabledApi,
            lambda transcript_url, video_id: fetch_transcript_with_ytdlp(
                transcript_url, video_id, executable=base / "yt-dlp.exe",
                runner=fake_ytdlp_runner,
            ),
        )
        assert fallback_transcript["status"] == "complete"
        assert fallback_transcript["retrieval_path"] == "yt-dlp"
        assert fallback_transcript["caption_kind"] == "auto-generated"
        assert ytdlp_flags == ["--write-sub", "--write-auto-sub"]
        assert "TranscriptsDisabled" in fallback_transcript["primary_failure_reason"]
        fallback_doc = build_transcript_doc(
            "Fallback Fixture", url_forms[0], fallback_transcript
        )
        assert "Retrieval path:** yt-dlp" in fallback_doc
        assert "Caption track:** Automatically generated" in fallback_doc
        assert "Primary retrieval failure:** TranscriptsDisabled" in fallback_doc

        duration = "14:34"
        procedure_result = (
            "## Overview\n### 1.) Video Title and Length\n#### Overview detail\n"
            "```markdown\n## Overview\n### 2.) Fenced child\n## Steps\n```\n"
            "## Steps\n### STEP 1: Fixture\n#### Step detail"
        )
        acts = (
            "## 🎭 ACT I: Start\n### Act child\n#### Act detail\n"
            "```markdown\n## 🎭 ACT II: Code sample\n```\n"
            "## 🎭 FINAL ACT: Key Takeaways"
        )

        omitted_effective = build_effective_prompts(
            selected_phase_defs(False, False, False), "Omitted Fixture", duration
        )
        omitted_results, omitted_errors, omitted_attempts, omitted_models = (
            execute_phases(
                omitted_effective,
                lambda pd, model: procedure_result,
                free_policy,
                sleeper=lambda _: None,
            )
        )
        omitted_path = save_outputs(
            base / "omitted", "Omitted Fixture", duration, url_forms[0],
            "summarize", free_policy, omitted_effective, omitted_results,
            omitted_errors, omitted_attempts, omitted_models,
            unavailable_transcript, "default", "full video",
            run_ts="20000101-000001", subject="Fixtures",
        )
        omitted_text = omitted_path.read_text(encoding="utf-8")
        omitted_transcript = omitted_path.with_name("transcript.md")
        assert "Not selected for this run." in omitted_text
        assert "Manual recovery required" in omitted_transcript.read_text(
            encoding="utf-8"
        )

        manual_input = base / "manual-input.txt"
        manual_input.write_text("00:00 Manual fallback text.", encoding="utf-8")
        complete_manual_transcript(omitted_transcript, manual_input)
        completed_manual = omitted_transcript.read_text(encoding="utf-8")
        assert "Complete via manual fallback" in completed_manual
        assert "Automatic failure reason" in completed_manual
        assert "00:00 Manual fallback text." in completed_manual
        assert MANUAL_RECOVERY_START not in completed_manual

        isolated_effective = build_effective_prompts(
            selected_phase_defs(True, True, True), "Isolated Fixture", duration
        )

        def isolated_runner(pd, model):
            if pd["key"] == "deep_summary":
                raise FakeSdkError("invalid fixture", 400)
            return procedure_result if pd["key"] == "procedure" else "fixture technical"

        isolated_results, isolated_errors, isolated_attempts, isolated_models = (
            execute_phases(
                isolated_effective, isolated_runner, free_policy,
                sleeper=lambda _: None,
            )
        )
        assert set(isolated_results) == {"procedure", "technical"}
        assert [item["phase"] for item in isolated_errors] == ["deep_summary"]
        isolated_path = save_outputs(
            base / "isolated", "Isolated Fixture", duration, url_forms[0],
            "summarize", free_policy, isolated_effective, isolated_results,
            isolated_errors, isolated_attempts, isolated_models,
            blocked_transcript, "default", "full video",
            run_ts="20000101-000002", subject="Fixtures",
        )
        isolated_text = isolated_path.read_text(encoding="utf-8")
        assert "Deep Summary extraction failed; see Extraction Errors." in isolated_text
        assert "Not selected for this run." not in isolated_text
        isolated_transcript = isolated_path.with_name("transcript.md").read_text(
            encoding="utf-8"
        )
        assert "Manual recovery required" in isolated_transcript
        assert "yt-dlp fallback: yt-dlp fixture absent" in isolated_transcript
        assert "fixture technical" in isolated_text

        success_effective = build_effective_prompts(
            selected_phase_defs(True, False, False), "Success Fixture", duration
        )
        fixture_outcomes = {
            "procedure": [
                FakeSdkError("high demand", 503, "UNAVAILABLE"),
                FakeSdkError("high demand", 503, "UNAVAILABLE"),
                FakeSdkError("high demand", 503, "UNAVAILABLE"),
                procedure_result,
            ],
            "deep_summary": [acts],
        }

        def success_runner(pd, model):
            outcome = fixture_outcomes[pd["key"]].pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        success_results, success_errors, success_attempts, success_models = (
            execute_phases(
                success_effective, success_runner, free_policy,
                sleeper=lambda _: None,
            )
        )
        single_base = base / "single-invocation"
        success_path = save_outputs(
            single_base, "Success Fixture", duration, url_forms[0],
            "summarize", free_policy, success_effective, success_results,
            success_errors, success_attempts, success_models,
            successful_transcript, "default", "full video",
            run_ts="20000101-000003", subject="Fixtures",
        )
        run_directories = [item for item in (single_base / 'Fixtures').iterdir() if item.is_dir()]
        assert len(run_directories) == 1
        assert (single_base / "latest.json").is_file()
        assert (single_base / 'Fixtures' / 'latest.json').read_bytes() == (single_base / 'latest.json').read_bytes()

        success_text = success_path.read_text(encoding="utf-8")
        success_prompts = success_path.with_name("prompts.md").read_text(
            encoding="utf-8"
        )
        success_transcript = success_path.with_name("transcript.md").read_text(
            encoding="utf-8"
        )
        assert "**Primary model:** gemini-3.8-flash" in success_text
        assert "**Fallback model:** gemini-3.6-flash" in success_text
        assert "fallback 1/1" in success_text
        assert "procedure=gemini-3.6-flash" in success_text
        assert "**Processing:** static" in success_text
        assert "**Agentic status:** never probed" in success_text
        assert "fallback 1/1" in success_prompts
        assert "## Procedure" in success_text and "## Detailed Summary" in success_text
        assert "\n### Overview\n" in success_text and "\n### Steps\n" in success_text
        assert "\n#### 1.) Video Title and Length\n" in success_text
        assert "\n#### STEP 1: Fixture\n" in success_text
        assert "\n### 🎭 ACT I: Start\n" in success_text
        assert "\n### 🎭 FINAL ACT: Key Takeaways\n" in success_text
        assert "```markdown\n## Overview\n### 2.) Fenced child\n## Steps\n```" in success_text
        assert "Complete via automatic retrieval" in success_transcript
        assert "Retrieval path:** youtube-transcript-api" in success_transcript
        assert "[00:00:00.080–00:00:01.580] Hola" in success_transcript
        failure_messages = transcript_result_messages(
            blocked_transcript, isolated_path.with_name("transcript.md")
        )
        assert failure_messages[0].startswith("TRANSCRIPT FAILURE:")
        assert "--complete-transcript" in failure_messages[1]
        assert "--manual-transcript-file" in failure_messages[1]
        duration_rule = (
            f"This video's exact total length is {duration}; use it verbatim as the "
            f"Length, and ensure every timestamp falls within 00:00–{duration}."
        )
        assert duration_rule in success_effective[0]["prompt"]
        assert duration_rule in success_effective[1]["prompt"]
        assert f"**Duration supplied:** {duration}" in success_prompts
        assert success_effective[0]["prompt"] in success_prompts
        assert success_effective[1]["prompt"] in success_prompts

        for report_path in (omitted_path, isolated_path, success_path):
            assert report_path.name == "report.md"
            assert report_path.with_name("prompts.md").is_file()
            assert report_path.with_name("transcript.md").is_file()

    print(
        "Self-test passed: free-tier policy, bounded retry/fallback, phase "
        "selection and isolation, single-folder output, provenance, prompts, "
        "URLs, headings, env discovery, transcript fallback/reporting, and "
        "secret redaction."
    )
    return True

def main() -> None:
    try:
        load_env_files()
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description="Extract a deterministic video report")
    parser.add_argument("url", nargs="?")
    parser.add_argument(
        "--intent", default="summarize",
        choices=["follow", "summarize", "learn"],
    )
    parser.add_argument(
        "--tier", default=os.environ.get("GEMINI_API_TIER", DEFAULT_TIER),
        choices=["free", "paid"],
    )
    parser.add_argument(
        "--model", default=os.environ.get("VIDEO_TO_ACTION_MODEL", DEFAULT_MODEL)
    )
    parser.add_argument(
        "--fallback-model",
        default=os.environ.get(
            "VIDEO_TO_ACTION_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL
        ),
    )
    parser.add_argument("--start", type=parse_offset)
    parser.add_argument("--end", type=parse_offset)
    parser.add_argument("--resolution", default="default", choices=["default", "low"])
    parser.add_argument("--processing", default=DEFAULT_PROCESSING, choices=list(PROCESSING_MODES),
                        help="Video processing; agentic falls back to static per phase on failure.")
    parser.add_argument("--agentic-probe", action="store_true",
                        help="One agentic call on a fixed short video; records agentic-status.json")
    parser.add_argument("--output-dir", default=os.environ.get(
        "VIDEO_TO_ACTION_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
    parser.add_argument("--title")
    parser.add_argument("--subject", help="Broad, unnumbered subject folder (required for extraction)")
    parser.add_argument("--repair-pointers", action="store_true",
                        help="Replay pending latest-pointer writes without an API call")
    parser.add_argument("--duration", type=normalize_duration)
    parser.add_argument("--deep-summary", action=argparse.BooleanOptionalAction, default=True,
                        help="Include Deep Summary by default; --no-deep-summary opts out.")
    parser.add_argument("--custom-request", default="",
                        help="Explicit additional user instruction; included in the main call")
    parser.add_argument("--technical", action="store_true")
    parser.add_argument("--coding-video", action="store_true")
    parser.add_argument("--check-setup", action="store_true")
    parser.add_argument("--dump-prompts", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--complete-transcript", type=Path)
    parser.add_argument("--manual-transcript-file", type=Path)
    args = parser.parse_args()
    if args.repair_pointers:
        repaired = repair_pointers(Path(args.output_dir))
        print("Pointers repaired." if repaired else "No pending pointer transaction.")
        return
    if bool(args.complete_transcript) != bool(args.manual_transcript_file):
        parser.error(
            "--complete-transcript and --manual-transcript-file must be used together"
        )
    if args.complete_transcript:
        completed = complete_manual_transcript(
            args.complete_transcript, args.manual_transcript_file
        )
        print(f"Completed: {completed}")
        return
    if args.dump_prompts:
        print(f"Wrote {dump_prompts()}")
        return
    if args.self_test:
        sys.exit(0 if run_self_test() else 1)
    if args.check_setup:
        sys.exit(0 if check_setup(args.tier) else 1)
    if args.agentic_probe:
        if not check_setup(args.tier, verbose=False):
            check_setup(args.tier, verbose=True)
            sys.exit(1)
        sys.exit(run_agentic_probe(Path(args.output_dir), args.tier,
                                   args.model, args.fallback_model))

    missing = []
    if not args.subject:
        missing.append("subject (--subject)")
    if not args.url:
        missing.append("public YouTube URL")
    if not args.title or not args.title.strip():
        missing.append("exact title (--title)")
    if not args.duration:
        missing.append("exact duration (--duration)")
    if missing:
        parser.error("missing required inputs: " + ", ".join(missing))
    try:
        subject_path(Path(args.output_dir), args.subject)
    except ValueError as exc:
        parser.error(str(exc))
    if not is_youtube_url(args.url):
        parser.error("a valid public YouTube URL is required")
    try:
        validate_agentic_options(args.start, args.end)
    except ValueError as exc:
        parser.error(str(exc))
    if args.technical and not args.coding_video:
        parser.error("--technical requires --coding-video")
    if not check_setup(args.tier, verbose=False):
        check_setup(args.tier, verbose=True)
        sys.exit(1)
    sys.exit(run_extraction(
        args.url, args.intent, args.model, args.fallback_model, args.tier,
        args.start, args.end, args.resolution == "low", Path(args.output_dir),
        args.title.strip(), args.duration, args.deep_summary, args.technical,
        args.coding_video, args.subject, args.custom_request,
        processing=args.processing,
    ))


if __name__ == "__main__":
    main()
