# Workflows

This workspace is Uzo's local-master home for reusable agent skills.

It holds local master copies of reusable skills, including skills created from scratch, skills adapted from other people's work, and skills brought in directly for use in personal workflows.

The `Skills/` directory is authoritative. New skills and skill changes are created and validated here before optional propagation to global agent locations. A later reviewed sync is the preferred default; explicit same-pass authorization permits local creation, validation, and global synchronization in one pass.

Global sync targets may include Codex, Claude, Antigravity, Hermes, and zCode, but their installed copies are transport destinations rather than independent sources.

Workflows is an independent Git repository registered in the Uzzys Universe Hub as the `MilkyWay/Tools/Workflows` submodule. This repository owns its skill source and private durable history; the Hub owns the wider AI OS map.

## Structure

- `Skills/` - local master copies of reusable skills
- `Archive/` - private durable artifacts organized by Live and Historical lifecycle state
- `wiki/` - private schema-driven knowledge map; `wiki/wiki-schema.md` is its rulebook
- `.agents/` - coordination settings for Antigravity, Hermes, and Z Code
- `.codex/` - Codex-owned `config.toml` plus workspace-local `settings.local.json`
- `.claude/`, `.obsidian/` - platform-owned local state where required
- `tmp/` - disposable scratch space; nothing durable belongs here
- `CLAUDE.md` - canonical workspace contract and operating instructions
- `AGENTS.md` - compatibility wrapper for agent runtimes

This repository may become public. Keep secrets, local platform settings, `Archive/`, `wiki/`, and `tmp/` untracked, and run a privacy audit before public exposure.
