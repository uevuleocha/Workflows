# Workspace Setup

`workspace-setup` sets up a new workspace, restores an existing workspace to parity against the universal standards, or maintains hub-level standards. It inspects the target against the complete setup and parity checklist, uses `set-the-stage` to give the user an evidence-based briefing before any changes, and then supports one-shot or phased execution.

Every child workspace gets its own local clone of the universal standards document under `Archive/Live/Documentation/Personal/AI OS & Knowledge Bases/`. The clone is the skill's statefulness anchor: no clone means no prior baseline exists (the workspace may still be existing — determine workspace age from all evidence, not clone absence alone); clone found means parity update against the known baseline.

## Related skills

- `set-the-stage` — **required**. `workspace-setup` uses it to present the setup/parity briefing before execution. `set-the-stage` remains read-only.
- `global-skills-creator-auto` — created and synced this skill across all agent platforms.
