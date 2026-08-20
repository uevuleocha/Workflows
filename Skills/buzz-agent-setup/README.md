# Buzz Agent Setup — Adoption Guide

Generates the complete hand-entered configuration for a Buzz managed agent: dialog fields, agent instructions that always open with the mandatory model-identity line (with the stale-hardcoded-model warning), a curated under-2 KB `core` memory built through a written admission test, and optional cold memory slugs. Branches on harness class (in-process runner vs external-CLI) rather than names, carries the new-lab recipe with the `OPENAI_COMPAT_BASE_URL` warning, and never enumerates labs, models, endpoints, context windows, or harness names. Output only — no Buzz CLI, no network, no file writes, no secrets.

Invoke with `/buzz-agent-setup` or "set up a new Buzz agent".

## Related skills

- `buzz-channel-description` — owns channel descriptions; this skill deliberately does not produce them.
- Standalone otherwise: no scripts, no network, no dependencies.
