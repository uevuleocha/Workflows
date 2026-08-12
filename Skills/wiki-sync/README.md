# Wiki Sync

Maintains an existing schema-driven workspace wiki. It detects and synthesizes new or changed declared sources, updates whatever page taxonomy the active schema defines, refreshes navigation and logs, and verifies that sources stayed unchanged. Large ingests may be proposed as batches only with user confirmation; user-requested order or one-shot execution remains authoritative. Detected historical-record groups always use mine-and-fold plus light provenance pages: that treatment is the mandatory, compulsory default and is applied without asking. A full schema-defined source page for such a group is the one exception, allowed only when the agent has a specific strong reason, stops, states it, and receives explicit user permission; if the user declines, the default applies immediately and the run continues.

## Related skills

- `wiki-this` — creates the initial wiki, schema, source-root declaration, and workspace pointers.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

