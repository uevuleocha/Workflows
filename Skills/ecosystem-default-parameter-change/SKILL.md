---
name: ecosystem-default-parameter-change
description: Safely change DefaultValue on named cAlgo Parameter declarations in live Uzzy Ecosystem cAlgo tools and force loaded cTrader instances to adopt the new values through the required disappear/reappear build cycle. Use when the user explicitly invokes or clearly names ecosystem-default-parameter-change, or when an active ecosystem-calgo-greenlight task uses it for exact existing parameter changes already approved by the user; supports indicators and cBots, arbitrary user-requested target values, two-step and three-step modes, agent-run live cAlgo builds by default or user-run builds when requested, full workspace-diff verification, final cAlgo-to-workspace synchronization, and explicit cBot persistence warnings.
---

# Ecosystem Default Parameter Change

Change one or more named cAlgo `[Parameter]` defaults and make loaded cTrader instances actually display the new values. Keep the work surgical, build-backed, and honest about the difference between an indicator value that persists and a cBot value that is merely visible in the current session.

## Explicit Invocation Only

For a standalone request, begin only when the user explicitly invokes or clearly names this skill:

- `/ecosystem-default-parameter-change`
- `$ecosystem-default-parameter-change`
- `use ecosystem-default-parameter-change`
- `run the ecosystem default parameter change skill`
- clear equivalents that name this skill

Do not invoke it merely because a request mentions cAlgo parameters, `DefaultValue`, cTrader, an indicator, or a cBot.

Explicit invocation is scoped direct-edit authorization for only the named parameter declarations and the same-line split described below. It is not authorization for unrelated source changes, cleanup, refactoring, or workspace mirror edits outside the verified final synchronization.

## Use From Ecosystem cAlgo Greenlight

When an active `ecosystem-calgo-greenlight` task needs to change existing parameter defaults, it uses this skill for the exact tools, parameters, and new values already approved by the user. The user does not need to invoke this skill a second time.

This additional entry path applies only inside that active greenlight task. It does not make ordinary parameter requests implicit or expand which parameters may be changed.

## Required Inputs

The user needs to provide only:

1. the tool or tools;
2. the parameters, identified by label, property name, source line, or a bounded group; and
3. the desired new default value for each parameter or group.

Read the current defaults from source. Infer an obvious file, tool type, label-to-property match, and value syntax when the source makes them clear. Ask only when competing matches would materially change the result. Never add parameters outside the user's named scope.

Use two-step mode by default. Use three-step mode only when the user asks to make the new value live in cTrader and then restore the original source default.

The agent runs the builds by default. If the user explicitly says they will run the builds, stop at each build gate and wait for their result.

## Pre-Edit Resolution

For every tool:

