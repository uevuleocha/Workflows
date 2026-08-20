# Exact Model Confirmation Gate

Resolves the exact current model once before a first-party durable-artifact write, reuses it during an unchanged session, and safely re-resolves it when the model context changes. Durable-artifact skills call this gate; it does not write their artifacts or provenance itself.

## Related skills

- `tread-lightly` is required only for the rare field-minimized sensitive lookup branch.
- `global-skills-creator` and `global-skills-creator-auto` enforce adoption by future model-writing skills.
