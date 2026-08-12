#!/usr/bin/env python3
"""Regression checks for field-minimized model discovery."""
from __future__ import annotations
import subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("extract_model_field.py")
def run(path: Path, key: str = "model") -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), str(path), "--key", key], capture_output=True, text=True, timeout=15)

def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); fake_token = "synthetic-secret-that-must-never-appear"
        toml_path = root / "fixture.toml"
        toml_path.write_text('model = "gpt-5.6-sol"\n[mcp_servers.example]\n' + f'url = "https://example.invalid/connect?token={fake_token}"\n', encoding="utf-8")
        result = run(toml_path)
        assert result.returncode == 0 and result.stdout == "gpt-5.6-sol\n" and result.stderr == ""
        assert fake_token not in result.stdout + result.stderr
        json_path = root / "fixture.json"
        json_path.write_text('{"runtime":{"model":"Claude Opus 5"},"credential":"synthetic-private"}', encoding="utf-8")
        result = run(json_path, "runtime.model")
        assert result.returncode == 0 and result.stdout == "Claude Opus 5\n" and "synthetic-private" not in result.stdout + result.stderr
        unsafe = root / "unsafe.toml"
        unsafe.write_text('model = "https://example.invalid/?token=synthetic"\n', encoding="utf-8")
        result = run(unsafe)
        assert result.returncode == 2 and result.stdout == "" and "synthetic" not in result.stderr
    print("field-minimized model discovery regression: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
