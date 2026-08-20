# Coverage Reconciliation Contract

`wiki-sync` uses `scripts/reconcile_wiki_sources.py` as a read-only coverage gate. The helper receives all workspace-specific meaning through a versioned JSON contract declared or referenced by the active `wiki/wiki-schema.md`. It never assumes `Archive/`, `Skills/`, a page taxonomy, or a particular provenance page type.

## Contract

```json
{
  "version": 1,
  "case_sensitive_paths": true,
  "nested_workspace_markers": ["CLAUDE.md", "AGENTS.md", ".git"],
  "allowed_skip_reasons": ["schema-excluded", "user-deferred"],
  "source_roots": [
    {
      "id": "archive",
      "path": "Archive",
      "identity_mode": "file",
      "include": ["*", "**/*"],
      "exclude": []
    },
    {
      "id": "skills",
      "path": "Skills",
      "identity_mode": "immediate-directory",
      "include": ["*"],
      "exclude": []
    }
  ],
  "wiki": {
    "path": "wiki",
    "page_globs": ["*.md", "**/*.md"],
    "exclude": ["index.md", "log.md", "wiki-schema.md", "unresolved-verification.md"],
    "provenance_field": "sources"
  }
}
```

All paths are workspace-relative and must remain inside the resolved workspace. `identity_mode: file` makes every included file an eligible identity. `identity_mode: immediate-directory` makes every included immediate child directory one semantic identity and maps provenance for files beneath that directory back to the bundle. A schema needing another identity model must define and implement that model explicitly before claiming deterministic full coverage; the helper must not guess.

Exclusions and nested-workspace markers are applied during enumeration. Marker comparison is exact-case. `case_sensitive_paths` controls identity and provenance path comparison and must be chosen by the schema rather than inferred from the operating system.

The helper reads the schema-designated frontmatter field from every included wiki page. It ignores provenance outside declared roots, reports provenance inside a declared root that no longer resolves to an eligible identity as stale, and treats malformed in-scope provenance as an operational error.

## Manifest

```json
{
  "version": 1,
  "entries": [
    {
      "identity": "archive:Archive/Live/Example.md",
      "status": "represented-unchanged"
    },
    {
      "identity": "archive:Archive/Live/Renamed.md",
      "status": "changed",
      "previous_paths": ["Archive/Live/Old Name.md"]
    }
  ]
}
```

Every selected identity appears exactly once with one status: `represented-unchanged`, `new`, `changed`, `uncertain`, or `skipped`. `skipped` also requires a `skip_reason` listed by the contract. `previous_paths` explains stale provenance for a renamed or moved identity; it does not establish content equality by itself.

The agent remains responsible for the evidence supporting `represented-unchanged`, `changed`, and `uncertain`. Use hashes or version-control comparison when timestamps are unreliable. The helper proves coverage and status-claim integrity, not semantic synthesis quality.

## Commands And Exit Codes

```text
python -X utf8 scripts/reconcile_wiki_sources.py inventory --workspace <root> --contract <contract.json>
python -X utf8 scripts/reconcile_wiki_sources.py check --workspace <root> --contract <contract.json> --manifest <manifest.json> --scope workspace-full --phase before --claim none
python -X utf8 scripts/reconcile_wiki_sources.py check --workspace <root> --contract <contract.json> --manifest <manifest.json> --scope workspace-full --phase after --claim workspace-synced
```

Use `root-full` with exactly one `--root-id`, or `named-source` with one or more `--source-id`. The `before` phase requires new identities to lack current provenance and permits moved-source stale paths only when `previous_paths` explains them. The `after` phase requires new and changed identities to have current provenance and requires all stale provenance to be repaired. Claims are `workspace-synced`, `root-synced`, or `scoped-synced`; each is valid only in the `after` phase and only for its matching scope. A synchronized status claim also requires complete reconciliation with zero uncertain and zero skipped identities.

Exit `0` means the inventory completed or the manifest passed the requested gate. Exit `1` means coverage or claim findings exist. Exit `2` means the contract, manifest, path, encoding, or runtime operation failed, so validity is unknown. JSON results go to stdout and operational errors go to stderr.

Run the check once before manifest confirmation and again after synthesis against a freshly enumerated source state. The second pass catches sources introduced or moved during the run.
