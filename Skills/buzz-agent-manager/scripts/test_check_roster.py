"""Synthetic safety and drift tests for the read-only roster checker."""

from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from unittest.mock import patch

import check_roster as roster


def fixture(runtime: str = "codex") -> tuple[dict, dict, dict, dict, dict, dict]:
    name = "Tunde"
    definition = {
        "name": name, "runtime": runtime, "provider": None,
        "model": "gpt-5.6-sol[medium]" if runtime == "codex" else "claude-sonnet-5",
        "description": "CTO --> owns the technical chain",
        "env_vars": {
            "BUZZ_ACP_CONTEXT_MESSAGE_LIMIT": "20",
            "OPENAI_COMPAT_API_KEY": "SYNTHETIC_DO_NOT_PRINT",
            "OPENAI_COMPAT_BASE_URL": "SYNTHETIC_URL_DO_NOT_PRINT",
            **({"CLAUDE_CODE_EFFORT_LEVEL": "Medium"} if runtime == "claude" else {}),
        },
    }
    instance = {"name": name, "pubkey": "synthetic", "parallelism": 3,
                "acp_command": "buzz-acp", "system_prompt": "You are Tunde. Read the roster."}
    entry = {"stub": "You are Tunde. Read the roster.", "lab": "OpenAI" if runtime == "codex" else "Anthropic", "instruction_name": "Tunde",
             "role": "CTO", "pronouns": "he/him", "summary_pronouns": "he/him",
             "description": "CTO --> owns the technical chain", "charter_complete": True}
    row = {"Agent": name, "Model": "gpt-5.6-sol" if runtime == "codex" else "claude-sonnet-5",
           "Runtime": runtime, "Lab": "OpenAI" if runtime == "codex" else "Anthropic",
           "Effort level": "medium", "Endpoint -> [e]": "native runtime"}
    standards = {"Parallelism": "3", "BUZZ_ACP_CONTEXT_MESSAGE_LIMIT": "20",
                 "BUZZ_AGENT_MAX_CONTEXT_TOKENS": "1M"}
    digest = {name: {"pronouns": "he/him", "description": "CTO --> owns the technical chain"}}
    return definition, instance, entry, row, standards, digest


def run_case(items: tuple[dict, dict, dict, dict, dict, dict]) -> tuple[int, int, str]:
    definition, instance, entry, row, standards, digest = items
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        differences, unknowns = roster.check({"Tunde": definition}, {"Tunde": instance},
                                              {"Tunde": entry}, {"Tunde": row}, standards, digest)
    text = output.getvalue()
    assert "SYNTHETIC_DO_NOT_PRINT" not in text
    assert "SYNTHETIC_URL_DO_NOT_PRINT" not in text
    return differences, unknowns, text


