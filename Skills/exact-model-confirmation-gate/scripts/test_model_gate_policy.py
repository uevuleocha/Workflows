"""Deterministic scenarios required by Prompt 21."""

from __future__ import annotations

import unittest

from model_gate_policy import GateCache, SessionFingerprint, append_only, resolve


class ModelGatePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = SessionFingerprint("Codex Agent", "thread-1", "desktop", "model-slot-a")

    def test_authoritative_runtime_model_available(self) -> None:
        decision = resolve(fingerprint=self.session, runtime_model="GPT-5.6 Sol", runtime_authoritative=True)
        self.assertEqual((decision.status, decision.model, decision.source), ("ready", "GPT-5.6 Sol", "authoritative session"))

    def test_unavailable_model_requires_and_accepts_user_confirmation(self) -> None:
        blocked = resolve(fingerprint=self.session)
        self.assertEqual(blocked.status, "ask_user")
        confirmed = resolve(fingerprint=self.session, user_confirmation="GPT-5.6 Sol")
        self.assertEqual((confirmed.status, confirmed.model), ("ready", "GPT-5.6 Sol"))

    def test_stable_session_reuses_confirmation(self) -> None:
        cache = GateCache(self.session, "GPT-5.6 Sol", "user confirmed")
        decision = resolve(fingerprint=self.session, cache=cache)
        self.assertIs(decision.cache, cache)
        self.assertEqual(decision.reason, "stable-session reuse")

    def test_proactive_user_model_change_is_prospective(self) -> None:
        old = GateCache(self.session, "GPT-5.6 Sol", "user confirmed")
        decision = resolve(fingerprint=self.session, cache=old, user_reported_change="GPT-5.6 Terra")
        self.assertEqual(decision.model, "GPT-5.6 Terra")
        self.assertEqual(old.model, "GPT-5.6 Sol")

    def test_agent_task_or_environment_change_invalidates_cache(self) -> None:
        cache = GateCache(self.session, "GPT-5.6 Sol", "user confirmed")
        variants = (
            SessionFingerprint("Claude Agent", "thread-1", "desktop", "model-slot-a"),
            SessionFingerprint("Codex Agent", "thread-2", "desktop", "model-slot-a"),
            SessionFingerprint("Codex Agent", "thread-1", "cli", "model-slot-a"),
            SessionFingerprint("Codex Agent", "thread-1", "desktop", "model-slot-b"),
        )
        for changed in variants:
            with self.subTest(changed=changed):
                self.assertEqual(resolve(fingerprint=changed, cache=cache).status, "ask_user")

    def test_reasoning_effort_and_other_labels_are_not_model_identity(self) -> None:
        for label in ("Medium", "Priority", "OpenAI", "GPT-5", "Codex Agent"):
            with self.subTest(label=label):
                self.assertEqual(resolve(fingerprint=self.session, user_confirmation=label).status, "ask_user")

    def test_unsafe_file_lookup_is_refused(self) -> None:
        decision = resolve(fingerprint=self.session, lookup_model="GPT-5.6 Sol")
        self.assertEqual(decision.status, "refuse_lookup")

    def test_field_minimized_lookup_requires_tread_lightly_protection(self) -> None:
        decision = resolve(
            fingerprint=self.session,
            lookup_model="GPT-5.6 Sol",
            lookup_unavoidable=True,
            lookup_protected=True,
            lookup_current_session=True,
        )
        self.assertEqual((decision.status, decision.source), ("ready", "protected current-session lookup"))

    def test_unattended_unresolvable_fallback(self) -> None:
        decision = resolve(fingerprint=self.session, interactive=False)
        self.assertEqual((decision.status, decision.model), ("fallback", "Not recorded"))

    def test_history_is_append_only(self) -> None:
        history = ("historical row",)
        updated = append_only(history, "current row")
        self.assertEqual(history, ("historical row",))
        self.assertEqual(updated, ("historical row", "current row"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
