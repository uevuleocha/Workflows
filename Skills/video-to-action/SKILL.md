---
name: video-to-action
description: Extract deterministic report.md, transcript.md, and prompts.md artifacts from public YouTube videos with a non-blocking free-tier default, Gemini 3.8 Flash primary processing, bounded Gemini 3.6 Flash fallback, static video processing by default with opt-in agentic processing that falls back to static, an agentic recovery probe, default-on Deep Summary and opt-in Technical, and provenance-safe failure isolation. Run only when explicitly invoked with /video-to-action.
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

Resolve a broad Subject too: reuse the user's supplied subject, otherwise reuse a clear existing category from context and ask only when genuinely ambiguous. Subject folders are unnumbered (for example `AI Agents` or `Trading`); do not create a category for every video. Pass the resolved value as `--subject`. Missing or unsafe subjects fail before an API call. Maintenance-only modes do not require a subject.

When more than one is missing, request all missing values together once. Never infer the title or duration.

Reuse choices already supplied in the request or current context:

- Deep Summary is on by default. An explicit request to skip it passes `--no-deep-summary`; `--deep-summary` remains supported.
- An explicit Technical request selects Technical when the content is coding or software related.
- Technical remains off unless requested. Do not ask users to opt into the default Deep Summary.
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
3. Include Deep Summary unless explicitly declined; select Technical only when requested.
4. Present one concise preflight summary and proceed.

Stop only when setup or required inputs are missing, a paid run lacks its paid credential, or no safe supported route exists.

## Model And Recovery Policy

The free-tier defaults are deterministic:

- Primary: `gemini-3.8-flash`.
- Fallback: `gemini-3.6-flash`.
- Primary budget: three total attempts per selected phase.
- Backoff: one second, then three seconds.
- Fallback budget: one attempt after three transient primary failures.

Google deprecated `gemini-3.7-flash` and `gemini-3.5-flash` on 2026-10-08 and serves them as `gemini-3.8-flash` and `gemini-3.6-flash`. The helper maps those IDs to their served models before any call and records a preflight override, so a fallback never silently duplicates the primary.

Retry only recognized transient capacity failures, primarily structured Gemini `503 UNAVAILABLE`. Do not retry authentication, permission, invalid-input, unsupported-feature, paid-authorization, or generic `429 RESOURCE_EXHAUSTED` errors. A failed fallback ends automatic attempts for that phase and is reported to the user.

Each selected phase has an independent attempt budget. Procedure failure does not block Deep Summary or Technical. Optional-phase failure does not erase a successful Procedure. The run fails only when every selected Gemini phase fails.

## Call Model

Every selected Gemini phase uses the Interactions API. `--processing` chooses how Gemini reads the video:

- `static` (default): Gemini samples the whole video at fixed intervals with its audio. No processing evidence is required.
- `agentic` (opt-in, only when the user asks): the model inspects relevant video sections dynamically; this is not a guarantee that every frame is examined. Success requires `processing_call` and `processing_result` evidence. When an agentic phase ends without a result after its own model recovery, the helper runs that phase again with static processing and the same prompt, and records those attempts as `agentic-to-static` recovery.

Static is the default because Google's agentic video route failed for every tested model on 2026-10-28 (INTERNAL and DEADLINE_EXCEEDED) while static processing on the same video, key, and models completed. The helper records processing mode, processing counts, numeric usage totals, interaction IDs, states, and sanitized error details, never internal reasoning or raw response payloads.

The helper creates one background interaction per attempt, then polls that same job up to 120 times at five-second intervals (each network request has a 30-second timeout). Polling does not create another analysis. SDK retries are disabled so the helper owns the attempt budget. Transient status-check failures (HTTP 408/500/502/503/504, connection errors, or timeouts) receive at most three retries per interaction, waiting 2, 5, and 10 seconds and always querying the same interaction ID. These retries count within the 120-check budget; successful checks resume the usual five-second interval. Authentication, invalid-input, and generic 429 errors stop immediately. Exhausted retries or polling budget trigger best-effort cancellation and end the phase without automatic resubmission; cancellation can be unconfirmed. Sanitized polling failures and retry delays remain in provenance even when the job recovers. Terminal failed/cancelled states, and missing processing evidence in agentic mode, fail explicitly. Recognized create-time capacity failures and terminal failures with explicit `503` or `UNAVAILABLE` error codes use the existing bounded model recovery.

SDK 2.29.0 rewrites a zero retry setting during client construction. The helper therefore disables retries on the generated Interactions configuration after construction and fails closed if that adapter changes. Actual HTTP request-count tests cover quota, capacity, authentication, and connection failures; rerun them when upgrading the SDK.

Hard `--start`/`--end` clipping is not supported in either processing mode and is rejected before any API call. Do not silently drop offsets. An explicit custom request may ask about a timestamp range, but the full video remains available to Gemini. `--resolution low` sets the video input's `resolution: "low"`.

## Agentic Probe

