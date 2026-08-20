# Finalize Plan — Adoption Guide

Finalizes active implementation plans: verifies completion evidence, applies completed styling, and renames `_plan_active.md` to `_plan_finalized.md`.

## Dependency

`finalize-plan` has a soft dependency on the `prompt-contracts` skill. It reads and verifies the Prompt Contract that `plan-this` embedded in the plan — walking each DEFINITION OF DONE item and FAILURE condition before finalizing (see the `## Prompt Contract Review` section in `SKILL.md`). It does not need to invoke `prompt-contracts` itself, and it falls back gracefully for plans that predate the contract convention.

**If you adopted `finalize-plan` from Uzo (U-Z-O), adopt it together with `plan-this` and `prompt-contracts`.** The three form the plan lifecycle: `plan-this` writes the contract, `prompt-contracts` defines its shape, and `finalize-plan` verifies against it.

`finalize-plan` preserves a plan's complete `N.) ` prefix — **including any lowercase child suffix** (`Na.)`, `Nb.)`, …) — through finalization and through reopening. It never strips or renumbers a child prefix.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill pairs with `plan-this` and understands the
`prompt-contracts` contract format; make sure all three are installed in the same agent installs
(Codex / Claude / Antigravity). Use my OS path conventions and ask before creating missing folders.
```

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
