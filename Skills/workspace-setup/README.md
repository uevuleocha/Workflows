# Workspace Setup

`workspace-setup` sets up a new workspace, restores an existing workspace to parity against the universal standards, or maintains hub-level standards. It inspects the target against the complete setup and parity checklist, uses `set-the-stage` to give the user an evidence-based briefing before any changes, and then supports one-shot or phased execution.

Every child workspace gets its own local clone of the universal standards document under `Archive/Live/Documentation/Personal/AI OS & Knowledge Bases/`. The clone is the skill's statefulness anchor: no clone means no prior baseline exists (the workspace may still be existing — determine workspace age from all evidence, not clone absence alone); clone found means parity update against the known baseline.

The clone also persists evidence-backed checklist markers and a dated workspace parity status. Stable implementation remains checked while present; recurring checks are reverified on each applicable run; conditional N/A items require a specific local reason.

The Hub source is named `N.) Universal Workspace Standards + Setup & Parity Checklist_Master.md`. Every child clone is created as `N.) Universal Workspace Standards + Setup & Parity Checklist_{Workspace Name} Clone.md`, using the next workspace-local number and the canonical workspace name.

Platform parity uses root `.codex/` for Codex's harness-managed `config.toml` and workspace `settings.local.json`; `.agents/` contains only Antigravity, Hermes, and Z Code coordination homes.

Any actual instruction text supplied by the Hub standard or another authoritative setup source is copied verbatim; only marked placeholders or expressly adaptable text may change.

## Related skills

- `set-the-stage` — **required**. `workspace-setup` uses it to present the setup/parity briefing before execution. `set-the-stage` remains read-only.
- `global-skills-creator-auto` — created and synced this skill across all agent platforms.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.
