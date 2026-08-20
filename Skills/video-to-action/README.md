# Video-to-Action

`video-to-action` turns an explicitly requested public YouTube video into one deterministic run folder containing `report.md`, `transcript.md`, and `prompts.md`. It defaults to the free tier with Gemini 3.7 Flash, uses bounded Gemini 3.6 Flash fallback for transient capacity failures, and never repeats phase choices already supplied by the user.

The Python helper is the sole artifact writer. Invoke `/video-to-action` with the public URL, exact title, exact duration, and any optional Deep Summary or coding-only Technical selection. Run it from the workspace root: `.env` lookup checks the current working directory first and the helper's `scripts/` directory second, and `--check-setup` reports both paths without exposing credential values. Use `--self-test` for no-API verification; `--dump-prompts` regenerates `PROMPTS.md`.

Paid execution is opt-in through `--tier paid` and `GEMINI_API_KEY_PAID`. Transcript retrieval remains independent from Gemini processing: `youtube-transcript-api` stays primary, optional `yt-dlp` provides a manual-first English-caption fallback, and the existing `--complete-transcript` route remains available when both automatic paths fail. Transcript failures never discard successful Gemini artifacts and must be stated in the chat results report.

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
