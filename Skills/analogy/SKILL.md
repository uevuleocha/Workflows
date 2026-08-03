---
name: analogy
description: Re-explain the user-referenced topic using one or more concise analogies. Use when the user invokes /analogy, $analogy, "use analogy", "use the analogy skill", "explain with an analogy", "explain with analogies", "re-explain that with an analogy", or clear equivalents asking for analogy-based explanation.
---

# Analogy

Re-explain the idea, code behavior, plan, error, workflow, or decision the user is referring to by using concise analogies that make the underlying concept easier to picture.


## Required Composition With Say More

`say-more` always applies this skill together with `for-dummies`, in both its
concise and expanded modes. When called by `say-more`, contribute a brief,
accurate comparison to one cohesive response. Do not restart this skill's
invocation workflow, ask a duplicate clarification question, or emit a separate
full answer. `say-more` owns the overall depth and response shape.

## Invocation

Treat these as direct invocation and begin the skill:

- `/analogy`
- `$analogy`
- `use analogy`
- `use the analogy skill`
- `explain with an analogy`
- `explain with analogies`
- `re-explain that with an analogy`
- clear equivalents where the user asks for an analogy-based re-explanation

## Workflow

1. Identify what the user is referring to from the current conversation or provided context.
2. If the referent is unclear, ask one short clarification question before explaining.
3. Restate the core idea in one direct sentence.
4. Give one to three short analogies that map cleanly to the core idea.
5. Name the limits of the analogy only when the topic is technical, high-stakes, or easy to overextend.

## Style Rules

- Keep analogies brief and useful.
- Prefer familiar, everyday comparisons over elaborate stories.
- Use multiple analogies only when they add clarity from different angles.
- Do not use an analogy as a substitute for factual accuracy.
- Do not force humor, metaphors, or extended narratives.
- If the user asks for a child-friendly, expert-level, trading-focused, coding-focused, or domain-specific analogy, adapt the analogy to that level.

## Output Shape

Default response:

```text
In plain terms: [one-sentence restatement]

Analogy: [short analogy]

Where it maps: [brief mapping, if useful]
```

For multiple analogies, use a short bullet list.