`--agentic-probe` checks whether Google's agentic route works again. It makes exactly one agentic call (no retries, no static fallback) on a fixed 19-second public video using the resolved primary model, creates no run folder, and writes `agentic-status.json` at the output root with the last result, timestamp, sanitized error, consecutive-success count, and the last 20 checks. It prints `WORKING` (exit 0), `STILL BROKEN` (exit 1), or `INCONCLUSIVE` (exit 2) when the only provider codes are quota or rate-limit codes (`429`, `RESOURCE_EXHAUSTED`); an inconclusive probe keeps the consecutive-success count unchanged because it says nothing about agentic health. Every later `report.md` and `prompts.md` shows the latest probe result, or `never probed`. Treat agentic as recovered only after three consecutive `WORKING` probes; switching the default back to agentic is a separate, user-authorized change. Run the probe only when the user asks.

## Optional Custom Request

`--custom-request` defaults to empty. Populate it only from an explicit additional user instruction, such as "also explain", "focus on", or "my custom request is"; no special phrase is required. Do not infer a request from the title, subject folder, video content, or assumed interests. Do not ask for an optional request when none was supplied. Whitespace-only input is absent.

Pass the user's supplied request to the helper without inventing additions. It supplements normal work in the same Procedure call; it does not select Deep Summary or Technical or trigger a separate analysis. The helper appends the request to that prompt, records the exact effective prompt in `prompts.md`, and places the answer under `## Your Specific Request` in `report.md`. With no request, that section is omitted. Missing normal content or a missing/empty requested answer is an explicit phase failure, not a fabricated answer or an automatic second review. Extra content and internal inspection can consume more tokens even without another top-level analysis call.

| Phase        | Contents                          | Selection                     |
| ------------ | --------------------------------- | ----------------------------- |
| Procedure    | Overview and detailed steps       | Always                        |
| Deep Summary | Chronological ACTS summary        | Default-on; opt-out available |
| Technical    | Code, commands, and configuration | Opt-in; coding/software only  |

Normally two phases are selected (Procedure and Deep Summary); opting out of Deep Summary leaves one, and Technical can add one. Each phase normally makes one Gemini call and can make at most three primary attempts plus one fallback attempt during a recognized transient-capacity incident. Documentation and artifacts distinguish selected phases from actual attempts.

## Single-Folder Artifact Contract

One helper invocation creates exactly one final run folder after internal model attempts finish:

```text
Archive\Historical\Video-to-action\<Subject>\<timestamp - title>\
```

Internal attempts never create separate Historical folders. Do not externally rerun the helper merely because one attempt returns `503`; the helper owns recovery. A complete, partial, or failed invocation retains one honest folder. Historical folders from separate invocations are never deleted automatically.

Each run folder contains:

| File            | Description                                     |
| --------------- | ----------------------------------------------- |
| `report.md`     | Deterministic extraction and attempt provenance |
| `transcript.md` | Captions or honest manual-recovery marker       |
| `prompts.md`    | Exact selected prompts and attempt provenance   |

The output root and each populated Subject contain `latest.json`. The root points to the latest finished invocation across subjects; each Subject points to its latest finished invocation. These include partial and failed runs with honest `completed` and `successful_models` fields, not only successful runs. Both pointers use the same metadata and explicit `subject`. Relative `run_dir` values resolve from the workspace working directory, including in the Subject pointer; an absolute custom output root produces absolute run paths. `--output-dir` is always the root above subjects.

The helper validates subject names and containment, reuses existing casing, and rejects traversal, Windows-invalid/reserved names, and redirected paths escaping the root. An OS lock serializes pointer publication; each JSON replacement is atomic. A `.latest-pending.json` journal survives interrupted publication. Run `--repair-pointers --output-dir <root>` from the original workspace to replay it without a Gemini call. The next pointer publication also repairs an existing journal first. Do not rerun extraction to repair pointers. The persistent lock is operational state under `<workspace>/tmp/video-to-action-locks/<output-root-hash>.lock`, never in the video archive. The nearest ancestor containing `CLAUDE.md`, `AGENTS.md`, or `.git` owns the lock; for custom roots without such an ancestor, the current workspace working directory owns it. Always invoke operations on a custom root from that same workspace. The resolved output-root hash gives separate roots separate locks and reuses the same lock for equivalent root paths. Clearing temporary locks is safe only when no extraction, migration, or pointer repair is active; the next operation recreates the directory and file automatically. The recovery journal stays in the archive so idle tmp cleanup cannot erase pending pointer recovery. If publication fails before its journal is saved, retain the run and inspect its report metadata to reconstruct pointers; never invent success.

## Existing Archive Migration

Only when separately requested, use `scripts/migrate_legacy.py --workspace <root> --evidence <JSON path>` to inventory flat timestamped runs, then repeat with `--apply`. Evidence retains source/destination paths, SHA-256 hashes, original pointer bytes, and the resulting pointer. Move run folders intact into `Legacy`, including old `procedure.md` outputs; never re-extract or rewrite historical content. Check the actual workspace contract, permissions, collisions, and concurrent changes before applying. Each workspace is independent.

