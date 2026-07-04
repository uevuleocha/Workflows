# Model Chat Setup Guide

This skill runs a script-backed multi-agent debate through the Anthropic API. It requires an Anthropic API key and Python dependencies.

On first run, the agent should run the no-cost setup check, identify missing prerequisites, and create or update a setup task in the host workspace's configured task directory. The agent must never print or save API key values.

If the workspace has a task convention, use it. A common default is `<project root>\Archive\Tasks\` on Windows or `<project root>/Archive/Tasks/` on macOS/Linux. If no task convention exists, the agent should ask the user where setup tasks should live before creating one.

The setup task should help the user install dependencies, provide an API key through a safe environment mechanism, run the harmless preflight, and confirm the skill is ready before any paid API call.
