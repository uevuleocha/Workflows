---
name: exact-model-confirmation-gate
description: Resolve and cache the exact current model once per stable session before a first-party durable-artifact write, block once for user confirmation when authoritative session evidence is unavailable, invalidate prospectively when model context changes, and protect any unavoidable file-backed lookup with tread-lightly. Use when a durable-artifact skill calls this gate, when the user invokes /exact-model-confirmation-gate, or when exact model provenance must be established safely before writing.
---

# Exact Model Confirmation Gate

Establish one truthful exact-model identity before the first model-attributed write to a first-party durable artifact, reuse it throughout an unchanged session, and re-resolve it only when the model context changes. This skill owns model resolution and session-cache behavior; the calling artifact skill retains content, provenance placement, history, lifecycle, and write ownership.

## Project Contract

Obey the active workspace contract, permissions, and secret-handling rules. This gate narrows model discovery and never authorizes a durable-artifact write that the caller could not otherwise perform.

## Invocation

Invoke this skill:

- before a first-party durable-artifact workflow creates or materially edits its first artifact in the current session;
- before a caller writes a new `Original writing LLM` or current-run Agent Change Log `Model` value;
- when the user reports that the current model changed; or
- when authoritative evidence shows that the model, agent, task or thread, or execution environment changed.

Direct triggers include `/exact-model-confirmation-gate`, `use exact-model-confirmation-gate`, and clear equivalents asking to confirm the exact model before durable writing.

## Stable Session

A stable session is the unchanged combination of:

- exact model context;
- acting agent family;
- current task or thread; and
- execution environment.

Keep the confirmed identity in current session context. Do not create a configuration file, hidden cache, durable artifact, transcript note, or workspace record merely to persist the cache. Later callers in the same unchanged session reuse the established identity without asking again.

## Gate Workflow

Run these steps before the caller's first durable-artifact write:

1. Check whether the current session already carries a gate result for the same stable-session context. If so, return it unchanged.
2. Otherwise inspect only authoritative current runtime or session metadata supplied by the active platform, task, or session. A current-model field is valid evidence; a model catalog, provider label, agent name, remembered value from another task, or configured default is not.
3. If authoritative evidence supplies a full exact identity, cache and return it.
4. If authoritative evidence cannot safely establish the exact identity and an interactive user is available, stop the pending artifact write and ask once: `What exact model is running this chat?` Validate the answer, then cache and return it.
5. If the user cannot identify the model, no user is available, or the identity remains safely unresolvable after the permitted attempt, return `Not recorded` as the honest fallback.

The gate returns the exact model identity and its source category: `authoritative session`, `user confirmed`, `protected current-session lookup`, or `unresolved fallback`. It never substitutes the acting-agent label for the model.

## Exact Identity Rules

- Accept full identities such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`.
- Reject family-only labels such as `GPT-5`, provider-only labels such as `OpenAI`, agent labels such as `Codex Agent`, and reasoning-effort or service-tier labels such as `Medium` or `Priority`.
- Keep reasoning effort, service tier, provider, and agent family separate from model identity.
- Treat `Not recorded` as a fallback result, never as a user-confirmed or authoritative exact identity.

## Invalidation

Invalidate the cached identity prospectively when:

- the user says the model changed, in which case validate and use the newly supplied identity immediately;
- authoritative evidence reports a different exact model;
- the acting agent changes;
- the task or thread changes; or
- the execution environment changes.

After invalidation, resolve again and ask once only if authoritative current-session evidence remains unavailable. Never rewrite earlier provenance or change-log rows because the current identity changed.

## Sensitive Lookup Boundary

Do not inspect configuration, environment, credential stores, logs, transcripts, or unrelated workspace files by default. A configured model is not proof of the current runtime model.

Only when the active platform genuinely requires a file-backed lookup, the lookup is necessary to identify the current session, and it can be field-minimized safely:

1. invoke `tread-lightly` for that lookup;
2. request only the single required model field;
3. never display, copy, search, diff, or log surrounding contents; and
4. reject the result if it cannot be tied authoritatively to the current session.

Callers do not acquire a blanket `tread-lightly` dependency. This gate alone owns the optional sensitive branch.

## Caller Contract

The calling durable-artifact skill must:

- invoke this gate before its first current-session model-attributed write;
- stop before writing while the gate is waiting for user confirmation;
- use the returned exact identity for all later writes in the same stable session;
- preserve agent family and model in separate provenance fields;
- preserve all historical provenance and change-log rows; and
- fail closed if this dependency is unavailable and no safe gate result already exists.

Copying or global synchronization is transport, not a new artifact-writing event and not a new authorship identity.

## Boundaries

Do:

- resolve from current-session evidence first;
- ask once and block the first write when interactive confirmation is needed;
- reuse the result during an unchanged session;
- invalidate prospectively on context change; and
- return `Not recorded` only for the defined unresolved cases.

Do not:

- infer an exact model from an agent, provider, family, effort, tier, catalog, or stale default;
- repeatedly ask during an unchanged session;
- persist a hidden cross-session cache;
- rummage through sensitive or unrelated files;
- expose more than one protected model field; or
- rewrite historical attribution.

## Deterministic Validation

Run:

```text
python -X utf8 scripts/test_model_gate_policy.py
python -X utf8 scripts/validate_carriers.py --workspace-root <Workflows-root>
```

The policy suite must cover authoritative runtime resolution, user confirmation, stable-session reuse, proactive model change, agent/task/environment invalidation, reasoning-effort exclusion, unsafe lookup refusal, protected field-minimized lookup, unattended fallback, and append-only history.

The carrier validator must confirm the complete expected carrier set uses the byte-identical canonical caller block from `references/canonical-caller-block.md`, every carrier README names this dependency, both creator-governance skills enforce future adoption, and no unexpected carrier variant exists.

## Validation

When creating or updating this skill:

- run both deterministic validation commands above and require exit `0`;
- validate the folder with the official `quick_validate.py` in Python UTF-8 mode;
- confirm this skill creates no durable artifact and writes no Markdown table, so provenance and table-aligner integrations remain intentionally exempt;
- confirm `tread-lightly` appears only on the optional file-backed lookup branch; and
- confirm local and global copies have recursive byte parity after synchronization.
