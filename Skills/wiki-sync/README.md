# Wiki Sync

Maintains an existing schema-driven workspace wiki. It detects and synthesizes
new or changed declared sources, updates whatever page taxonomy the active
schema defines, refreshes navigation and logs, and verifies that sources stayed
unchanged. Large ingests may be proposed as batches only with user confirmation;
user-requested order or one-shot execution remains authoritative. Historical-
record groups may use mine-and-fold plus light provenance pages only after the
agent names the group and the user explicitly agrees.

## Related skills

- `wiki-this` — creates the initial wiki, schema, source-root declaration, and
  workspace pointers.

