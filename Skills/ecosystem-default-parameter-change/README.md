# Ecosystem Default Parameter Change

Explicitly runs the safe cTrader disappear/reappear build cycle for named cAlgo `[Parameter]` defaults. It supports two-step and source-clean three-step modes, agent-run live cAlgo builds by default or user-run builds when requested, full workspace-diff verification, final cAlgo-to-workspace synchronization, indicators, and honest cBot persistence reporting.

## Related skills

- `ecosystem-calgo-greenlight` - uses this skill whenever its approved work changes existing cAlgo parameter defaults.
- `global-sync` - propagates this local master to all configured platforms.
- `inspect` - audits source, diffs, and build evidence.
- `push-tool` - may synchronize the verified final live cAlgo source to its `Tools\Sources\` workspace mirror.
