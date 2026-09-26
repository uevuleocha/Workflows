---
name: buzz-agent-manager
description: Create Buzz managed-agent configuration, check the eight-agent roster for drift, record confirmed app changes, and reconcile Buzz documentation toward the side the user names as authoritative. Also handles the former buzz-agent-setup invocation phrases. Never writes to Buzz.
---

# Buzz Agent Manager

## Project Contract

Follow the active workspace contract. The local master is `Skills/buzz-agent-manager/`. This skill maintains documentation but never writes the Buzz Agents panel, relay, or `managed-agents.json`. Keep historical provenance and change-log rows unchanged. Obtain the exact current model through `exact-model-confirmation-gate` before a durable write.

## Invocation

Use this skill for `/buzz-agent-manager`, `use buzz-agent-manager`, `check Buzz agents`, `sync the Buzz roster`, or a report that an agent changed in the Buzz app. Former `/buzz-agent-setup`, `use buzz-agent-setup`, `use the buzz-agent-setup skill`, `set up a new Buzz agent`, `configure a Buzz managed agent`, `add a new lab to Buzz`, and `prepare agent instructions and core memory for Buzz` requests route here in Create mode. If the user names no mode, use **Check**.

## Dependencies

| Dependency                      | Requirement                                      |
| ------------------------------- | ------------------------------------------------ |
| `tread-lightly`                 | Hard; invoke first on every run, before any read |
| `exact-model-confirmation-gate` | Before the first first-party durable write       |
| `markdown-table-aligner`        | Check each materially edited Markdown table      |

`managed-agents.json` is a credential store. Invoke `tread-lightly` unconditionally before opening **any** file on every run, including Create and no-drift Check. Use a real JSON parser. Never print the JSON, bulk-search it, send it to another service, or redact a whole-file dump. The included `scripts/check_roster.py` emits only approved fields and presence flags. Its default app path is `%APPDATA%/xyz.block.buzz.app/agents/managed-agents.json`. Inspect the app file only through this field-minimized helper or an equally narrow parser. UTF-8 reads and writes must be explicit; never round-trip with PowerShell `Get-Content -Raw` and `Set-Content`.

## Sources And Facts

The app has a **definition** (model, provider, runtime, environment variables) and an **instance** (pubkey, live `acp_command`, live parallelism) per active agent. Never substitute definition or persona defaults for the two instance fields. `Current Roster State` and each Roster entry in hub doc 3 are the full workspace record. The comma-separated `Agents:` line below `END BUZZ MANAGED` in the nest `.buzz/AGENTS.md` is the routing digest.

Track seven facts per agent, in this order. Charter is the file-authoritative bundle of Role, Personality, Nationality & Dialect, and Sign-off in doc 3's Standard Shape; the app holds only a short `system_prompt` stub.

| No. | Fact         | App source                   | Doc 3 source                 | Digest |
| --- | ------------ | ---------------------------- | ---------------------------- | ------ |
| 1   | Name         | Definition and instance name | Heading, table, instructions | Yes    |
| 2   | Pronouns     | None                         | Summary row and instruction  | Yes    |
| 3   | Model        | Definition model             | State row and instruction    | No     |
| 4   | Provider     | Runtime and endpoint lab     | State Runtime and Lab        | No     |
| 5   | Effort level | Runtime-specific control     | State Effort level           | No     |
| 6   | Charter      | `system_prompt` stub only    | Full instruction text        | Role   |
| 7   | Description  | Definition `description`     | Summary Description row      | Yes    |

| Fact changed                         | Hub doc 3 | Nest digest |
| ------------------------------------ | --------- | ----------- |
| Name, Pronouns, Charter, Description | Update    | Update      |
| Model, Provider, Effort level        | Update    | No change   |

Pronouns are supplied by Uzo, never inferred, and must be `she/her`, `he/him`, or `they/them`. Check compares doc 3's summary and instruction with the digest. Description is public and must be one short line of standard English. Buzz's length limit is unknown, so there is no fixed cap. Check compares the panel, doc 3, and digest side by side; Sync asks Uzo which wording to keep when they differ and never guesses.

| Runtime      | Effort control                            |
| ------------ | ----------------------------------------- |
| `claude`     | Definition env `CLAUDE_CODE_EFFORT_LEVEL` |
| `codex`      | Model selection suffix, e.g. `[medium]`   |
| `buzz-agent` | Not settable; record `default`            |

For Claude, compare effort case-insensitively. A missing variable or a value outside `low`, `medium`, `high`, `xhigh`, and `max` is drift even if doc 3 happens to match. `CLAUDE_EFFORT` in the panel is a readback, not an input; report its presence without its value. Never use `settings.json` for effort. Compare the app model string with doc 3 exactly. For a Claude bare alias (`opus`, `sonnet`, `haiku`, `fable`), leave its exact model unverified until the agent is asked; never translate the alias.

