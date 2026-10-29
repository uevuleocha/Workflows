"""No-network static/agentic transport, probe and custom-request regression tests."""
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
import video_to_action as v


def fixture_root():
    from pathlib import Path
    root = Path.cwd() / "tmp"
    root.mkdir(exist_ok=True)
    return root


def completed(text="Normal report", steps=True):
    return NS(id="test", status="completed", output_text=text,
              steps=[NS(type="processing_call"), NS(type="processing_result")] if steps else [],
              usage=NS(total_tokens=123, total_input_tokens=90))


class AgenticTests(unittest.TestCase):
    def test_poll_recovery_same_job_and_backoff(self):
        client = self.client(NS(id="same-job", status="in_progress", steps=[]))
        client.interactions.get.side_effect = [RuntimeError("503 UNAVAILABLE")] * 3 + [completed()]
        sleeps = []
        result = v.run_phase(client, v.DEFAULT_MODEL, "url", "prompt", None, None,
                             False, sleeper=sleeps.append)
        self.assertEqual(sleeps, [5, 2, 5, 10])
        self.assertEqual(client.interactions.create.call_count, 1)
        self.assertTrue(all(call.args == ("same-job",) for call in client.interactions.get.call_args_list))
        client.interactions.cancel.assert_not_called()
        self.assertEqual(len(result.evidence["poll_failures"]), 3)

    def test_poll_retry_exhaustion_and_fatal_errors(self):
        for code, expected in ((503, 4), (401, 1), (403, 1), (400, 1), (429, 1)):
            client = self.client(NS(id="same-job", status="in_progress", steps=[]))
            error = RuntimeError("provider error")
            error.status_code = code
            client.interactions.get.side_effect = error
            with self.assertRaises(v.AgenticInteractionError) as raised:
                self.run_phase(client)
            self.assertEqual(client.interactions.get.call_count, expected)
            self.assertEqual(client.interactions.create.call_count, 1)
            client.interactions.cancel.assert_called_once_with("same-job", timeout=30)
            self.assertFalse(v.is_transient_capacity_error(raised.exception))

    def test_poll_retries_respect_overall_budget(self):
        client = self.client(NS(id="same-job", status="in_progress", steps=[]))
        client.interactions.get.side_effect = TimeoutError("temporary timeout")
        with self.assertRaises(v.AgenticInteractionError):
            self.run_phase(client, max_polls=2)
        self.assertEqual(client.interactions.get.call_count, 2)

    def test_diagnostics_and_terminal_recovery(self):
        policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        for code, count in (("503", 4), ("https://errors/UNAVAILABLE", 4),
                            ("429", 1), ("api_error", 1)):
            response = NS(id="interaction-123", status="failed", steps=[],
                          errors=[NS(code=code, message="Failure secret-test Bearer hidden-token")])
            client = self.client(response)
            with patch.dict(v.os.environ, {"GEMINI_API_KEY": "secret-test"}):
                result, attempts = v.execute_phase_with_recovery(
                    {"key": "procedure"}, lambda pd, model: self.run_phase(client),
                    policy, sleeper=lambda _: None)
            self.assertIsNone(result)
            self.assertEqual(len(attempts), count)
            evidence = attempts[-1]["evidence"]
            self.assertEqual(evidence["interaction_id"], "interaction-123")
            self.assertNotIn("secret-test", str(evidence))
            self.assertNotIn("hidden-token", str(evidence))
            self.assertIn("interaction-123", str(v.build_attempt_provenance(attempts)))

    def test_cli_summary_default_and_opt_out(self):
        base = ["helper", "https://youtu.be/1nLm36XB0fY", "--title", "Title", "--duration", "1:00",
                "--subject", "Tests"]
        for flags, expected in (([], True), (["--no-deep-summary"], False),
                                (["--deep-summary"], True)):
            with patch.object(v.sys, "argv", base + flags), patch.object(v, "load_env_files"), \
                 patch.object(v, "check_setup", return_value=True), \
                 patch.object(v, "subject_path"), \
                 patch.object(v, "run_extraction", return_value=0) as run:
                with self.assertRaises(SystemExit):
                    v.main()
                self.assertEqual(run.call_args.args[11], expected)

    def client(self, response=None):
        client = Mock()
        client.interactions.create.return_value = response or completed()
        return client

    def run_phase(self, client, **kwargs):
        return v.run_phase(client, v.DEFAULT_MODEL, "https://youtu.be/test", "Prompt",
                           kwargs.pop("start", None), None, kwargs.pop("low_res", False),
                           sleeper=lambda _: None, **kwargs)

    def selected_run(self, client, processing):
        phases = v.build_effective_prompts(v.selected_phase_defs(True, True, True), "Title", "01:00")
        policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        return v.execute_phases(
            phases, lambda pd, model, mode: v.run_phase(client, model, "https://youtu.be/test",
            pd["prompt"], None, None, False, processing=mode), policy, processing=processing)

    def test_selected_phases_default_static_and_explicit_agentic(self):
        for processing in ("static", "agentic"):
            client = self.client()
            results, errors, attempts, models = self.selected_run(client, processing)
            self.assertEqual(len(results), 3)
            self.assertFalse(errors)
            self.assertEqual(client.interactions.create.call_count, 3)
            for call in client.interactions.create.call_args_list:
                self.assertEqual(call.kwargs["input"][0]["processing"], processing)
                self.assertEqual(call.kwargs["model"], v.DEFAULT_MODEL)
            self.assertEqual(attempts[0]["processing"], processing)
            self.assertEqual(attempts[0]["evidence"]["processing"], processing)
            self.assertEqual(attempts[0]["evidence"]["total_tokens"], 123)
            self.assertEqual(attempts[0]["evidence"]["interaction_id"], "test")
            client.models.generate_content.assert_not_called()
        self.assertEqual(v.DEFAULT_PROCESSING, "static")
        self.assertEqual(self.client().interactions.create.call_count, 0)

    def test_static_accepts_response_without_processing_evidence(self):
        client = self.client(completed(steps=False))
        result = self.run_phase(client)
        self.assertEqual(str(result), "Normal report")
        self.assertEqual(client.interactions.create.call_args.kwargs["input"][0]["processing"], "static")
        with self.assertRaisesRegex(RuntimeError, "evidence"):
            self.run_phase(self.client(completed(steps=False)), processing="agentic")

    def test_agentic_failure_recovers_through_static(self):
        failed = NS(id="agentic-job", status="failed", steps=[],
                    errors=[NS(code="INTERNAL", message="There was a problem")])
        client = Mock()
        client.interactions.create.side_effect = lambda **kw: (
            failed if kw["input"][0]["processing"] == "agentic" else completed(steps=False))
        results, errors, attempts, models = self.selected_run(client, "agentic")
        self.assertEqual(len(results), 3)
        self.assertFalse(errors)
        modes = [call.kwargs["input"][0]["processing"]
                 for call in client.interactions.create.call_args_list]
        self.assertEqual(modes, ["agentic", "static"] * 3)
        self.assertEqual([(a["processing"], a["status"]) for a in attempts[:2]],
                         [("agentic", "failed"), ("static", "success")])
        self.assertEqual(attempts[1]["recovery"], "agentic-to-static")
        lines = "\n".join(v.build_attempt_provenance(attempts))
        self.assertIn("agentic primary 1/3", lines)
        self.assertIn("static primary 1/3 (agentic-to-static recovery)", lines)

    def test_static_failure_has_no_agentic_attempt(self):
        failed = NS(id="static-job", status="failed", steps=[],
                    errors=[NS(code="INTERNAL", message="boom")])
        client = self.client(failed)
        results, errors, attempts, models = self.selected_run(client, "static")
        self.assertFalse(results)
        self.assertEqual(len(errors), 3)
        self.assertTrue(all(call.kwargs["input"][0]["processing"] == "static"
                            for call in client.interactions.create.call_args_list))
        self.assertEqual(client.interactions.create.call_count, 3)

    def test_quota_failure_is_named_and_not_retried(self):
        failed = NS(id="quota-job", status="failed", steps=[],
                    errors=[NS(code="RESOURCE_EXHAUSTED", message="There was a problem")])
        client = self.client(failed)
        results, errors, attempts, models = self.selected_run(client, "static")
        self.assertFalse(results)
        self.assertEqual(client.interactions.create.call_count, 3)
        self.assertIn("quota or rate limit", errors[0]["error"])
        self.assertFalse(attempts[0]["transient"])

    def test_deprecated_model_aliases(self):
        policy = v.resolve_model_policy("free", "gemini-3.7-flash", "gemini-3.5-flash")
        self.assertEqual((policy["primary"], policy["fallback"]),
                         ("gemini-3.8-flash", "gemini-3.6-flash"))
        self.assertTrue(all("deprecated" in item for item in policy["overrides"]))
        same = v.resolve_model_policy("free", "gemini-3.7-flash", "gemini-3.8-flash")
        self.assertNotEqual(same["primary"], same["fallback"])
        default = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        self.assertEqual((default["primary"], default["fallback"], default["overrides"]),
                         ("gemini-3.8-flash", "gemini-3.6-flash", []))

    def test_agentic_probe_status_history_and_report_line(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory(dir=fixture_root()) as temp:
            root = Path(temp)
            self.assertIsNone(v.load_agentic_status(root))
            self.assertIn("never probed", v.describe_agentic_status(None))
            broken = Mock()
            broken.interactions.create.return_value = NS(
                id="probe", status="failed", steps=[],
                errors=[NS(code="INTERNAL", message="There was a problem")])
            self.assertEqual(v.run_agentic_probe(root, "free", v.DEFAULT_MODEL,
                                                 v.DEFAULT_FALLBACK_MODEL, client=broken), 1)
            call = broken.interactions.create.call_args
            self.assertEqual(broken.interactions.create.call_count, 1)
            self.assertEqual(call.kwargs["input"][0]["processing"], "agentic")
            self.assertEqual(call.kwargs["input"][0]["uri"], v.PROBE_URL)
            status = v.load_agentic_status(root)
            self.assertEqual((status["last_result"], status["consecutive_successes"]), ("broken", 0))
            self.assertIn("INTERNAL", status["last_detail"])
            self.assertIn("STILL BROKEN", v.describe_agentic_status(status))
            for expected in (1, 2):
                self.assertEqual(v.run_agentic_probe(root, "free", v.DEFAULT_MODEL,
                                 v.DEFAULT_FALLBACK_MODEL, client=self.client()), 0)
                self.assertEqual(v.load_agentic_status(root)["consecutive_successes"], expected)
            self.assertIn("WORKING", v.describe_agentic_status(v.load_agentic_status(root)))
            self.assertEqual([p.name for p in root.iterdir()], [v.AGENTIC_STATUS_FILE])
            quota = Mock()
            quota.interactions.create.return_value = NS(
                id="probe", status="failed", steps=[],
                errors=[NS(code="RESOURCE_EXHAUSTED", message="quota")])
            self.assertEqual(v.run_agentic_probe(root, "free", v.DEFAULT_MODEL,
                                                 v.DEFAULT_FALLBACK_MODEL, client=quota), 2)
            status = v.load_agentic_status(root)
            self.assertEqual((status["last_result"], status["consecutive_successes"]),
                             ("inconclusive", 2))
            self.assertIn("INCONCLUSIVE", v.describe_agentic_status(status))
            with self.assertRaises(ValueError):
                v.record_probe_result(root, "maybe", v.DEFAULT_MODEL, "fixture")
            for _ in range(v.PROBE_HISTORY_LIMIT + 5):
                v.record_probe_result(root, "broken", v.DEFAULT_MODEL, "fixture")
            status = v.load_agentic_status(root)
            self.assertEqual(len(status["history"]), v.PROBE_HISTORY_LIMIT)
            self.assertEqual(status["consecutive_successes"], 0)
            policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
            report = v.compile_report("Title", "01:00", "url", "learn", policy, ["procedure"],
                                      {"procedure": "Main"}, [], [], {}, "", "static",
                                      v.describe_agentic_status(status))
            self.assertIn("**Processing:** static", report)
            self.assertIn("**Agentic status:** STILL BROKEN", report)

    def test_probe_redacts_credentials(self):
        import tempfile
        from pathlib import Path
        client = Mock()
        client.interactions.create.side_effect = RuntimeError("bad key secret-test")
        with tempfile.TemporaryDirectory(dir=fixture_root()) as temp, \
             patch.dict(v.os.environ, {"GEMINI_API_KEY": "secret-test"}):
            v.run_agentic_probe(Path(temp), "free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL,
                                client=client)
            text = (Path(temp) / v.AGENTIC_STATUS_FILE).read_text(encoding="utf-8")
        self.assertNotIn("secret-test", text)

    def test_cli_processing_flag(self):
        base = ["helper", "https://youtu.be/1nLm36XB0fY", "--title", "Title", "--duration", "1:00",
                "--subject", "Tests"]
        for flags, expected in (([], "static"), (["--processing", "agentic"], "agentic")):
            with patch.object(v.sys, "argv", base + flags), patch.object(v, "load_env_files"), \
                 patch.object(v, "check_setup", return_value=True), \
                 patch.object(v, "subject_path"), \
                 patch.object(v, "run_extraction", return_value=0) as run:
                with self.assertRaises(SystemExit):
                    v.main()
                self.assertEqual(run.call_args.kwargs["processing"], expected)
        with patch.object(v.sys, "argv", ["helper", "--agentic-probe"]), \
             patch.object(v, "load_env_files"), patch.object(v, "check_setup", return_value=True), \
             patch.object(v, "run_agentic_probe", return_value=1) as probe:
            with self.assertRaises(SystemExit) as code:
                v.main()
            self.assertEqual(code.exception.code, 1)
            probe.assert_called_once()

    def test_delayed_result_and_low_resolution(self):
        client = self.client(NS(id="test", status="in_progress", steps=[]))
        client.interactions.get.return_value = completed()
        result = self.run_phase(client, low_res=True)
        self.assertEqual(str(result), "Normal report")
        self.assertEqual(client.interactions.create.call_args.kwargs["input"][0]["resolution"], "low")
        client.interactions.get.assert_called_once_with("test", timeout=30)

    def test_timeout_cancels_without_resubmit(self):
        pending = NS(id="test", status="in_progress", steps=[])
        client = self.client(pending)
        client.interactions.get.return_value = pending
        with self.assertRaisesRegex(RuntimeError, "no automatic resubmission"):
            self.run_phase(client, max_polls=2)
        self.assertEqual(client.interactions.create.call_count, 1)
        self.assertEqual(client.interactions.get.call_count, 2)
        client.interactions.cancel.assert_called_once()

    def test_poll_error_is_not_capacity_retry(self):
        client = self.client(NS(id="test", status="in_progress", steps=[]))
        client.interactions.get.side_effect = RuntimeError("503 UNAVAILABLE")
        with self.assertRaises(RuntimeError) as result:
            self.run_phase(client)
        self.assertFalse(v.is_transient_capacity_error(result.exception))
        self.assertEqual(result.exception.evidence["interaction_id"], "test")
        self.assertIn("503", result.exception.evidence["poll_error"])
        self.assertEqual(result.exception.evidence["cancellation"], "requested")

    def test_terminal_states_and_missing_evidence(self):
        for status in ("failed", "cancelled", "requires_action", None):
            response = completed()
            response.status = status
            with self.subTest(status=status), self.assertRaises(RuntimeError):
                self.run_phase(self.client(response))
        with self.assertRaisesRegex(RuntimeError, "evidence"):
            self.run_phase(self.client(completed(steps=False)), processing="agentic")
        with self.assertRaisesRegex(RuntimeError, "empty"):
            self.run_phase(self.client(completed(text="")))

    def test_clip_rejected_before_call(self):
        client = self.client()
        with self.assertRaisesRegex(ValueError, "hard --start/--end"):
            self.run_phase(client, start="0s")
        client.interactions.create.assert_not_called()

    def test_absent_and_multiline_custom_request(self):
        defs = v.selected_phase_defs(True, True, True)
        baseline = v.build_effective_prompts(defs, "Title", "01:00")
        for value in ("", " ", "\n\t"):
            self.assertEqual(v.build_effective_prompts(defs, "Title", "01:00", value), baseline)
        request = "Also explain the chart.\nCompare the two examples."
        phases = v.build_effective_prompts(defs, "Title", "01:00", request)
        self.assertIn(request, phases[0]["prompt"])
        self.assertEqual(phases[1:], baseline[1:])
        self.assertIn(baseline[0]["prompt"], phases[0]["prompt"])
        policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        result = "Main content\n\n## Your Specific Request\n\nThe chart shows X."
        runner = Mock(return_value=result)
        results, errors, attempts, models = v.execute_phases(phases[:1], runner, policy)
        self.assertEqual(runner.call_count, 1)
        report = v.compile_report("Title", "01:00", "url", "learn", policy,
                                  ["procedure"], results, errors, attempts, models, request)
        self.assertEqual(report.count(v.CUSTOM_HEADING), 1)
        self.assertIn("Main content", report)
        self.assertIn("The chart shows X.", report)
        plain = v.compile_report("Title", "01:00", "url", "learn", policy,
                                 ["procedure"], {"procedure": "Main"}, [], [], {})
        self.assertNotIn(v.CUSTOM_HEADING, plain)

    def test_missing_custom_answer_is_failure(self):
        pd = v.build_effective_prompts(v.selected_phase_defs(False, False, False),
                                       "Title", "01:00", "Explain X")[0]
        policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        for text in ("Normal only", "Normal\n## Your Specific Request\n", "## Your Specific Request\nAnswer"):
            runner = Mock(return_value=text)
            result, attempts = v.execute_phase_with_recovery(pd, runner, policy)
            self.assertIsNone(result)
            self.assertEqual(runner.call_count, 1)

    def test_sdk_serialization_and_retry_configuration(self):
        from google import genai
        from google.genai import interactions
        video = interactions.VideoContent(type="video", uri="https://youtu.be/test",
                                          processing="agentic", resolution="low")
        self.assertEqual(video.model_dump()["processing"], "agentic")
        self.assertEqual(video.model_dump()["resolution"], "low")
        with v.create_client("fixture-not-a-real-key") as client:
            self.assertTrue(callable(client.interactions.create))
            self.assertTrue(callable(client.interactions.get))
            self.assertTrue(callable(client.interactions.cancel))

    def test_actual_sdk_http_attempt_counts(self):
        import httpx
        policy = v.resolve_model_policy("free", v.DEFAULT_MODEL, v.DEFAULT_FALLBACK_MODEL)
        pd = v.selected_phase_defs(False, False, False)[0]
        for status, expected in ((429, 1), (503, 4), (401, 1)):
            requests = []
            def respond(request, **kwargs):
                requests.append(request)
                return httpx.Response(status, request=request, json={"error": {
                    "code": status, "message": "fixture error", "status":
                    "UNAVAILABLE" if status == 503 else "RESOURCE_EXHAUSTED"}})
            with self.subTest(status=status), patch.object(httpx.Client, "send", side_effect=respond):
                with v.create_client("fixture-not-a-real-key") as client:
                    result, attempts = v.execute_phase_with_recovery(pd,
                        lambda phase, model: v.run_phase(client, model, "https://youtu.be/test",
                            phase["prompt"], None, None, False), policy, sleeper=lambda _: None)
            self.assertIsNone(result)
            self.assertEqual(len(requests), expected, [(r.method, str(r.url)) for r in requests])
            self.assertEqual(len(attempts), expected)
        with patch.object(httpx.Client, "send", side_effect=httpx.ConnectError("fixture")) as send:
            with v.create_client("fixture-not-a-real-key") as client:
                result, attempts = v.execute_phase_with_recovery(pd,
                    lambda phase, model: v.run_phase(client, model, "https://youtu.be/test",
                        phase["prompt"], None, None, False), policy, sleeper=lambda _: None)
        self.assertEqual(send.call_count, 1)
        self.assertEqual(len(attempts), 1)


if __name__ == "__main__":
    unittest.main()