Preserve existing valid latest metadata and change relocation fields only; root and Legacy pointers initially agree. An empty archive with an empty pointer becomes explicit no-run JSON (`latest_run` and `run_dir` null, `completed` false), with the old bytes retained in evidence. No subject pointer or invented run is created. Repeating a completed migration verifies hashes and performs no duplicate moves. Interrupted migration stops for evidence-led recovery rather than overwriting destinations.

Rollback procedure: first verify every destination still matches its recorded hashes, every original path is absent, and current pointers equal the recorded post-migration state. Move only recorded destinations back to their exact sources, restore original pointer bytes from evidence, and remove only the migration-created Legacy pointer after confirming it is unchanged. If any check fails, stop for review; do not overwrite newer runs or pointers.

## Attempt Provenance

Both `report.md` and `prompts.md` record, per phase:

- primary and fallback model names;
- processing mode, and `agentic-to-static` recovery when it applies;
- attempt role and bounded attempt number;
- sanitized error and transient/non-retryable classification;
- interaction ID, terminal state, and bounded provider error codes/messages when supplied;
- polling failure and cancellation outcome when polling stops;
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

| Parameter           | Default                              | Purpose                         |
| ------------------- | ------------------------------------ | ------------------------------- |
| `url`               | required                             | Public YouTube URL              |
| `--title`           | required                             | Exact supplied title            |
| `--subject`         | required for extraction              | Broad output category           |
| `--duration`        | required                             | Exact normalized duration       |
| `--tier`            | `free`                               | Credential and billing policy   |
| `--model`           | `gemini-3.8-flash`                   | Primary model                   |
| `--fallback-model`  | `gemini-3.6-flash`                   | One-attempt fallback            |
| `--processing`      | `static`                             | `static` or opt-in `agentic`    |
| `--agentic-probe`   | off                                  | One-call agentic status check   |
| `--deep-summary`    | on                                   | Include Deep Summary            |
| `--no-deep-summary` | off                                  | Skip Deep Summary               |
| `--technical`       | off                                  | Select Technical                |
| `--coding-video`    | off                                  | Confirm Technical relevance     |
| `--custom-request`  | empty                                | Explicit additional instruction |
| `--resolution`      | `default`                            | Optional low video resolution   |
| `--start` / `--end` | none                                 | Rejected in both modes          |
| `--output-dir`      | `Archive\Historical\Video-to-action` | Run-record root                 |
| `--check-setup`     | off                                  | No-API setup check              |
| `--dump-prompts`    | off                                  | Regenerate prompt reference     |
| `--self-test`       | off                                  | Deterministic no-API fixtures   |
| `--repair-pointers` | off                                  | Replay pending pointer writes   |

## Intent Routing

- `summarize`: present report findings; execute nothing.
- `learn`: treat the report as knowledge; saving elsewhere needs authorization.
- `follow`: present the Procedure and stop; execution needs authorization.

## Workflow

1. Confirm explicit invocation.
2. Gather missing URL, title, and duration together once; resolve Subject from supplied choices or clear context.
3. Reuse stated optional-phase and tier choices; default Deep Summary on, Technical off, and tier free. Forward an explicit additional user instruction through `--custom-request`; otherwise leave it empty.
4. From the workspace root, run the no-API setup check for the selected tier.
5. State the concise preflight and run the helper once.
6. Let the helper own per-phase retry, fallback, transcript, and artifact writes.
7. Present results, processing mode, attempt history (including any agentic-to-static recovery), phase errors, the report's agentic status line, transcript retrieval path, and LOW CONFIDENCE warnings.
8. If the transcript failed, name it as a failure in chat and include the exact `--complete-transcript` command printed by the helper.
9. Do not act on Procedure steps without separate authorization.

## Runtime Dependencies

The helper script imports the third-party packages below. It checks them before doing work (`--check-setup` and the automatic run preflight) and, when one is missing, reports the package with its install command. Always install with `python -m pip install <install-name>` — never bare `pip`, which can resolve to a different interpreter than the one running the helper. To restore every Skills dependency in one command, run `python -m pip install -r Skills/requirements.txt` from the workspace root.

| Import name            | Install name           | Used for          | Minimum version |
| ---------------------- | ---------------------- | ----------------- | --------------- |
| google.genai           | google-genai           | Video analysis    | 2.29.0          |
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
- run `python -X utf8 scripts/test_agentic.py` for static-default and explicit agentic inputs, agentic-to-static fallback, deprecated-model aliasing, the agentic probe and its status line, SDK serialization, bounded polling/cancellation, evidence checks, clipping rejection, and optional custom-request behavior;
- run `python -X utf8 scripts/test_subject_outputs.py` for subject safety, independent pointers, concurrency, interrupted publication, Legacy hash preservation, reruns, and collisions;
- compile with Python UTF-8 mode;
- audit Markdown tables for visual alignment and cells of at most 80 characters;
- validate the folder with `quick_validate.py` using separated streams; and
- make no real Gemini call during deterministic validation.

Terminal failed interactions retain their structured provider errors. Only explicit `503` or `UNAVAILABLE` codes qualify for the existing bounded capacity recovery; unknown failures, cancellation, and exhausted polling failures do not trigger resubmission. Diagnostics retain allowlisted fields only, never raw response payloads.
