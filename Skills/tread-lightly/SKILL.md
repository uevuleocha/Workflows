---
name: tread-lightly
description: Protect secrets and sensitive data while reading, inspecting, validating, editing, or otherwise handling .env files, configuration files, credentials, tokens, passwords, API keys, private keys, authentication material, or files that may contain them. Use when the user explicitly invokes Tread Lightly and automatically whenever a task touches a sensitive or potentially sensitive file, secret store, command, output, log, patch, or Git operation.
---

# Tread Lightly

Handle sensitive material with minimal access and no unnecessary exposure. This is a turn-scoped safety overlay, not a persistent workflow.

## Project Contract

Obey the active workspace contract, permissions, and safety rules. Tread Lightly narrows handling; it never grants access, overrides a stricter rule, or authorizes secret transmission.

## Activation

Activate for the current turn when either condition applies:

- the user explicitly invokes `/tread-lightly`, `$tread-lightly`, `use tread-lightly`, `tread lightly`, or a clear equivalent naming this skill; or
- the task reads, inspects, validates, edits, copies, searches, stages, commits, transmits, or otherwise handles material that contains or may contain secrets or sensitive data.

Automatic triggers include:

- `.env` files and variants such as `.env.local` or `.env.production`;
- configuration or settings files that may hold credentials;
- credential stores, cloud profiles, private keys, certificates, SSH material, authentication exports, CI/CD variables, secret-manager output, database dumps, backups, browser exports, and logs with possible credentials;
- commands, patches, diffs, screenshots, or tool results that could reveal a password, token, API key, connection string, cookie, session identifier, recovery code, or other authentication material.

Decide from the filename, path, task purpose, file type, and known context before reading content whenever possible. Treat uncertain material as sensitive until shown otherwise without exposing it. For every file you intend to touch, run the formal triage step in Scope And Triage before opening content whenever possible.

At first activation in a turn, briefly say:

```text
Tread Lightly is active. I’ll inspect only what is necessary and will not
reproduce sensitive values.
```

Do not repeat that notice for every file or command in the same turn.

## Scope And Triage

Invocation is a request to triage, not an assertion that secrets are present. When the user invokes `tread-lightly` on a target, they are asking you to determine which parts of that target are sensitive and to handle those parts carefully. Never infer from the invocation alone that a secret exists, never refuse or narrow work merely because the skill is active, and never ask the user to confirm sensitivity that you can determine yourself.

Sensitivity is assessed per file, never per target. When the invocation target is a directory, workspace, repository, archive, or any other multi-file scope, classify each file you actually intend to touch. A sensitive file inside a directory does not make its siblings sensitive. Handling restrictions attach to the individual file, and through it to its values, never to the enclosing folder.

Classify each file you intend to touch into exactly one of three verdicts, decided from the filename, extension, path, directory role, known product conventions, and task purpose, before opening content wherever that is possible:

- **Sensitive** -- apply the full Core Handling Rules to this file.
- **Not sensitive** -- handle it normally and completely, with no restriction beyond the standing no-reproduction rule on any value that turns out to be a secret.
- **Uncertain** -- resolve it cheaply, per the resolution path below, before defaulting to caution.

The not-sensitive verdict grants ordinary, full handling. Read such files completely, quote them, summarize them, include them in reports, and diff them as any normal task would. Logs, build stamps, version manifests, licenses, process listings, lockfiles, and similar operational metadata are ordinarily in this class. Do not thin your output, hedge your findings, or seek permission for these files merely because `tread-lightly` is active on the surrounding scope.

Resolve the uncertain verdict cheaply so it does not collapse into blanket caution on large targets. Before treating an uncertain file as sensitive, prefer a non-echoing structural probe that reveals shape without values: parse validity, top-level key names, entry counts, schema markers, or the presence or absence of an expected field. If the probe shows no credential-bearing structure, reclassify the file as not sensitive and proceed normally. If it shows credential-bearing structure, or the probe cannot be run safely, keep the sensitive verdict. Genuinely unresolved material remains sensitive until shown otherwise, and resolution itself must never expose a value.