Every Check also inspects the global `@agentclientprotocol/claude-agent-acp` install offline. Report its version, bundled `@anthropic-ai/claude-agent-sdk` version, and whether the bundled `claude-agent-sdk-win32-x64/claude.exe` contains each pinned Claude model ID. A missing ID is drift because Buzz cannot run that pin. Emit no binary content. On request, and once during each Change involving a Claude seat, run the separate online `freshness` mode: compare installed and npm latest versions for `claude-agent-acp` and `@anthropic-ai/claude-code`. Failed lookup is unverified, never up to date. Recommend updates only; installation requires Buzz closed and Uzo's go-ahead.

Doc 3: `C:\Users\Admin\Uzzys Universe\Archive\Live\Documentation\Personal\Buzz\3.) Buzz Agent Instructions.md`. Read The Standard Shape, Standard Configuration For Every Agent, Roster, Current Roster State, and The Roster-Awareness Rule before a documentation write. Update every place carrying the changed fact, including the Roster summary, full instruction text, and Current Roster State where applicable. Nest digest: `C:\Users\Admin\.buzz\AGENTS.md`, user-authored `Agents:` line only. Do not edit the managed block.

| Additional check      | App source                | File source             |
| --------------------- | ------------------------- | ----------------------- |
| `acp_command`         | Raw instance record       | Runtime-derived command |
| Parallelism           | Raw instance record       | Standard Configuration  |
| Context message limit | Definition env, exact key | Standard Configuration  |
| Context token limit   | Definition env, exact key | Standard Configuration  |
| `system_prompt` stub  | Record `system_prompt`    | Roster entry stub       |

The environment display allowlist is `BUZZ_ACP_CONTEXT_MESSAGE_LIMIT`, `BUZZ_AGENT_MAX_CONTEXT_TOKENS`, and `CLAUDE_CODE_EFFORT_LEVEL`; only plain integers or valid level words may be displayed. For every other environment key, report presence or absence only. Never read an API-key value. Never print `OPENAI_COMPAT_API_KEY` or `OPENAI_COMPAT_BASE_URL` values. The helper reads only the base URL field needed to classify its host internally against known provider hosts; it emits only a lab label or `unverified`, never a URL or fragment. Unknown hosts remain unverified. Compare `acp_command` with the documented runtime expectation; if that expectation is not documented, report **unknown**. Parallelism corrections belong to `4.) Buzz Logistics.md` because the UI only sets it at creation. A non-empty `name_pool` on a non-built-in agent is a warning pointing to doc 3 note [np]; ignore retired Pollen, Fizz, and Honey and never hand-edit their records.

## Diff Rule And Authority

This is a diff, never a mirror. Report each discrepancy with agent, field, panel value, and file value on one line. For sensitive or arbitrary free-text fields, use a safe status (`different`, `present`, `absent`) rather than printing their content. Suggest which side may be current, but do not choose for the user. When the user has already named the authoritative side, proceed without asking again. File-authoritative Charter is not replaced by the panel stub.

## Modes

### Check (default)

Invoke `python -X utf8 Skills/buzz-agent-manager/scripts/check_roster.py check` after `tread-lightly`. It is read-only and covers all seven facts plus the additional app checks. The digest format is `Agents: Name (pronouns): Description, ...`; parse entries by the `Name (pronouns): ` anchor, never by splitting on commas inside Descriptions. Also read each doc 3 Role and corresponding one-line digest remit; compare their meaning. Review output for accidental disclosure. Treat `unknown` comparisons as unverified, not clean. Report any name present on only one side. Do not write any file. Emit a short clean report only when the helper and manual role review find no drift, noting any lab comparison that remains unverified.

### Create

Collect agent name, Uzo-supplied Pronouns, role (optional), Description in `<Seat> --> <remit>` format, selected harness and its **class** (in-process runner or external CLI), exact provider model string and display name, provider and matching endpoint when using the in-process runner, user-confirmed real context window, and core-memory candidates. For Claude Code, require one of the five valid `CLAUDE_CODE_EFFORT_LEVEL` values; for Codex, effort belongs in the model selection. Ask only for missing user-owned choices. Never infer Pronouns or invent model strings, windows, labs, endpoints, personas, or memory slugs. Check name uniqueness.

Produce four paste-ready blocks in order:

