# Markdown Table Aligner

Checks and deterministically pads Markdown pipe tables using Unicode display width while preserving content and bytes outside proven tables. Invoke it after table content is authored and before a Markdown artifact is saved or serialized.

A clean check is authoritative for monospaced Unicode display-column alignment; renderer-specific pixel offsets are not padding failures.

## Related skills

- Called by applicable durable-artifact authoring and finalization skills.
- Requires Python plus `wcwidth` with Unicode `17.0.0` data.
- Pairs with `global-sync` for cross-agent installation.
