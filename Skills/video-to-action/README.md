# Video-to-Action

`video-to-action` turns an explicitly requested public YouTube video into one
deterministic run folder containing `report.md`, `transcript.md`, and
`prompts.md`. It defaults to the free tier with Gemini 3.6 Flash, uses bounded
Gemini 3.5 Flash fallback for transient capacity failures, and never repeats
phase choices already supplied by the user.

The Python helper is the sole artifact writer. Invoke `/video-to-action` with the
public URL, exact title, exact duration, and any optional Deep Summary or
coding-only Technical selection. Use `--check-setup` and `--self-test` for
no-API verification; `--dump-prompts` regenerates `PROMPTS.md`.

Paid execution is opt-in through `--tier paid` and `GEMINI_API_KEY_PAID`.
Transcript retrieval remains independent from Gemini processing and retains the
existing manual recovery route when captions cannot be fetched.

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable
artifacts while this skill retains content and workflow ownership.
