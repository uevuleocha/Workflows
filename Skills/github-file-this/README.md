# GitHub File This

Publishes any GitHub involvement — issues (bugs and enhancements), pull requests, discussions, and comments — after an evidence-currency check, open-and-closed duplicate search, in-chat draft review, explicit approval gate, and redaction pass, then records every successful publication to the workspace GitHub Involvements document in the same pass. Also tracks (passively follows) GitHub posts the user did not create or participate in, recording them with a `passive` marker after explicit approval.

Invoke with `/github-file-this`, `$github-file-this`, "file an issue," "open a GitHub issue," "open a pull request," "comment on this," "track this," or "follow this."

## Related skills

- Requires `report-this` and `finalize-report` for durable outcome reporting.
- Pairs with `github-involvement`, which owns the Involvements document after creation and never files.
- Requires `exact-model-confirmation-gate` before delegated model-attributed report writes.
- Uses `tread-lightly` whenever evidence or targets are credential-adjacent.