### Where Credentials Actually Hide

When probing a file's structure, you are looking for credential-bearing shape. Look for these carriers:

- **URLs and endpoints** carrying a credential in a query string (`?token=...`, `?key=...`) or in userinfo (`https://user:pass@host`). The field's key name is typically `url`, `endpoint`, `uri`, `server`, or `host`, none of which hint at a secret.
- **Connection strings and DSNs** with an embedded password, whether in key-value form or packed into a single URI.
- **Header values** -- `Authorization`, `Proxy-Authorization`, `Cookie`, `Set-Cookie`, `X-Api-Key`, and similar -- wherever headers are configured or logged.
- **High-entropy opaque values with no vendor prefix**: base64 or hex blobs, JWTs, random-looking strings. No prefix-based pattern will catch these, because there is no prefix to match.
- **Private key and certificate bodies**, including PEM blocks and their base64 payloads, whether inline or referenced.
- **Nested structures**, where a credential sits several levels inside a JSON or TOML value rather than at a top-level assignment, and so is missed by any check that only inspects top-level keys.

The governing principle, because no list of carriers can ever be complete: **a field's key name is not a reliable signal of whether it carries a credential.** Classify by the shape and role of the value, not by whether the key is named `token`, `secret`, or `password`. A credential in a field named `url` is still a credential; a field named `token_endpoint` may hold no secret at all.

This list is illustrative, not exhaustive. An unlisted carrier is still a carrier, and encountering one is not a reason to treat the file as safe.

This subsection guides **how to probe** a file, not **what to classify as sensitive**. It does not widen the sensitivity verdict. A file containing an ordinary URL with no credential in it is not sensitive because a URL can theoretically carry one -- classify it on what it actually holds, and give a not-sensitive file the full normal handling granted above.

Triage stays invisible unless it matters. Do not narrate a file-by-file classification table in ordinary responses. Report only the classifications that affected what the user received: a file left unread, a finding reported with its value withheld, or an action declined.

## Turn-Scoped Mode Footer

End every response produced during an active Tread Lightly turn with:

```text
Mode = Tread Lightly
```

If another mode is active in that response, follow the workspace's multi-mode footer rule and include `Tread Lightly` exactly once.

Every response that carries the footer must also disclose, in one short phrase, why the mode is active on that turn. Attach the disclosure as a parenthetical on the same line as the `Tread Lightly` footer entry, in one of the fixed forms:

- `Mode = Tread Lightly (explicit invocation)` -- the user invoked the skill this turn;
- `Mode = Tread Lightly (re-armed: <category>)` -- automatic re-arm because this turn handles a named category of sensitive material, such as a credential store, an `.env` file, or a secret-bearing log; or
- `Mode = Tread Lightly (continuation: <short reason>)` -- a multi-turn task that keeps touching such material.

In a multi-mode footer, attach the same parenthetical to the `Tread Lightly` entry. The disclosure names the trigger category, may name the file when the filename itself is not sensitive, and never reproduces a value.

