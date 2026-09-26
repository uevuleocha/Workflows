"""Read-only, field-minimized comparison of Buzz agents and workspace records.

Never print an app record, arbitrary environment value, auth tag, URL, or full pubkey.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

DEFAULT_DOC = Path(r"C:\Users\Admin\Uzzys Universe\Archive\Live\Documentation\Personal\Buzz\3.) Buzz Agent Instructions.md")
DEFAULT_DIGEST = Path(r"C:\Users\Admin\.buzz\AGENTS.md")
CONTEXT_KEYS = ("BUZZ_ACP_CONTEXT_MESSAGE_LIMIT", "BUZZ_AGENT_MAX_CONTEXT_TOKENS")
DISPLAY_ENV_KEYS = (*CONTEXT_KEYS, "CLAUDE_CODE_EFFORT_LEVEL")
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
VALID_PRONOUNS = {"she/her", "he/him", "they/them"}
BARE_ALIASES = {"opus", "sonnet", "haiku", "fable"}
BUILTIN_PERSONAS = {"Pollen", "Fizz", "Honey"}
EXPECTED_COMMAND = {"claude": "buzz-acp", "codex": "buzz-acp", "buzz-agent": "buzz-acp"}
KNOWN_COMPAT_HOSTS = {"api.z.ai": "Z.ai", "api.deepseek.com": "DeepSeek"}


def app_path() -> Path:
    root = os.environ.get("APPDATA")
    if not root:
        raise ValueError("APPDATA is unavailable")
    return Path(root) / "xyz.block.buzz.app" / "agents" / "managed-agents.json"


def safe_name(value: object) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", text) else "[invalid name]"


def safe_token(value: object) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[A-Za-z0-9_.\[\]-]{1,80}", text) else "[unsafe or absent]"


def safe_int(value: object) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[0-9]{1,10}", text) else "absent"


def safe_description(value: object) -> str:
    """Display a public description only if it has a small, plain-text shape."""
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9 ,.'()/-]{1,200}|[A-Za-z0-9 ,.'()/-]+ --> [A-Za-z0-9 ,.'()/-]+", value):
        return "[unsafe or absent]"
    return value if not re.search(r"(?i)(api.?key|token|secret|password|https?://)", value) else "[unsafe or absent]"


def safe_pronouns(value: object) -> str:
    text = str(value or "")
    return text if text in VALID_PRONOUNS else "[invalid or absent]"


def load_app(path: Path) -> tuple[dict[str, dict], dict[str, dict], int]:
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError("app JSON root must be an array")
    definitions: dict[str, dict] = {}
    instances: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("app JSON contains a non-object record")
        name = safe_name(record.get("name"))
        if name == "[invalid name]":
            continue
        if record.get("pubkey"):
            if name in instances:
                raise ValueError("duplicate active instance name")
            instances[name] = record
        elif record.get("is_active") is not False:
            if name in definitions:
                raise ValueError("duplicate active definition name")
            definitions[name] = record
    return definitions, instances, len(records)


def section(text: str, start: str, end: str) -> str:
    before, marker, tail = text.partition(start)
    if not marker:
        raise ValueError("required documentation section missing")
    body, marker, after = tail.partition(end)
    if not marker:
        raise ValueError("documentation section end missing")
    return body


def parse_doc(path: Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    roster = section(text, "## Roster\n", "## Current Roster State")
    state = section(text, "## Current Roster State", "## Delegation Notes")
    entries: dict[str, dict] = {}
    for match in re.finditer(r"(?m)^### [A-Z]\. ([A-Za-z][A-Za-z0-9_-]*) -- .*?$", roster):
        name = match.group(1)
        finish = roster.find("\n### ", match.end())
        block = roster[match.start():finish if finish >= 0 else None]
        full = re.search(r"\*\*Full instruction text[^\n]*\n\s*```text\n(.*?)\n```", block, re.S)
        stub = re.search(r"\*\*Buzz UI stub[^\n]*\n\s*```text\n(.*?)\n```", block, re.S)
        lab = re.search(r"(?m)^\| Lab\s*\|\s*([^|]+?)\s*\|", block)
        role = re.search(r"(?m)^Role:\s*(.+)$", full.group(1)) if full else None
        entries[name] = {
            "stub": stub.group(1).strip() if stub else None,
            "lab": lab.group(1).strip() if lab else None,
            "role": role.group(1).strip() if role else None,
            "instruction_name": (re.search(r"(?m)^Name:\s*(.+)$", full.group(1)).group(1).strip() if full and re.search(r"(?m)^Name:\s*(.+)$", full.group(1)) else None),
            "pronouns": (re.search(r"(?m)^Pronouns:\s*(.+)$", full.group(1)).group(1).strip() if full and re.search(r"(?m)^Pronouns:\s*(.+)$", full.group(1)) else None),
            "summary_pronouns": (re.search(r"(?m)^\| Pronouns\s*\|\s*([^|]+?)\s*\|", block).group(1).strip() if re.search(r"(?m)^\| Pronouns\s*\|\s*([^|]+?)\s*\|", block) else None),
            "description": (re.search(r"(?m)^\| Description\s*\|\s*`?([^|`]+?)`?\s*\|", block).group(1).strip() if re.search(r"(?m)^\| Description\s*\|\s*`?([^|`]+?)`?\s*\|", block) else None),
            "charter_complete": bool(full and all(re.search(r"(?m)^" + re.escape(key) + r":?", full.group(1)) for key in ("Name", "Pronouns", "Personality", "Nationality & Dialect", "Role", "Model", "Sign off for Agent Provenance and Changelog"))),
        }
    rows: dict[str, dict] = {}
    header = None
    for line in state.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Seat":
            header = cells
        elif header and len(cells) == len(header) and not set(cells[0]) <= {"-", ":", " "}:
            row = dict(zip(header, cells))
            if row.get("Agent"):
                rows[row["Agent"]] = row
    config = section(text, "## Standard Configuration For Every Agent", "## Roster")
    standards = {}
    for key in ("Parallelism", *CONTEXT_KEYS):
        match = re.search(r"(?m)^\|\s*`?" + re.escape(key) + r"`?\s*\|\s*([^|]+)", config)
        standards[key] = match.group(1).strip() if match else "unknown"
    return entries, rows, standards


def parse_digest(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    marker = "<!-- END BUZZ MANAGED -->"
    if marker not in text:
        raise ValueError("managed-block end marker missing")
    authored = text.split(marker, 1)[1]
    lines = re.findall(r"(?m)^Agents: (.+)$", authored)
    if len(lines) != 1:
        raise ValueError("expected exactly one user-authored Agents line")
    digest = lines[0].split(". Full roster", 1)[0]
    anchors = list(re.finditer(r"(?:^|, )([A-Za-z][A-Za-z0-9_-]{0,39}) \(([^)]{1,32})\): ", digest))
    if not anchors or anchors[0].start() != 0:
        raise ValueError("digest format invalid")
    result: dict[str, dict[str, str]] = {}
    for index, match in enumerate(anchors):
        end = anchors[index + 1].start() if index + 1 < len(anchors) else len(digest)
        description = digest[match.end():end].removesuffix(", ").strip()
        if index + 1 == len(anchors):
            description = description.removesuffix(".")
        if not description or match.group(1) in result:
            raise ValueError("digest entry invalid")
        result[match.group(1)] = {"pronouns": match.group(2), "description": description}
    return result


def model_and_effort(definition: dict) -> tuple[str, str]:
    runtime = safe_token(definition.get("runtime"))
    raw = safe_token(definition.get("model"))
    match = re.fullmatch(r"(.+)\[([A-Za-z]+)\]", raw)
    if runtime == "codex" and match:
        return match.group(1), match.group(2).lower()
    if runtime == "claude":
        env = definition.get("env_vars")
        value = env.get("CLAUDE_CODE_EFFORT_LEVEL") if isinstance(env, dict) else None
        if value is None:
            return raw, "missing"
        word = str(value)
        if not re.fullmatch(r"[A-Za-z]{1,16}", word):
            return raw, "[invalid unsafe value]"
        return raw, word.lower() if word.lower() in VALID_EFFORTS else word
    return raw, "default"


def installed_package_version(path: Path) -> str:
    """Read only package version metadata; never echo parser errors."""
    try:
        data = json.loads((path / "package.json").read_text(encoding="utf-8"))
        return safe_token(data.get("version"))
    except (OSError, ValueError, json.JSONDecodeError):
        return "unverified"


def adapter_paths() -> tuple[Path, Path, Path]:
    root = Path(os.environ["APPDATA"]) / "npm" / "node_modules"
    acp = root / "@agentclientprotocol" / "claude-agent-acp"
    sdk = acp / "node_modules" / "@anthropic-ai" / "claude-agent-sdk"
    binary = acp / "node_modules" / "@anthropic-ai" / "claude-agent-sdk-win32-x64" / "claude.exe"
    return acp, sdk, binary


def binary_contains(path: Path, model_id: str) -> bool:
    """Scan without printing binary bytes, including UTF-16 strings."""
    needles = [model_id.encode("ascii"), model_id.encode("utf-16-le")]
    overlap = max(map(len, needles)) - 1
    tail = b""
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            data = tail + chunk
            if any(needle in data for needle in needles):
                return True
            tail = data[-overlap:]
    return False


def check_adapter(definitions: dict[str, dict]) -> tuple[int, int]:
    seats = {name: safe_token(item.get("model")) for name, item in definitions.items() if item.get("runtime") == "claude"}
    if not seats:
        return 0, 0
    try:
        acp, sdk, binary = adapter_paths()
    except KeyError:
        print("Adapter | versions=unverified | binary=unverified")
        return 0, len(seats)
    print(f"Adapter | claude-agent-acp={installed_package_version(acp)} | bundled SDK={installed_package_version(sdk)}")
    differences = unknowns = 0
    for name, model in sorted(seats.items()):
        if model in BARE_ALIASES:
            continue
        try:
            found = binary_contains(binary, model)
        except OSError:
            print(f"{name} | Adapter model {model} | found=unverified")
            unknowns += 1
            continue
        print(f"{name} | Adapter model {model} | found={'yes' if found else 'no'}")
        differences += not found
    return differences, unknowns


def latest_package_version(package: str) -> str:
    try:
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if npm:
            result = subprocess.run([npm, "view", package, "version", "--json"], capture_output=True, text=True, timeout=15, check=False)
            if result.returncode == 0:
                return safe_token(json.loads(result.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    try:
        with urlopen("https://registry.npmjs.org/" + package.replace("/", "%2F") + "/latest", timeout=15) as response:
            metadata = json.load(response)
        return safe_token(metadata.get("version"))
    except (OSError, ValueError):
        return "unverified"


def check_freshness() -> int:
    """Report installed and latest versions; never install packages."""
    root = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules"
    unknowns = 0
    for package, location in (("@agentclientprotocol/claude-agent-acp", root / "@agentclientprotocol" / "claude-agent-acp"), ("@anthropic-ai/claude-code", root / "@anthropic-ai" / "claude-code")):
        installed = installed_package_version(location)
        latest = latest_package_version(package)
        unknowns += latest == "unverified" or installed == "unverified"
        print(f"Freshness | {package} | installed={installed} | latest={latest} | status={'unverified' if latest == 'unverified' or installed == 'unverified' else ('up to date' if installed == latest else 'review update')}")
    return unknowns


def compatible_lab(env: dict) -> str:
    """Classify one needed URL internally; never return or print URL content."""
    value = env.get("OPENAI_COMPAT_BASE_URL")
    if not isinstance(value, str):
        return "unverified"
    try:
        parsed = urlparse(value)
        host = parsed.hostname
    except ValueError:
        return "unverified"
    if parsed.scheme != "https" or not host or parsed.username or parsed.password:
        return "unverified"
    return KNOWN_COMPAT_HOSTS.get(host.lower(), "unverified")


def diff(name: str, field: str, panel: str, file: str) -> None:
    print(f"{name} | {field} | panel={panel} | file={file}")


def check(definitions: dict[str, dict], instances: dict[str, dict], entries: dict[str, dict], rows: dict[str, dict], standards: dict[str, str], digest: dict[str, dict[str, str]]) -> tuple[int, int]:
    differences = unknowns = 0
    for name in sorted(set(definitions) | set(instances) | set(entries) | set(rows) | set(digest)):
        definition, instance, entry, row = definitions.get(name), instances.get(name), entries.get(name), rows.get(name)
        if not all((definition, instance, entry, row, name in digest)):
            diff(name, "Name/record presence", "/".join("yes" if x else "no" for x in (definition, instance)), "/".join("yes" if x else "no" for x in (entry, row, name in digest)))
            differences += 1
            if not all((definition, instance, entry, row)):
                continue
        assert definition and instance and entry and row
        if entry.get("instruction_name") != name:
            diff(name, "Name in instructions", name, safe_name(entry.get("instruction_name")))
            differences += 1
        model, effort = model_and_effort(definition)
        file_model = safe_token(row.get("Model"))
        if model != file_model:
            diff(name, "Model", model, file_model)
            differences += 1
        if runtime := safe_token(definition.get("runtime")):
            if runtime == "claude" and model in BARE_ALIASES:
                print(f"{name} | Model alias {model} | exact model=unverified until agent asked")
                unknowns += 1
        file_effort = safe_token(row.get("Effort level"))
        if runtime == "claude" and effort not in VALID_EFFORTS:
            diff(name, "Effort level", effort, file_effort)
            differences += 1
        elif effort.lower() != file_effort.lower():
            diff(name, "Effort level", effort, file_effort)
            differences += 1
        file_runtime = safe_token(row.get("Runtime"))
        if runtime != file_runtime:
            diff(name, "Provider runtime", runtime, file_runtime)
            differences += 1
        provider = safe_token(definition.get("provider") or "native")
        lab = safe_token(row.get("Lab"))
        env = definition.get("env_vars")
        env = env if isinstance(env, dict) else {}
        if "CLAUDE_EFFORT" in env:
            print(f"{name} | CLAUDE_EFFORT | panel=present | status=not an input")
        if runtime != "claude" and "CLAUDE_CODE_EFFORT_LEVEL" in env:
            print(f"{name} | CLAUDE_CODE_EFFORT_LEVEL | panel=present | status=not used by runtime")
        expected_lab = {"claude": "Anthropic", "codex": "OpenAI"}.get(runtime)
        if runtime == "buzz-agent":
            expected_lab = compatible_lab(env)
        if expected_lab and expected_lab != "unverified" and lab != expected_lab:
            diff(name, "Provider lab", expected_lab, lab)
            differences += 1
        elif expected_lab == "unverified":
            print(f"{name} | Provider lab | panel=unverified compatible endpoint | file={lab}")
            unknowns += 1
        file_endpoint = str(row.get("Endpoint -> [e]") or "")
        expected_protocol = "native" if file_endpoint == "native runtime" else "openai-compat"
        if provider != expected_protocol:
            diff(name, "Provider protocol", provider, expected_protocol)
            differences += 1
        if not entry["charter_complete"]:
            diff(name, "Charter", "file-authoritative", "incomplete")
            differences += 1
        if name in digest:
            doc_pronouns = safe_pronouns(entry.get("pronouns"))
            summary_pronouns = safe_pronouns(entry.get("summary_pronouns"))
            digest_pronouns = safe_pronouns(digest[name].get("pronouns"))
            if doc_pronouns not in VALID_PRONOUNS or summary_pronouns != doc_pronouns or digest_pronouns != doc_pronouns:
                print(f"{name} | Pronouns | panel=n/a | file=instruction:{doc_pronouns}, summary:{summary_pronouns}, digest:{digest_pronouns}")
                differences += 1
            raw_descriptions = (definition.get("description"), entry.get("description"), digest[name].get("description"))
            app_description, doc_description, digest_description = map(safe_description, raw_descriptions)
            if len(set(map(str, raw_descriptions))) != 1:
                print(f"{name} | Description | panel={app_description} | doc={doc_description} | digest={digest_description}")
                differences += 1
        pools = (definition.get("name_pool"), instance.get("name_pool"))
        if name not in BUILTIN_PERSONAS and any(pool not in (None, "", []) for pool in pools):
            print(f"{name} | Instance name pool warning | panel=non-empty | see doc 3 note [np]")
        # The stub is untrusted arbitrary text; compare without printing either copy.
        app_stub = instance.get("system_prompt") or definition.get("system_prompt")
        file_stub = entry.get("stub")
        if isinstance(app_stub, str) and isinstance(file_stub, str):
            if " ".join(app_stub.split()) != " ".join(file_stub.split()):
                diff(name, "system_prompt stub", "different", "different")
                differences += 1
        else:
            diff(name, "system_prompt stub", "present" if app_stub else "absent", "present" if file_stub else "absent")
            differences += 1
        command = safe_token(instance.get("acp_command"))
        expected = EXPECTED_COMMAND.get(runtime)
        if expected and command != expected:
            diff(name, "acp_command (instance)", command, expected)
            differences += 1
        elif not expected:
            diff(name, "acp_command (instance)", command, "unknown")
            unknowns += 1
        parallelism = safe_int(instance.get("parallelism"))
        expected_parallelism = safe_int(standards.get("Parallelism"))
        if parallelism != expected_parallelism:
            diff(name, "parallelism (instance)", parallelism, expected_parallelism)
            differences += 1
        for key in CONTEXT_KEYS:
            observed = safe_int(env.get(key))
            expected_value = "1000000" if standards.get(key) == "1M" else safe_int(standards.get(key))
            if key == "BUZZ_AGENT_MAX_CONTEXT_TOKENS" and runtime != "buzz-agent":
                expected_value = "absent"
            if observed != expected_value:
                diff(name, key, observed, expected_value)
                differences += 1
        if runtime == "buzz-agent" and provider == "openai-compat":
            for key in ("OPENAI_COMPAT_API_KEY", "OPENAI_COMPAT_BASE_URL"):
                if key not in env:
                    diff(name, key + " presence", "absent", "present")
                    differences += 1
    return differences, unknowns


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["check", "freshness"])
    parser.add_argument("--app", type=Path, default=None)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--digest", type=Path, default=DEFAULT_DIGEST)
    args = parser.parse_args()
    if args.mode == "freshness":
        return 1 if check_freshness() else 0
    try:
        definitions, instances, count = load_app(args.app or app_path())
        entries, rows, standards = parse_doc(args.doc)
        digest = parse_digest(args.digest)
        differences, unknowns = check(definitions, instances, entries, rows, standards, digest)
        adapter_differences, adapter_unknowns = check_adapter(definitions)
        differences += adapter_differences
        unknowns += adapter_unknowns
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # Never print exception text; parser exceptions can contain source data.
        print(f"Check failed safely: {type(exc).__name__}")
        return 2
    print(f"Check complete: {len(instances)} instances, {len(definitions)} active definitions, {count} records; instance acp_command and parallelism checked; {differences} differences, {unknowns} unverified comparisons.")
    return 1 if differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
