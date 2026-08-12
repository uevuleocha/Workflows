# Wiki This

Sets up a schema-driven plain-Markdown wiki in the current workspace. It helps the user choose source roots and a context-appropriate taxonomy, creates the wiki scaffold, and adds root contract pointers without touching source files or creating an Obsidian vault. It adapts the established Hub schema as an example, surfaces the wiki-follows-sources track/ignore choice, and confirms any proposed batching before an optional first sync. It also proposes a history location and light-history page format as part of the taxonomy, because `wiki-sync` applies mine-and-fold plus light history to detected historical groups as its mandatory default and needs somewhere declared to file them.

## Related skills

- `wiki-sync` — maintains and ingests an existing schema-governed wiki.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

