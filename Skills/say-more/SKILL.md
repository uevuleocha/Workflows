---
name: say-more
description: Explain the user-referenced topic more clearly, defaulting to a short and concise expansion while automatically combining the for-dummies and analogy approaches. Use when the user invokes /say-more, $say-more, "say more", "explain that more", "go into more detail", or clear equivalents asking for a better or fuller explanation. Use a moderately longer explanation when the user explicitly asks for one or invokes say-more again for the same context after a prior say-more response.
---

# Say More

Explain more about whatever the user is pointing at, with enough added clarity to improve understanding but without turning the answer into a story, episode, wall of text, or exhaustive lecture.

Every run combines the methods of `for-dummies` and `analogy`: explain the actual topic in simple, jargon-free language and include a brief comparison that makes it easier to picture. Apply those companion procedures as one cohesive answer; do not require the user to invoke them separately.

## Invocation

Treat these as direct invocation and begin the skill:

- `/say-more`
- `$say-more`
- `say more`
- `say more about that`
- `explain that more`
- `explain it a bit more`
- `go into more detail`
- clear equivalents asking for a better, fuller explanation of the current referent

## Resolve The Referent

Identify the idea, code behavior, plan, error, workflow, decision, or prior answer the user is pointing at. If there is no reliable referent, ask one short clarification question. Do not make the user restate context that is already clear from the conversation.

## Choose The Depth

Use exactly one of these depths:

- **Concise** *(default)* - add the smallest useful amount of explanation. Clarify the core idea in plain language, add the missing detail, and use one short analogy.
- **Expanded** - give a moderately longer explanation with a few small steps, distinctions, or examples, plus one or two concise analogies when useful.

Select **Expanded** when either condition is true:

1. The user explicitly asks for a long, longer, detailed, thorough, or deeper explanation.
2. The user invokes `say-more` again for the same referent after already receiving a `say-more` response about it.

Explicit user length instructions override the default. A repeated invocation may escalate from Concise to Expanded once, but further repetition does not create progressively larger modes. If the referent has changed, treat it as a new context and default to Concise.

## Required Companion Composition

Every response, at either depth, must apply both companion approaches:

1. **For Dummies:** state the real idea simply, literally, and without unexplained jargon. Define any unavoidable term inline.
2. **Analogy:** add at least one brief, accurate analogy and make its mapping clear when it is not obvious.

Blend both into one answer. When applying the companion skills on behalf of `say-more`, use their methods without restarting their invocation workflows, asking duplicate clarification questions, or producing three separate full answers.

## Workflow

1. Resolve the referent from the conversation.
2. Choose Concise or Expanded using the depth rules.
3. Identify what was missing, compressed, or hard to understand in the prior explanation.
4. Explain the topic itself in plain, jargon-free terms.
5. Add only the details needed for the selected depth.
6. Include a short analogy that reinforces the explanation.
7. End once the user has a clearer mental model; do not keep expanding merely because more related information exists.

## Style Rules

- Default to short, direct, and useful.
- Prefer small paragraphs or a short list over one long paragraph.
- Keep Expanded bounded and focused; it means more explanation, not everything known about the subject.
- Do not use stories, episodes, extended narratives, scene-setting, or filler.
- Do not repeat the prior answer verbatim. Add clarity, missing reasoning, or a better framing.
- Keep analogies brief and subordinate to factual accuracy.
- Do not become condescending when simplifying.
- Preserve necessary nuance for technical, legal, medical, financial, or safety-sensitive topics.

## Output Shape

Concise default:

```text
In plain terms: [clearer explanation of the real idea]

[One or two short pieces of added detail.]

Analogy: [brief comparison]
```

Expanded mode:

```text
In plain terms: [clear core explanation]

[A few small steps, distinctions, or examples that deepen understanding.]

Analogy: [brief comparison, with mapping when useful]

Takeaway: [one-sentence mental model]
```

The labels are optional when a natural response reads better, but the plain explanation and analogy are mandatory.
