#!/usr/bin/env python3
"""Deterministic state and lifecycle helper for Brainstorm captures."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path


STATE_RE = re.compile(
    r"<!-- BRAINSTORM_STATE_START\n(?P<json>.*?)\nBRAINSTORM_STATE_END -->",
    re.DOTALL,
)
NUMBER_RE = re.compile(r"^(?P<number>\d+)\.\)")
SAFE_SEGMENT_RE = re.compile(r'^[^<>:"/\\|?*\x00-\x1f]+$')
SECTION_RE = re.compile(r"(?ms)^## (?P<title>[^\r\n]+)\r?\n(?P<body>.*?)(?=^## |\Z)")
FEEDBACK_NUMBER_RE = re.compile(r"(?m)^### Feedback (?P<number>\d+)\b")
CANONICAL_SECTIONS = {
    "Agent Provenance",
    "Working Direction",
    "North Star",
    "Running Summary",
    "Key Decisions",
    "Q&A Log",
    "Assumptions And Evidence",
    "Decision-Tree Coverage",
    "Contradictions And Superseded Decisions",
    "Open Flags",
    "Completeness State",
    "Next Step Or Handoff",
    "Lifecycle And Reopen History",
    "Feedback Section",
    "Agent Change Log",
}
PROVENANCE_FIELDS = (
    "Content owner",
    "Original writing agent",
    "Original writing LLM",
    "Created",
    "Artifact role",
)


class BrainstormError(RuntimeError):
    """Raised when a lifecycle invariant would be violated."""


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_log() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


def recorded_identity(value: str) -> str:
    return value.strip() or "Not recorded"


def display_width(value: str) -> int:
    width = 0
    for character in value:
        if unicodedata.combining(character):
            continue
        width += 2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1
    return width


def table_cell(value: object) -> str:
    cleaned = " ".join(str(value).splitlines()).strip().replace("|", r"\|")
    if display_width(cleaned) > 80:
        raise BrainstormError(f"Markdown table cell exceeds 80 columns: {cleaned!r}")
    return cleaned


def markdown_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    normalized = [[table_cell(cell) for cell in headers]]
    normalized.extend([[table_cell(cell) for cell in row] for row in rows])
    widths = [
        max(display_width(row[index]) for row in normalized)
        for index in range(len(headers))
    ]
    if sum(widths) + (3 * len(widths)) + 1 > 120:
        raise BrainstormError("Markdown table exceeds 120 display columns.")

    def render_row(row: list[str]) -> str:
        cells = [
            f" {cell}{' ' * (widths[index] - display_width(cell))} "
            for index, cell in enumerate(row)
        ]
        return "|" + "|".join(cells) + "|"

    delimiter = ["-" * max(3, width) for width in widths]
    return [render_row(normalized[0]), render_row(delimiter)] + [
        render_row(row) for row in normalized[1:]
    ]


def parse_table(body: str, columns: int) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [
            cell.strip().replace(r"\|", "|")
            for cell in stripped[1:-1].split("|")
        ]
        if len(cells) != columns:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def visible_sections(text: str) -> dict[str, str]:
    visible = text.split("<!-- BRAINSTORM_STATE_START", 1)[0]
    return {
        match.group("title").strip(): match.group("body").rstrip()
        for match in SECTION_RE.finditer(visible)
    }


def default_provenance(state: dict, agent: str, model: str) -> dict[str, str]:
    return {
        "Content owner": "Uzo",
        "Original writing agent": recorded_identity(agent),
        "Original writing LLM": recorded_identity(model),
        "Created": state["created_at"],
        "Artifact role": f"Durable Brainstorm capture for {state['topic']}",
    }


def adopt_visible_sections(
    state: dict, text: str, agent: str, model: str, migrating: bool
) -> None:
    sections = visible_sections(text)
    provenance_rows = parse_table(sections.get("Agent Provenance", ""), 2)
    parsed_provenance = {field: value for field, value in provenance_rows}
    if all(field in parsed_provenance for field in PROVENANCE_FIELDS):
        state["provenance"] = {
            field: parsed_provenance[field] for field in PROVENANCE_FIELDS
        }
    else:
        state.setdefault("provenance", default_provenance(state, agent, model))

    feedback_body = sections.get("Feedback Section")
    if feedback_body is not None:
        state["feedback"] = [feedback_body.strip()] if feedback_body.strip() else []
    else:
        state.setdefault("feedback", [])

    change_rows = parse_table(sections.get("Agent Change Log", ""), 5)
    if change_rows:
        state["change_log"] = [
            {
                "at": row[0],
                "agent": row[1],
                "model": row[2],
                "action": row[3],
                "scope": row[4],
            }
            for row in change_rows
        ]
    else:
        state.setdefault("change_log", [])

    preserved = list(state.get("preserved_sections", []))
    for title, body in sections.items():
        if title not in CANONICAL_SECTIONS:
            section = f"## {title}\n{body}".rstrip()
            if section not in preserved:
                preserved.append(section)
    state["preserved_sections"] = preserved

    if migrating:
        append_change_log(
            state,
            agent,
            model,
            "Migrated",
            "Upgraded Brainstorm state schema from v1 to v2",
        )


def append_change_log(
    state: dict, agent: str, model: str, action: str, scope: str
) -> None:
    state.setdefault("change_log", []).append(
        {
            "at": now_log(),
            "agent": recorded_identity(agent),
            "model": recorded_identity(model),
            "action": action,
            "scope": scope,
        }
    )


def safe_segment(value: str, label: str) -> str:
    cleaned = value.strip()
    if (
        not cleaned
        or cleaned in {".", ".."}
        or cleaned.endswith((" ", "."))
        or not SAFE_SEGMENT_RE.fullmatch(cleaned)
    ):
        raise BrainstormError(f"Unsafe {label}: {value!r}")
    return cleaned


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_state(
    path: Path, agent: str = "Not recorded", model: str = "Not recorded"
) -> dict:
    text = path.read_text(encoding="utf-8")
    match = STATE_RE.search(text)
    if not match:
        raise BrainstormError(f"Brainstorm state block is missing: {path}")
    state = json.loads(match.group("json"))
    version = state.get("version")
    if version not in {1, 2}:
        raise BrainstormError("Unsupported Brainstorm state version.")
    migrating = version == 1
    if migrating:
        state["version"] = 2
    adopt_visible_sections(state, text, agent, model, migrating)
    return state


def numbered_max(*folders: Path) -> int:
    highest = 0
    for folder in folders:
        if not folder.exists():
            continue
        for child in folder.iterdir():
            match = NUMBER_RE.match(child.name)
            if match:
                highest = max(highest, int(match.group("number")))
    return highest


def topic_candidates(topic: str, *folders: Path) -> list[Path]:
    pattern = re.compile(
        rf"^\d+\.\) {re.escape(topic)}_(?:chivita|fini)\.md$",
        re.IGNORECASE,
    )
    return sorted(
        child
        for folder in folders
        if folder.exists()
        for child in folder.iterdir()
        if child.is_file() and pattern.fullmatch(child.name)
    )


def bullets(values: list[str], empty: str) -> list[str]:
    return [f"- {value}" for value in values] if values else [f"- {empty}"]


def render(state: dict) -> str:
    north_star = state["north_star"]
    north_star_text = north_star["text"] or "Pending — finalized at convergence."
    provenance_rows = [
        [field, state["provenance"][field]] for field in PROVENANCE_FIELDS
    ]
    lines = [
        f"# {state['topic']}: Brainstorm",
        "",
        f"Status: {state['status'].upper()}",
        f"Subject: {state['subject']}",
        f"Topic: {state['topic']}",
        f"Permanent number: {state['number']}",
        f"Created: {state['created_at']}",
        f"Updated: {state['updated_at']}",
        "",
        "## Agent Provenance",
        "",
        *markdown_table(["Field", "Value"], provenance_rows),
        "",
        "## Working Direction",
        "",
        state["working_direction"] or "To be discovered through brainstorming.",
        "",
        "## North Star",
        "",
        f"State: {north_star['status']}",
        "",
        north_star_text,
        "",
        "## Running Summary",
        "",
        state["summary"] or "No answers captured yet.",
        "",
        "## Key Decisions",
        "",
    ]
    decision_lines = [
        f"- [{item['at']}] {item['text']}" for item in state["key_decisions"]
    ]
    lines.extend(decision_lines or ["- None yet."])
    lines.extend(["", "## Q&A Log", ""])
    if state["qa_log"]:
        for item in state["qa_log"]:
            lines.extend(
                [
                    f"### Q{item['number']} — {item['topic']}",
                    "",
                    f"- Asked: {item['question']}",
                    f"- Recommended: {item['recommendation']}",
                    f"- User answer: {item['answer']}",
                    f"- Captured: {item['captured']}",
                    f"- Checkpointed: {item['at']}",
                    "",
                ]
            )
    else:
        lines.extend(["No questions captured yet.", ""])
    lines.extend(["## Assumptions And Evidence", ""])
    assumption_lines = [
        f"- [{item['at']}] {item['text']}"
        for item in state["assumptions_evidence"]
    ]
    lines.extend(assumption_lines or ["- None yet."])
    lines.extend(["", "## Decision-Tree Coverage", ""])
    lines.extend(bullets(state["coverage"], "Not mapped yet."))
    lines.extend(["", "## Contradictions And Superseded Decisions", ""])
    if state["contradictions"]:
        for index, item in enumerate(state["contradictions"], start=1):
            disposition = item["disposition"] or "UNRESOLVED"
            lines.append(
                f"- C{index} [{item['at']}] {item['text']} "
                f"— Disposition: {disposition}"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Open Flags", ""])
    if state["flags"]:
        for item in state["flags"]:
            disposition = item["disposition"] or "Pending input"
            lines.append(
                f"- {item['id']} [{item['status']}] {item['item']} "
                f"→ Owner: {item['owner']} → {disposition}"
            )
    else:
        lines.append("- None.")
    completeness = state["completeness"]
    lines.extend(
        [
            "",
            "## Completeness State",
            "",
            f"- [{'x' if completeness['branches_reviewed'] else ' '}] "
            "Relevant decision-tree branches reviewed.",
            f"- [{'x' if completeness['contradictions_disposed'] else ' '}] "
            "Contradictions explicitly disposed.",
            f"- [{'x' if completeness['flags_disposed'] else ' '}] "
            "Open flags resolved, deferred, or accepted.",
            f"- [{'x' if completeness['shared_understanding'] else ' '}] "
            "User confirmed shared understanding.",
            f"- [{'x' if north_star['status'] == 'finalized' else ' '}] "
            "North Star finalized at convergence.",
            "",
            "## Next Step Or Handoff",
            "",
            state["next_step"] or "Continue the Brainstorm interview.",
            "",
            "## Lifecycle And Reopen History",
            "",
        ]
    )
    lines.extend(
        f"- [{item['at']}] {item['event']}: {item['note']}"
        for item in state["lifecycle"]
    )
    for section in state.get("preserved_sections", []):
        lines.extend(["", section.rstrip()])
    lines.extend(["", "## Feedback Section"])
    if state["feedback"]:
        lines.extend(["", *state["feedback"]])
    change_rows = [
        [
            item["at"],
            item["agent"],
            item["model"],
            item["action"],
            item["scope"],
        ]
        for item in state["change_log"]
    ]
    lines.extend(
        [
            "",
            "## Agent Change Log",
            "",
            *markdown_table(
                ["Date and Time", "Agent", "Model", "Action", "Scope"],
                change_rows,
            ),
            "",
            "<!-- BRAINSTORM_STATE_START",
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            "BRAINSTORM_STATE_END -->",
            "",
        ]
    )
    return "\n".join(lines)


def write_state(path: Path, state: dict) -> None:
    state["updated_at"] = now_iso()
    atomic_write(path, render(state))


def parse_pair(value: str, label: str) -> tuple[str, str]:
    if "::" not in value:
        raise BrainstormError(f"{label} must use TEXT::VALUE format.")
    left, right = (part.strip() for part in value.split("::", 1))
    if not left or not right:
        raise BrainstormError(f"{label} cannot contain an empty part.")
    return left, right


def cmd_create(args: argparse.Namespace) -> None:
    root = Path(args.workspace_root).resolve()
    subject = safe_segment(args.subject, "Subject")
    topic = safe_segment(args.topic, "Topic")
    live = root / "Archive" / "Live" / "Brainstorms" / subject
    historical = root / "Archive" / "Historical" / "Brainstorms" / subject
    existing = topic_candidates(topic, live, historical)
    if existing:
        joined = ", ".join(str(item) for item in existing)
        raise BrainstormError(
            f"Topic already has a Brainstorm; resume or reopen it: {joined}"
        )
    number = numbered_max(live, historical) + 1
    path = live / f"{number}.) {topic}_chivita.md"
    timestamp = now_iso()
    state = {
        "version": 2,
        "run_id": timestamp.replace(":", "").replace("-", ""),
        "workspace_root": str(root),
        "subject": subject,
        "topic": topic,
        "number": number,
        "status": "chivita",
        "created_at": timestamp,
        "updated_at": timestamp,
        "working_direction": args.working_direction or "",
        "north_star": {"status": "provisional", "text": ""},
        "north_star_history": [],
        "summary": args.summary or "",
        "key_decisions": [],
        "qa_log": [],
        "assumptions_evidence": [],
        "coverage": [],
        "contradictions": [],
        "flags": [],
        "completeness": {
            "branches_reviewed": False,
            "contradictions_disposed": True,
            "flags_disposed": True,
            "shared_understanding": False,
        },
        "next_step": "Ask Question 1.",
        "lifecycle": [
            {
                "at": timestamp,
                "event": "CREATED",
                "note": "Chivita capture created before Question 1.",
            }
        ],
        "provenance": {
            "Content owner": recorded_identity(args.content_owner),
            "Original writing agent": recorded_identity(args.agent),
            "Original writing LLM": recorded_identity(args.model),
            "Created": timestamp,
            "Artifact role": f"Durable Brainstorm capture for {topic}",
        },
        "feedback": [],
        "change_log": [],
        "preserved_sections": [],
    }
    append_change_log(
        state,
        args.agent,
        args.model,
        "Created",
        "Capture before Question 1",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(render(state))
    except FileExistsError as exc:
        raise BrainstormError(f"Collision refused: {path}") from exc
    print(json.dumps({"artifact_path": str(path), "number": number}))


def cmd_checkpoint(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    if state["status"] != "chivita":
        raise BrainstormError("Only a chivita Brainstorm can accept answers.")
    timestamp = now_iso()
    qa_number = len(state["qa_log"]) + 1
    state["qa_log"].append(
        {
            "number": qa_number,
            "topic": args.topic or f"Decision {qa_number}",
            "question": args.question.strip(),
            "recommendation": args.recommendation.strip(),
            "answer": args.answer.strip(),
            "captured": args.captured.strip(),
            "at": timestamp,
        }
    )
    if args.summary is not None:
        state["summary"] = args.summary.strip()
    state["key_decisions"].extend(
        {"at": timestamp, "text": value.strip()} for value in args.decision
    )
    state["assumptions_evidence"].extend(
        {"at": timestamp, "text": value.strip()} for value in args.evidence
    )
    state["contradictions"].extend(
        {"at": timestamp, "text": value.strip(), "disposition": ""}
        for value in args.contradiction
    )
    for value in args.flag:
        item, owner = parse_pair(value, "flag")
        state["flags"].append(
            {
                "id": f"F{len(state['flags']) + 1}",
                "item": item,
                "owner": owner,
                "status": "open",
                "disposition": "",
            }
        )
    state["coverage"].extend(
        value for value in args.coverage if value not in state["coverage"]
    )
    state["completeness"]["contradictions_disposed"] = all(
        item["disposition"] for item in state["contradictions"]
    )
    state["completeness"]["flags_disposed"] = all(
        item["status"] in {"resolved", "deferred", "accepted"}
        for item in state["flags"]
    )
    state["next_step"] = args.next_step or f"Ask Question {qa_number + 1}."
    append_change_log(
        state, args.agent, args.model, "Checkpointed", f"Captured Question {qa_number}"
    )
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "checkpointed_q": qa_number}))


def cmd_resolve_flag(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    match = next((item for item in state["flags"] if item["id"] == args.flag_id), None)
    if not match:
        raise BrainstormError(f"Unknown flag: {args.flag_id}")
    match["status"] = args.status
    match["disposition"] = args.disposition.strip()
    state["completeness"]["flags_disposed"] = all(
        item["status"] in {"resolved", "deferred", "accepted"}
        for item in state["flags"]
    )
    append_change_log(
        state, args.agent, args.model, "Resolved flag", f"Updated {args.flag_id}"
    )
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "flag": args.flag_id}))


def cmd_resolve_contradiction(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    index = args.index - 1
    if index < 0 or index >= len(state["contradictions"]):
        raise BrainstormError(f"Unknown contradiction index: {args.index}")
    state["contradictions"][index]["disposition"] = args.disposition.strip()
    state["completeness"]["contradictions_disposed"] = all(
        item["disposition"] for item in state["contradictions"]
    )
    append_change_log(
        state,
        args.agent,
        args.model,
        "Resolved contradiction",
        f"Updated C{args.index}",
    )
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "contradiction": args.index}))


def cmd_pause(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    if state["status"] != "chivita":
        raise BrainstormError("Only a chivita Brainstorm can be paused.")
    state["status"] = "paused"
    state["next_step"] = "Resume this Brainstorm before asking another question."
    state["lifecycle"].append(
        {"at": now_iso(), "event": "PAUSED", "note": args.reason.strip()}
    )
    append_change_log(state, args.agent, args.model, "Paused", "Paused interview")
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "status": "paused"}))


def cmd_resume(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    if state["status"] != "paused":
        raise BrainstormError("Only a paused Brainstorm can be resumed.")
    state["status"] = "chivita"
    state["next_step"] = f"Continue with Question {len(state['qa_log']) + 1}."
    state["lifecycle"].append(
        {"at": now_iso(), "event": "RESUMED", "note": "Interview resumed."}
    )
    append_change_log(state, args.agent, args.model, "Resumed", "Resumed interview")
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "status": "chivita"}))


def cmd_set_ready(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    if state["status"] != "chivita":
        raise BrainstormError("Resume the Brainstorm before setting readiness.")
    if not args.user_accepted:
        raise BrainstormError("Readiness requires explicit user acceptance.")
    unresolved = [
        item["id"]
        for item in state["flags"]
        if item["status"] not in {"resolved", "deferred", "accepted"}
    ]
    contradictions = [
        index
        for index, item in enumerate(state["contradictions"], start=1)
        if not item["disposition"]
    ]
    if unresolved or contradictions:
        raise BrainstormError(
            f"Readiness blocked; flags={unresolved}, contradictions={contradictions}"
        )
    timestamp = now_iso()
    state["north_star"] = {
        "status": "finalized",
        "text": args.north_star.strip(),
    }
    state["north_star_history"].append(
        {"at": timestamp, "text": args.north_star.strip()}
    )
    state["completeness"] = {
        "branches_reviewed": True,
        "contradictions_disposed": True,
        "flags_disposed": True,
        "shared_understanding": True,
    }
    state["next_step"] = args.next_step or "Invoke finalize-brainstorm."
    state["lifecycle"].append(
        {
            "at": timestamp,
            "event": "READY",
            "note": "User accepted shared understanding and the final North Star.",
        }
    )
    append_change_log(
        state, args.agent, args.model, "Set ready", "Finalized North Star"
    )
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "ready": True}))


def cmd_finalize(args: argparse.Namespace) -> None:
    source = Path(args.artifact).resolve()
    state = read_state(source, args.agent, args.model)
    if state["status"] != "chivita":
        raise BrainstormError("Only a chivita Brainstorm can be finalized.")
    checks = state["completeness"]
    if not all(checks.values()) or state["north_star"]["status"] != "finalized":
        raise BrainstormError("Finalization refused: completeness evidence is missing.")
    root = Path(state["workspace_root"])
    expected_source = (
        root
        / "Archive"
        / "Live"
        / "Brainstorms"
        / state["subject"]
        / f"{state['number']}.) {state['topic']}_chivita.md"
    ).resolve()
    if source != expected_source:
        raise BrainstormError(f"Unexpected chivita source path: {source}")
    destination_folder = (
        root / "Archive" / "Historical" / "Brainstorms" / state["subject"]
    )
    destination = destination_folder / (
        f"{state['number']}.) {state['topic']}_fini.md"
    )
    if destination.exists():
        raise BrainstormError(f"Historical collision refused: {destination}")
    timestamp = now_iso()
    state["status"] = "fini"
    state["next_step"] = args.next_step or "Use the finalized North Star."
    state["lifecycle"].append(
        {
            "at": timestamp,
            "event": "FINALIZED",
            "note": args.acceptance.strip(),
        }
    )
    append_change_log(
        state, args.agent, args.model, "Finalized", "Moved capture to Historical"
    )
    state["updated_at"] = timestamp
    destination_folder.mkdir(parents=True, exist_ok=True)
    atomic_write(destination, render(state))
    source.unlink()
    print(json.dumps({"artifact_path": str(destination), "status": "fini"}))


def cmd_reopen(args: argparse.Namespace) -> None:
    source = Path(args.artifact).resolve()
    state = read_state(source, args.agent, args.model)
    if state["status"] != "fini":
        raise BrainstormError("Only a fini Brainstorm can be reopened.")
    root = Path(state["workspace_root"])
    expected_source = (
        root
        / "Archive"
        / "Historical"
        / "Brainstorms"
        / state["subject"]
        / f"{state['number']}.) {state['topic']}_fini.md"
    ).resolve()
    if source != expected_source:
        raise BrainstormError(f"Unexpected fini source path: {source}")
    destination_folder = root / "Archive" / "Live" / "Brainstorms" / state["subject"]
    destination = destination_folder / (
        f"{state['number']}.) {state['topic']}_chivita.md"
    )
    if destination.exists():
        raise BrainstormError(f"Live collision refused: {destination}")
    timestamp = now_iso()
    previous = state["north_star"]["text"]
    state["status"] = "chivita"
    state["working_direction"] = previous or state["working_direction"]
    state["north_star"] = {"status": "provisional", "text": ""}
    state["completeness"] = {
        "branches_reviewed": False,
        "contradictions_disposed": all(
            item["disposition"] for item in state["contradictions"]
        ),
        "flags_disposed": all(
            item["status"] in {"resolved", "deferred", "accepted"}
            for item in state["flags"]
        ),
        "shared_understanding": False,
    }
    state["next_step"] = f"Continue with Question {len(state['qa_log']) + 1}."
    state["lifecycle"].append(
        {"at": timestamp, "event": "REOPENED", "note": args.reason.strip()}
    )
    append_change_log(
        state, args.agent, args.model, "Reopened", "Moved capture back to Live"
    )
    state["updated_at"] = timestamp
    destination_folder.mkdir(parents=True, exist_ok=True)
    atomic_write(destination, render(state))
    source.unlink()
    print(json.dumps({"artifact_path": str(destination), "status": "chivita"}))


def cmd_feedback(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path, args.agent, args.model)
    existing_numbers = [
        int(match.group("number"))
        for entry in state["feedback"]
        for match in FEEDBACK_NUMBER_RE.finditer(entry)
    ]
    number = max(existing_numbers, default=0) + 1
    descriptor = " ".join(args.descriptor.split()).strip()
    body = args.body.strip()
    if not descriptor or not body:
        raise BrainstormError("Feedback descriptor and body cannot be empty.")
    entry = (
        f"### Feedback {number} - {datetime.now().date().isoformat()} - "
        f"{recorded_identity(args.agent)} - {descriptor}\n\n{body}"
    )
    state["feedback"].append(entry)
    append_change_log(
        state, args.agent, args.model, "Added feedback", f"Appended Feedback {number}"
    )
    write_state(path, state)
    print(json.dumps({"artifact_path": str(path), "feedback": number}))


def cmd_status(args: argparse.Namespace) -> None:
    path = Path(args.artifact).resolve()
    state = read_state(path)
    result = {
        "artifact_path": str(path),
        "subject": state["subject"],
        "topic": state["topic"],
        "number": state["number"],
        "status": state["status"],
        "questions": len(state["qa_log"]),
        "north_star": state["north_star"],
        "completeness": state["completeness"],
        "open_flags": [
            item["id"] for item in state["flags"] if item["status"] == "open"
        ],
        "unresolved_contradictions": [
            index
            for index, item in enumerate(state["contradictions"], start=1)
            if not item["disposition"]
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


def add_attribution_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--agent", default="Not recorded")
    command.add_argument("--model", default="Not recorded")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create")
    create.add_argument("--workspace-root", required=True)
    create.add_argument("--subject", required=True)
    create.add_argument("--topic", required=True)
    create.add_argument("--working-direction")
    create.add_argument("--summary")
    create.add_argument("--content-owner", default="Uzo")
    add_attribution_arguments(create)
    create.set_defaults(func=cmd_create)

    checkpoint = commands.add_parser("checkpoint")
    checkpoint.add_argument("--artifact", required=True)
    checkpoint.add_argument("--topic")
    checkpoint.add_argument("--question", required=True)
    checkpoint.add_argument("--recommendation", required=True)
    checkpoint.add_argument("--answer", required=True)
    checkpoint.add_argument("--captured", required=True)
    checkpoint.add_argument("--summary")
    checkpoint.add_argument("--decision", action="append", default=[])
    checkpoint.add_argument("--evidence", action="append", default=[])
    checkpoint.add_argument("--contradiction", action="append", default=[])
    checkpoint.add_argument("--flag", action="append", default=[])
    checkpoint.add_argument("--coverage", action="append", default=[])
    checkpoint.add_argument("--next-step")
    add_attribution_arguments(checkpoint)
    checkpoint.set_defaults(func=cmd_checkpoint)

    flag = commands.add_parser("resolve-flag")
    flag.add_argument("--artifact", required=True)
    flag.add_argument("--flag-id", required=True)
    flag.add_argument(
        "--status", choices=["resolved", "deferred", "accepted", "blocking"],
        required=True,
    )
    flag.add_argument("--disposition", required=True)
    add_attribution_arguments(flag)
    flag.set_defaults(func=cmd_resolve_flag)

    contradiction = commands.add_parser("resolve-contradiction")
    contradiction.add_argument("--artifact", required=True)
    contradiction.add_argument("--index", type=int, required=True)
    contradiction.add_argument("--disposition", required=True)
    add_attribution_arguments(contradiction)
    contradiction.set_defaults(func=cmd_resolve_contradiction)

    pause = commands.add_parser("pause")
    pause.add_argument("--artifact", required=True)
    pause.add_argument("--reason", required=True)
    add_attribution_arguments(pause)
    pause.set_defaults(func=cmd_pause)

    resume = commands.add_parser("resume")
    resume.add_argument("--artifact", required=True)
    add_attribution_arguments(resume)
    resume.set_defaults(func=cmd_resume)

    ready = commands.add_parser("set-ready")
    ready.add_argument("--artifact", required=True)
    ready.add_argument("--north-star", required=True)
    ready.add_argument("--user-accepted", action="store_true")
    ready.add_argument("--next-step")
    add_attribution_arguments(ready)
    ready.set_defaults(func=cmd_set_ready)

    finalize = commands.add_parser("finalize")
    finalize.add_argument("--artifact", required=True)
    finalize.add_argument("--acceptance", required=True)
    finalize.add_argument("--next-step")
    add_attribution_arguments(finalize)
    finalize.set_defaults(func=cmd_finalize)

    reopen = commands.add_parser("reopen")
    reopen.add_argument("--artifact", required=True)
    reopen.add_argument("--reason", required=True)
    add_attribution_arguments(reopen)
    reopen.set_defaults(func=cmd_reopen)

    feedback = commands.add_parser("feedback")
    feedback.add_argument("--artifact", required=True)
    feedback.add_argument("--descriptor", required=True)
    feedback.add_argument("--body", required=True)
    add_attribution_arguments(feedback)
    feedback.set_defaults(func=cmd_feedback)

    status = commands.add_parser("status")
    status.add_argument("--artifact", required=True)
    status.add_argument("--pretty", action="store_true")
    status.set_defaults(func=cmd_status)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        args.func(args)
        return 0
    except (BrainstormError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
