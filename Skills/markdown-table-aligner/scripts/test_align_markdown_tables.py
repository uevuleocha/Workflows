#!/usr/bin/env python3
"""Regression tests for the deterministic Markdown table aligner."""

from __future__ import annotations

import codecs
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("align_markdown_tables.py")
SPEC = importlib.util.spec_from_file_location("align_markdown_tables", SCRIPT)
assert SPEC and SPEC.loader
ALIGNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ALIGNER
SPEC.loader.exec_module(ALIGNER)


class TransformTests(unittest.TestCase):
    def test_ascii_outer_pipes_and_idempotence(self):
        source = "| Name | State |\n|---|:---:|\n| A | Done |\n"
        expected = "| Name | State |\n| ---- | :---: |\n| A    | Done  |\n"
        output, findings = ALIGNER.transform(source)
        self.assertEqual(output, expected)
        self.assertTrue(any(f.code == "needs_alignment" for f in findings))
        second, second_findings = ALIGNER.transform(output)
        self.assertEqual(second, output)
        self.assertEqual(second_findings, [])

    def test_without_outer_pipes_and_alignment_colons(self):
        source = "Left | Center | Right\n:--- | :---: | ---:\na | b | c\n"
        expected = "Left | Center | Right\n:--- | :----: | ----:\na    | b      | c    \n"
        output, _ = ALIGNER.transform(source)
        self.assertEqual(output, expected)

    def test_escaped_and_inline_code_pipes(self):
        source = "| Key | Value |\n|---|---|\n| a\\|b | `x|y` |\n"
        output, findings = ALIGNER.transform(source)
        self.assertIn("a\\|b", output)
        self.assertIn("`x|y`", output)
        self.assertFalse(any(f.code == "malformed_table" for f in findings))

    def test_fences_and_prose_are_byte_identical(self):
        source = (
            "before a | b prose\n"
            "```markdown\n| A | B |\n|---|---|\n| x | y |\n```\n"
            "~~~\n| C | D |\n|---|---|\n~~~\n"
        )
        output, findings = ALIGNER.transform(source)
        self.assertEqual(output, source)
        self.assertEqual(findings, [])

    def test_unicode_display_width(self):
        source = "| Kind | Value |\n|---|---|\n| emoji | 🟣 |\n| cjk | 界 |\n| combining | é |\n| variation | ✈️ |\n| joined | 👨‍👩‍👧‍👦 |\n"
        output, findings = ALIGNER.transform(source)
        self.assertTrue(any(f.code == "needs_alignment" for f in findings))
        second, second_findings = ALIGNER.transform(output)
        self.assertEqual(second, output)
        self.assertEqual(second_findings, [])

    def test_over_cap_is_report_only(self):
        long_cell = "x" * 81
        source = f"| Key | Value |\n|---|---|\n| a | {long_cell} |\n"
        output, findings = ALIGNER.transform(source)
        self.assertEqual(output, source)
        self.assertTrue(any(f.code == "cell_over_cap" for f in findings))

    def test_exactly_eighty_is_allowed(self):
        source = f"| Key | Value |\n|---|---|\n| a | {'x' * 80} |\n"
        _, findings = ALIGNER.transform(source)
        self.assertFalse(any(f.code == "cell_over_cap" for f in findings))

    def test_trailing_spaces_after_outer_pipe_are_preserved(self):
        source = "| A | B |  \n|---|---|  \n| x | y |  \n"
        output, _ = ALIGNER.transform(source)
        self.assertEqual([line[-3:] for line in output.splitlines()], ["|  ", "|  ", "|  "])

    def test_unclosed_inline_code_candidate_is_report_only(self):
        source = "| A | `B |\n|---|---|\n"
        output, findings = ALIGNER.transform(source)
        self.assertEqual(output, source)
        self.assertTrue(any(f.code == "malformed_table" for f in findings))

    def test_malformed_is_report_only(self):
        source = "| A | B |\n|---|---|---|\n| x | y |\n"
        output, findings = ALIGNER.transform(source)
        self.assertEqual(output, source)
        self.assertTrue(any(f.code == "malformed_table" for f in findings))


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def test_bom_crlf_final_newline_and_collision_safety(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            staged = root / "staged.md"
            data = codecs.BOM_UTF8 + b"| A | B |\r\n|---|---|\r\n| x | y |"
            source.write_bytes(data)
            first = self.run_cli("format", str(source), "--output", str(staged), "--json")
            self.assertEqual(first.returncode, 0, first.stderr)
            result = staged.read_bytes()
            self.assertTrue(result.startswith(codecs.BOM_UTF8))
            self.assertIn(b"\r\n", result)
            self.assertFalse(result.endswith(b"\n"))
            collision = self.run_cli("format", str(source), "--output", str(staged), "--json")
            self.assertEqual(collision.returncode, 2)
            self.assertIn("refusing overwrite", collision.stderr)
            in_place = self.run_cli("format", str(source), "--output", str(source), "--json")
            self.assertEqual(in_place.returncode, 2)

    def test_check_json_and_format_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            output = root / "output.md"
            source.write_text(
                "| A | B |\n|---|---|\n| x | " + ("z" * 81) + " |\n",
                encoding="utf-8",
            )
            check = self.run_cli("check", str(source), "--json")
            self.assertEqual(check.returncode, 1)
            payload = json.loads(check.stdout)
            self.assertTrue(any(item["code"] == "cell_over_cap" for item in payload))
            formatted = self.run_cli("format", str(source), "--output", str(output), "--json")
            self.assertEqual(formatted.returncode, 1)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
