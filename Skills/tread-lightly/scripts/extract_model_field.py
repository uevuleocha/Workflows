#!/usr/bin/env python3
"""Emit one model field from JSON or TOML without echoing unrelated content."""
from __future__ import annotations
import argparse, json, re, sys, tomllib
from pathlib import Path

SAFE_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/ -]{0,127}$")
class ExtractionError(RuntimeError): pass

def load_mapping(path: Path) -> dict:
    try:
        raw = path.read_bytes()
        if path.suffix.casefold() == ".json": value = json.loads(raw.decode("utf-8"))
        elif path.suffix.casefold() in {".toml", ".tml"}: value = tomllib.loads(raw.decode("utf-8"))
        else: raise ExtractionError("Only JSON and TOML configuration are supported.")
    except ExtractionError: raise
    except Exception as exc: raise ExtractionError("Configuration could not be parsed safely.") from exc
    if not isinstance(value, dict): raise ExtractionError("Configuration root must be a mapping.")
    return value

def extract_model(mapping: dict, dotted_key: str) -> str:
    if not dotted_key or any(not part for part in dotted_key.split(".")): raise ExtractionError("A valid dotted model key is required.")
    current: object = mapping
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current: raise ExtractionError("Requested model field is unavailable.")
        current = current[part]
    if not isinstance(current, str) or not SAFE_MODEL_RE.fullmatch(current): raise ExtractionError("Requested model field is not a safe model identifier.")
    return current

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("config", type=Path); parser.add_argument("--key", default="model"); args = parser.parse_args()
    try: model = extract_model(load_mapping(args.config), args.key)
    except ExtractionError as exc: print(str(exc), file=sys.stderr); return 2
    print(model); return 0

if __name__ == "__main__": raise SystemExit(main())
