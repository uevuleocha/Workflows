#!/usr/bin/env python3
"""Maintain artifact-backed North Star lifecycle and per-turn pursuit state."""
from __future__ import annotations
import argparse, base64, json, os, re, secrets, sys, tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

INDICATORS = ("\u2b50", "\U0001f31f", "\U0001f320", "\U0001f4ab", "\u2728", "\u2726", "\u2727", "\u2734\ufe0f")
SECTION_HEADING = "## North Star"
RUN_BEGIN = "<!-- north-star:run-begin {run_id} -->"
RUN_END = "<!-- north-star:run-end -->"
STATE_PREFIX = "<!-- north-star:state-b64 "
STATE_SUFFIX = " -->"
BLOCK_RE = re.compile(r"<!-- north-star:run-begin (?P<run_id>[^\s]+) -->(?P<body>.*?)<!-- north-star:run-end -->", re.DOTALL)
STATE_RE = re.compile(r"<!-- north-star:state-b64 (?P<payload>[A-Za-z0-9_\-=]+) -->")
PROVENANCE_SECTION_RE = re.compile(r"(?ms)^## Agent Provenance[ \t]*\n.*?(?=^\*\*Subject:|^## |\Z)")
CHANGE_LOG_SECTION_RE = re.compile(r"(?ms)^## Agent Change Log[ \t]*\n.*?(?=^## |\Z)")
NONTERMINAL = {"in_progress", "active", "paused"}
SAFE_SEGMENT_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
NUMBERED_ARTIFACT_RE = re.compile(r"^(?P<number>-?\d+)\.\) .+\.md$", re.I)
AMBIGUOUS_MODEL_IDENTITIES = {"chatgpt", "claude", "codex", "gemini", "gpt"}
GPT_FAMILY_ONLY_RE = re.compile(r"^gpt[- ]?5(?:\.\d+)?$", re.I)

class NorthStarError(RuntimeError): pass

def validate_exact_model_identity(value):
    """Reject known family-only or agent-family substitutions on new writes."""
    model=(value or "").strip(); folded=model.casefold()
    if folded=="not recorded": return model
    if not model or folded in AMBIGUOUS_MODEL_IDENTITIES or GPT_FAMILY_ONLY_RE.fullmatch(model) or folded.endswith(" agent"):
        raise NorthStarError("Model identity must be a full exact model name or the honest Not recorded fallback; family-only and agent-family labels are invalid.")
    return model

