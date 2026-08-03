# Push Tool — Adoption Guide

Copies a cTrader tool folder (Indicator or Robot) from the cAlgo Sources
directory into the matching Uzzy Ecosystem Tools/Sources directory, so the agent's
workspace mirrors the latest version compiled in cTrader. One direction only:
cAlgo → workspace, never the reverse, and it never touches the cAlgo
directory itself. Successful runs append to and git-seal the permanent log at
`"Archive/Live/Documentation/Personal/Logs/1.) push-log.md"`. Invoked with
`/push-tool` or "push the tool".

## Related skills

- None required. Standalone, project-specific utility.