The footer form defined in this skill is authoritative for the `Tread Lightly` entry and overrules the generic `Mode = <Mode Name>` shape defined in the workspace canonical contract (`CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). The workspace contract defines the general default; a mode-emitting skill that specifies its own richer footer form governs its own entry. Follow the parenthetical disclosure form defined here and never strip, shorten, or normalize it to match the generic shape. In a multi-mode footer, other modes keep whatever form their own skills define, and `Tread Lightly` keeps this one. This rule is self-contained: it remains correct after global installation on any of the five agent platforms without depending on a matching edit in any workspace contract file.

The mode ends when that response is sent. It does not persist merely because it appeared previously. Reactivate it independently on every later turn that again handles sensitive material. Therefore, five consecutive sensitive turns show the footer five times; the first later non-sensitive turn does not. Repeated appearance across consecutive turns is expected and correct when each turn independently touches sensitive material, and it is not evidence of a stuck mode. The agent is responsible for making the distinction visible through the disclosure rather than leaving the user to infer it.

When a turn follows one that carried the footer but does not itself handle sensitive material, the absent footer is itself information. If the preceding turn carried it and the user could plausibly expect it to continue, state briefly in the response body that the mode did not re-arm this turn and why, for example: "Tread Lightly did not re-arm this turn: no sensitive material was handled."

Explicit invocation activates the footer for that turn even if no secret is ultimately found.

## Core Handling Rules

### 1. Minimize Access

- Inspect only what the task requires.
- Prefer existence, size, line count, permissions, syntax, key presence, or structure emitted without values, over plaintext values.
- Read a specific field or bounded region instead of a whole file when possible.
- Do not browse neighboring sensitive files without a task-specific need.
- Do not ask the user to paste a secret into chat.

### 2. Prevent Reproduction And Persistence

Never intentionally place a sensitive value into:

- assistant messages, reasoning summaries, mode notices, or questions;
- tool calls, command-line arguments, terminal output, shell history, process listings, logs, error messages, or transcripts;
- patches, diffs, source files, comments, documentation, plans, reports, summaries, screenshots, clipboard content, fixtures, or test snapshots;
- commits, branches, pull requests, issues, build artifacts, caches, or other durable storage.

Do not quote, summarize, transform, partially reveal, or repeat a real secret. Masking only part of a value can still make it identifiable; prefer statements such as `credential present`, `value missing`, `format valid`, or `redacted`.

Treat secret-looking test data as real until proven otherwise.

### 3. Prevent Unnecessary Transmission

- Do not send sensitive values to subagents, plugins, connectors, web services, external APIs, issue trackers, or remote validation services.
- Do not upload or attach a sensitive file when a local, non-echoing check can answer the question.
- If the task genuinely requires a specific external transfer, explain the destination and purpose and obtain explicit authorization for that transfer. Share only the minimum necessary through an approved secure mechanism.

### 4. Use Non-Echoing Operations

- Avoid whole-file display commands such as `cat`, `type`, or `Get-Content` against sensitive files.
- Avoid broad searches whose matching lines would print values.

Echoing a file's contents through a redaction filter, sanitizer, masking regex, or any other output-side transform is **not** an acceptable substitute for reading only what the task requires. This is not a lesser form of compliance; it is a different and unsafe method. An output-side filter is a denylist, and a denylist catches only the secret shapes you thought of in advance. Whether a value survives the filter depends on whether you guessed its shape correctly -- which is exactly the judgement this rule exists to remove. A credential whose key name you did not anticipate, or whose format carries no prefix you pattern-matched on, passes straight through and is exposed. Do not reason that filtered output is safe output.

Do this instead. Emit structure without values: key names, section names, parse validity, entry counts, and the presence or absence of an expected field. When the task genuinely needs a value, read that specific field individually -- not the file it lives in.

This prohibition is not limited to `cat`, `type`, and `Get-Content`. It covers any operation whose output includes file contents the task did not require: broad content searches, full-file diffs, whole-config dumps pasted into a report or summary, and screenshots of an open file. The test is whether unneeded contents reach any output surface, not which command produced them.

- Avoid secret-bearing command arguments, inline environment assignments, or commands that echo expanded variables.
- Use a local parser or command that reads silently and emits only safe, bounded metadata.
- Suppress error output that could include source lines or values. Suppress it rather than filtering it, for the reason given below -- a filter over error text is the same denylist gamble.
- Never place a real secret in an `apply_patch` patch or another edit payload that becomes durable tool output. Use a secure non-echoing local edit mechanism when one is authorized and available. Otherwise ask the user to perform the value change through their secure environment.

## Safe Editing And Validation

When editing a potentially sensitive file:

1. Identify the exact requested key or structural change without displaying unrelated content.
2. Preserve existing secret values whenever possible.
3. Change only the requested structure or non-secret field.
4. Use placeholders such as `YOUR_API_KEY_HERE` in examples and `.env.example` files.
5. Validate with a non-echoing parser or a result limited to safe status.
6. Report the outcome without values.

Do not claim a secret is valid merely because it exists or matches a shape. Network authentication tests can transmit the secret and require normal task authorization plus the narrowest safe destination.

## Git Safety

For a sensitive or potentially sensitive file:

- check ignored or tracked status without displaying contents;
- never use a content diff as the first inspection method;
- never stage, commit, or push the real file or its values;
- use a sanitized example file containing names and placeholders when useful;
- if the real file is already tracked, report that fact without showing a diff, stop further propagation, and recommend removal from tracking and credential rotation as appropriate;
- do not rewrite Git history, remove files, or rotate credentials without explicit authorization.

## Reporting

Report only safe facts needed for the task, for example:

- file exists or is missing;
- expected variable is present or absent;
- duplicate keys were found;
- syntax is valid or invalid;
- sensitive file is ignored, untracked, or already tracked;
- a requested non-secret structural change was completed.

Do not include the sensitive value, a reversible encoding, a secret-bearing source line, or enough fragments to reconstruct it. Key names, filenames, and paths can also be sensitive; redact them when they are not necessary to the user's decision.

## Accidental Exposure

If a sensitive value appears unexpectedly:

1. Stop output or propagation immediately.
2. Do not repeat the value, even while explaining the incident.
3. Identify only the exposure surface, such as terminal output, transcript, patch, log, or commit.
4. Contain further spread using safe, authorized actions.
5. Tell the user what category of credential may be affected and recommend revocation or rotation.
6. Do not delete records, rewrite history, revoke, or rotate anything without explicit permission.

Never claim that prior transcript or tool exposure has been erased unless the relevant system provides verified deletion evidence.

## Completion Check

Before ending an active turn, confirm internally:

- access was limited to the minimum necessary;
- no sensitive value was reproduced in the response or tool output;
- no unauthorized external transfer or durable copy occurred;
- any Git or edit operation avoided secret-bearing diffs and patches;
- the user received a useful result containing no sensitive values; and
- the footer includes `Tread Lightly` exactly once.

## Markdown Table Alignment

Every Markdown table this skill writes or causes to be written must be visually pipe-aligned. Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view.

Rendered visual alignment is authoritative; raw `|` indices are diagnostic only, because Unicode display width (emoji, arrows, wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. When a table exceeds approximately 120 characters in total width, narrow the columns and move detail to notes so it renders on one line without word-wrapping.

## Safe Model Field Extraction

When exact model attribution cannot be resolved from current runtime or session metadata and a local JSON or TOML configuration lookup is genuinely unavoidable, use `scripts/extract_model_field.py <config> --key <dotted.model.key>`. It parses locally and emits only one validated model identifier. Never display the configuration, search its contents broadly, or pass a credential-bearing field to the extractor.

Prefer current runtime or session metadata over configuration. A safely extracted field is evidence only for the configuration's value; do not treat stale configuration as proof of the current runtime model. If the field is missing, unsafe, or cannot be tied to the current session, use `Not recorded` rather than guessing.

## Validation

When creating or updating this skill:

- run `python -X utf8 scripts/test_extract_model_field.py` and require exit `0`;
- confirm the synthetic token-bearing fixtures emit only the requested model identifier and never echo the unrelated value;
- validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`), reading pass/fail from the process exit code with stdout and stderr captured separately;
- confirm the `## Markdown Table Alignment` section above remains present in full;
- confirm the three-verdict triage step and the footer trigger disclosure remain in force;
- confirm the prohibition on redaction-on-output remains present in `Core Handling Rules` section 4, names the denylist reasoning error, states the affirmative method, and extends beyond display commands;
- confirm `Where Credentials Actually Hide` remains present with all six carrier categories, the key-name-is-not-a-signal principle, and the illustrative-not-exhaustive statement, and that it still does not widen the sensitivity verdict; and
- confirm the footer remains strictly turn-scoped with no persistence and no exit command.
