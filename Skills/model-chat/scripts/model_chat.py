#!/usr/bin/env python3
"""
Model Chat - Multi-agent debate orchestrator (Uzzy adaptation).

Spawns N Claude participants into a shared conversation room where they debate,
disagree, and converge on solutions using round-robin turns. All participant
calls within a round run in parallel; later rounds see the full prior history.
A synthesizer call merges the debate into a final structured answer.

Worker participants are Anthropic Claude models called through the Anthropic
API. The orchestrating agent that launches this script may be Claude, Codex,
Antigravity, or the user directly.

Requires: Python 3.10+, `anthropic`, `python-dotenv`, and ANTHROPIC_API_KEY.
Run `model_chat.py --check-setup` to verify prerequisites without any API call.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_AGENTS = 5
DEFAULT_ROUNDS = 5
MAX_AGENTS = 8
MAX_ROUNDS = 10
MAX_TOKENS = 2048
SYNTHESIS_MAX_TOKENS = 4096
DEFAULT_OUTPUT_DIR = Path("tmp") / "model-chat"

SETUP_TASK_HINT = (
    "Setup is incomplete. See the pending model-chat setup/learning task in your "
    "workspace (Archive\\Tasks\\) for API key creation, safe storage, and dependency "
    "installation steps."
)

AGENT_FRAMINGS = [
    {
        "id": "systems-thinker",
        "framing": (
            "You tend to think in systems and architecture. You reason about "
            "structure, dependencies, second-order effects, and how pieces fit "
            "together. You look for leverage points and compounding mechanisms."
        ),
    },
    {
        "id": "pragmatist",
        "framing": (
            "You tend to think practically and focus on what ships fast. You're "
            "skeptical of overengineering and prefer simple, proven approaches. "
            "You ask 'does this actually work in practice?' before anything else."
        ),
    },
    {
        "id": "edge-case-finder",
        "framing": (
            "You tend to find edge cases, failure modes, and hidden assumptions. "
            "You stress-test ideas by asking 'what happens when X goes wrong?' "
            "You're the one who prevents catastrophic oversights."
        ),
    },
    {
        "id": "user-advocate",
        "framing": (
            "You tend to think about user experience and how things feel in "
            "practice. You optimize for clarity, simplicity, and delight. You "
            "ask 'would a real person actually use this?' and 'is this intuitive?'"
        ),
    },
    {
        "id": "contrarian",
        "framing": (
            "You tend to challenge assumptions and propose unconventional "
            "alternatives. You play devil's advocate not to be difficult, but "
            "because the best ideas survive strong opposition. You ask 'what if "
            "the opposite were true?'"
        ),
    },
    {
        "id": "first-principles",
        "framing": (
            "You reason from first principles. You strip away conventions and "
            "ask 'why does it have to be this way?' You're willing to propose "
            "radical simplifications that others overlook."
        ),
    },
    {
        "id": "risk-analyst",
        "framing": (
            "You think in terms of risk, probability, and downside protection. "
            "You weigh the cost of being wrong against the cost of being slow. "
            "You look for irreversible decisions and flag them."
        ),
    },
    {
        "id": "integrator",
        "framing": (
            "You look for synthesis and common ground. You find the 80% that "
            "everyone agrees on and surface the 20% that actually matters. You "
            "bridge different perspectives into coherent plans."
        ),
    },
]

SYSTEM_PROMPT_TEMPLATE = """\
You are one of {agent_count} AI participants in a collaborative debate room. \
Your role is to help solve a problem through genuine intellectual discourse.

{framing}

## Rules of engagement
- Read all previous messages carefully before responding.
- Build on, challenge, or refine what others have said — don't just repeat your own position.
- If you agree with someone, say so briefly and add something new.
- If you disagree, explain WHY with concrete reasoning.
- Be concise. 150-300 words max per response. No filler.
- Use your unique perspective — that's why you're here.
- Address other participants directly when responding to their points.
- It's fine to change your mind if someone makes a compelling argument.

## Format
Start your response with **[{agent_id}]:** then your contribution. No preamble.\
"""

SYNTHESIZER_PROMPT = """\
You are a senior synthesizer. You've just observed a {round_count}-round debate \
between {agent_count} AI participants on the following topic:

**{topic}**

Read the full debate transcript below, then produce a structured synthesis.

## Your output format

### Consensus
What did most or all participants agree on? List the 3-5 strongest points of agreement.

