# Assignment Packet Template

One packet per platform/agent. In Mode A these are embedded in the delegation record. In Mode B the same fields become the subagent's instruction — no record file is required for dispatch alone.

A packet must be **self-contained enough that a fresh agent can act on it** without the user reconstructing the orchestrator's reasoning. A receiving agent may read the whole record for context, but executes only its own packet.

Every field is required. Where a field genuinely does not apply, retain the line and write `N/A` plus a short reason — never delete it. The **Cost/trust rationale is never omitted**; when the route needs no defence, write `N/A — routing self-evident`.

---

```markdown
### Packet <N> — <Platform> — <Role>

| Field                | Value                                                      |
|----------------------|------------------------------------------------------------|
| Platform / agent     | <Claude Code / Codex / zCode / Hermes / Antigravity>       |
| Assigned role        | <Workstream lead / Worker / Reviewer / Resolver>           |
| Execution wave       | <Wave 1 / Wave 2 / …>                                      |
| Prerequisites        | <What must complete first, or `None — may start at once`>  |
| Recommended model    | <Model, with one-line reason, or `No recommendation`>      |
| Parent artifact      | <Absolute path to the parent plan and/or task>             |
| Mini artifact        | `<Plan/Task family child prefix + path>`                   |
| Reserved prefix      | `<Exact lowercase Plan/Task prefix, e.g. 1a.)>`            |
| Return report        | `<Summary-family prefix + path, e.g. 9a.) …Report.md>`     |

**Prefix family notes** (the table cells are kept short on purpose):

- **Mini artifact** belongs to the **Plan/Task family**. Give the reserved
  child prefix (e.g. `1a.)`) plus its path, or write
  `(reserved, created after recon)` with instructions. The prefix is reserved by
  the orchestrator before dispatch.
- **Reserved prefix** is the exact lowercase **Plan/Task family** child prefix
  (e.g. `1a.)`), reserved by the orchestrator. Never invent or renumber it.
- **Return report** uses its **separately reserved Summary-family** child prefix
  (e.g. `9a.)`), not the Plan/Task prefix. Its path ends in `Report.md`. The two
  prefixes come from different families and need not match.

**Required reference paths**

- `<path>` — <why this agent needs it>
- `<path>` — <why this agent needs it>

**Goal**

<One paragraph. The outcome this agent is responsible for. Not the method.>

**Exact scope**

- <Bounded, concrete item>
- <Bounded, concrete item>

**Explicit exclusions**

- <Thing this agent must NOT touch, and why>
- <Thing another agent owns>

**Owned surfaces (write access)**

- `<file or directory>` — this agent is the ONLY writer

**Read-only surfaces**

- `<file or directory>` — read for context; do not edit

**Dependencies and expected inputs**

- <What arrives from which agent/wave, in what form>

**Deliverables**

- <Artifact, file, report, or decision this agent returns>

**Constraints and safety rules**

- Obey the host workspace's canonical contract (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`).
- One editor per file. Do not write outside your owned surfaces.
- <Assignment-specific constraint>
- Paid API use: <`Not authorized` / `Authorized for this run: <model>`>

**Definition of Done**

- <Positive, verifiable completion criterion>
- <Positive, verifiable completion criterion>

**Verification requirements**

- <Command, test, validator, or manual check this agent must run and report>

**Handoff format and destination**

- Format: <e.g. session summary, mini plan update, diff, structured report>
- Destination: <where it goes, and who consumes it next>

**Checkpoint Policy**

- Where execution stops: <default: complete the packet continuously; intermediate
  milestones are not user checkpoints unless labelled `USER CHECKPOINT`>.
- Sync allowed: <default for skill work: No — centralized sync; the orchestrator
  runs one final global-sync + parity pass. State Yes only with explicit
  authorization>.
- Must return first: <the return report at its reserved prefix + any named deliverables>.

**Stop-and-return conditions**

Stop immediately and return to the user if:

- The assignment requires writing outside your owned surfaces.
- A prerequisite deliverable is missing, malformed, or contradicts this packet.
- The work requires a paid API call not authorized above.
- You find a conflict between this packet and the parent artifact.
- <Assignment-specific tripwire>

**Return report (mandatory at packet/wave completion)**

On completion, write a return report at the reserved **Summary family** child
prefix and path above (filename ending in `Report.md`), under
`<workspace>\Archive\Historical\Summaries\<Subject>\`. It uses session-summary
structure plus an append-only `## Feedback` ledger. The Summary prefix (e.g.
`9a.)`) is independent of the Plan/Task mini-artifact prefix (e.g. `1a.`) — use
the exact reserved Summary prefix, never invent or renumber it.

**Cost / trust rationale**

<Why this platform, at this trust level, for this assignment. One or two sentences.
Never omit this field. If the route needs no defence, write exactly:
`N/A — routing self-evident`>
```

---

## Filling notes

- **Recommended model** — give a reason or write `No recommendation`. Never name a model you are not confident currently exists on that platform. The receiving platform gets one chance to counter-recommend.
- **Cost / trust rationale** — mandatory. `N/A — routing self-evident` is the only permitted shorthand, and it is still a filled field, not an omission.
- **Mini artifact / Reserved prefix / Return report** — the orchestrator reserves two separate lowercase child prefixes: a **Plan/Task family** prefix (e.g. `1a.)`) for the mini artifact and a **Summary family** prefix (e.g. `9a.)`) for the return report. The prefixes come from different namespaces and need not match. The agent either receives a path that already exists or is instructed to create the artifact at its reserved prefix after investigation. Never leave a prefix blank or write "create later" without a reservation.
- **Checkpoint Policy** — mandatory. State where execution stops, whether sync is allowed, and what must be returned first. The default for skill work is continuous completion with centralized sync (the worker does not sync).
- **Return report** — mandatory at packet/wave completion. It lives at the reserved **Summary family** prefix under the execution workspace's `Archive\Historical\Summaries\<Subject>\`, ends in `Report.md`, uses session-summary structure plus an append-only `## Feedback` ledger.
- **Owned surfaces** — this is the one-editor-per-file guarantee. If two packets would list the same path, the routing is wrong. Split the file's work or serialize the waves.
- **Stop-and-return conditions** — always include the four generic tripwires above. They are what prevent a well-meaning agent from silently exceeding its packet.
