---
name: for-dummies
description: Re-explain the user-referenced topic in dead-simple, jargon-free terms, dumbed down as if for a beginner or young child. Use when the user invokes /for-dummies, $for-dummies, "for dummies", "dumb it down", "explain simply", "ELI5", "explain like I'm 5", "explain it to me like a child", or clear equivalents asking for a simplified explanation. Sibling of the analogy skill — analogy explains sideways by comparing to another thing, while for-dummies explains downward by simplifying the thing itself.
---

# For Dummies

Re-explain the idea, code behavior, plan, error, workflow, or decision the user is
referring to by stripping it down to the simplest, most literal, jargon-free version —
the "[topic] for dummies" treatment. Explain the thing itself in plain words and small
steps, not by comparing it to something else.

This is the downward sibling of `analogy`. Reach for `analogy` when a comparison to a
familiar thing helps most; reach for `for-dummies` when the user just needs the real
thing said simply and slowly.

## Required Composition With Say More

`say-more` always applies this skill together with `analogy`, in both its
concise and expanded modes. When called by `say-more`, contribute the plain,
literal, jargon-free explanation to one cohesive response. Do not restart this
skill's invocation workflow, ask a duplicate clarification question, or emit a
separate full answer. `say-more` owns the overall depth and response shape.


## Invocation

Treat these as direct invocation and begin the skill:

- `/for-dummies`
- `$for-dummies`
- `for dummies`
- `dumb it down` / `dumb this down`
- `explain simply` / `explain it simply`
- `ELI5` / `explain like I'm 5` / `explain like I'm five`
- `explain it to me like a child`
- clear equivalents where the user asks for a simplified, dumbed-down explanation

## Levels

Match the depth to what the user asks for. If they don't specify, use **Plain**.

- **ELI5** — youngest, baby-simple. Tiny words, short sentences, zero jargon.
  Triggered by "ELI5", "like I'm 5", "like a little kid", "as dumb as possible".
- **Plain** *(default)* — simple and jargon-free, but not babyish. Assumes a smart
  person who is simply new to the topic.
- **Bit-more** — plain, but keeps one or two real terms, each defined inline, so the
  user starts picking up the actual vocabulary. Triggered by "new but not clueless",
  "keep some real terms", "I want to learn the words".

The agent may offer more than one level in a single reply when it helps
(e.g. a Plain explanation followed by a one-line ELI5 recap).

## Workflow

1. Identify what the user is referring to from the current conversation or context.
2. If the referent is unclear, ask one short clarification question before explaining.
3. Pick the level: honor any hint the user gave; otherwise default to Plain.
4. Restate the core idea in one plain, jargon-free sentence.
5. Explain it in a few small, literal steps — one idea per step. Define any
   unavoidable term inline in plain words.
6. Optionally add ONE short analogy at the end only if it genuinely helps. The
   simplification, not the analogy, is the main event. (For an analogy-first
   explanation, use `analogy` instead.)
7. Close with a one-line takeaway the user can remember.

## Style Rules

- Simplest accurate version wins. Never sacrifice correctness to sound simple.
- Prefer short words and short sentences. Cut jargon; if a term is unavoidable,
  define it the moment you use it.
- One idea at a time. Small steps beat one dense paragraph.
- Do not be condescending. "Simple" means clear, not baby-talk — unless the user
  explicitly asks for the ELI5 / kid-level treatment.
- Analogies are optional seasoning here, not the dish. Use at most one, and only
  if it earns its place.
- Adapt to a named level (ELI5 / Plain / Bit-more) whenever the user hints at one.

## Output Shape

Default response:

```text
In plain terms: [one-sentence, jargon-free restatement]

Simply put:
- [small literal step]
- [small literal step]
- [small literal step]

One-line takeaway: [memorable summary]
```

Add an optional `Analogy:` line before the takeaway only when a comparison genuinely
helps. For a requested ELI5, keep every line shorter and simpler than Plain.
