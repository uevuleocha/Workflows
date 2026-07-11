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
| Mini artifact        | <Path, or `Create after investigation` + instructions>     |

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

**Stop-and-return conditions**

Stop immediately and return to the user if:

- The assignment requires writing outside your owned surfaces.
- A prerequisite deliverable is missing, malformed, or contradicts this packet.
- The work requires a paid API call not authorized above.
- You find a conflict between this packet and the parent artifact.
- <Assignment-specific tripwire>

**Cost / trust rationale**

<Why this platform, at this trust level, for this assignment. One or two sentences.
Never omit this field. If the route needs no defence, write exactly:
`N/A — routing self-evident`>
```

---

## Filling notes

- **Recommended model** — give a reason or write `No recommendation`. Never name a model you are not confident currently exists on that platform. The receiving platform gets one chance to counter-recommend.
- **Cost / trust rationale** — mandatory. `N/A — routing self-evident` is the only permitted shorthand, and it is still a filled field, not an omission.
- **Mini artifact** — either hand the agent a path that already exists, or instruct it to investigate first and then create its own mini plan/task. Both are first-class; say which.
- **Owned surfaces** — this is the one-editor-per-file guarantee. If two packets would list the same path, the routing is wrong. Split the file's work or serialize the waves.
- **Stop-and-return conditions** — always include the four generic tripwires above. They are what prevent a well-meaning agent from silently exceeding its packet.
