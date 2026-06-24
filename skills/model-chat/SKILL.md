---
name: model-chat
description: Run a script-backed multi-agent debate where N Claude participants discuss a topic across parallel rounds via the Anthropic API, then synthesize a final answer. Setup-gated; requires an Anthropic API key. Use only when the user explicitly invokes /model-chat.
---

# Model Chat

Run a deterministic multi-agent debate through the bundled `scripts\model_chat.py` helper. N Claude participants with distinct reasoning framings debate a topic across R rounds — all participants respond in parallel each round and see the full prior history — then a synthesizer call merges the debate into a structured final answer. Every run saves durable artifacts.

**Worker participants are Anthropic Claude models called through the Anthropic API.** This skill does not pretend to be provider-neutral: the orchestrating agent that launches and supervises the script may be Claude, Codex, or Antigravity, but the debate itself runs on the Anthropic API and bills per token.

## Project Contract

Follow the host project's canonical contract, such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Its safety rules, approval gates, path limits, and product-code workflow remain unchanged.

This is a discussion and decision-support workflow. Invoking it does not authorize implementation, product-code edits, or operational commands beyond running the bundled script with the user's explicit consent.

## Invocation

Run this workflow only when the user explicitly invokes:

- `/model-chat`

Do not activate from phrases such as "model chat", "agent debate", "spawn a chat room", or similar natural language unless the slash command is present.

## Distinction From agent-chatrooms

These two skills overlap conceptually but stay separate:

- `agent-chatrooms` uses whatever native subagent capability the active environment provides. Chat-first, no API key, no script, billed through the host platform.
- `model-chat` runs the bundled Python script against the Anthropic API. Deterministic mechanics, durable artifacts every run, interactive moderator injection, works even when the host exposes no native subagent tools — but requires API setup and pays Anthropic directly.

Prefer `agent-chatrooms` for quick zero-setup debates. Prefer `model-chat` when determinism, durable logs, moderator steering, or host-independence matter.

## Prerequisites And Setup Gate

Before any real run, the orchestrating agent must verify:

1. `scripts\model_chat.py` exists in this skill folder.
2. Python 3.10+ is available.
3. The `anthropic` and `python-dotenv` packages are installed.
4. `ANTHROPIC_API_KEY` is available via the environment or a `.env` file. Never display, echo, or save the key value.

Run the harmless preflight (no API call, no cost):

```text
python scripts\model_chat.py --check-setup
```

If any prerequisite is missing, **stop**. Do not attempt the debate. Route the user to the pending model-chat setup/learning task under the host workspace's task directory (for the Uzzy Ecosystem: `Archive\Tasks\`). Do not improvise installation steps outside that task without the user's consent.

## Cost Warning

