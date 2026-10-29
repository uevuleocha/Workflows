# Video-to-Action

Gemini analysis uses static video processing by default. `--processing agentic` opts into agentic processing; any agentic phase that fails is retried through static processing automatically. Google's agentic video route was failing for every model as of 2026-10-28, so run `--agentic-probe` (one agentic call on a fixed 19-second video, writes `agentic-status.json` at the output root, creates no run folder) to check whether it has recovered; every report shows the latest probe result, and three consecutive WORKING probes are the bar before considering agentic again. An optional `--custom-request` carries only an explicit additional user instruction in the main call and adds a `Your Specific Request` answer section to `report.md`; omitted requests add no section or call. Deep Summary is included by default; explicitly opt out with `--no-deep-summary`. Technical remains opt-in. No FFmpeg, video download, or screenshot pipeline is involved.

Requires `google-genai>=2.29.0`. Hard `--start`/`--end` clipping is rejected in both processing modes; a custom timestamp question does not restrict video input. Run `scripts/test_agentic.py` for no-network static/agentic, fallback, probe and custom-request checks. Successful and failed interactions retain IDs and sanitized provider errors. Transient polling failures retry the same job at most three times (2/5/10-second delays), without duplicate analysis submissions. Background polling is bounded and records processing evidence and available numeric token usage; see SKILL.md for failure and cancellation behavior.

`video-to-action` turns an explicitly requested public YouTube video into one deterministic run folder containing `report.md`, `transcript.md`, and `prompts.md`. It defaults to the free tier with Gemini 3.8 Flash, uses bounded Gemini 3.6 Flash fallback for transient capacity failures (Google retired 3.7 Flash on 2026-10-08 and serves it as 3.8, so the helper maps deprecated IDs to their served models), and never repeats phase choices already supplied by the user.

The Python helper is the sole artifact writer. Invoke `/video-to-action` with the public URL, exact title, exact duration, resolved broad subject, and any Deep Summary opt-out or coding-only Technical selection. Run it from the workspace root: `.env` lookup checks the current working directory first and the helper's `scripts/` directory second, and `--check-setup` reports both paths without exposing credential values. Use `--self-test` for no-API verification; `--dump-prompts` regenerates `PROMPTS.md`.

Paid execution is opt-in through `--tier paid` and `GEMINI_API_KEY_PAID`. Transcript retrieval remains independent from Gemini processing: `youtube-transcript-api` stays primary, optional `yt-dlp` provides a manual-first English-caption fallback, and the existing `--complete-transcript` route remains available when both automatic paths fail. Transcript failures never discard successful Gemini artifacts and must be stated in the chat results report.

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.

## Subjects and latest runs

Runs live under Archive/Historical/Video-to-action/<Subject>/<timestamp - title>/. Root and populated-subject latest.json pointers track the latest finished invocation with honest status. Use --subject for extraction and --repair-pointers to recover an interrupted pointer update without another API call. Use scripts/test_subject_outputs.py for no-API subject and migration checks. The separately authorized migrate_legacy.py helper moves old runs intact and saves hash/pointer recovery evidence. See SKILL.md for migration and rollback rules.

Pointer locks live in the owning workspace's tmp/video-to-action-locks folder and are recreated after idle cleanup. Clear that folder only when no extraction, migration, or pointer repair is running. Recovery journals stay with the archive. Custom output roots without an ancestor workspace marker must always be operated from the same workspace working directory.
