---
name: video-to-action
description: Extract deterministic report.md, transcript.md, and prompts.md artifacts from public YouTube videos with a non-blocking free-tier default, Gemini 3.6 Flash primary processing, bounded Gemini 3.5 Flash fallback, explicit optional phases, and provenance-safe failure isolation. Run only when explicitly invoked with /video-to-action.
---

# Video-to-Action

Extract a public YouTube video into deterministic `report.md`, `transcript.md`, and `prompts.md` artifacts. The bundled Python helper is the sole writer. The orchestrating agent selects already-requested phases and presents results but never assembles or invents video content.

## Project Contract

Follow the host contract. Extraction does not authorize executing tutorial steps, editing product files, installing software, or exposing secrets.

## Invocation

Run only when the user explicitly invokes `/video-to-action`. Natural-language requests do not activate the workflow.

## Non-Blocking Preflight

Free tier is the default. State that assumption briefly and proceed without a cost-confirmation question. Ask only for missing required inputs:

- public YouTube URL;
- exact user-authoritative title; and
- exact user-authoritative duration.

When more than one is missing, request all missing values together once. Never infer the title or duration.

Reuse choices already supplied in the request or current context:

- An explicit Deep Summary request selects Deep Summary.
- An explicit Technical request selects Technical when the content is coding or software related.
- Unmentioned optional phases remain off.
- Do not show another pop-up or request another chat confirmation for supplied choices.

## Tier And Credential Policy

`free` is the helper and orchestrator default. It reads `GEMINI_API_KEY`. The optional paid credential is `GEMINI_API_KEY_PAID`; its presence alone never authorizes its use. A paid run requires explicit user authorization represented by `--tier paid` for that scoped invocation.

If free mode receives a model outside the helper's documented free-model set, the preflight automatically selects the supported free primary or fallback and records the override. It never makes a paid-only call in free mode.

API keys are project credentials, not intrinsic billing labels. The tier fields express the user's intended policy; they do not change Google project billing. Never print, store in artifacts, or echo either credential value.

## Setup Gate

Before a real call:

1. Run `--check-setup` for the selected tier.
2. Confirm URL, exact title, and exact duration are present.
3. Derive optional phases from the user's current request.
4. Present one concise preflight summary and proceed.

Stop only when setup or required inputs are missing, a paid run lacks its paid credential, or no safe supported route exists.

## Model And Recovery Policy

The free-tier defaults are deterministic:

- Primary: `gemini-3.6-flash`.
- Fallback: `gemini-3.5-flash`.
- Primary budget: three total attempts per selected phase.
- Backoff: one second, then three seconds.
- Fallback budget: one attempt after three transient primary failures.

Retry only recognized transient capacity failures, primarily structured Gemini `503 UNAVAILABLE`. Do not retry authentication, permission, invalid-input, unsupported-feature, paid-authorization, or generic `429 RESOURCE_EXHAUSTED` errors. A failed fallback ends automatic attempts for that phase and is reported to the user.

Each selected phase has an independent attempt budget. Procedure failure does not block Deep Summary or Technical. Optional-phase failure does not erase a successful Procedure. The run fails only when every selected Gemini phase fails.

## Call Model

| Phase        | Contents                          | Selection                    |
| ------------ | --------------------------------- | ---------------------------- |
| Procedure    | Overview and detailed steps       | Always                       |
| Deep Summary | Chronological ACTS summary        | Explicit opt-in              |
| Technical    | Code, commands, and configuration | Opt-in; coding/software only |

One to three phases are selected. Each phase normally makes one Gemini call and can make at most three primary attempts plus one fallback attempt during a recognized transient-capacity incident. Documentation and artifacts distinguish selected phases from actual attempts.

## Single-Folder Artifact Contract

One helper invocation creates exactly one final run folder after internal model attempts finish:

```text
Archive\Historical\Video-to-action\<timestamp - title>\
```

Internal attempts never create separate Historical folders. Do not externally rerun the helper merely because one attempt returns `503`; the helper owns recovery. A complete, partial, or failed invocation retains one honest folder. Historical folders from separate invocations are never deleted automatically.

Each run folder contains:

| File            | Description                                     |
| --------------- | ----------------------------------------------- |
| `report.md`     | Deterministic extraction and attempt provenance |
| `transcript.md` | Captions or honest manual-recovery marker       |
| `prompts.md`    | Exact selected prompts and attempt provenance   |

The output root also contains `latest.json`, a Windows-safe pointer to the latest completed invocation.

## Attempt Provenance

Both `report.md` and `prompts.md` record, per phase:

- primary and fallback model names;
- attempt role and bounded attempt number;
- sanitized error and transient/non-retryable classification;
- successful model; and
- any free-mode model-policy override.

Repeated attempts reuse the exact phase prompt. `prompts.md` stores each exact selected prompt once and associates all attempts with it. Error text is bounded and credential-shaped or configured key values are redacted.