def now_local(): return datetime.now().astimezone().replace(microsecond=0)
def iso(value): return value.isoformat()
def parse_time(value):
    try: parsed = datetime.fromisoformat(value)
    except ValueError as exc: raise NorthStarError(f"Invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None: raise NorthStarError("Timestamp must include a UTC offset.")
    return parsed

def make_run_id(started): return f"{started.strftime('%Y%m%dT%H%M%S%z')}-{secrets.token_hex(3)}"
def read_artifact(path):
    if not path.is_file(): raise NorthStarError(f"Artifact does not exist: {path}")
    raw = path.read_bytes(); bom = raw.startswith(b"\xef\xbb\xbf")
    if bom: raw = raw[3:]
    try: decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise NorthStarError("Artifact must be UTF-8 encoded.") from exc
    crlf = decoded.count("\r\n"); bare = decoded.count("\n") - crlf
    return decoded.replace("\r\n", "\n"), ("\r\n" if crlf > bare else "\n"), bom

def atomic_write(path, text, newline, bom):
    rendered = text if newline == "\n" else text.replace("\n", newline)
    payload = rendered.encode("utf-8"); payload = (b"\xef\xbb\xbf" + payload) if bom else payload
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try: os.unlink(temp_name)
        except FileNotFoundError: pass
        raise

def encode_state(state):
    raw = json.dumps(state, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")
def decode_state(body):
    matches = list(STATE_RE.finditer(body))
    if len(matches) != 1: raise NorthStarError("Each North Star run must contain exactly one state marker.")
    try: state = json.loads(base64.urlsafe_b64decode(matches[0].group("payload")).decode("utf-8"))
    except Exception as exc: raise NorthStarError("North Star state marker is invalid.") from exc
    if not isinstance(state, dict): raise NorthStarError("North Star state must be an object.")
    normalize_state(state); return state

def parse_runs(text):
    runs=[]
    for match in BLOCK_RE.finditer(text):
        state=decode_state(match.group("body"))
        if state.get("run_id") != match.group("run_id"): raise NorthStarError("Run marker and state run_id do not match.")
        runs.append({"start":match.start(),"end":match.end(),"state":state})
    return runs

def select_run(runs, run_id=None, allow_terminal=False):
    if run_id:
        matches=[r for r in runs if r["state"].get("run_id")==run_id]
        if len(matches)!=1: raise NorthStarError(f"Expected one run_id match, found {len(matches)}.")
        run=matches[0]
    else:
        matches=[r for r in runs if r["state"].get("status") in NONTERMINAL]
        if matches: run=matches[-1]
        elif allow_terminal and runs: run=runs[-1]
        else: raise NorthStarError("No active or paused North Star run was found.")
    if not allow_terminal and run["state"].get("status") not in NONTERMINAL: raise NorthStarError("The selected North Star run is already terminal.")
    return run

def legacy_active_seconds(state):
    frozen=state.get("active_duration_seconds")
    if frozen is not None: return max(0,int(frozen))
    started=parse_time(state["started_at"])
    end=parse_time(state.get("finished_at") or state.get("last_active_at") or state["started_at"])
    elapsed=max(0,int((end-started).total_seconds()))
    return max(0,elapsed-int(state.get("paused_total_seconds",0))-int(state.get("inactive_excluded_total_seconds",0)))

def normalize_state(state):
    if "pursuits" not in state:
        seconds=legacy_active_seconds(state)
        legacy={k:state.get(k) for k in ("paused_total_seconds","inactive_excluded_total_seconds","inactivity_threshold_seconds","inactivity_exclusions","active_duration_seconds") if k in state}
        state["pursuits"]=[]
        if seconds:
            state["pursuits"].append({"number":1,"phase":"Legacy pursuit","summary":"Pursuit recorded before per-turn ledger migration.","started_at":state.get("started_at"),"ended_at":state.get("finished_at") or state.get("last_active_at"),"duration_seconds":seconds})
        state["legacy_timing"]=legacy
        state["pursuit_ledger_migrated"]=True
    clean=[]
    for index,item in enumerate(state.get("pursuits",[]),1):
        if not isinstance(item,dict): raise NorthStarError("Pursuit ledger entries must be objects.")
        row=dict(item); row["number"]=index
        try: row["duration_seconds"]=max(0,int(row.get("duration_seconds",0)))
        except (TypeError,ValueError) as exc: raise NorthStarError("Invalid pursuit duration.") from exc
        row.setdefault("phase","Unspecified"); row.setdefault("summary","Work pursued."); clean.append(row)
    state["pursuits"]=clean; state.setdefault("active_pursuit",None); state.setdefault("provisional",None); state.setdefault("pursuit_corrections",[]); state.setdefault("reopen_count",0)
    state.setdefault("initial_mode","full"); state.setdefault("current_mode",state["initial_mode"]); state.setdefault("mode_transitions",[])
    if "prompt_contract" not in state:
        state["prompt_contract"]={"goal":state.get("objective", ""),"constraints":state.get("constraints",[])+state.get("boundaries",[]),"format":[],"definition_of_done":state.get("verification",[]),"failure":state.get("stop_when",[])}
        state["definition_of_done_complete"]=state.get("verification_complete",[])
    state.setdefault("definition_of_done_complete",[]); state.setdefault("failure_active",[]); state.setdefault("contract_review",None)
    created_day=str(state.get("started_at",""))[:10] or "Not recorded"
    state.setdefault("provenance",{"content_owner":"Uzo","original_writing_agent":"Not recorded","original_writing_llm":"Not recorded","created":created_day,"artifact_role":"Durable North Star pursuit record"})
    state["provenance"].setdefault("original_writing_llm","Not recorded")
    state.setdefault("change_log",[{"date":created_day,"agent":state["provenance"].get("original_writing_agent","Not recorded"),"model":state["provenance"].get("original_writing_llm","Not recorded"),"action":"Created the North Star artifact."}])
    for entry in state["change_log"]:
        entry.setdefault("model","Not recorded")
    state.setdefault("feedback",[])
    clean_feedback=[]
    for index,item in enumerate(state.get("feedback",[]),1):
        if not isinstance(item,dict): raise NorthStarError("Feedback entries must be objects.")
        row=dict(item); row["number"]=index
        row.setdefault("date","Not recorded"); row.setdefault("agent","Not recorded"); row.setdefault("model","Not recorded")
        row.setdefault("descriptor","Feedback"); row.setdefault("body","Not recorded")
        clean_feedback.append(row)
    state["feedback"]=clean_feedback
    state["schema_version"]=7
    for key in ("inactivity_threshold_seconds","inactive_excluded_total_seconds","inactivity_exclusions","paused_total_seconds","active_duration_seconds"):
        state.pop(key,None)

def contract(state):
    normalize_state(state); value=state.get("prompt_contract")
    if not isinstance(value,dict): raise NorthStarError("Prompt Contract state must be an object.")
    for key in ("goal","constraints","format","definition_of_done","failure"):
        if key not in value: raise NorthStarError(f"Prompt Contract is missing {key}.")
    return value

def transition_to_batch(state,reason):
    if state.get("current_mode")=="batch": return False
    if state.get("current_mode")!="full": raise NorthStarError("North Star current mode must be full or batch.")
    state["current_mode"]="batch"; state.setdefault("mode_transitions",[]).append({"from":"full","to":"batch","at":iso(now_local()),"reason":reason})
    state.setdefault("notes",[]).append(f"Mode changed permanently from Full to Batch: {reason}")
    return True

def total_seconds(state): normalize_state(state); return sum(x["duration_seconds"] for x in state["pursuits"])
def latest_pursuit(state): normalize_state(state); return state["pursuits"][-1] if state["pursuits"] else None
def human_duration(value):
    value=max(0,int(value)); days,rem=divmod(value,86400); hours,rem=divmod(rem,3600); mins,secs=divmod(rem,60); parts=[]
    if days: parts.append(f"{days}d")
    if hours or days: parts.append(f"{hours}h")
    if mins or hours or days: parts.append(f"{mins}m")
    parts.append(f"{secs}s"); return " ".join(parts)
def markdown_lines(values,empty="- none"): return [f"- {v}" for v in values] if values else [empty]
def esc_cell(value): return str(value).replace("|","\\|").replace("\n"," ")
def cap_cell(value):
    value=esc_cell(value)
    return value if len(value)<=80 else value[:77].rstrip()+"..."
def pursuit_table(state):
    headers=["#","Batch","Work summary","Duration"]
    body=[[str(x["number"]),cap_cell(x.get("batch") or x.get("phase") or "Unspecified"),cap_cell(x["summary"]),human_duration(x["duration_seconds"])] for x in state["pursuits"]]
    if not body: body=[["-","-","No completed pursuits yet.","0s"]]
    widths=[max(len(headers[i]),*(len(row[i]) for row in body)) for i in range(4)]
    def row(values): return "| "+" | ".join(values[i].ljust(widths[i]) for i in range(4))+" |"
    return [row(headers),"|"+"|".join("-"*(w+2) for w in widths)+"|",*(row(values) for values in body)]

def provenance_section(state):
    normalize_state(state)
    provenance=state["provenance"]
    headers=["Field","Value"]
    body=[
        ["Content owner",cap_cell(provenance.get("content_owner") or "Not recorded")],
        ["Original writing agent",cap_cell(provenance.get("original_writing_agent") or "Not recorded")],
        ["Original writing LLM",cap_cell(provenance.get("original_writing_llm") or "Not recorded")],
        ["Created",cap_cell(provenance.get("created") or "Not recorded")],
        ["Artifact role",cap_cell(provenance.get("artifact_role") or "Durable North Star pursuit record")],
    ]
    widths=[max(len(headers[i]),*(len(row[i]) for row in body)) for i in range(2)]
    def row(values): return "| "+" | ".join(values[i].ljust(widths[i]) for i in range(2))+" |"
    table=[row(headers),"|"+"|".join("-"*(w+2) for w in widths)+"|",*(row(values) for values in body)]
    return "\n".join(["## Agent Provenance","",*table])

def append_change(state,agent,action,model=None,scope=None):
    agent=(agent or "").strip()
    if not agent: raise NorthStarError("A truthful --acting-agent is required for this material North Star change.")
    exact_model=validate_exact_model_identity((model or "").strip() or "Not recorded")
    state.setdefault("change_log",[]).append({"date":now_local().strftime("%Y-%m-%d-%H:%M:%S"),"agent":agent,"model":exact_model,"action":action,"scope":(scope or "").strip() or None})

def change_log_lines(state):
    normalize_state(state)
    entries=state.get("change_log") or []
    lines=["## Agent Change Log",""]
    if not entries: return [*lines,"- Not recorded"]
    headers=["Date and Time","Agent","Model","Action","Scope"]
    body=[]
    for entry in entries:
        action=str(entry.get("action") or "Material North Star change.")
        scope=entry.get("scope") or action
        body.append([
            cap_cell(entry.get("date") or "Not recorded"),
            cap_cell(entry.get("agent") or "Not recorded"),
            cap_cell(entry.get("model") or "Not recorded"),
            cap_cell(action.split(".")[0].split(";")[0].strip() or "Updated"),
            cap_cell(scope),
        ])
    widths=[max(len(headers[i]),*(len(row[i]) for row in body)) for i in range(5)]
    def row(values): return "| "+" | ".join(values[i].ljust(widths[i]) for i in range(5))+" |"
    return [*lines,row(headers),"|"+"|".join("-"*(w+2) for w in widths)+"|",*(row(values) for values in body)]

def feedback_section_lines(state):
    normalize_state(state)
    entries=state.get("feedback") or []
    lines=["## Feedback Section",""]
    if not entries:
        return [*lines,"_No feedback yet. Use `feedback-add` to append a numbered `### Feedback N` subsection._"]
    for entry in entries:
        lines.append(f"### Feedback {entry['number']} — {entry.get('date') or 'Not recorded'} — {entry.get('agent') or 'Not recorded'} — {entry.get('descriptor') or 'Feedback'}")
        lines.append("")
        lines.append(str(entry.get("body") or "Not recorded"))
        lines.append("")
    return [line for line in lines[:-1]]

def append_feedback(state,agent,descriptor,body,model=None):
    normalize_state(state)
    agent=(agent or "").strip()
    if not agent: raise NorthStarError("A truthful --acting-agent is required to append feedback.")
    body=(body or "").strip()
    if not body: raise NorthStarError("Feedback requires a non-empty --body.")
    exact_model=validate_exact_model_identity((model or "").strip() or "Not recorded")
    state.setdefault("feedback",[]).append({
        "number":len(state.get("feedback",[]))+1,
        "date":now_local().strftime("%Y-%m-%d-%H:%M:%S"),
        "agent":agent,
        "model":exact_model,
        "descriptor":(descriptor or "").strip() or "Feedback",
        "body":body,
    })

def normalize_human_sections(text,state):
    cleaned=PROVENANCE_SECTION_RE.sub("",text)
    cleaned=CHANGE_LOG_SECTION_RE.sub("",cleaned).rstrip("\n")
    lifecycle=list(re.finditer(r"(?m)^North Star lifecycle: [^\n]*$",cleaned))
    if len(lifecycle)!=1: raise NorthStarError("North Star must contain exactly one lifecycle line before Agent Provenance.")
    match=lifecycle[0]
    return f"{cleaned[:match.end()]}\n\n{provenance_section(state)}\n\n{cleaned[match.end():].lstrip()}"

def validate_artifact_layout(text):
    if len(re.findall(r"(?m)^## Agent Provenance[ \t]*$",text))!=1: raise NorthStarError("North Star must contain exactly one Agent Provenance section.")
    if len(re.findall(r"(?m)^## Agent Change Log[ \t]*$",text))!=1: raise NorthStarError("North Star must contain exactly one Agent Change Log section.")
    if len(re.findall(r"(?m)^## Feedback Section[ \t]*$",text))!=1: raise NorthStarError("North Star must contain exactly one Feedback Section.")
    lifecycle=list(re.finditer(r"(?m)^North Star lifecycle: [^\n]*$",text))
    provenance=re.search(r"(?m)^## Agent Provenance[ \t]*$",text)
    north=re.search(r"(?m)^## North Star[ \t]*$",text)
    feedback=re.search(r"(?m)^## Feedback Section[ \t]*$",text)
    change_log=re.search(r"(?m)^## Agent Change Log[ \t]*$",text)
    state_marker=STATE_RE.search(text)
    if len(lifecycle)!=1 or not all((provenance,north,feedback,change_log,state_marker)): raise NorthStarError("North Star mandatory structure is incomplete.")
    if text[lifecycle[0].end():provenance.start()].strip(): raise NorthStarError("Agent Provenance must appear immediately after the North Star lifecycle line.")
    if not (lifecycle[0].start()<provenance.start()<north.start()<feedback.start()<change_log.start()<state_marker.start()): raise NorthStarError("North Star sections are not in the mandatory lifecycle, provenance, content, feedback, change-log, machine-state order.")
    if re.search(r"(?m)^#{1,6} ",text[change_log.end():state_marker.start()]): raise NorthStarError("Agent Change Log must be the final human-readable section.")
    required_rows=("Content owner","Original writing agent","Original writing LLM","Created","Artifact role")
    provenance_text=text[provenance.start():north.start()]
    if not all(f"| {field}" in provenance_text for field in required_rows): raise NorthStarError("Agent Provenance must use the mandatory Field/Value table.")

def render_block(state):
    normalize_state(state)
    status={"active":"IN PROGRESS","in_progress":"IN PROGRESS","paused":"PAUSED","finalized":"FINALIZED","reached":"FINALIZED","ended":"ENDED"}.get(str(state["status"]),str(state["status"]).upper())
    pc=contract(state); completed=set(state.get("definition_of_done_complete",[])); dod=pc.get("definition_of_done",[]); active_failures=set(state.get("failure_active",[]))
    checklist=[f"- [{'x' if i in completed else ' '}] {item}" for i,item in enumerate(dod,1)] or ["- [ ] No Definition of Done criteria recorded"]
    failures=[f"- [{'!' if i in active_failures else ' '}] {item}" for i,item in enumerate(pc.get("failure",[]),1)] or ["- none recorded"]
    rows=pursuit_table(state)
    active=state.get("active_pursuit")
    active_label=(f"Pursuit {active['number']} open since {active['started_at']}" if active else "None")
    prov=state.get("provisional")
    prov_label=(f"Open since {prov['started_at']}" if prov else "None")
    lines=[RUN_BEGIN.format(run_id=state["run_id"]),f"### {state['indicator']} North Star Run `{state['run_id']}`","",f"- **Mode:** `north-star`",f"- **Status:** {status}",f"- **Indicator:** {state['indicator']} (`{state['indicator_index']}`)",f"- **Initial run mode:** {str(state['initial_mode']).title()}",f"- **Current run mode:** {str(state['current_mode']).title()}",f"- **Started:** {state['started_at']}",f"- **Finished:** {state.get('finished_at') or chr(0x2014)}",f"- **Formal pause:** {'Yes' if state.get('status')=='paused' else 'No'}",f"- **Open pursuit:** {active_label}",f"- **Provisional timer:** {prov_label}",f"- **Completed pursuits:** {len(state['pursuits'])}",f"- **Grand total active pursuit time:** {human_duration(total_seconds(state))}",f"- **Current batch:** {state.get('current_batch') or 'Not recorded'}",f"- **Next action:** {state.get('next_action') or 'Not recorded'}","","#### Pursuit","",state.get("pursuit") or "Not recorded.","","#### Prompt Contract","","##### GOAL","",pc["goal"],"","##### CONSTRAINTS","",*markdown_lines(pc["constraints"]),"","##### FORMAT","",*markdown_lines(pc["format"]),"","##### DEFINITION OF DONE","",*checklist,"","##### FAILURE","",*failures,"","#### Mode Transition History","",*markdown_lines([f"{x['at']}: {x['from'].title()} -> {x['to'].title()} — {x['reason']}" for x in state.get("mode_transitions",[])]),"","#### Active Pursuit Log","",*rows,"","#### Evidence","",*markdown_lines(state.get("evidence",[])),"","#### Checkpoint Notes","",*markdown_lines(state.get("notes",[])),"",*feedback_section_lines(state),"",*change_log_lines(state),"",f"{STATE_PREFIX}{encode_state(state)}{STATE_SUFFIX}",RUN_END]
    return "\n".join(lines)

def append_run(text,block,state):
    text=normalize_human_sections(text,state)
    headings=list(re.finditer(r"(?m)^## North Star[ \t]*$",text))
    if len(headings)>1: raise NorthStarError("Artifact contains multiple exact '## North Star' headings.")
    if not headings: return f"{text.rstrip(chr(10))}\n\n{SECTION_HEADING}\n\n{block}\n"
    h=headings[0]
    if text[h.end():].strip(): raise NorthStarError("Initializing a populated North Star heading requires manual structural review.")
    return f"{text[:h.end()].rstrip(chr(10))}\n\n{block}\n"
def replace_run(text,run,state):
    without=(text[:run["start"]]+text[run["end"]:]).rstrip("\n")
    without=normalize_human_sections(without,state)
    return f"{without}\n\n{render_block(state)}\n"
def load_context(artifact):
    path=Path(artifact).expanduser().resolve(); text,newline,bom=read_artifact(path); return path,text,newline,bom,parse_runs(text)
def save_context(path,text,newline,bom):
    if parse_runs(text):
        if not text.rstrip().endswith(RUN_END): raise NorthStarError("North Star machine state must be the final nonblank content.")
        validate_artifact_layout(text)
    atomic_write(path,text,newline,bom)
def validate_segment(value,label):
    cleaned=value.strip()
    if not cleaned or cleaned in {".",".."} or SAFE_SEGMENT_RE.search(cleaned) or cleaned.endswith((" ",".")): raise NorthStarError(f"{label} is not a safe filename segment.")
    return cleaned
def numbered_values(directory):
    if not directory.is_dir(): return []
    return [int(m.group("number")) for p in directory.iterdir() if p.is_file() and (m:=NUMBERED_ARTIFACT_RE.match(p.name))]
def number_is_owned(directory,number): return directory.is_dir() and any(p.is_file() and p.name.startswith(f"{number}.) ") for p in directory.iterdir())
def artifact_shell(subject,topic,created,state): return f"# {topic}\n\nStatus: IN PROGRESS \u2014 created {created.date().isoformat()}.\n\nNorth Star lifecycle: IN PROGRESS since {iso(created)}.\n\n{provenance_section(state)}\n\n**Subject:** {subject}  \n**Topic:** {topic}\n"
def exclusive_write(path,text,newline="\n",bom=False):
    if parse_runs(text):
        if not text.rstrip().endswith(RUN_END): raise NorthStarError("North Star machine state must be the final nonblank content.")
        validate_artifact_layout(text)
    rendered=text if newline=="\n" else text.replace("\n",newline); payload=rendered.encode("utf-8"); payload=(b"\xef\xbb\xbf"+payload) if bom else payload
    try:
        with path.open("xb") as handle: handle.write(payload); handle.flush(); os.fsync(handle.fileno())
    except FileExistsError as exc: raise NorthStarError(f"Refusing to overwrite existing artifact: {path}") from exc

def rewrite_header(text,status,when):
    old=re.compile(r"(?m)^Status: (?:IN PROGRESS|FINALIZED|ENDED)[^\n]*$"); life=re.compile(r"(?m)^North Star lifecycle: (?:IN PROGRESS|FINALIZED|ENDED)[^\n]*$")
    sm=list(old.finditer(text)); lm=list(life.finditer(text))
    if len(sm)!=1 or len(lm)!=1: raise NorthStarError("North Star must contain one recognized status and lifecycle line.")
    created=re.search(r"created (\d{4}-\d{2}-\d{2})",sm[0].group(0)); created_date=created.group(1) if created else "unknown"; day=when.date().isoformat()
    if status=="IN PROGRESS": s=f"Status: IN PROGRESS \u2014 created {created_date}, reopened {day}."; l=f"North Star lifecycle: IN PROGRESS since {iso(when)}."
    elif status=="FINALIZED": s=f"Status: FINALIZED \u2705 \u2014 created {created_date}, finalized {day}."; l=f"North Star lifecycle: FINALIZED on {day}."
    else: s=f"Status: ENDED \u26a0\ufe0f \u2014 created {created_date}, ended {day}."; l=f"North Star lifecycle: ENDED on {day}."
    return life.sub(l,old.sub(s,text,count=1),count=1)

def command_init(args):
    path,text,newline,bom,runs=load_context(args.artifact)
    if any(r["state"].get("status") in NONTERMINAL for r in runs): raise NorthStarError("Artifact already has an active or paused North Star run.")
    current=now_local(); started=parse_time(args.started_at) if args.started_at else current
    if started>current: raise NorthStarError("North Star start time cannot be in the future.")
    idx=secrets.randbelow(len(INDICATORS)) if args.indicator_index is None else args.indicator_index
    complete=set(args.verify_complete or []); maximum=len(args.definition_of_done or [])
    if any(i<1 or i>maximum for i in complete): raise NorthStarError("Definition of Done index is outside the checklist.")
    writing_llm=validate_exact_model_identity(getattr(args,"writing_llm",None) or "Not recorded")
    state={"schema_version":7,"run_id":make_run_id(started),"pursuit":(args.pursuit or "").strip(),"initial_mode":args.mode,"current_mode":args.mode,"mode_transitions":[],"prompt_contract":{"goal":args.goal.strip(),"constraints":args.constraint or [],"format":args.format or [],"definition_of_done":args.definition_of_done or [],"failure":args.failure or []},"definition_of_done_complete":sorted(complete),"failure_active":[],"contract_review":None,"provenance":{"content_owner":args.content_owner,"original_writing_agent":args.writing_agent,"original_writing_llm":writing_llm,"created":started.date().isoformat(),"artifact_role":args.artifact_role},"change_log":[{"date":started.strftime("%Y-%m-%d-%H:%M:%S"),"agent":args.writing_agent,"model":writing_llm,"action":"Created the North Star artifact.","scope":"Initial authoring"}],"indicator_index":idx,"indicator":INDICATORS[idx],"status":"in_progress","started_at":iso(started),"finished_at":None,"current_batch":args.batch or "Activation","next_action":args.next_action or "Begin pursuit","evidence":args.evidence or [],"notes":args.note or [],"pursuits":[],"active_pursuit":None,"provisional":None,"pursuit_corrections":[],"reopen_count":0,"pursuit_ledger_migrated":True}
    save_context(path,append_run(text,render_block(state),state),newline,bom); return state

def command_create(args):
    root=Path(args.workspace_root).expanduser().resolve(); subject=validate_segment(args.subject,"Subject"); topic=validate_segment(args.topic,"Topic")
    if not root.is_dir(): raise NorthStarError(f"Workspace root does not exist: {root}")
    live=root/"Archive"/"Live"/"North Stars"/subject; hist=root/"Archive"/"Historical"/"North Stars"/subject; live.mkdir(parents=True,exist_ok=True)
    prev=max(numbered_values(live)+numbered_values(hist),default=0); number=prev+1
    if number_is_owned(live,number) or number_is_owned(hist,number): raise NorthStarError(f"Number {number} is already owned.")
    artifact=live/f"{number}.) {topic}_in_progress.md"; started=parse_time(args.started_at) if args.started_at else now_local()
    writing_llm=validate_exact_model_identity(getattr(args,"writing_llm",None) or "Not recorded")
    seed={"started_at":iso(started),"provenance":{"content_owner":args.content_owner,"original_writing_agent":args.writing_agent,"original_writing_llm":writing_llm,"created":started.date().isoformat(),"artifact_role":args.artifact_role},"change_log":[]}
    exclusive_write(artifact,artifact_shell(subject,topic,started,seed)); args.artifact=str(artifact)
    try: state=command_init(args)
    except BaseException:
        artifact.unlink(missing_ok=True); raise
    state["artifact_path"]=str(artifact); state["previous_max"]=prev; return state

def mutate(args,fn,allow_terminal=False,change_action=None):
    path,text,newline,bom,runs=load_context(args.artifact); run=select_run(runs,args.run_id,allow_terminal=allow_terminal); state=dict(run["state"]); normalize_state(state); fn(state)
    if change_action: append_change(state,getattr(args,"acting_agent",None),change_action,getattr(args,"acting_llm",None))
    save_context(path,replace_run(text,run,state),newline,bom); return state

def command_feedback_add(args):
    return mutate(args,lambda state: append_feedback(state,getattr(args,"acting_agent",None),args.descriptor,args.body,getattr(args,"acting_llm",None)),change_action="Appended a Feedback Section entry.")

def command_pursuit_start(args):
    def fn(state):
        if state["status"]=="paused": raise NorthStarError("Resume the North Star before starting a pursuit.")
        if state.get("active_pursuit"): raise NorthStarError("A pursuit is already open; stop or recover it first.")
        started=parse_time(args.started_at) if args.started_at else now_local()
        if started>now_local(): raise NorthStarError("Pursuit start cannot be in the future.")
        if state.get("current_mode")=="full" and state.get("pursuits"): transition_to_batch(state,"Another pursuit is beginning after the initial Full Mode pursuit.")
        state["active_pursuit"]={"number":len(state["pursuits"])+1,"batch":args.batch or state.get("current_batch") or state.get("current_mode","full").title(),"summary":args.summary.strip(),"started_at":iso(started)}
        state["current_batch"]=args.batch or state.get("current_batch"); state["next_action"]="Complete this agent turn and close its pursuit before the final response."
    return mutate(args,fn)

def command_pursuit_stop(args):
    def fn(state):
        active=state.get("active_pursuit")
        if not active: raise NorthStarError("No pursuit is open.")
        ended=parse_time(args.ended_at) if args.ended_at else now_local(); started=parse_time(active["started_at"])
        if ended<started or ended>now_local(): raise NorthStarError("Pursuit end must be between its start and now.")
        item=dict(active); item["ended_at"]=iso(ended); item["duration_seconds"]=int((ended-started).total_seconds())
        if args.summary: item["summary"]=args.summary.strip()
        if args.batch: item["batch"]=args.batch
        state["pursuits"].append(item); state["active_pursuit"]=None; state["provisional"]=None
        if args.note: state.setdefault("notes",[]).append(args.note)
        state["next_action"]="Await the next user turn or finalize when verification is complete."
    return mutate(args,fn,change_action="Completed and recorded a North Star pursuit.")

def command_pursuit_remove(args):
    def fn(state):
        if state.get("active_pursuit"): raise NorthStarError("Close or recover the open pursuit before correcting the ledger.")
        target=next((p for p in state["pursuits"] if p["number"]==args.number),None)
        if not target: raise NorthStarError(f"Pursuit {args.number} does not exist.")
        state["pursuits"]=[p for p in state["pursuits"] if p is not target]
        for i,p in enumerate(state["pursuits"],1): p["number"]=i
        state["pursuit_corrections"].append({"removed_number":args.number,"removed_entry":target,"reason":args.reason,"corrected_at":iso(now_local()),"renumbered":True})
        state.setdefault("notes",[]).append(f"Removed pursuit {args.number} and renumbered the ledger: {args.reason}")
    return mutate(args,fn,change_action="Corrected the North Star pursuit ledger.")

def command_provisional_start(args):
    def fn(state):
        if state["status"]=="paused": raise NorthStarError("Resume the North Star before starting provisional timing.")
        if state["status"] in ("finalized","ended"): raise NorthStarError("Cannot start provisional timing on a terminal North Star.")
        if state.get("active_pursuit"): raise NorthStarError("Close the authoritative pursuit before starting a provisional timer.")
        if state.get("provisional"): return state
        state["provisional"]={"started_at":iso(parse_time(args.started_at) if args.started_at else now_local()),"pursuit_number":len(state["pursuits"])+1}
        state.setdefault("notes",[]).append("Provisional turn timer opened.")
    return mutate(args,fn)

def command_provisional_discard(args):
    def fn(state):
        if state.get("provisional"):
            state.setdefault("notes",[]).append("Provisional timer discarded without a pursuit entry.")
            state["provisional"]=None
    return mutate(args,fn)

def command_provisional_commit(args):
    def fn(state):
        prov=state.get("provisional")
        if not prov: raise NorthStarError("No provisional timer is open.")
        if state.get("active_pursuit"): raise NorthStarError("Close the authoritative pursuit before committing a provisional fallback.")
        ended=parse_time(args.ended_at) if args.ended_at else now_local(); started=parse_time(prov["started_at"])
        if ended<started or ended>now_local(): raise NorthStarError("Provisional fallback end must be between its start and now.")
        if state.get("current_mode")=="full" and state.get("pursuits"): transition_to_batch(state,"Another pursuit is being recorded after the initial Full Mode pursuit.")
        item={"number":len(state["pursuits"])+1,"batch":args.batch or state.get("current_batch") or state.get("current_mode","full").title(),"summary":args.summary.strip(),"started_at":iso(started),"ended_at":iso(ended),"duration_seconds":int((ended-started).total_seconds()),"timing_source":"provisional_fallback"}
        state["pursuits"].append(item); state["provisional"]=None
        state.setdefault("notes",[]).append("Provisional timer committed as disclosed full-turn fallback pursuit.")
        state["next_action"]="Await the next user turn or finalize when verification is complete."
    return mutate(args,fn,change_action="Recorded a disclosed fallback pursuit.")

def command_checkpoint(args):
    def fn(state):
        if state["status"]=="paused": raise NorthStarError("Resume before checkpointing.")
        if args.batch: state["current_batch"]=args.batch
        if args.next_action: state["next_action"]=args.next_action
        if args.note: state.setdefault("notes",[]).append(args.note)
        if args.another_iteration: transition_to_batch(state,args.another_iteration)
        complete=set(state.get("definition_of_done_complete",[])); maximum=len(contract(state).get("definition_of_done",[]))
        for i in args.verify_complete or []:
            if i<1 or i>maximum: raise NorthStarError(f"Definition of Done index {i} is outside 1..{maximum}.")
            complete.add(i)
        state["definition_of_done_complete"]=sorted(complete)
        if args.clear_failures:
            state["failure_active"]=[]
        elif args.failure_active is not None:
            maximum_failure=len(contract(state).get("failure",[])); active=set(args.failure_active)
            if any(i<1 or i>maximum_failure for i in active): raise NorthStarError(f"Failure index is outside 1..{maximum_failure}.")
            state["failure_active"]=sorted(active)
    return mutate(args,fn,change_action="Checkpointed North Star progress and verification state.")

def command_refine(args):
    def fn(state):
        pc=contract(state); material=False
        if args.goal: pc["goal"]=args.goal.strip(); material=True
        if args.pursuit is not None: state["pursuit"]=args.pursuit.strip()
        if args.constraint is not None: pc["constraints"]=args.constraint; material=True
        if args.format is not None: pc["format"]=args.format; material=True
        if args.definition_of_done is not None: pc["definition_of_done"]=args.definition_of_done; state["definition_of_done_complete"]=[]; material=True
        if args.failure is not None: pc["failure"]=args.failure; state["failure_active"]=[]; material=True
        if material and state.get("pursuits"): transition_to_batch(state,"The North Star Prompt Contract was materially refined after pursuit work began.")
        complete=set(state.get("definition_of_done_complete",[])); maximum=len(pc.get("definition_of_done",[]))
        for i in args.verify_complete or []:
            if i<1 or i>maximum: raise NorthStarError(f"Definition of Done index {i} is outside 1..{maximum}.")
            complete.add(i)
        state["definition_of_done_complete"]=sorted(complete); state["prompt_contract"]=pc
        if args.batch: state["current_batch"]=args.batch
        if args.next_action: state["next_action"]=args.next_action
        if getattr(args,"writing_llm",None):
            current=(state.get("provenance",{}).get("original_writing_llm") or "Not recorded").strip()
            if current and current!="Not recorded": raise NorthStarError("Original writing LLM is immutable once recorded; it cannot be rewritten.")
            state.setdefault("provenance",{})["original_writing_llm"]=validate_exact_model_identity(args.writing_llm)
        if args.note: state.setdefault("notes",[]).append(f"Refined: {args.note}")
    return mutate(args,fn,change_action="Refined the North Star scope or Prompt Contract.")

def command_pause(args):
    def fn(state):
        if state["status"]=="paused": raise NorthStarError("The North Star is already paused.")
        if state.get("active_pursuit"): raise NorthStarError("Close the current pursuit before formally pausing.")
        if state.get("provisional"): raise NorthStarError("Close or discard the provisional timer before pausing.")
        state["status"]="paused"; state["paused_at"]=iso(now_local()); state["next_action"]="Resume North Star to continue."
        if args.reason: state.setdefault("notes",[]).append(f"Paused with user agreement: {args.reason}")
    return mutate(args,fn,change_action="Paused the North Star with user agreement.")
def command_resume(args):
    def fn(state):
        if state["status"]!="paused": raise NorthStarError("The North Star is not paused.")
        state["status"]="in_progress"; state["paused_at"]=None; state["next_action"]="Start a new pursuit for the next agent turn."; state.setdefault("notes",[]).append("Resumed with user direction.")
    return mutate(args,fn,change_action="Resumed the North Star with user direction.")
def command_recover(args):
    def fn(state):
        active=state.get("active_pursuit")
        if active:
            state["pursuit_corrections"].append({"discarded_open_pursuit":active,"reason":args.note or "Interrupted before the turn closed.","corrected_at":iso(now_local())}); state["active_pursuit"]=None
            state.setdefault("notes",[]).append("Recovered by discarding the interrupted open pursuit; no unverified duration was counted.")
        prov=state.get("provisional")
        if prov:
            state.setdefault("notes",[]).append(f"Recovered by discarding open provisional timer from {prov['started_at']}; no fallback pursuit was manufactured.")
            state["provisional"]=None
        if not active and not prov and args.note: state.setdefault("notes",[]).append(f"Recovery note: {args.note}")
    return mutate(args,fn,change_action="Recovered interrupted North Star timing state.")

def path_parts(path):
    subject=path.parent; north=subject.parent; phase=north.parent; archive=phase.parent
    if north.name.lower()!="north stars" or archive.name.lower()!="archive": raise NorthStarError("Artifact is not under Archive/<Lifecycle>/North Stars/<Subject>/.")
    return subject,north,phase,archive

def command_reopen(args):
    path,text,newline,bom,runs=load_context(args.artifact)
    if not path.name.endswith(("_finalized.md","_ended.md")): raise NorthStarError("Reopen requires a finalized or ended artifact.")
    subject,north,phase,archive=path_parts(path)
    if phase.name.lower()!="historical": raise NorthStarError("Reopen requires an artifact under Archive/Historical.")
    run=select_run(runs,args.run_id,allow_terminal=True); state=dict(run["state"]); normalize_state(state)
    if state.get("active_pursuit"): raise NorthStarError("Terminal artifact unexpectedly has an open pursuit.")
    current=now_local(); state["status"]="in_progress"; state["finished_at"]=None; state["reopen_count"]=int(state.get("reopen_count",0))+1; transition_to_batch(state,"A terminal North Star was reopened for another iteration."); state["current_batch"]=args.batch or "Reopened"; state["next_action"]=args.next_action or "Start the next pursuit."; state.setdefault("notes",[]).append(f"Reopened on {current.date().isoformat()}; existing pursuit ledger preserved.")
    append_change(state,args.acting_agent,"Reopened the terminal North Star for another Batch iteration.")
    updated=rewrite_header(replace_run(text,run,state),"IN PROGRESS",current); live=archive/"Live"/"North Stars"/subject.name; live.mkdir(parents=True,exist_ok=True); stem=re.sub(r"_(?:finalized|ended)\.md$","_in_progress.md",path.name); target=live/stem; exclusive_write(target,updated,newline,bom)
    try: path.unlink()
    except OSError:
        target.unlink(missing_ok=True); raise
    state["artifact_path"]=str(target); return state

def terminal(args,status):
    path,text,newline,bom,runs=load_context(args.artifact)
    if not path.name.endswith("_in_progress.md"): raise NorthStarError("Terminal transition requires an _in_progress.md artifact.")
    subject,north,phase,archive=path_parts(path)
    if phase.name.lower()!="live": raise NorthStarError("Terminal transition requires Archive/Live.")
    run=select_run(runs,args.run_id); state=dict(run["state"]); normalize_state(state)
    if state.get("active_pursuit"): raise NorthStarError("Close the current pursuit before a terminal transition.")
    if state.get("provisional"): raise NorthStarError("Close or discard the provisional timer before a terminal transition.")
    if status=="finalized":
        pc=contract(state); complete=set(state.get("definition_of_done_complete",[])); maximum=len(pc.get("definition_of_done",[]))
        for i in getattr(args,"verify_complete",None) or []:
            if i<1 or i>maximum: raise NorthStarError(f"Definition of Done index {i} is outside 1..{maximum}.")
            complete.add(i)
        state["definition_of_done_complete"]=sorted(complete); missing=sorted(set(range(1,maximum+1))-complete)
        if not pc.get("definition_of_done"): raise NorthStarError("A North Star needs Definition of Done criteria to finalize.")
        if missing: raise NorthStarError("Cannot finalize; unchecked Definition of Done items: "+", ".join(map(str,missing)))
        if state.get("failure_active"): raise NorthStarError("Cannot finalize; active Failure conditions: "+", ".join(map(str,state["failure_active"])))
        if not args.constraints_verified: raise NorthStarError("Cannot finalize until Prompt Contract constraints are verified.")
        if not args.format_verified: raise NorthStarError("Cannot finalize until Prompt Contract format is verified.")
        if not args.failure_reviewed: raise NorthStarError("Cannot finalize until Prompt Contract Failure conditions are reviewed.")
        state["contract_review"]={"reviewed_at":iso(now_local()),"constraints_verified":True,"format_verified":True,"failure_reviewed":True,"definition_of_done_complete":sorted(complete),"evidence":getattr(args,"evidence",None) or []}
    current=now_local(); state["status"]=status; state["finished_at"]=iso(current); state["current_batch"]="Finalized" if status=="finalized" else "Ended"; state["next_action"]="None \u2014 North Star finalized." if status=="finalized" else "None \u2014 North Star ended."
    if getattr(args,"evidence",None): state["evidence"]=state.get("evidence",[])+args.evidence
    if getattr(args,"note",None): state.setdefault("notes",[]).append(args.note)
    append_change(state,args.acting_agent,"Finalized the North Star and moved it to Historical." if status=="finalized" else "Ended the North Star and moved it to Historical.")
    updated=rewrite_header(replace_run(text,run,state),"FINALIZED" if status=="finalized" else "ENDED",current); hist=archive/"Historical"/"North Stars"/subject.name; hist.mkdir(parents=True,exist_ok=True); suffix="_finalized.md" if status=="finalized" else "_ended.md"; target=hist/(path.name[:-len("_in_progress.md")]+suffix); exclusive_write(target,updated,newline,bom)
    try: path.unlink()
    except OSError:
        target.unlink(missing_ok=True); raise
    state["artifact_path"]=str(target); return state
def command_finalize(args): return terminal(args,"finalized")
def command_end(args): return terminal(args,"ended")
def command_finish(args): raise NorthStarError("The finish command is retired; use finalize or end after closing the current pursuit.")
def command_status(args):
    _,_,_,_,runs=load_context(args.artifact); return dict(select_run(runs,args.run_id,allow_terminal=True)["state"])

def command_format_receipt(args):
    """Output production user-facing receipt text for testable output contracts."""
    state = command_status(args)
    normalize_state(state)
    rtype = args.type
    # All receipt types refuse open timing state
    if state.get("active_pursuit"):
        raise NorthStarError("Close the authoritative pursuit before producing receipt output.")
    if state.get("provisional"):
        raise NorthStarError("Close or discard the provisional timer before producing receipt output.")
    if rtype == "timing-statement":
        latest = latest_pursuit(state)
        if not latest:
            raise NorthStarError("No completed pursuit available for timing statement.")
        total = human_duration(total_seconds(state))
        dur = human_duration(latest["duration_seconds"])
        summary = latest["summary"]
        num = latest["number"]
        print(f"Pursuit {num}: {dur} — {summary}. Grand total: {total}.")
    elif rtype == "fallback-disclosure":
        latest = latest_pursuit(state)
        if not latest or latest.get("timing_source") != "provisional_fallback":
            raise NorthStarError("Latest pursuit is not a provisional fallback.")
        print("Full-turn fallback scoping was used for this pursuit — precise authoritative timing was missed.")
    elif rtype == "mode-footer":
        indicator=state.get("indicator","?"); status=state.get("status"); mode=str(state.get("current_mode","full")).upper()
        if status in ("in_progress","active"): print(f"Mode = {indicator} North Star ({mode})")
        elif status=="paused": print(f'Mode = {indicator} North Star ({mode}, PAUSED — say "resume North Star" to continue)')
        elif status in ("finalized","reached"): print(f"Mode = {indicator} North Star (FINALIZED THIS TURN)")
        else: raise NorthStarError("A mode footer is unavailable for this North Star status.")
    elif rtype == "prompt-contract":
        pc=contract(state)
        print("GOAL: "+pc["goal"]+"\n\nCONSTRAINTS:\n"+"\n".join(f"- {x}" for x in pc["constraints"])+"\n\nFORMAT:\n"+"\n".join(f"- {x}" for x in pc["format"])+"\n\nDEFINITION OF DONE:\n"+"\n".join(f"- {x}" for x in pc["definition_of_done"])+"\n\nFAILURE:\n"+"\n".join(f"- {x}" for x in pc["failure"]))
    elif rtype == "finalizer-receipt":
        if state.get("status") not in ("finalized", "reached"):
            raise NorthStarError("North Star is not finalized.")
        subject = args.subject
        if not subject:
            raise NorthStarError("--subject is required for finalizer-receipt.")
        import re
        m = re.search(r"^(\d+)\.\) ", Path(args.artifact).name)
        n_num = m.group(1) if m else "?"
        latest = latest_pursuit(state)
        if not latest:
            raise NorthStarError("No completed pursuit for finalizer receipt.")
        total = human_duration(total_seconds(state))
        dur = human_duration(latest["duration_seconds"])
        summary = latest["summary"]
        p_num = latest["number"]
        resolved = Path(args.artifact).resolve().as_posix()
        # Application-valid absolute Markdown link with angle brackets for spaces
        link = f"[{subject} North Star {n_num}](<{resolved}>)"
        print(f"North Star {n_num} was verified and finalized. Pursuit {p_num}: {dur} — {summary}. Grand total: {total}. {link}")
    else:
        raise NorthStarError(f"Unknown receipt type: {rtype}")
    return state

def print_result(state,as_json=False):
    normalize_state(state); latest=latest_pursuit(state); output=dict(state); output["active_pursuit_seconds_current"]=total_seconds(state); output["active_pursuit_time_current"]=human_duration(total_seconds(state)); output["grand_total_seconds"]=total_seconds(state); output["grand_total_time"]=human_duration(total_seconds(state)); output["latest_pursuit"]=latest
    if as_json: print(json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)); return
    for key in ("artifact_path","previous_max"):
        if state.get(key) is not None: print(f"{key}={state[key]}")
    print(f"run_id={state['run_id']}\nstatus={state['status']}\nindicator={state['indicator']}\nindicator_index={state['indicator_index']}")
    print(f"open_pursuit={state.get('active_pursuit') is not None}\ncompleted_pursuits={len(state['pursuits'])}")
    print(f"provisional_open={state.get('provisional') is not None}")
    if latest: print(f"latest_pursuit_number={latest['number']}\nlatest_pursuit_time={human_duration(latest['duration_seconds'])}\nlatest_pursuit_summary={latest['summary']}")
    print(f"grand_total_active_pursuit_time={human_duration(total_seconds(state))}\ninitial_mode={state.get('initial_mode') or ''}\ncurrent_mode={state.get('current_mode') or ''}\ncurrent_batch={state.get('current_batch') or ''}\nnext_action={state.get('next_action') or ''}")

def add_common(p): p.add_argument("--artifact",required=True); p.add_argument("--run-id")
def add_actor(p): p.add_argument("--acting-agent",required=True); p.add_argument("--acting-llm")
def init_args(p):
    p.add_argument("--writing-agent",required=True); p.add_argument("--writing-llm"); p.add_argument("--content-owner",default="Uzo"); p.add_argument("--artifact-role",default="Durable North Star pursuit record"); p.add_argument("--goal",required=True); p.add_argument("--pursuit"); p.add_argument("--mode",choices=("full","batch"),default="full"); p.add_argument("--definition-of-done",action="append"); p.add_argument("--verify-complete",type=int,action="append"); p.add_argument("--constraint",action="append"); p.add_argument("--format",action="append"); p.add_argument("--failure",action="append"); p.add_argument("--batch"); p.add_argument("--next-action"); p.add_argument("--started-at"); p.add_argument("--evidence",action="append"); p.add_argument("--note",action="append"); p.add_argument("--indicator-index",type=int,choices=range(len(INDICATORS)),metavar="0..7")
def build_parser():
    parser=argparse.ArgumentParser(description="Maintain artifact-backed North Star state and per-turn pursuit timing."); subs=parser.add_subparsers(dest="command",required=True)
    p=subs.add_parser("create"); p.add_argument("--workspace-root",required=True); p.add_argument("--subject",required=True); p.add_argument("--topic",required=True); init_args(p); p.set_defaults(handler=command_create)
    p=subs.add_parser("init"); p.add_argument("--artifact",required=True); init_args(p); p.set_defaults(handler=command_init)
    p=subs.add_parser("reopen"); add_common(p); add_actor(p); p.add_argument("--batch"); p.add_argument("--next-action"); p.set_defaults(handler=command_reopen)
    p=subs.add_parser("pursuit-start"); add_common(p); p.add_argument("--summary",required=True); p.add_argument("--batch"); p.add_argument("--started-at"); p.set_defaults(handler=command_pursuit_start)
    p=subs.add_parser("pursuit-stop"); add_common(p); add_actor(p); p.add_argument("--summary"); p.add_argument("--batch"); p.add_argument("--ended-at"); p.add_argument("--note"); p.set_defaults(handler=command_pursuit_stop)
    p=subs.add_parser("pursuit-remove"); add_common(p); add_actor(p); p.add_argument("--number",type=int,required=True); p.add_argument("--reason",required=True); p.set_defaults(handler=command_pursuit_remove)
    p=subs.add_parser("provisional-start"); add_common(p); p.add_argument("--started-at"); p.set_defaults(handler=command_provisional_start)
    p=subs.add_parser("provisional-discard"); add_common(p); p.set_defaults(handler=command_provisional_discard)
    p=subs.add_parser("provisional-commit"); add_common(p); add_actor(p); p.add_argument("--summary",required=True); p.add_argument("--batch"); p.add_argument("--ended-at"); p.set_defaults(handler=command_provisional_commit)
    p=subs.add_parser("checkpoint"); add_common(p); add_actor(p); p.add_argument("--batch"); p.add_argument("--next-action"); p.add_argument("--note"); p.add_argument("--another-iteration"); p.add_argument("--verify-complete",type=int,action="append"); p.add_argument("--failure-active",type=int,action="append"); p.add_argument("--clear-failures",action="store_true"); p.set_defaults(handler=command_checkpoint)
    p=subs.add_parser("refine"); add_common(p); add_actor(p); p.add_argument("--writing-llm"); p.add_argument("--goal"); p.add_argument("--pursuit"); p.add_argument("--constraint",action="append"); p.add_argument("--format",action="append"); p.add_argument("--definition-of-done",action="append"); p.add_argument("--failure",action="append"); p.add_argument("--verify-complete",type=int,action="append"); p.add_argument("--batch"); p.add_argument("--next-action"); p.add_argument("--note"); p.set_defaults(handler=command_refine)
    p=subs.add_parser("feedback-add"); add_common(p); add_actor(p); p.add_argument("--descriptor",required=True); p.add_argument("--body",required=True); p.set_defaults(handler=command_feedback_add)
    p=subs.add_parser("pause"); add_common(p); add_actor(p); p.add_argument("--reason"); p.set_defaults(handler=command_pause)
    p=subs.add_parser("resume"); add_common(p); add_actor(p); p.set_defaults(handler=command_resume)
    p=subs.add_parser("recover"); add_common(p); add_actor(p); p.add_argument("--interrupted-at"); p.add_argument("--note"); p.set_defaults(handler=command_recover)
    p=subs.add_parser("finish"); add_common(p); p.add_argument("--result",choices=("reached","ended"),required=True); p.add_argument("--evidence",action="append"); p.add_argument("--note"); p.set_defaults(handler=command_finish)
    p=subs.add_parser("finalize"); add_common(p); add_actor(p); p.add_argument("--evidence",action="append"); p.add_argument("--note"); p.add_argument("--verify-complete",type=int,action="append"); p.add_argument("--constraints-verified",action="store_true"); p.add_argument("--format-verified",action="store_true"); p.add_argument("--failure-reviewed",action="store_true"); p.set_defaults(handler=command_finalize)
    p=subs.add_parser("end"); add_common(p); add_actor(p); p.add_argument("--note"); p.set_defaults(handler=command_end)
    p=subs.add_parser("status"); add_common(p); p.add_argument("--json",action="store_true"); p.set_defaults(handler=command_status)
    p=subs.add_parser("format-receipt"); add_common(p); p.add_argument("--type",required=True,choices=("timing-statement","fallback-disclosure","mode-footer","prompt-contract","finalizer-receipt")); p.add_argument("--subject",help="Required for finalizer-receipt"); p.set_defaults(handler=command_format_receipt)
    return parser
def main():
    args=build_parser().parse_args()
    try: state=args.handler(args)
    except NorthStarError as exc: print(f"north-star: {exc}",file=sys.stderr); return 2
    except OSError as exc: print(f"north-star: filesystem error: {exc}",file=sys.stderr); return 3
    if state is not None and args.command != "format-receipt":
        print_result(state,getattr(args,"json",False))
    return 0
if __name__=="__main__": raise SystemExit(main())
