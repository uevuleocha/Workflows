---
name: tread-lightly
description: Protect secrets and sensitive data while reading, inspecting, validating, editing, or otherwise handling .env files, configuration files, credentials, tokens, passwords, API keys, private keys, authentication material, or files that may contain them. Use when the user explicitly invokes Tread Lightly and automatically whenever a task touches a sensitive or potentially sensitive file, secret store, command, output, log, patch, or Git operation.
---

# Tread Lightly

Handle sensitive material with minimal access and no unnecessary exposure.
This is a turn-scoped safety overlay, not a persistent workflow.

## Project Contract

Obey the active workspace contract, permissions, and safety rules. Tread
Lightly narrows handling; it never grants access, overrides a stricter rule, or
authorizes secret transmission.

## Activation

Activate for the current turn when either condition applies:

- the user explicitly invokes `/tread-lightly`, `$tread-lightly`, `use
  tread-lightly`, `tread lightly`, or a clear equivalent naming this skill; or
- the task reads, inspects, validates, edits, copies, searches, stages,
  commits, transmits, or otherwise handles material that contains or may
  contain secrets or sensitive data.

Automatic triggers include:

- `.env` files and variants such as `.env.local` or `.env.production`;
- configuration or settings files that may hold credentials;
- credential stores, cloud profiles, private keys, certificates, SSH material,
  authentication exports, CI/CD variables, secret-manager output, database
  dumps, backups, browser exports, and logs with possible credentials;
- commands, patches, diffs, screenshots, or tool results that could reveal a
  password, token, API key, connection string, cookie, session identifier,
  recovery code, or other authentication material.

Decide from the filename, path, task purpose, file type, and known context
before reading content whenever possible. Treat uncertain material as
sensitive until shown otherwise without exposing it.

At first activation in a turn, briefly say:

```text
Tread Lightly is active. I’ll inspect only what is necessary and will not
reproduce sensitive values.
```

Do not repeat that notice for every file or command in the same turn.

## Turn-Scoped Mode Footer

End every response produced during an active Tread Lightly turn with:

```text
Mode = Tread Lightly
```

If another mode is active in that response, follow the workspace's multi-mode
footer rule and include `Tread Lightly` exactly once.

The mode ends when that response is sent. It does not persist merely because
it appeared previously. Reactivate it independently on every later turn that
again handles sensitive material. Therefore, five consecutive sensitive turns
show the footer five times; the first later non-sensitive turn does not.

Explicit invocation activates the footer for that turn even if no secret is
ultimately found.

## Core Handling Rules

### 1. Minimize Access

- Inspect only what the task requires.
- Prefer existence, size, line count, permissions, syntax, key presence, or
  redacted structure over plaintext values.
- Read a specific field or bounded region instead of a whole file when
  possible.
- Do not browse neighboring sensitive files without a task-specific need.
- Do not ask the user to paste a secret into chat.

### 2. Prevent Reproduction And Persistence

Never intentionally place a sensitive value into:

- assistant messages, reasoning summaries, mode notices, or questions;
- tool calls, command-line arguments, terminal output, shell history, process
  listings, logs, error messages, or transcripts;
- patches, diffs, source files, comments, documentation, plans, reports,
  summaries, screenshots, clipboard content, fixtures, or test snapshots;
- commits, branches, pull requests, issues, build artifacts, caches, or other
  durable storage.

Do not quote, summarize, transform, partially reveal, or repeat a real secret.
Masking only part of a value can still make it identifiable; prefer statements
such as `credential present`, `value missing`, `format valid`, or `redacted`.

Treat secret-looking test data as real until proven otherwise.

### 3. Prevent Unnecessary Transmission

- Do not send sensitive values to subagents, plugins, connectors, web
  services, external APIs, issue trackers, or remote validation services.
- Do not upload or attach a sensitive file when a local, non-echoing check can
  answer the question.
- If the task genuinely requires a specific external transfer, explain the
  destination and purpose and obtain explicit authorization for that transfer.
  Share only the minimum necessary through an approved secure mechanism.

### 4. Use Non-Echoing Operations

- Avoid whole-file display commands such as `cat`, `type`, or `Get-Content`
  against sensitive files.
- Avoid broad searches whose matching lines would print values.
- Avoid secret-bearing command arguments, inline environment assignments, or
  commands that echo expanded variables.
- Use a local parser or command that reads silently and emits only safe,
  bounded metadata.
- Suppress or sanitize error output that could include source lines or values.
- Never place a real secret in an `apply_patch` patch or another edit payload
  that becomes durable tool output. Use a secure non-echoing local edit
  mechanism when one is authorized and available. Otherwise ask the user to
  perform the value change through their secure environment.

## Safe Editing And Validation

When editing a potentially sensitive file:

1. Identify the exact requested key or structural change without displaying
   unrelated content.
2. Preserve existing secret values whenever possible.
3. Change only the requested structure or non-secret field.
4. Use placeholders such as `YOUR_API_KEY_HERE` in examples and
   `.env.example` files.
5. Validate with a non-echoing parser or a result limited to safe status.
6. Report the outcome without values.

Do not claim a secret is valid merely because it exists or matches a shape.
Network authentication tests can transmit the secret and require normal task
authorization plus the narrowest safe destination.

## Git Safety

For a sensitive or potentially sensitive file:

- check ignored or tracked status without displaying contents;
- never use a content diff as the first inspection method;
- never stage, commit, or push the real file or its values;
- use a sanitized example file containing names and placeholders when useful;
- if the real file is already tracked, report that fact without showing a
  diff, stop further propagation, and recommend removal from tracking and
  credential rotation as appropriate;
- do not rewrite Git history, remove files, or rotate credentials without
  explicit authorization.

## Reporting

Report only safe facts needed for the task, for example:

- file exists or is missing;
- expected variable is present or absent;
- duplicate keys were found;
- syntax is valid or invalid;
- sensitive file is ignored, untracked, or already tracked;
- a requested non-secret structural change was completed.

Do not include the sensitive value, a reversible encoding, a secret-bearing
source line, or enough fragments to reconstruct it. Key names, filenames, and
paths can also be sensitive; redact them when they are not necessary to the
user's decision.

## Accidental Exposure

If a sensitive value appears unexpectedly:

1. Stop output or propagation immediately.
2. Do not repeat the value, even while explaining the incident.
3. Identify only the exposure surface, such as terminal output, transcript,
   patch, log, or commit.
4. Contain further spread using safe, authorized actions.
5. Tell the user what category of credential may be affected and recommend
   revocation or rotation.
6. Do not delete records, rewrite history, revoke, or rotate anything without
   explicit permission.

Never claim that prior transcript or tool exposure has been erased unless the
relevant system provides verified deletion evidence.

## Completion Check

Before ending an active turn, confirm internally:

- access was limited to the minimum necessary;
- no sensitive value was reproduced in the response or tool output;
- no unauthorized external transfer or durable copy occurred;
- any Git or edit operation avoided secret-bearing diffs and patches;
- the user received a useful redacted result; and
- the footer includes `Tread Lightly` exactly once.