## Transcript Artifact

Transcript retrieval is independent from Gemini phases and happens once per invocation. The helper parses standard watch, `youtu.be`, Shorts, and embed URLs, then uses `youtube-transcript-api`. It prefers original manual captions and never silently translates.

If retrieval fails, `transcript.md` records the reason and points to `https://youtubetotranscript.com/` for manual recovery. Complete a pending manual fallback without rerunning Gemini:

```text
python scripts\video_to_action.py --complete-transcript <transcript.md> --manual-transcript-file <copied-transcript.txt>
```

## Phase Prompts

Procedure always requests the Overview and detailed Steps in one response. Deep Summary is a dedicated ACTS call. Technical is a dedicated coding/software-only call. Exact title and duration are injected into the relevant prompts. Prompt constants generate `PROMPTS.md` through `--dump-prompts`.

## Configuration

| Parameter           | Default                              | Purpose                       |
| ------------------- | ------------------------------------ | ----------------------------- |
| `url`               | required                             | Public YouTube URL            |
| `--title`           | required                             | Exact supplied title          |
| `--duration`        | required                             | Exact normalized duration     |
| `--tier`            | `free`                               | Credential and billing policy |
| `--model`           | `gemini-3.6-flash`                   | Primary model                 |
| `--fallback-model`  | `gemini-3.5-flash`                   | One-attempt fallback          |
| `--deep-summary`    | off                                  | Select Deep Summary           |
| `--technical`       | off                                  | Select Technical              |
| `--coding-video`    | off                                  | Confirm Technical relevance   |
| `--resolution`      | `default`                            | `low` reduces video tokens    |
| `--start` / `--end` | none                                 | Optional clip offsets         |
| `--output-dir`      | `Archive\Historical\Video-to-action` | Run-record root               |
| `--check-setup`     | off                                  | No-API setup check            |
| `--dump-prompts`    | off                                  | Regenerate prompt reference   |
| `--self-test`       | off                                  | Deterministic no-API fixtures |

## Intent Routing

- `summarize`: present report findings; execute nothing.
- `learn`: treat the report as knowledge; saving elsewhere needs authorization.
- `follow`: present the Procedure and stop; execution needs authorization.

## Workflow

1. Confirm explicit invocation.
2. Gather missing URL, title, and duration together once.
3. Reuse stated optional-phase and tier choices; default omissions off/free.
4. Run the no-API setup check for the selected tier.
5. State the concise preflight and run the helper once.
6. Let the helper own per-phase retry, fallback, transcript, and artifact writes.
7. Present results, attempt history, phase errors, and LOW CONFIDENCE warnings.
8. Offer manual transcript recovery when needed.
9. Do not act on Procedure steps without separate authorization.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to human-readable report, transcript, and prompt artifacts without altering exact captured prompt or transcript content.

For every in-scope artifact:

- place an `## Agent Provenance` section immediately after the artifact's opening block -- its title, status, and lifecycle lines -- carrying `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role`, in that order;
- record `Original writing LLM` as the model that produced the artifact, kept distinct from the agent family that performed the write; use `Not recorded` when the model is genuinely unknown, and never infer it from the agent label or backfill it later;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`, `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` as the last section, or immediately above any section the artifact already reserves for the last position, rendered as a five-column `Date and Time | Agent | Model | Action | Scope` table with one row per material edit;
- stamp every change-log row `YYYY-MM-DD-HH:mm:ss` on a 24-hour clock, read from the machine clock and never estimated; leave historical date-only rows exactly as written rather than backfilling them, because a log carrying both shapes is correct and the boundary between them is itself information;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves to `Uzo`; do not confuse content ownership with the agent that performed the filesystem write. Do not inject provenance into product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill owns video retrieval, provenance, phase isolation, prompts, transcript content, report content, run-folder naming, and its deterministic helper. When co-invoked with `html-this` or `pdf-this`, the helper may write native intermediates only under an approved temporary path; convert `report.md`, `transcript.md`, and `prompts.md` to the requested format and leave only their `.html` or `.pdf` equivalents in the durable run folder. Keep `latest.json` and machine state native.

Repeated-attempt and exact-prompt provenance must survive conversion. Treat same-stem variants as one logical artifact. This section overrides the three `.md` durable-output examples only during a co-invoked format run.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

After updates:

- run `--check-setup` without an API call;
- run `--dump-prompts` and confirm `PROMPTS.md` matches live constants;
- run `--self-test` for tier policy, selection reuse, bounded retry/fallback, non-retryable errors, phase isolation, single-folder output, provenance, transcript states, and secret redaction;
- compile with Python UTF-8 mode;
- audit Markdown tables for visual alignment and cells of at most 80 characters;
- validate the folder with `quick_validate.py` using separated streams; and
- make no real Gemini call during deterministic validation.