### Key Disagreements
Where did participants genuinely disagree? For each disagreement:
- State the tension clearly
- Summarize each side's strongest argument
- Give your assessment of which side is stronger and why

### Surprising Insights
Any unexpected ideas, edge cases, or reframings that emerged from the debate?

### Final Recommendation
Based on the full debate, what is the best path forward? Be specific and actionable.

## Debate Transcript
{transcript}\
"""


# ── Console helpers ──────────────────────────────────────────────────────────

def enable_windows_ansi() -> None:
    """Enable ANSI escape processing on Windows consoles."""
    if os.name == "nt":
        os.system("")


def get_width() -> int:
    try:
        return min(os.get_terminal_size().columns, 80)
    except OSError:
        return 80


def color(text: str, code: str) -> str:
    """ANSI color wrapper."""
    return f"\033[{code}m{text}\033[0m"


AGENT_COLORS = ["36", "33", "35", "32", "31", "34", "96", "93"]


def agent_color(agent_idx: int, text: str) -> str:
    return color(text, AGENT_COLORS[agent_idx % len(AGENT_COLORS)])


def print_header(text: str) -> None:
    w = get_width()
    print(color(f"\n{'=' * w}", "1;37"))
    print(color(f"  {text}", "1;37"))
    print(color(f"{'=' * w}\n", "1;37"))


def print_round_header(round_num: int, total: int) -> None:
    w = get_width()
    print(color(f"\n{'-' * w}", "90"))
    print(color(f"  ROUND {round_num}/{total}", "1;97"))
    print(color(f"{'-' * w}", "90"))


# ── Preflight ────────────────────────────────────────────────────────────────

def load_env_files() -> None:
    """Load .env from the current working directory, then the script's folder.

    Values already present in the environment are never overwritten.
    """
    from dotenv import load_dotenv

    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        load_dotenv(cwd_env)
    script_env = Path(__file__).resolve().parent / ".env"
    if script_env.is_file():
        load_dotenv(script_env)


def check_setup(verbose: bool = True) -> bool:
    """Verify dependencies and API key without making any API call.

    Never prints the key itself - only whether it is present.
    """
    ok = True

    try:
        import anthropic  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: the 'anthropic' package is not installed "
                  "(install with: python -m pip install anthropic).")

    try:
        import dotenv  # noqa: F401
    except ImportError:
        ok = False
        if verbose:
            print("MISSING: the 'python-dotenv' package is not installed "
                  "(install with: python -m pip install python-dotenv).")

    if ok:
        load_env_files()
        if os.environ.get("ANTHROPIC_API_KEY"):
            if verbose:
                print("OK: ANTHROPIC_API_KEY is set (value not displayed).")
        else:
            ok = False
            if verbose:
                print("MISSING: ANTHROPIC_API_KEY is not set in the environment "
                      "or a discoverable .env file.")

    if verbose:
        if ok:
            print("Setup check passed. No API call was made.")
        else:
            print(SETUP_TASK_HINT)
    return ok


# ── Core ─────────────────────────────────────────────────────────────────────

async def get_agent_response(
    client,
    agent_id: str,
    system_prompt: str,
    conversation_history: list,
    topic: str,
    model: str,
) -> str:
    """Get a single agent's response (collected, not streamed to stdout)."""
    messages = []

    # First message: the topic
    messages.append({"role": "user", "content": f"**Topic for debate:** {topic}"})

    # Build alternating messages from conversation history
    for entry in conversation_history:
        messages.append({"role": "assistant", "content": entry["content"]})
        messages.append({
            "role": "user",
            "content": "Continue the debate. Respond to the points made above."
        })

    if conversation_history:
        # Replace the last generic prompt with a more specific one
        messages.pop()
        messages.append({
            "role": "user",
            "content": (
                "It's your turn. Respond to the discussion above. "
                "Build on, challenge, or refine what's been said."
            ),
        })

    # Use streaming + get_final_message for timeout protection, collect silently
    async with client.messages.stream(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=messages,
    ) as stream:
        response = await stream.get_final_message()

    return response.content[0].text


def print_agent_response(agent_idx: int, agent_id: str, text: str) -> None:
    """Print an agent's response with color and formatting."""
    prefix = agent_color(agent_idx, f"\n[{agent_id}]")
    sys.stdout.write(prefix + " ")
    sys.stdout.write(agent_color(agent_idx, text))
    sys.stdout.write("\n")
    sys.stdout.flush()


