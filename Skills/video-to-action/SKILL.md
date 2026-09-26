---
name: video-to-action
description: Extract deterministic report.md, transcript.md, and prompts.md artifacts from public YouTube videos with a non-blocking free-tier default, Gemini 3.7 Flash primary processing, bounded Gemini 3.6 Flash fallback, explicit optional phases, and provenance-safe failure isolation. Run only when explicitly invoked with /video-to-action.
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

The helper searches for `.env` in this fixed order: the current working directory, then the directory containing `scripts/video_to_action.py`. The expected location is the workspace-root `.env`, so the orchestrating agent must run the helper from the workspace root. `--check-setup` reports both searched paths and whether each file exists; when a file is loaded, it reports that path. It never displays a credential value.

If free mode receives a model outside the helper's documented free-model set, the preflight automatically selects the supported free primary or fallback and records the override. It never makes a paid-only call in free mode.

API keys are project credentials, not intrinsic billing labels. The tier fields express the user's intended policy; they do not change Google project billing. Never print, store in artifacts, or echo either credential value.

## Setup Gate

Before a real call:

1. Change to the workspace root, then run `--check-setup` for the selected tier.
2. Confirm URL, exact title, and exact duration are present.
3. Derive optional phases from the user's current request.
4. Present one concise preflight summary and proceed.

Stop only when setup or required inputs are missing, a paid run lacks its paid credential, or no safe supported route exists.

## Model And Recovery Policy

The free-tier defaults are deterministic:

- Primary: `gemini-3.7-flash`.
- Fallback: `gemini-3.6-flash`.
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

Transcript retrieval is independent from Gemini phases and happens once per invocation. The helper parses standard watch, `youtu.be`, Shorts, and embed URLs, then uses `youtube-transcript-api` as the primary path. It prefers original manual captions and never silently translates.

If the primary returns no usable captions, the helper resolves optional `yt-dlp` from `PATH` or its bounded WinGet package location. It tries original English captions first and only then invokes the English auto-caption fallback. The fallback strips WebVTT headers, cue timings, inline tags, and blank lines, then removes rolling-window duplication before writing the transcript. `transcript.md` records the retrieval path and caption kind. Missing `yt-dlp` is non-fatal and never fails `--check-setup`.

If both retrieval paths fail, the run and every successful Gemini artifact remain intact. `transcript.md` records the reason and points to `https://youtubetotranscript.com/` for manual recovery. The orchestrating agent must name the transcript failure plainly in its chat results report and include this retroactive completion command; a failure recorded only inside `transcript.md` is not an acceptable handoff:

```text
python Skills\video-to-action\scripts\video_to_action.py --complete-transcript <transcript.md> --manual-transcript-file <copied-transcript.txt>
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
| `--model`           | `gemini-3.7-flash`                   | Primary model                 |
| `--fallback-model`  | `gemini-3.6-flash`                   | One-attempt fallback          |
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
4. From the workspace root, run the no-API setup check for the selected tier.
5. State the concise preflight and run the helper once.
6. Let the helper own per-phase retry, fallback, transcript, and artifact writes.
7. Present results, attempt history, phase errors, transcript retrieval path, and LOW CONFIDENCE warnings.
8. If the transcript failed, name it as a failure in chat and include the exact `--complete-transcript` command printed by the helper.
9. Do not act on Procedure steps without separate authorization.

## Runtime Dependencies

The helper script imports the third-party packages below. It checks them before doing work (`--check-setup` and the automatic run preflight) and, when one is missing, reports the package with its install command. Always install with `python -m pip install <install-name>` — never bare `pip`, which can resolve to a different interpreter than the one running the helper. To restore every Skills dependency in one command, run `python -m pip install -r Skills/requirements.txt` from the workspace root.

| Import name            | Install name           | Used for          | Minimum version |
| ---------------------- | ---------------------- | ----------------- | --------------- |
| google.genai           | google-genai           | Gemini analysis   | N/A             |
| dotenv                 | python-dotenv          | Loading API keys  | N/A             |
| youtube_transcript_api | youtube-transcript-api | Caption retrieval | N/A             |

## Durable Artifact Format Handling

This skill owns video retrieval, provenance, phase isolation, prompts, transcript content, report content, run-folder naming, and its deterministic helper. When co-invoked with `html-this` or `pdf-this`, the helper may write native intermediates only under an approved temporary path; convert `report.md`, `transcript.md`, and `prompts.md` to the requested format and leave only their `.html` or `.pdf` equivalents in the durable run folder. Keep `latest.json` and machine state native.

Repeated-attempt and exact-prompt provenance must survive conversion. Treat same-stem variants as one logical artifact. This section overrides the three `.md` durable-output examples only during a co-invoked format run.

The helper writes run artifacts deterministically, so they carry no Agent Provenance or Agent Change Log at creation; an agent that later materially edits a run artifact by hand may append an Agent Change Log row for that edit.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Exact Model Attribution

Before this skill creates or materially edits the first first-party durable artifact in a session, invoke `exact-model-confirmation-gate`. The gate must finish before any new `Original writing LLM` or current-run Agent Change Log `Model` value is written.

- Reuse the gate's verified identity for later durable-artifact writes while the exact model context, acting agent, task or thread, and execution environment remain unchanged. Do not ask again during that stable session.
- If authoritative current runtime or session evidence cannot establish the exact model, stop before the first write and ask the user once. Cache a valid answer only for the current stable session.
- Invalidate prospectively when the user reports a model change or authoritative evidence shows that the model, agent, task or thread, or execution environment changed. Never rewrite historical provenance or change-log rows.
- Keep reasoning effort, service tier, provider, model family, and agent family separate from exact identity. Reject labels such as `Medium`, `Priority`, `OpenAI`, `GPT-5`, and `Codex Agent` as substitutes for a full model identity.
- Do not inspect configuration, environment data, credentials, logs, transcripts, or unrelated files by default. Only the gate's genuinely unavoidable file-backed branch may invoke `tread-lightly`, request one model field, and accept it only when it authoritatively identifies the current session. This skill does not gain a blanket `tread-lightly` dependency.
- Use `Not recorded` only when no interactive user is available, the user cannot identify the model, or exact identity remains safely unresolvable after the permitted attempt.

If `exact-model-confirmation-gate` is unavailable and no verified stable-session result already exists, fail closed before the artifact write rather than guessing, silently using `Not recorded`, or performing broader discovery.

**Validation check:** Confirm the dependency is named in this skill and its README; the canonical caller block is byte-identical to `exact-model-confirmation-gate/references/canonical-caller-block.md`; first-write blocking, one-time confirmation, stable-session reuse, proactive change, context invalidation, identity separation, targeted lookup, unresolved fallback, and append-only history pass the shared deterministic suite; and no historical row was rewritten.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;
- confirm `## Exact Model Attribution` remains byte-identical to the canonical caller block: `validate_carriers.py` requires it across the carrier set, and it still gates agent hand-edits of run artifacts;

After updates:

- run `--check-setup` without an API call;
- run `--dump-prompts` and confirm `PROMPTS.md` matches live constants;
- run `--self-test` for tier policy, selection reuse, bounded retry/fallback, non-retryable errors, phase isolation, single-folder output, provenance, transcript primary/fallback/failure states, VTT deduplication, chat reporting, and secret redaction;
- compile with Python UTF-8 mode;
- audit Markdown tables for visual alignment and cells of at most 80 characters;
- validate the folder with `quick_validate.py` using separated streams; and
- make no real Gemini call during deterministic validation.