1. Read the applicable Ecosystem project contract and local settings.
2. Resolve the live cAlgo source, its live `.csproj`, generated `.algo` destination, and corresponding workspace mirror under `Tools\Sources\` by exact path.
3. Determine Robot versus Indicator from project/source evidence. Do not guess.
4. Confirm no other agent, editor, or user is changing the same file.
5. Capture an exact recoverable snapshot and hash of the pre-edit live source, then record a full live-versus-workspace diff.
6. Explain and preserve any legitimate pre-existing divergence before editing.
7. Locate every requested declaration and property. Reject missing, duplicate, or ambiguous matches.
8. Record each declaration's final line number, label, property name, original complete line, old `DefaultValue`, and requested value.

The workspace `Tools\Sources\` copy is the protected comparison and recovery mirror during the cycle. Do not change or synchronize it while a declaration is in an intermediate commented-out state. It receives only the verified final live cAlgo source, through `push-tool` or a verified direct copy.

## Declaration Safety

The normal shape is:

```csharp
[Parameter("X", Group = "G", DefaultValue = "")]
public string X { get; set; }
```

Comment only the `[Parameter(...)]` declaration line. Never comment a property, variable, or `{ get; set; }` line. Removing the property breaks every source reference and makes the build fail.

### Same-Line Hazard

If the declaration and property share one physical line, first split them into two lines without changing behavior:

```csharp
[Parameter("X", Group = "G", DefaultValue = "")]
public string X { get; set; }
```

Verify the split before continuing. Report the file and line where this behavior-preserving reformat was required. Never comment any line that still contains `get; set;`.

## Safe Editing Method

Edit only the resolved declaration-line indexes.

- Use line-array and string-index operations such as `IndexOf` and `Substring` to replace the `DefaultValue` segment on one known line.
- Preserve the file's UTF-8 encoding, BOM status, and newline style.
- Never feed a chained regex transformation into whole-file `.Replace()`. That pattern has caused self-nesting corruption across multiple files.
- In PowerShell, use flat, index-based loops. Never pipe filtered rows through `Where-Object` into `foreach`; a single match may unroll into scalars and silently substitute a character for a line number.
- Before every write, assert that only the expected line indexes will change.
- After every write, print every edited line with its current line number and verify it before building.

Windows path defaults must use a C# verbatim string:

```csharp
DefaultValue = @"C:\Users\..."
```

A plain `"C:\..."` may raise `CS1009` because of invalid escape sequences. The `@` is compiler syntax and does not become part of the value stored by cTrader.

## Why The Reset Cycle Is Mandatory

cTrader keeps a stored per-instance value for an existing parameter. Changing only `DefaultValue` normally does not replace that stored value.

One build without the declaration makes the parameter disappear and causes the loaded instance to discard its stored value. Restoring the declaration in the next build makes the parameter reappear with the requested default.

The disappear/reappear cycle is required. Do not shorten it to one build and do not report a displayed value as updated unless the complete cycle succeeded.

## Two-Step Mode

For every selected parameter:

1. Change `DefaultValue` to the requested value.
2. Comment out only its `[Parameter(...)]` declaration line.
3. Print and verify every edited line.
4. Build the affected tool. Expected UI result: the parameter disappears.
5. Uncomment the declaration line, preserving the requested `DefaultValue`.
6. Print and verify every edited line again.
7. Build the tool again. Expected UI result: the parameter returns with the requested value.

This mode leaves the requested default in source.

## Three-Step Mode

Run the complete two-step mode first, then:

1. Restore each declaration's original `DefaultValue` in source without removing the declaration.
2. Print and verify every edited line.
3. Build the tool a third time.

The requested value remains live in the loaded cTrader instance while the source returns to its original shareable default. For cBots, this does not remove the restart-persistence limitation below.

## Who Confirms The UI Transition

The UI transition is always confirmed by the user, never by the agent.

- The agent must not wait for that confirmation or treat it as a gate. It proceeds through the full cycle without pausing.
- The agent's evidence for each transition is the build exit code and compiler error count together with the full workspace diff showing only the expected declaration-line change. Those two forms of evidence are sufficient for the agent to continue and report.
- The agent must never claim to have observed a UI state. Any expected UI behavior it mentions must be labeled `expected`, not `observed`.
- The user may confirm the transition visually at any point and report a mismatch, which is then handled as a defect.

This cycle is tried and tested. It works reliably when its mechanics are followed correctly, so blocking on UI confirmation adds delay without adding safety.

## Who Runs The Builds

The agent runs the real project build for every affected tool by default:

```text
dotnet build "<...\Tool\Tool\Tool.csproj>" -c Release
```

Each project is expected to use `Microsoft.NET.Sdk`, target `net6.0`, and carry the cTrader Automate package reference. The build compiles and deploys the `.algo` file that cTrader loads, propagating the update to running instances.

Resolve and build the live cAlgo `.csproj`. Never run this command against the workspace `Tools\Sources` copy; building the review mirror does not update the live cTrader tool.

Do not try to click the cTrader IDE Build button. Computer-use access grants cTrader at the `read` tier; do not work around that restriction.

For every build, capture and report:

- tool and cycle step;
- command;
- exit code;
- compiler error count;
- whether the expected `.algo` output was produced or updated.

If any build fails, stop that tool's cycle, preserve the inspectable source state, and report the exact recovery point. Do not continue to later builds on assumption.

If the user explicitly says they will run the builds, make only the current source transition, tell them exactly which project to build and what UI result to confirm, then wait for their result before applying the next transition. Never claim a user-run build passed without evidence.

## Full Workspace-Diff Verification

After every source transition and after the final build:

1. Run a full-file diff between the edited live source and the still-unchanged `Tools\Sources\` workspace mirror.
2. Compare the full result with the pre-edit diff and the exact expected declaration-line changes.
3. Treat every unexpected differing line as a failure, regardless of its shape.
4. If corruption occurred, stop and restore the captured pre-edit live snapshot. Do not overwrite legitimate pre-existing divergence from the workspace mirror and never "repair" unexpected differences with broad replacement.

Pattern matching is not a substitute for the full workspace diff. It has missed real corruption that only the compiler or full diff exposed.

For three-step mode, the final expected source delta is normally only any reported same-line split; the requested default itself must be restored to the original value.

## Final cAlgo-To-Workspace Synchronization

After every build required by the selected mode succeeds and the final full workspace diff contains only expected differences:

1. Confirm the live cAlgo source contains no intermediate commented-out declarations.
2. Synchronize that verified final live source to its resolved `Tools\Sources\` workspace mirror using `push-tool` or a verified direct copy.
3. Compare the final hashes and full content of the live and workspace files.
4. Require exact parity before reporting synchronization complete.

Never synchronize the disappearance-build state or any failed, partial, or unverified source state. When legitimate divergence existed before the task, reconcile it explicitly so the final synchronization preserves all intended content.

## Indicators And cBots

### Indicators

For indicators, a successful reset cycle persists the new value. No additional user action is required.

### cBots

For cBots, the requested value applies in the running session but does not necessarily survive a cTrader restart. cTrader may treat a value equal to its `DefaultValue` as unset, omit it from stored/synced parameters, and restore the previous stored value on the next login.

Whenever any target is a cBot:

- warn the user before execution;
- never describe the value as persisted merely because it is displayed;
- end the report by naming the user action still required to commit it.

The user can commit a cBot value by one of these methods:

1. Manually paste or re-enter the value in the parameter field.
2. Save Parameters, restart and observe the reversion, then Load Parameters. The old-to-new load is what commits the value; loading identical displayed values is a no-op.
3. Observed shortcut for algo-tab bots only: while the new value is displayed, edit any other parameter by typing and deleting a digit, then Save. This dirties the whole parameter set and has survived restart.

Method 3 is an observation, not a rule, and did not work for chart-attached bots. Do not recommend it as universally reliable.

## Reporting

Report:

- mode used: two-step or three-step;
- who ran the builds;
- every parameter changed: tool, final line, label, property, old value, new value;
- every same-line split performed;
- every build per tool: cycle step, exit code, error count, output status;
- full workspace-diff result per tool, including unexpected-line count;
- final synchronization method and live/workspace parity result;
- final source state;
- UI transition status labeled `expected`, or `user-confirmed` only when the user reports it; never agent-observed;
- indicator persistence status;
- for every cBot, `expected in-session` versus `persisted`, the remaining user action, and any method the user selected.

Do not claim completion while a build result, workspace diff, final synchronization, target parameter, or required cBot persistence warning is missing.

## Safety Boundaries

- Touch only the parameters the user explicitly selected.
- Do not opportunistically normalize nearby declarations.
- Never comment a property, variable, or `get; set;` line.
- Never build the workspace `Tools\Sources` copy.
- Never synchronize an intermediate, failed, partial, or unverified live state.
- Never bypass a permission tier, build restriction, or missing path.
- Stop and report rather than working around a blocked permission or tier.
- Do not edit product source merely because this skill was discussed; direct edits begin only after standalone explicit invocation or the authorized nested entry from an active `ecosystem-calgo-greenlight` task.

## Completion Criteria

The run is complete only when:

1. every selected declaration completed every build required by its mode;
2. every build result is known and successful;
3. every edited line was printed and verified before its build;
4. every final full workspace diff contains only expected differences;
5. every verified final live source is synchronized to its workspace mirror with exact parity;
6. every parameter and source state is reported;
7. every indicator is labeled persisted; and
8. every cBot is labeled expected in-session or persisted accurately from build and workspace-diff evidence, with the remaining user action stated when required.