def main() -> None:
    assert roster.model_and_effort({"runtime": "codex", "model": "gpt-5.6-sol[medium]"}) == ("gpt-5.6-sol", "medium")
    assert roster.compatible_lab({"OPENAI_COMPAT_BASE_URL": "https://api.z.ai/v1"}) == "Z.ai"
    assert roster.compatible_lab({"OPENAI_COMPAT_BASE_URL": "https://api.z.ai.evil.example/v1"}) == "unverified"
    assert roster.compatible_lab({"OPENAI_COMPAT_BASE_URL": "https://user:password@api.z.ai/v1"}) == "unverified"
    assert run_case(fixture())[:2] == (0, 0)

    items = fixture()
    items[1]["parallelism"] = 5
    assert "parallelism (instance) | panel=5 | file=3" in run_case(items)[2]
    items = fixture()
    items[3]["Model"] = "gpt-5.6-terra"
    assert "Model | panel=gpt-5.6-sol | file=gpt-5.6-terra" in run_case(items)[2]
    items = fixture()
    items[1]["acp_command"] = "wrong-acp"
    assert "acp_command (instance) | panel=wrong-acp | file=buzz-acp" in run_case(items)[2]

    for condition, value in (("missing", None), ("invalid", "Extra"), ("valid", "HIGH")):
        items = fixture("claude")
        if value is None:
            del items[0]["env_vars"]["CLAUDE_CODE_EFFORT_LEVEL"]
        else:
            items[0]["env_vars"]["CLAUDE_CODE_EFFORT_LEVEL"] = value
        if condition == "valid":
            items[3]["Effort level"] = "high"
            assert run_case(items)[:2] == (0, 0)
        else:
            count, _, output = run_case(items)
            assert count == 1 and "Effort level" in output and ("missing" if value is None else "Extra") in output

    items = fixture("claude")
    items[0]["env_vars"]["CLAUDE_EFFORT"] = "SYNTHETIC_DO_NOT_PRINT"
    assert "CLAUDE_EFFORT | panel=present | status=not an input" in run_case(items)[2]
    items = fixture("claude")
    items[0]["env_vars"]["CLAUDE_CODE_EFFORT_LEVEL"] = "SYNTHETIC_DO_NOT_PRINT"
    assert "SYNTHETIC_DO_NOT_PRINT" not in run_case(items)[2]
    items = fixture("claude")
    items[0]["model"] = "sonnet"
    items[3]["Model"] = "sonnet"
    assert run_case(items)[1] == 1 and "exact model=unverified" in run_case(items)[2]

    items = fixture()
    items[0]["description"] = "CTO --> app text"
    items[2]["description"] = "CTO --> document text"
    items[5]["Tunde"]["description"] = "CTO --> digest text"
    count, _, output = run_case(items)
    assert count == 1 and all(value in output for value in ("app text", "document text", "digest text"))
    items = fixture()
    description = "CTO --> owns the technical chain and guides the team"
    items[0]["description"] = description
    items[2]["description"] = description
    items[5]["Tunde"]["description"] = description
    assert run_case(items)[:2] == (0, 0) and "Description warning" not in run_case(items)[2]
    items = fixture()
    items[5]["Tunde"]["pronouns"] = "they/them"
    assert "Pronouns | panel=n/a | file=instruction:he/him, summary:he/him, digest:they/them" in run_case(items)[2]
    items = fixture()
    del items[5]["Tunde"]
    count, _, output = run_case(items)
    assert count == 1 and output.count("Name/record presence") == 1
    items = fixture()
    items[0]["name_pool"] = ["worker"]
    assert "Instance name pool warning" in run_case(items)[2]

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        digest_file = root / "AGENTS.md"
        digest_file.write_text("<!-- END BUZZ MANAGED -->\nAgents: Tunde (he/him): CTO --> handles code, reviews, Uche (he/him): Tester --> tests.\n", encoding="utf-8")
        parsed = roster.parse_digest(digest_file)
        assert parsed["Tunde"]["description"] == "CTO --> handles code, reviews"
        assert parsed["Uche"]["description"] == "Tester --> tests"
        digest_file.write_text("<!-- END BUZZ MANAGED -->\nAgents: Tunde (invalid): CTO --> owns the technical chain.\n", encoding="utf-8")
        parsed = roster.parse_digest(digest_file)
        items = fixture()
        items[5].update(parsed)
        assert "Pronouns | panel=n/a" in run_case(items)[2]
        binary = root / "claude.exe"
        binary.write_bytes(b"some other model")
        with patch.object(roster, "adapter_paths", return_value=(root, root, binary)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                drift, unknown = roster.check_adapter({"Tunde": fixture("claude")[0]})
            assert drift == 1 and unknown == 0 and "found=no" in output.getvalue()
        with patch.object(roster, "latest_package_version", return_value="unverified"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                assert roster.check_freshness() == 2
            assert "up to date" not in output.getvalue()

    print("PASS: digest, effort, alias, adapter, descriptions, pronouns, name pool, freshness, and secret non-disclosure")


if __name__ == "__main__":
    main()
