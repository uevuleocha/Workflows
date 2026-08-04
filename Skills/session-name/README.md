# Session Name

Suggests exactly eight grounded, naturally varied chat-session labels: four focused foundation options led by Outcome, Artifact/Tool, Method, and Headline Result, followed by four adaptive syntheses that may carry richer integrated detail. Outside Hermes, 240 characters excluding any prefix is the default maximum; a user can simply ask for longer names in the initial request or afterward, without supplying a new maximum, and the agent may reasonably exceed 240. Hermes retains its 100-character hard cap including any prefix. Selection and the opt-in `N.)` prefix are permanently optional and non-blocking, and the skill never renames a chat or creates an artifact.

## Related skills

- `finalize-session` — the convenience caller for combined name-plus-summary closure; it runs `session-name` and `session-summary` in one pass and supplies the chat-session identifier as this skill's verbatim `N.)` prefix. It is a thin orchestrator and owns none of the naming logic. Standalone `session-name` invocation is unchanged and never routes through the wrapper.
- `session-summary` — an independent durable recap that may follow session naming; neither workflow depends on a reported selection.
- `plan-this`, `task-this`, `prompt-this`, and `report-this` — own durable artifact naming; `session-name` labels only the chat session.
