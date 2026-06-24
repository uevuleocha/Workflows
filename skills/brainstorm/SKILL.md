---
name: brainstorm
description: Enter Brainstorming mode for structured, collaborative, no-code-first thinking around a problem, tool, workflow, automation, architecture, implementation direction, or prompt-engineering target. Use when the user explicitly invokes /brainstorm, use brainstorm, use the brainstorm skill, or a clear equivalent naming this skill.
---

# Brainstorm

Enter Brainstorming mode: a structured, collaborative, high-focus thinking phase where the User and Agent explore ideas before planning or implementation.

This skill is for shaping a problem, tool, workflow, automation, architecture, implementation direction, or prompt-engineering target. It should generate useful ideas early, then gradually converge toward stronger decisions and concrete next steps.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

## Invocation

Treat these as direct invocation and enter Brainstorming mode:

- `/brainstorm`
- `use brainstorm`
- `use the brainstorm skill`
- clear equivalents where the user explicitly names this skill

Do not auto-trigger this skill from broad planning, debugging, or idea language unless the user explicitly names or invokes the `brainstorm` skill.

If the user only wants a quick answer or feasibility check outside Brainstorming mode, answer directly without entering the mode.

## Brainstorming Mode Contract

Invoking this skill means the session is in Brainstorming mode.

While in Brainstorming mode:

- every assistant response must end with the mode footer described below
- Brainstorming mode remains active until the user explicitly exits, ends, stops, clears, or terminates Brainstorming mode. A later invocation of another mode does not end Brainstorming mode; the modes layer together.
- if the user says "exit all modes", "end all modes", "stop all modes", "clear all modes", or "terminate all modes", all active modes including Brainstorming are ended
- the Agent should be locked in, active, and willing to speak up
- the Agent should ask clarifying and enlightening questions
- the Agent should contribute ideas, tradeoffs, risks, and alternate paths
- the Agent should help the User converge toward a verdict, direction, or next steps
- do not silently create plans, summaries, workflows, memory updates, or implementation files

Mode footer: if Brainstorming is the only active mode, end with `Mode = Brainstorming`. If multiple modes are active, end with `Modes = Brainstorming + Mode B + ... + Mode Z` using every active mode exactly once. Order does not matter, but keep it consistent when practical.

When the User ends Brainstorming mode, the normal next step is often `$imp-upd-plan`, but that handoff is not automatic.

## Required Intake

Before deep brainstorming, ask for or confirm the intake. If the user already supplied enough detail, summarize what is known and ask only for missing or uncertain items.

Use this prompt shape when intake is needed:

```text
We are in Brainstorming mode. Before we start throwing ideas around, let me frame the target.

1. What are we building, solving, or working toward?
2. What is the north-star goal?
3. How would you like to approach this brainstorming session?
4. Are there milestones, stepping stones, or implementation checkpoints you already care about?
5. Are there debugging-friendly checkpoints we should design in from the start?
6. What building blocks or smaller pieces do we need to fully understand first?
7. What does the ideal workflow look like?
8. Can we explain this in an "Explanation for Dummies" version?
```

After intake, summarize the working frame back to the user before pushing deeper.

## Brainstorming Workflow

Use this order unless the user clearly wants a smaller path:

1. **Frame the north star**
   - Identify the end goal, success conditions, and what problem the idea solves.
   - Separate what is confirmed from what is still assumed.

2. **Open the idea field**
   - Generate useful options, questions, approaches, constraints, and possible shapes.
   - Balance quantity and quality early so the User has enough surface area to react to.

3. **Understand the building blocks**
   - Identify smaller concepts, inputs, data flows, tools, workflows, or dependencies that must be understood first.
   - Use existing patterns, skills, workflows, or components as reference points when relevant.

4. **Simplify the concept**
   - When useful, produce an `Explanation for Dummies` version.
   - Use plain-language breakdowns to test whether the idea is actually understood.

5. **Pressure-test the ideas**
   - Ask clarifying questions.
   - Identify tradeoffs, weak assumptions, risks, missing pieces, and likely failure paths.
   - Challenge ideas respectfully when the reasoning is weak or incomplete.

6. **Converge toward quality**
   - Narrow the field toward the best direction, likely verdict, or next-step sequence.
   - Make clear what is decided, what is still open, and what should be deferred.

7. **Define next steps**
   - End each meaningful cycle with concrete next-step options.
   - If implementation planning is ready, suggest `$imp-upd-plan` after the User ends Brainstorming mode.

## No-Code / LTNEY-First Behavior

Brainstorming mode is no-code / LTNEY-first by default.

Do:

- discuss feasibility
- sketch architecture and workflow shapes
- compare approaches
- define milestones and stepping stones
- design debugging-friendly checkpoints
- refine prompts or operating instructions
- identify what a future implementation plan should contain

Do not:

- generate implementation code by default
- directly edit product source files
- create implementation plans automatically
- create or edit workflow/memory files silently
- treat brainstorming as approval to execute

If the User asks to move into code, planning, skill creation, or another execution workflow, confirm the mode switch or use the appropriate skill such as `green-light`, `imp-upd-plan`, or `global-skills-creator`.

## Agent Participation Rules

The Agent is a thinking partner, not just a stenographer.

The Agent should:

- bring useful ideas to the table
- ask strong clarifying questions
- point out hidden dependencies
- name tradeoffs clearly
- identify missing inputs
- offer alternate paths when one path looks weak
- preserve the User's north star while raising the technical bar
- avoid being timid when a design choice looks risky or underdefined

The Agent should not dominate the verdict. The User primarily decides when the direction is good enough.

## Explanation For Dummies

When useful, create a simplified explanation of the idea as if explaining it to a very young beginner.

Use this to test clarity:

```text
Explanation for Dummies:
[plain-language version of what we are trying to do]
```

If the simple version is confusing, the original idea probably needs more framing before implementation planning.

## Next-Step Convergence

Brainstorming should move toward next steps.

As the session develops, keep a visible sense of:

- what seems decided
- what still needs an answer
- which ideas are strongest
- what can be ignored or deferred
- what the next practical move should be

When the User indicates the verdict is in or calls off Brainstorming mode, summarize:

- the chosen direction
- key decisions
- remaining open questions
- recommended next steps
- whether `$imp-upd-plan` is the right next skill to invoke

Do not create the plan automatically.

## Output Format

Use the output shape that fits the moment.

Useful Brainstorming outputs include:

- question sets
- idea lists
- tradeoff comparisons
- workflow sketches
- architecture options
- risk lists
- assumptions and unknowns
- `Explanation for Dummies`
- next-step options
- verdict summaries

Keep responses structured enough to be useful, but do not over-format every exchange if a direct thinking response is better.

Every response while Brainstorming mode remains active must end with the mode footer as described in the Brainstorming Mode Contract section above.

## Boundaries

Do:

- think collaboratively
- ask questions
- contribute ideas
- clarify the north star
- surface risks
- converge toward next steps
- recommend the right next skill when ready

Do not:

- edit product source files directly
- generate product code by default
- automatically create implementation plans
- treat Brainstorming mode as a greenlight for execution

## Validation

After creating or updating this skill itself:

- confirm local skill files exist
- confirm `Mode = Brainstorming` appears exactly
- confirm the no-code / LTNEY-first boundary exists
- confirm the skill does not automatically invoke `imp-upd-plan`
- validate folder-style skills with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`).
