# Stage Commit Push — Adoption Guide

Deterministic, explicitly invoked stage/commit/push workflow with scoped staging, remote safety gates, and optional user-approved pointer-only synchronization when the current repository is a parent hub submodule. Nothing is pushed without the gates passing.

## Related skills

- `git-diff` — the read-only review pass that naturally precedes this skill.
