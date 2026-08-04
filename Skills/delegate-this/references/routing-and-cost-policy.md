# Routing and Cost Policy

Read this before routing any Mode A or Mode B work. It governs *which* platform receives *which* assignment, and under what cost and trust constraints.

Nothing here expands the user's authorization. The authorized platform set for a run is decided by the user, not by this policy.

---

## Standing Preference Order

1. Claude Code
2. Codex
3. zCode
4. Hermes
5. Antigravity

This guides **recommendations only**. It is a tiebreaker, not a routing algorithm. A lower-preference platform wins whenever the routing factors below say it should — for example, when it holds local state the higher-preference platform lacks.

---

## Routing Factors

Weigh all of these against the assignment before choosing a platform:

- Reasoning difficulty
- Risk and reversibility
- Platform-local knowledge or state
- Required tools, browser sessions, or logins
- Context size
- Parallelizability
- File ownership conflicts
- Subscription usage
- Pay-as-you-go cost
- Need for independent verification
- Integration complexity

Two factors override preference outright:

- **Platform-local state.** If only one platform can see the thing, route there.
- **File ownership.** If routing two assignments to the same platform would create two writers for one file, split or serialize instead.

---

## Standing Policies

- **Claude Code and Codex** are preferred for complex architecture, integration, and higher-risk skill work — when authorized and available.
- **zCode** normally uses its native subscription-backed GLM models.
- **Hermes is provider-neutral.** Its provider/model surface is dynamic — see the **Provider-Neutral Hermes Routing** section below. Never permanently bind Hermes to a single provider, and never downgrade it based on GLM, OpenAI, Codex, or zCode.
- **Avoid unnecessary simultaneous heavy usage** of a shared quota pool. If two assignments draw on the same subscription/quota pool in the same wave, either serialize them or justify the concurrency.
- **Any paid API model requires explicit user approval.** Never infer it. Never treat a previous run's approval as standing. **Pay-as-you-go providers always require explicit approval.**
- **Antigravity** defaults to low-risk research and review. It may receive very small, isolated, low-risk edits only when the user specifically includes it for that. Never high-risk work under the default profile.

---

## Provider-Neutral Hermes Routing

Hermes is routed by **capability, trust, and tools** — not by a fixed provider label. Before routing any assignment to Hermes:

1. **Ask which provider/model Hermes currently uses** and **which subscription/quota pool it shares.** Do not assume the previous run's provider; the surface is dynamic.
2. **Route by capability, trust, and tools** — the same routing factors as every other platform. Provider identity is an input to routing, not a label.
3. **Schedule according to current quota capacity.** If the configured provider is near its quota ceiling, serialize, defer, or reroute rather than overload it.
4. **Never permanently bind or downgrade Hermes** based on GLM, OpenAI, Codex, or zCode. A run-time pairing is a run-time decision, recorded in the delegation record, not a standing downgrade.
5. **Pay-as-you-go providers always require explicit approval** — for this run, not inferred from a previous one.

Record the resolved provider/model and quota pool in the delegation record (for example in the Assignment Overview's Hermes rows) so the run-time pairing is visible and reversible.

---

## Model Recommendation Policy

**Do not hardcode a fast-changing catalog of every model on every platform.** Model names, tiers, and availability change faster than this file can be maintained. Recommend from known capability and the shape of the task, not from a memorized list.

The handoff of model choice runs like this:

1. **The orchestrator may recommend** a platform/model pairing when it has a defensible reason.
2. **The user chooses the actual model** when launching the receiving platform.
3. **After reading its packet, the receiving platform gets one opportunity** to recommend a different, currently available model.
4. **If the user rejects that recommendation, the agent proceeds** with the user's selection. It does not re-argue.
5. **Paid API use still requires explicit approval**, regardless of who recommended it.
6. **Hermes may inspect its dynamic provider configuration** and recommend among the providers currently configured there.

### Three distinct things, never conflated

| Term                       | Meaning                                                   |
|----------------------------|-----------------------------------------------------------|
| Recommended model          | What the orchestrator suggests, from capability reasoning |
| User-selected model        | What the user actually picked when launching the platform |
| Programmatically confirmed | What the host runtime reports back as the resolved model  |

Be honest about uncertainty. **Never pretend a model is available, selected, or confirmed when the host does not expose that information.** In the assignment overview, write `User to select` (Mode A) or `Not exposed by platform` (Mode B) rather than guessing.

---

## Cost and Trust Gate

Before dispatching any assignment, answer these three questions explicitly:

1. **Is this platform authorized for this run?** If not, it receives nothing.
2. **Does this assignment require a paid API call?** If yes, has the user approved it *for this run*?
3. **Does the assignment's risk exceed the platform's trust profile?** If yes, reroute or downgrade the assignment's scope.

If any answer is unclear, stop and ask. A wrong routing decision that spends money or damages a repo is more expensive than a question.