Every participant receives the **entire prior conversation** each round, so input-token cost grows steeply — roughly quadratically — with agents × rounds. The default 5 agents × 5 rounds produces 25 debate responses plus a synthesis call over a growing transcript. For a first controlled run, use something like `--agents 3 --rounds 2` and verify current Anthropic pricing first. Never start a paid run without the user's explicit go-ahead for that run.

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic` | required | Topic or problem to debate (positional argument) |
| `--agents` | `5` | Number of participants; min `2`, max `8` |
| `--rounds` | `5` | Number of debate rounds; min `1`, max `10` |
| `--interactive` | off | Prompt for optional moderator input between rounds |
| `--model` | `claude-sonnet-4-6` | Anthropic model id; also via `MODEL_CHAT_MODEL` env var |
| `--output-dir` | `tmp\model-chat` | Base output directory relative to the working directory; also via `MODEL_CHAT_OUTPUT_DIR` env var |
| `--check-setup` | off | Verify dependencies and key presence with no API call, then exit |

## Agent Framings

The script cycles through eight reasoning framings (in order):

1. `systems-thinker` — structure, dependencies, second-order effects, leverage points
2. `pragmatist` — what ships fast; skeptical of overengineering
3. `edge-case-finder` — failure modes, hidden assumptions, stress tests
4. `user-advocate` — clarity, simplicity, "would a real person use this?"
5. `contrarian` — challenges assumptions; best ideas survive strong opposition
6. `first-principles` — strips conventions; proposes radical simplifications
7. `risk-analyst` — probability, downside protection, irreversible decisions
8. `integrator` — synthesis, common ground, bridging perspectives

With the default 5 agents, the first five framings participate.

## Debate Lifecycle

1. **Preflight** — dependency and key checks; on failure the script exits with a pointer to the setup task and makes no API call.
2. **Round loop** — each round, every participant receives the topic plus the full shared history and responds in parallel (async API calls). Responses append to the shared history with round number, agent id, and timestamp.
3. **Per-agent failure capture** — a failed API call is logged into the run's `failures` list and printed; the round continues with the remaining participants and reports the effective count. The debate stops early only if an entire round fails.
4. **Interactive mode** — with `--interactive`, the script pauses between rounds; the user may press Enter to continue or type a moderator message that is appended to the shared history as `[User (moderator)]`.
5. **Synthesis** — a separate API call reads the full transcript and streams a structured synthesis (Consensus / Key Disagreements / Surprising Insights / Final Recommendation). A synthesis failure is logged; the conversation log still saves.
6. **Save** — outputs are written to a timestamped run folder; a `latest.json` pointer is updated.
7. **Cancellation** — Ctrl+C stops cleanly without further API calls.

## Output Files

Each run saves to `<output-dir>\<YYYYMMDD-HHMMSS>\`:

| File | Description |
|------|-------------|
| `conversation.json` | Full structured log: topic, config, model, agents, every round entry, failures, synthesis, completion flag |
| `synthesis.md` | The final synthesized answer with run metadata |

`<output-dir>\latest.json` is a Windows-safe pointer (plain JSON metadata, not a symlink) recording the latest run folder, topic, and timestamp. Previous runs are preserved.

### conversation.json shape

```json
{
  "topic": "...",
  "agent_count": 5,
  "round_count": 5,
  "model": "claude-sonnet-4-6",
  "timestamp": "ISO-8601",
  "agents": [{"id": "systems-thinker", "idx": 0}],
  "conversation": [
    {"round": 1, "agent_id": "systems-thinker", "content": "**[systems-thinker]:** ...", "timestamp": "ISO-8601"}
  ],
  "failures": [
    {"round": 2, "agent_id": "contrarian", "error": "APIStatusError: ...", "timestamp": "ISO-8601"}
  ],
  "synthesis": "...",
  "completed": true
}
```

All files are written with explicit UTF-8 encoding.

## Orchestrating Agent Workflow

1. Confirm explicit `/model-chat` invocation and extract the topic, flags, and any model/output preferences.
2. Run `--check-setup`; if it fails, stop and route to the setup task.
3. Confirm the user accepts the cost of the configured run (agents, rounds, model).
4. Run the script from the host workspace root so the default output directory lands inside the workspace.
5. After completion, present: key agreements, genuine disagreements, the synthesis (or its path), notable debate moments, and the run folder path.
6. Do not proceed from debate output into implementation unless the user separately authorizes an execution workflow.

## Boundaries

Do:

- require the exact `/model-chat` slash command
- preflight setup before every real run and route to the setup task on failure
- warn about per-run API cost before launching
- keep API keys out of chat, logs, and saved artifacts
- report participant failures and the effective agent count honestly

Do not:

- auto-trigger this skill from natural language
- claim provider neutrality for the debate participants
- make any paid API call without the user's explicit go-ahead for that run
- expose, echo, or persist the API key
- hard-code course-machine paths, `.venv` locations, or Unix symlinks
- treat the synthesis as a decision that authorizes implementation

## Edge Cases

- **Missing key or packages:** preflight fails; stop and route to the pending setup task.
- **Invalid model id:** the first round fails per-agent with the API error; report it and suggest verifying the model id against current Anthropic documentation.
- **Single agent fails repeatedly:** debate continues; the run records each failure and the synthesis notes reduced perspectives via the effective count.
- **Entire round fails:** the script stops early, saves whatever conversation exists, and marks `completed` accordingly.
- **User cancels mid-run:** Ctrl+C exits cleanly; partial results before the interrupt are not saved — rerun with fewer rounds if cost is the concern.
- **More than 8 agents requested:** capped at 8 (framings would repeat and cost grows steeply).
- **Non-interactive shells:** `--interactive` degrades gracefully on EOF and continues the debate.

## Validation

After creating or updating this skill:

- confirm only `/model-chat` activates it
- confirm the setup gate stops the workflow when prerequisites are missing
- confirm the cost warning and key-safety rules are present
- confirm no Nick/Mac paths, fixed `.venv`, Unix symlinks, or course `active/` output paths remain
- confirm all file writes in the script specify UTF-8 explicitly
- run `python scripts\model_chat.py --check-setup` as a harmless smoke test (no API call)
- validate the folder with the installed `quick_validate.py` in UTF-8 mode (`-X utf8`)