def save_outputs(
    output_base: Path,
    conv_data: dict,
    topic: str,
    agent_count: int,
    round_count: int,
    model: str,
) -> tuple:
    """Save conversation.json, synthesis.md, and the latest-run pointer."""
    run_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = output_base / run_ts
    output_dir.mkdir(parents=True, exist_ok=True)

    conv_path = output_dir / "conversation.json"
    conv_path.write_text(
        json.dumps(conv_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    synth_path = output_dir / "synthesis.md"
    synth_path.write_text(
        f"# Model Chat Synthesis\n\n"
        f"**Topic:** {topic}\n"
        f"**Agents:** {agent_count} | **Rounds:** {round_count} | "
        f"**Model:** {model}\n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n{conv_data.get('synthesis', '')}\n",
        encoding="utf-8",
    )

    # Windows-safe latest-run pointer (JSON metadata file, not a symlink)
    latest_path = output_base / "latest.json"
    latest_path.write_text(
        json.dumps(
            {
                "latest_run": run_ts,
                "run_dir": str(output_dir),
                "topic": topic,
                "completed": conv_data.get("completed", True),
                "timestamp": datetime.now().isoformat(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return conv_path, synth_path


async def run_debate(
    topic: str,
    agent_count: int,
    round_count: int,
    interactive: bool,
    model: str,
    output_base: Path,
) -> dict:
    """Run a multi-agent debate."""
    import anthropic

    client = anthropic.AsyncAnthropic()

    # Select agents (cycle if more than available framings)
    agents = []
    for i in range(agent_count):
        framing = AGENT_FRAMINGS[i % len(AGENT_FRAMINGS)]
        agents.append({
            "idx": i,
            "id": framing["id"] if i < len(AGENT_FRAMINGS) else f"{framing['id']}-{i}",
            "system_prompt": SYSTEM_PROMPT_TEMPLATE.format(
                agent_count=agent_count,
                framing=framing["framing"],
                agent_id=framing["id"],
            ),
        })

    conversation: list = []
    failures: list = []

    print_header(f"MODEL CHAT — {agent_count} agents, {round_count} rounds")
    print(color(f"  Topic: {topic}\n", "97"))
    print(color(f"  Model: {model}", "90"))
    print(color(
        "  Cost note: every participant receives the full prior history each "
        "round,\n  so token cost grows steeply with agents x rounds.", "90"))
    print(color("\n  Agents:", "90"))
    for a in agents:
        print(agent_color(a["idx"], f"    - {a['id']}"))
    print()

    # ── Debate rounds ────────────────────────────────────────────────────
    for round_num in range(1, round_count + 1):
        print_round_header(round_num, round_count)

        tasks = [
            get_agent_response(
                client=client,
                agent_id=agent["id"],
                system_prompt=agent["system_prompt"],
                conversation_history=conversation.copy(),
                topic=topic,
                model=model,
            )
            for agent in agents
        ]

        print(color("  (all agents thinking...)", "90"))
        # Per-agent failure capture: one failed call must not kill the debate
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        effective = 0
        for agent, result in zip(agents, responses):
            if isinstance(result, BaseException):
                failures.append({
                    "round": round_num,
                    "agent_id": agent["id"],
                    "error": f"{type(result).__name__}: {result}",
                    "timestamp": datetime.now().isoformat(),
                })
                print(color(
                    f"\n[{agent['id']}] FAILED this round: "
                    f"{type(result).__name__}: {result}", "31"))
                continue

            effective += 1
            print_agent_response(agent["idx"], agent["id"], result)
            conversation.append({
                "round": round_num,
                "agent_id": agent["id"],
                "content": f"**[{agent['id']}]:** {result}",
                "timestamp": datetime.now().isoformat(),
            })

        print(color(
            f"\n  Round {round_num}: {effective}/{agent_count} agents responded.",
            "90"))

        if effective == 0:
            print(color(
                "  No agent succeeded this round. Stopping the debate early.",
                "31"))
            break

        # Interactive mode: prompt for user input between rounds
        if interactive and round_num < round_count:
            print(color(
                "\n  [Interactive] Press Enter to continue, or type to inject a message:",
                "90",
            ))
            try:
                user_input = input(color("  > ", "97")).strip()
                if user_input:
                    print(color(f"\n  [User]: {user_input}", "1;97"))
                    conversation.append({
                        "round": round_num,
                        "agent_id": "user",
                        "content": f"**[User (moderator)]:** {user_input}",
                        "timestamp": datetime.now().isoformat(),
                    })
            except EOFError:
                pass

    # ── Synthesis ────────────────────────────────────────────────────────
    synthesis = ""
    if conversation:
        print_header("SYNTHESIS")

        transcript = "\n\n".join(entry["content"] for entry in conversation)
        synth_prompt = SYNTHESIZER_PROMPT.format(
            round_count=round_count,
            agent_count=agent_count,
            topic=topic,
            transcript=transcript,
        )

        try:
            synthesis_parts = []
            async with client.messages.stream(
                model=model,
                max_tokens=SYNTHESIS_MAX_TOKENS,
                messages=[{"role": "user", "content": synth_prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    sys.stdout.write(color(text, "97"))
                    sys.stdout.flush()
                    synthesis_parts.append(text)
            synthesis = "".join(synthesis_parts)
            print("\n")
        except Exception as exc:  # noqa: BLE001
            synthesis = ""
            failures.append({
                "round": None,
                "agent_id": "synthesizer",
                "error": f"{type(exc).__name__}: {exc}",
                "timestamp": datetime.now().isoformat(),
            })
            print(color(
                f"\n  Synthesis failed: {type(exc).__name__}: {exc}\n"
                "  The conversation log will still be saved.", "31"))

    # ── Save outputs ─────────────────────────────────────────────────────
    conv_data = {
        "topic": topic,
        "agent_count": agent_count,
        "round_count": round_count,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "agents": [{"id": a["id"], "idx": a["idx"]} for a in agents],
        "conversation": conversation,
        "failures": failures,
        "synthesis": synthesis,
        "completed": bool(conversation),
    }

    conv_path, synth_path = save_outputs(
        output_base, conv_data, topic, agent_count, round_count, model
    )
    print(color(f"  Saved: {conv_path}", "90"))
    print(color(f"  Saved: {synth_path}", "90"))

    return conv_data


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    enable_windows_ansi()

    parser = argparse.ArgumentParser(
        description="Model Chat — Multi-agent debate via the Anthropic API"
    )
    parser.add_argument("topic", nargs="?", default=None,
                        help="Topic or problem to debate")
    parser.add_argument("--agents", type=int, default=DEFAULT_AGENTS,
                        help=f"Number of agents (default: {DEFAULT_AGENTS}, "
                             f"min 2, max {MAX_AGENTS})")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS,
                        help=f"Number of rounds (default: {DEFAULT_ROUNDS}, "
                             f"min 1, max {MAX_ROUNDS})")
    parser.add_argument("--interactive", action="store_true",
                        help="Prompt for optional moderator input between rounds")
    parser.add_argument("--model", default=os.environ.get(
                            "MODEL_CHAT_MODEL", DEFAULT_MODEL),
                        help=f"Anthropic model id (default: {DEFAULT_MODEL}, "
                             "or MODEL_CHAT_MODEL env var)")
    parser.add_argument("--output-dir", default=os.environ.get(
                            "MODEL_CHAT_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)),
                        help="Base directory for run outputs (default: "
                             "tmp\\model-chat under the current directory, or "
                             "MODEL_CHAT_OUTPUT_DIR env var)")
    parser.add_argument("--check-setup", action="store_true",
                        help="Verify dependencies and API key, make no API call, "
                             "then exit")
    args = parser.parse_args()

    if args.check_setup:
        sys.exit(0 if check_setup(verbose=True) else 1)

    if not args.topic:
        parser.error("a debate topic is required (or use --check-setup)")

    if not 2 <= args.agents <= MAX_AGENTS:
        parser.error(f"--agents must be between 2 and {MAX_AGENTS}")
    if not 1 <= args.rounds <= MAX_ROUNDS:
        parser.error(f"--rounds must be between 1 and {MAX_ROUNDS}")

    if not check_setup(verbose=False):
        check_setup(verbose=True)
        sys.exit(1)

    output_base = Path(args.output_dir)

    try:
        asyncio.run(run_debate(
            topic=args.topic,
            agent_count=args.agents,
            round_count=args.rounds,
            interactive=args.interactive,
            model=args.model,
            output_base=output_base,
        ))
    except KeyboardInterrupt:
        print(color("\n\nDebate cancelled by user. No further API calls will be "
                    "made.", "31"))
        sys.exit(130)


if __name__ == "__main__":
    main()