1. **Dialog fields:** name; Description; selected harness; exact model; provider; environment-variable **names only** except the allowed Claude effort level; user-confirmed context limit; max output and rounds as inherit; house parallelism 3 at creation; **Instance name pool empty**; ACP command `Buzz ACP (default)`; and Conversation context. For an external CLI, context limit, output, and rounds are managed by that CLI. Claude Code effort is set through `CLAUDE_CODE_EFFORT_LEVEL` in the panel; Codex effort stays in its model selection. For an in-process OpenAI-compatible lab, direct the user to set `OPENAI_COMPAT_BASE_URL` under Advanced and confirm its endpoint matches their key. Never request or echo a key or URL value in chat.
2. **Agent instructions:** begin exactly `You are running <Model Display Name> (`<exact-model-string>`).` Then add the user's role if supplied. Also prepare doc 3's seven-field Standard Shape, obtaining missing Charter fields from the user. Warn every time that the hardcoded model line must be updated by hand when the model changes.
3. **`core` memory:** target under 2 KB (hard cap 65,535 bytes). For every proposed line, state accepted or rejected and why under the admission test: does it need to be true on **every** turn, and is it already in nest or workspace instructions or the channel description? Include unless declined: the `[Context Handoff]` announcement, summary request, and user-summary supersession rule; and reading the channel description first and treating its workspace as context.
4. **Cold `mem/<slug>` proposals:** each with a one-line read trigger, or none.

The harness branch uses class, never a hardcoded harness catalogue. An unfamiliar harness requires its class from the user. This skill does not author channel descriptions; use `buzz-channel-description` for those.

After the user confirms the agent was saved in Desktop, rerun the safe parser and require the new definition and instance to exist. Then add its complete doc 3 entry, including Pronouns summary row and instruction line and Description summary row, plus the Current Roster State row. Add the `Name (pronouns): Description` digest entry. If the saved app facts disagree with the user-approved configuration, stop without writing.

### Change

A report that the user changed a value in Desktop makes the **app** authoritative for that reported change. Verify the exact reported field against the parsed app record first. If it differs, stop without writing and show the mismatch safely. If it matches, update doc 3 and, for Name, Pronouns, Charter, or Description, the digest. Never silently copy unrelated app drift during this operation. A model change must also refresh every model line that carries that fact; warn if the UI stub carries a stale model/name and supply a paste-ready replacement. For any Claude-seat Change, run the separate online freshness check once.

To move a Claude seat to a new model: (1) quit Buzz; (2) update `claude-agent-acp` globally from Uzo's terminal; (3) confirm its bundled binary contains the new exact model ID; (4) relaunch Buzz; (5) change the dropdown to that ID; (6) ask the agent for its exact model ID; (7) update doc 3. Never pin a model the adapter binary lacks. Installing or updating the adapter requires Uzo's go-ahead.

### Sync

Run Check and establish authority for each discrepancy. For a Description mismatch among the app, doc 3, and digest, show all three safe public values and ask Uzo which wording to keep or for new wording; never guess. **Panel wins:** update only the mapped workspace surfaces, preserving unrelated edits, then recheck. **File wins:** write nothing; give the user an exact agent-by-agent list of fields to change in the Buzz UI. Include a paste-ready instruction block when Charter or a model line changes. Do not attempt to correct parallelism here. If authority is not yet stated, ask once and wait. A rename changes current name fields and the digest; it never rewrites old Agent Provenance or Agent Change Log rows. Always warn that the old-name UI stub needs manual paste.

## Boundaries

Never write to Buzz through the dialog, `managed-agents.json`, or relay. Never edit `BEGIN BUZZ MANAGED` through `END BUZZ MANAGED`. Do not expose any API key, auth tag, endpoint value, or fragment. Do not use a redaction filter over whole-file output. Never infer successful UI save from a user report alone. Do not treat a settings-dialog value as proof of live `acp_command` or parallelism. Preserve all existing user changes and stop on competing file editors. Local master validation precedes any later authorized global sync.

## Markdown Table Alignment

All Markdown tables this skill writes, in durable artifacts or chat, must be visually pipe-aligned. Cap each cell at 80 characters including an overflow marker. Truncate longer cells at a word boundary, append a pointer such as `-> see note [row-id]` using that row's own identifier, and put the full text in a keyed note directly below the table. Pad columns for monospaced alignment; rendered Unicode display width is authoritative, so raw pipe indices are diagnostic only. Prefer ASCII `->`, `--`, and `...` inside cells. Keep tables near 120 display columns by shortening cells and moving detail to notes. Run `markdown-table-aligner check` after semantic edits and before handoff; correct any findings.

## Validation

Validate this folder with official `quick_validate.py` under `python -X utf8`, capturing stdout and stderr separately and using exit code. Run the helper's synthetic fixture tests and a live Check. For a controlled drift test, edit only a workspace-side fixture copy, show one agent and both safe values, then discard that copy. Verify a rename reports digest and stale-stub work with no provenance backfill. Inspect every test output for prohibited environment values. Verify Check did not change any file. Run `markdown-table-aligner check` on every edited Markdown file with tables. Record evidence and remaining limits in the commissioning prompt's Feedback Section; tick only boxes established by evidence.
