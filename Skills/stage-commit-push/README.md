# Stage Commit Push — Adoption Guide

Deterministic, explicitly invoked stage/commit/push workflow that completes its ordinary safe path end to end once an All or Particular scope is known. It preserves remote safety gates and automatically performs loud pointer-only synchronization when the current repository is a parent hub submodule unless the user opts out; Particular scope governs the nested commit without requiring a second pointer approval.

## Related skills

- `git-diff` — the read-only review pass that naturally precedes this skill.
