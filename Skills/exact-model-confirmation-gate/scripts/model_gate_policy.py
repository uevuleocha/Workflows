"""Pure policy model for the exact-model confirmation gate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, TypeVar


AMBIGUOUS_LABELS = {
    "claude",
    "codex agent",
    "gpt-5",
    "gpt-5.6",
    "high",
    "low",
    "medium",
    "openai",
    "priority",
}


@dataclass(frozen=True)
class SessionFingerprint:
    agent: str
    task_thread: str
    execution_environment: str
    model_context: str = ""


@dataclass(frozen=True)
class GateCache:
    fingerprint: SessionFingerprint
    model: str
    source: str


@dataclass(frozen=True)
class Decision:
    status: str
    model: Optional[str]
    source: Optional[str]
    cache: Optional[GateCache]
    reason: str


def is_exact_identity(value: Optional[str]) -> bool:
    if value is None:
        return False
    candidate = " ".join(value.split())
    lowered = candidate.casefold()
    if not candidate or lowered == "not recorded" or lowered in AMBIGUOUS_LABELS:
        return False
    if lowered.endswith(" agent"):
        return False
    return any(char.isdigit() for char in candidate) and len(candidate.split()) >= 2


def _ready(fingerprint: SessionFingerprint, model: str, source: str) -> Decision:
    cache = GateCache(fingerprint=fingerprint, model=model, source=source)
    return Decision("ready", model, source, cache, "exact identity established")


def resolve(
    *,
    fingerprint: SessionFingerprint,
    cache: Optional[GateCache] = None,
    runtime_model: Optional[str] = None,
    runtime_authoritative: bool = False,
    user_confirmation: Optional[str] = None,
    user_reported_change: Optional[str] = None,
    interactive: bool = True,
    lookup_model: Optional[str] = None,
    lookup_unavoidable: bool = False,
    lookup_protected: bool = False,
    lookup_current_session: bool = False,
) -> Decision:
    if user_reported_change is not None:
        if is_exact_identity(user_reported_change):
            return _ready(fingerprint, user_reported_change, "user confirmed")
        return Decision("ask_user", None, None, None, "reported change is not exact")

    if runtime_model is not None and runtime_authoritative:
        if is_exact_identity(runtime_model):
            return _ready(fingerprint, runtime_model, "authoritative session")
        return Decision("ask_user", None, None, None, "runtime label is not exact")

    if cache is not None and cache.fingerprint == fingerprint:
        return Decision("ready", cache.model, cache.source, cache, "stable-session reuse")

    if lookup_model is not None:
        if not (lookup_unavoidable and lookup_protected and lookup_current_session):
            return Decision("refuse_lookup", None, None, None, "lookup is unsafe or non-authoritative")
        if is_exact_identity(lookup_model):
            return _ready(fingerprint, lookup_model, "protected current-session lookup")
        return Decision("ask_user" if interactive else "fallback", None if interactive else "Not recorded", None if interactive else "unresolved fallback", None, "lookup did not establish an exact identity")

    if user_confirmation is not None:
        if is_exact_identity(user_confirmation):
            return _ready(fingerprint, user_confirmation, "user confirmed")
        return Decision("ask_user", None, None, None, "confirmation is not exact")

    if interactive:
        return Decision("ask_user", None, None, None, "confirmation required before write")

    return Decision("fallback", "Not recorded", "unresolved fallback", None, "no interactive user and no safe exact identity")


T = TypeVar("T")


def append_only(history: Sequence[T], row: T) -> tuple[T, ...]:
    """Return a new history with one prospective row and never mutate the input."""

    return (*history, row)
