---
name: ecosystem-calgo-greenlight
description: Authorize and run direct, reviewable C# implementation work for one or more named Uzzy Ecosystem cAlgo bots, indicators, tools, components, or .cs files, overriding the workspace's normal manual-copy rule only for the invoked task. Use only when the user explicitly invokes ecosystem-calgo-greenlight, asks to run the Ecosystem cAlgo greenlight skill, or clearly names this skill while approving direct cAlgo edits; enters persistent Eco-Greenlight mode and requires live-cAlgo-first editing, the Uzzy code-shape and documentation staples, phased or full-run execution, user-build or agent-build ownership, reusable existing-parameter default-change handling, session-scoped debug-parameter control, fixed read-only evidence locations, automatic post-build restart/reload verification, and a compulsory line-addressable change and verification ledger.
---

# Ecosystem cAlgo Greenlight

Execute approved C# work in the Uzzy Ecosystem while keeping every source change inspectable, attributable, and bounded.

This skill exists because the Ecosystem project contract normally prohibits agents from directly editing product `.cs` files. The user's explicit invocation of this skill is standing authorization for the invoked task to edit the necessary named or plan-scoped workspace and live cAlgo `.cs` files directly. It is a narrow exception, not a permanent weakening of the workspace contract.

## Explicit Invocation Only

Begin this workflow only when the user explicitly invokes or clearly names this skill, for example:

- `/ecosystem-calgo-greenlight`
- `$ecosystem-calgo-greenlight`
- `use ecosystem-calgo-greenlight`
- `run the Ecosystem cAlgo greenlight skill`
- `run the skill in phased mode`
- `run the skill as a full run`

Do not invoke it implicitly merely because the user discusses cAlgo, C#, a bot, an indicator, build errors, logs, or databases. Ordinary requests continue to follow the Ecosystem workspace's manual-copy rule.

An explicit invocation counts as the direct-edit greenlight for the invoked task. Do not require a second `green-light` invocation. Runtime permission prompts and destructive-operation approvals still apply.

If LTNEY is active for the same task, do not edit product code until the user ends LTNEY or explicitly applies a scoped execution override to that task.

## Eco-Greenlight Mode Contract

A valid invocation for a resolved task enters `Eco-Greenlight` mode. The mode is scoped to that greenlight run; it is distinct from the run's `phased` or `full-run` execution mode.

While `Eco-Greenlight` mode is active:

- every assistant response ends with the mode footer described below;
- the mode and its direct-edit authorization persist across phase handoffs, inspection and build gates, user feedback, runtime-sample waits, repair loops, context compression, and resumptions;
- a phased handoff, a blocked check, or waiting for the user to build or run an instance does not end the mode;
- a later invocation of another mode layers with this mode and does not silently replace it; and
- the mode ends only after the scoped run satisfies its completion contract and the completion report is delivered, or the user explicitly exits, cancels, stops, clears, or terminates this mode or all modes.

Footer rules:

- Eco-Greenlight only: `Mode = Eco-Greenlight`
- Multiple modes: `Modes = Eco-Greenlight + Mode B + ... + Mode Z`, including every active mode exactly once

The final completion report still carries the Eco-Greenlight footer; the mode is inactive on the next response. If the user ends the mode before completion, stop new implementation and perform the safest possible scoped closeout, including debug-parameter reversion and source synchronization when authority still permits it. Report every unfinished check or cleanup obligation. If the user explicitly revokes edit authority, do not mutate files merely to close the mode; report the exact pending cleanup instead.

## Authorization Scope

The greenlight may cover one or multiple:

- bots
- indicators
- tools or supporting components
- workspace `.cs` files
- live cAlgo `.cs` files

Resolve the authorized set from the user's request and any active plan or prompt. Multiple files may be edited together when they are genuinely required by the same approved implementation.

The authorization covers only:

- the named task or active-plan scope
- the `.cs` targets required for that scope
- corresponding Ecosystem workspace and live cAlgo copies
- relevant plan evidence when an invoked plan workflow owns that update
- user-supplied or clearly relevant build logs and databases for verification

It does not authorize:

- unrelated `.cs` files or cAlgo directories
- opportunistic refactors or cleanup
- deleting production files
- schema, parameter, payload, or public-interface changes outside scope
- plan, prompt, task, or report finalization without its explicit skill
- force operations or destructive source control actions

## Existing Parameter Default Changes

Whenever the approved work needs to change the `DefaultValue` of one or more existing cAlgo `[Parameter]` declarations, use `ecosystem-default-parameter-change` as the complete procedure. This applies to Boolean, numeric, string, directory-path, and other parameter types in any requested direction.

The user needs to provide only:

- the tool and parameter declarations, labels, property names, lines, or bounded parameter group to change; and
- the desired new default value for each parameter or group.

Read the current defaults from source. Do not ask the user to repeat values the source already proves. If the tools, parameters, and requested new values are already clear from the greenlight task, proceed without asking again.

Use the parameter-change skill with the exact resolved tools, declarations, and user-requested target values. Honor an explicitly requested two-step or three-step mode; otherwise let that skill resolve whether a final source-default restore is needed.

Parameter-cycle builds are a specialized exception to the surrounding greenlight run's normal build ownership. The agent runs the child skill's live cAlgo builds by default even when ordinary greenlight phase builds are user-owned. If the user explicitly says they will run the parameter-cycle builds, pass that choice to the child and stop at each of its build gates. This exception does not change ownership of any other greenlight build.

The user does not need to invoke `ecosystem-default-parameter-change` separately when `ecosystem-calgo-greenlight` is already running the approved task. This reuse does not expand the task's approved parameter scope.

Do not repeat declaration safety, same-line handling, disappear/reappear build mechanics, workspace-diff verification, or cBot persistence rules here. The parameter-change skill is the single source for that workflow.

A newly created parameter does not need a disappear/reappear reset before its first build because no stored instance value exists yet. Any later change to that existing parameter's default uses `ecosystem-default-parameter-change`.

## Session-Scoped Debug Parameter Control

Greenlight owns the decision to activate debug parameters, the session record, and the obligation to return them to a safe final state. The parameter-change skill owns every transition of an existing declaration.

### Selection And Activation

Debug activation is selective, never blanket:

- enable only the `DEBUGGING` parameters genuinely useful for the current work;
- enabling none is valid when none are useful;
- enabling all is valid only when all are genuinely useful; and
- report every selected parameter and why it is needed in one line.

For every selected existing debug parameter, invoke `ecosystem-default-parameter-change` with the exact tool and declaration, target value `true`, two-step mode, and the parameter-cycle build ownership defined above. Track every parameter successfully enabled.

Any new debug parameter added during implementation must be created with `DefaultValue = true` so it is active from its first live cAlgo build. It does not need a disappear/reappear cycle before that first build, but it is still session-scoped and must be tracked for reversion.

### Mandatory Session-End Revert

Before the greenlight session closes, invoke `ecosystem-default-parameter-change` for every tracked debug parameter with target value `false`, two-step mode, and the parameter-cycle build ownership defined above. State explicitly which parameters were reverted.

The user may explicitly ask for a named debug parameter to remain on. Record each approved exception and do not infer stay-on permission from silence.

Before closing, run a source check across the approved targets for `Group = "DEBUGGING"` declarations combined with `DefaultValue = true`. The result must contain zero hits except for the user's named stay-on exceptions. Do not complete the greenlight run while an unapproved debug parameter remains enabled.

## Evidence Locations

Use these standing evidence roots without asking the user to repeat them.

| What              | Path                                                                           |
|-------------------|--------------------------------------------------------------------------------|
| Databases & state | `C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Tools\Outputs`  |
| Runtime logs      | `C:\Users\Admin\OneDrive\Documents\cAlgo\Data`                                 |

Tool outputs — databases, bridge files, and state files:

`C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Tools\Outputs`

Outputs are organized first by tool and then by artifact type, with per-symbol JSON files, for example `Uzzy TREND\RANGEs\` and `Uzzy TREND\TRENDs\`.

Runtime logs:

`C:\Users\Admin\OneDrive\Documents\cAlgo\Data`

This root contains `cBots\`, `Indicators\`, and `Plugins\`, with per-instance folders keyed by instance ID and asset group, such as `...-SYNTHETICS`.

Resolve the correct tool folder, instance, and asset from the task, plan, build, and runtime context. Ask only when the instance or asset is genuinely ambiguous. Both evidence roots are strictly read-only to the agent: never write, modify, move, or delete anything in them.

When the user has not named a verification asset or instance, resolve one in this order:

1. use the asset and instance required by the active plan, prompt, acceptance example, or current runtime context;
2. otherwise discover suitable running instances of the affected tool and correlate them with fresh matching logs and output files;
3. when exactly one suitable running instance has usable matching evidence, select its asset without asking the user;
4. when several are suitable, infer one only when the current task context makes a representative choice clear and the choice cannot materially alter the conclusion; otherwise ask which asset or instance the user is testing;
5. when none is running or no usable sample exists, keep runtime verification pending and tell the user exactly which tool and asset must be run.

Do not choose an arbitrary asset merely to produce a result. Record the selected tool, instance, asset, evidence timestamps, and why the selection was representative.

## Required Inputs And Inference

Resolve these before editing:

1. **Task scope** - the requested fix, feature, plan, or error set.
2. **Targets** - every affected bot, indicator, tool, component, and `.cs` file.
3. **Execution mode** - `phased` or `full-run`.
4. **Ordinary phase build owner** - `user-build` or `agent-build`; parameter-cycle builds use the specialized ownership rule above.
5. **Verification evidence** - expected build output, logs, databases, runtime instances, or source-only checks.

Infer values from the request, active plan, prompt, and workspace when clear. Do not ask the user to repeat information already present there.

If execution mode is unspecified:

- use `phased` when the work is risky, plan-phased, broad, or the user wants review/build checkpoints;
- use `full-run` when the user clearly asks to finish the approved scope in one pass;
- ask only when either choice would materially change the user's control point.

If build owner is unspecified, default ordinary phase builds to `user-build`. The agent may run ordinary phase builds only when the user selects `agent-build` and the available environment can perform the real build. Parameter-cycle builds follow the specialized ownership exception above.

## Execution Modes

### Phased Mode

Implement one approved phase or reviewable batch at a time.

After each phase:

1. synchronize each approved live cAlgo target back to its Ecosystem workspace mirror;
2. run the narrow source-level checks;
3. report exact changes and review pointers;
4. stop at the agreed inspection/build gate;
5. continue only after the user supplies feedback or approves the next phase.

Closely related phases may be combined when the user approves the combined batch or the active plan already groups them.

### Full-Run Mode

Complete the entire approved scope without requiring approval between phases. Still provide concise progress checkpoints, preserve phase boundaries in the work, and perform the same verification. Synchronize cAlgo to the workspace after each intentional batch when the run uses batches, or once at the end when the full run is one continuous batch. Stop for new authority if a discovered issue materially expands the approved scope.

An active plan may govern either mode. Follow its checklists and locked decisions without silently redesigning them.

## Pre-Edit Safety Check

Before the first edit, and again before each synchronization:

1. Read the Ecosystem `CLAUDE.md`, wrapper instructions, local settings, active plan, and task-specific references.
2. Resolve every workspace/live source pair by exact path. Never guess whether a component is a Robot or Indicator.
3. Confirm each target is inside the approved workspace or cAlgo source scope.
4. Check for evidence that another agent, cTrader editor, or user is changing the same file. One editor per file remains mandatory.
5. Compare the workspace and live copies using hashes and a content diff.
6. Treat unexplained divergence as user-owned until reconciled. Never overwrite it blindly.
7. Establish a reviewable baseline with Git when available, without reverting unrelated or user-owned changes.
8. When runtime behavior is relevant and matching read-only evidence already exists, inspect the selected tool, instance, and asset before editing to establish a pre-change log/database baseline. Record its evidence window and reuse the same selection after the build when practical. If no trustworthy baseline exists, say so and never fabricate a before/after comparison.

When copies differ for a legitimate reason, preserve the newer intended state and merge the approved implementation into it. Report the reconciliation.

## Editing And Synchronization

The live cAlgo `.cs` file is the working copy because it is what builds and runs in cTrader. Edit the approved live cAlgo source directly, then synchronize it to the corresponding Ecosystem workspace review/version-control mirror.

All builds, including the parameter-change child's builds, must target the resolved live cAlgo `.csproj`. Never run `dotnet build` against a workspace `Tools\Sources` mirror; that copy is for review, recovery, and synchronization, not the project cTrader compiles and deploys.

cAlgo-first editing is mandatory in this workflow, not merely a default. Never edit or build the workspace mirror first. If the user requests workspace-only work, use the applicable manual-copy workflow instead of silently inverting this skill's direction.

Synchronization cadence follows execution mode:

- phased mode — cAlgo to workspace after every completed phase;
- batched work — cAlgo to workspace after every completed batch;
- one-batch full run — cAlgo to workspace once at the end.

`push-tool` may perform the cAlgo-to-workspace synchronization when it fits the task. A direct verified copy is equally acceptable. `push-tool` copies only cAlgo to the workspace, matching this required direction.

If the live and workspace files legitimately diverged before the task, preserve the newer intended state and reconcile the pair before applying or propagating the approved changes. Never use the new default direction as permission to erase a legitimate workspace-only edit.

For multiple targets:

- maintain an explicit mapping between every workspace and live file;
- edit only the necessary files;
- validate and report each file separately;
- verify synchronization for every mapped pair;
- do not claim the batch is synchronized because only one pair matches.

Keep changes surgical. Preserve compatible comments and XML summaries. Add or update a concise XML summary when a new or materially changed method needs one.

## Uzzy Code-Shape And Documentation Staples

Every new or materially changed C# block must look native to the Uzzy Ecosystem. Apply this section to the approved edit surface; do not reformat or reorganize unrelated legacy code merely to make an older file match it.

The standing reference corpus is the workspace mirror under:

`C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem\Tools\Sources`

Use the corpus to resolve a target-specific convention when this section does not settle it. Prefer the recurring structure across several maintained tools over a one-file outlier. In particular, do not copy the blanket field XML documentation or highly narrated field regions found in a few tools.

### Code-Shape Pipeline

Before writing:

1. **Observe** - inspect the target's imports, namespace, indentation, region spine, parameter groups, neighboring methods, helper types, and comments.
2. **Map** - decide the exact existing region and neighboring symbol where each addition belongs. Create a region only when the responsibility is genuinely new and substantial.
3. **Place** - add the code in that location using the target's naming and formatting conventions. Do not append unrelated members at the end merely because it is convenient.
4. **Document** - add concise XML documentation to behavioral members and helper types, plus only the inline comments needed to explain non-obvious intent.
5. **Prune** - remove draft narration, redundant comments, stale change tags, unused imports, and documentation that only repeats the code.
6. **Verify** - review the final file spine, region balance, documentation coverage, comment density, diff scope, and build-sensitive syntax.

### File Spine

Preserve the target's established structure when it is coherent. For a new file, or a new major section in a file without a clear structure, use this order as applicable:

1. required `using` directives;
2. `cAlgo.Robots` or `cAlgo.Indicators` namespace;
3. cAlgo attribute and main Robot or Indicator class;
4. outer `#region Parameters` with parameter-group subregions;
5. `#region Fields`;
6. cBot or indicator lifecycle;
7. initialization and core/domain engines;
8. data, persistence, UI, drawing, alerting, and other responsibility regions;
9. event handlers, cleanup, and timeframe or utility logic;
10. helper classes, data models, structs, and enums;
11. shared bridge code last when the tool embeds it.

This is a responsibility order, not a demand that every file contain every region. Use short, descriptive region names already established in neighboring tools, such as `Indicator Lifecycle`, `cBot Lifecycle`, `Core Logic`, `Data Management`, `UI Management`, `Event Handlers`, `Timeframe Logic`, and `Helper Classes & Enums`.

Use nested subregions only when they make a large parent responsibility easier to navigate. Do not create a region around one trivial member or fragment a small method collection into many decorative regions.

### Bottom-Of-File Type And Namespace Boundary

Close the main Robot or Indicator class before the bottom helper-type sections. Unless a type genuinely requires private nested access, place tool-specific enums, data models, structs, records, and helper classes outside the main class but inside the `cAlgo.Robots` or `cAlgo.Indicators` namespace.

Use this bottom-of-file order as applicable:

1. close the main Robot or Indicator class;
2. tool-specific helper classes, data models, structs, records, and enums;
3. embedded shared Uzzy Bridge types or code; and
4. close the namespace with the file's final structural brace.

Keep shared Bridge code after tool-specific helper types. Do not move an existing public or nested type merely for style when that would change its accessibility, identity, serialization contract, or API. A new nested type is an exception that must be justified by a genuine private-access or encapsulation need, not convenience.

For a new file or new bottom section without an established equivalent, use this shape:

```csharp
namespace cAlgo.Robots
{
    /// <summary>
    /// Runs the approved tool-specific cBot behavior.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]
    public class UzzyExample : Robot
    {
        #region Parameters
        #endregion

        #region Fields
        #endregion

        #region cBot Lifecycle
        #endregion

        #region Core Logic
        #endregion
    }

    #region Helper Classes & Enums
    /// <summary>
    /// Identifies the supported processing direction.
    /// </summary>
    public enum Direction
    {
        None,
        Bullish,
        Bearish
    }

    /// <summary>
    /// Stores state shared by the tool's processing stages.
    /// </summary>
    public sealed class ToolState
    {
        public DateTime UpdatedAt { get; set; }
    }
    #endregion

    #region Uzzy Bridge Shared Code
    /// <summary>
    /// Provides the shared bridge contract used by Ecosystem tools.
    /// </summary>
    public static class UzzyBridge
    {
    }
    #endregion
}
```

Use `cAlgo.Indicators`, the `[Indicator]` attribute, and indicator lifecycle regions for indicators. The example demonstrates structural placement only; include only the regions and types required by the actual tool.

### Parameters And Parameter Subregions

- Keep all cAlgo parameter properties inside the outer `Parameters` region.
- Give each meaningful UI `Group` its matching parameter subregion and keep related parameters together.
- Follow the target's existing subregion naming form, commonly `#region Group: <name>` or the exact established group name.
- Place directory and operational configuration early, feature and visual settings in coherent groups, and `DEBUGGING` near the end when present.
- Put a new parameter beside the settings that consume the same behavior; do not collect unrelated new parameters in a generic catch-all group.
- Preserve parameter labels, `Group` strings, public property names, defaults, ranges, persistence behavior, and ordering unless the approved task requires a change.
- Do not add XML summaries to every parameter property. Use a short summary or one-line comment only when a non-obvious contract, safety instruction, or persistence behavior cannot be expressed clearly by its label and group.

Existing `DefaultValue` changes still use `ecosystem-default-parameter-change`; this section governs placement and style, not the persistence-reset procedure.

### Fields

Keep the Fields region lean.

- Group fields by responsibility and proximity of use.
- Prefer a short one-line cluster label when a group is not self-explanatory.
- Add a one-line field comment only for a genuinely non-obvious invariant, unit, ownership rule, lifecycle, concurrency contract, or external mapping.
- Do not add XML summaries to ordinary fields.
- Do not comment every field, number every field group, or turn the Fields region into a prose inventory.
- Do not preserve temporary labels such as `[NEW]`, `[UPDATE]`, phase names, or implementation-history notes after the change becomes the normal design.

Classes, structs, records, and enums declared near the fields are helper types, not fields; document them under the XML rules below.

### XML Documentation

Add a brief `/// <summary>` immediately before every new method, class, struct, record, or enum introduced by the task. When materially changing one of those symbols, preserve and tighten its existing summary or add one if missing.

A useful summary states the member's responsibility, meaningful result, or important side effect. Keep it normally to one or two short sentences. Add `<param>`, `<returns>`, `<typeparam>`, or `<exception>` only when the contract would otherwise remain unclear.

Do not:

- paraphrase the symbol name without adding meaning;
- narrate implementation steps that belong inside the method;
- document obvious private fields or every parameter property;
- write speculative behavior, historical notes, or marketing-style prose; or
- let a summary disagree with the final implementation.

Small enum values need individual comments only when their domain meaning is not obvious from the member name.

### In-Method And Inline Comments

Comments inside methods should explain **why**, a non-obvious rule, or a useful mental boundary. Good reasons include:

- a domain invariant or trading-rule interpretation;
- a guard whose necessity is not obvious;
- a state transition, cache lifecycle, concurrency rule, or ordering dependency;
- a performance shortcut with correctness implications;
- an external file, payload, cTrader, or persistence contract; and
- the intent of a substantial multi-step block.

Prefer one concise comment immediately above the relevant block. A short end-of-line comment is acceptable for a small local constraint. Preserve existing comments that still explain retained behavior, update comments made stale by the edit, and remove comments attached only to deleted logic.

Avoid:

- narrating obvious assignments, loops, or conditionals;
- repeating the XML summary inside the method;
- banner walls and decorative separators where a region or one-line comment is enough;
- conversational storytelling that obscures the contract;
- numbered tours that must be renumbered after ordinary edits; and
- comments on nearly every line.

### Imports, Naming, And Formatting

- Keep only imports required by the final source.
- For an existing file, preserve its coherent import order and add a new import beside related `System` or `cAlgo` namespaces; do not reorder all imports as unrelated cleanup.
- For a new file, keep imports compact and consistently group the required .NET namespaces and cAlgo namespaces.
- Use four-space indentation and Allman braces, matching the corpus.
- Use PascalCase for types, methods, properties, and enum members; use `_camelCase` for private fields.
- Preserve established ecosystem acronyms and domain vocabulary instead of renaming them for generic style purity.
- Separate logical groups with one blank line. Avoid whitespace-only churn and broad formatter changes outside the approved edit.

### Code-Shape Verification

Before reporting an edit complete, confirm:

- every addition is in the correct responsibility region and parameter group;
- every region and subregion is balanced and meaningfully named;
- new or materially changed methods and helper types have concise, accurate XML summaries;
- ordinary fields and obvious parameter properties did not receive blanket XML documentation;
- inline comments explain intent without narrating the code;
- no stale `[NEW]`, `[UPDATE]`, phase, or temporary implementation notes remain;
- imports are necessary and no unrelated import reordering occurred;
- naming, indentation, braces, and blank-line rhythm match the target;
- the main Robot or Indicator class closes before bottom helper-type regions unless a documented nested-type exception genuinely needs private access;
- bottom helper types and embedded Bridge code remain inside the correct cAlgo namespace, with Bridge code after tool-specific helper types;
- the namespace closing brace is the file's final structural brace; and
- the final diff remains surgical.

## Required Change Report

After every phase, batch, or full run, return the exact report skeleton below. This manifest and ledger are mandatory, compulsory, and non-optional. Preserve the headings and order so reports remain comparable across agents. Never omit a field: write `None`, `Not applicable`, `Not run`, or `Pending` with the reason when a field has no value.

### 1. Run Identity

- **Report level:** Phase | Batch | Full run | Completion
- **Execution mode:** Phased | Full-run
- **Phase or batch:** Name and identifier
- **Ordinary build owner:** User | Agent
- **Parameter-cycle build owner:** User | Agent | Not applicable
- **Build-completion time:** Timestamp | Not run
- **Evidence window:** Pre-change and post-build timestamps
- **Selected runtime context:** Tool, instance ID, asset, and selection reason

### 2. Scope Manifest

- **Approved components:** Every bot, indicator, tool, and supporting component
- **Approved source pairs:** Every live cAlgo file mapped to its workspace file
- **Files changed:** Exact paths
- **Files inspected but unchanged:** Exact paths and why they were inspected
- **Out of scope:** Explicit exclusions or `None`

### 3. Change Ledger

Create one entry per logical change, using stable identifiers such as `C-01`, `C-02`, and so on. Every entry must contain:

- **Change ID and title:**
- **File:**
- **Final line pointer(s):** Exact clickable file-and-line links from the final synchronized source
- **Operation:** Added | Materially changed | Removed
- **Symbols affected:** Fields, methods, types, parameters, calls, or blocks
- **Before:** Previous behavior or structure
- **After and how it works:** New behavior and control/data flow
- **Reason:** Requirement, defect, or acceptance criterion satisfied
- **Compatibility and scope impact:** Interfaces, schemas, payloads, parameters, persistence, or `None`

Record additions, material changes, and removals separately. Do not hide a removal inside a general summary.

### 4. Verification Ledger

Report each check with **Check**, **Result**, and **Evidence**. Include every subsection even when it is not applicable:

- **Source and diff scope:** Syntax-sensitive review, stale references, conflict markers, whitespace, interface/schema/payload preservation, and actual result
- **Build:** Per-component command or user evidence, passed/failed/not run, and the exact errors or warnings that matter
- **Live-to-workspace parity:** Every mapped pair, live hash, workspace hash, and PASS/FAIL parity result
- **Automatic restart or reload:** Build time, expected cBot stop/start or indicator reload, observed log transition, and observation timestamps
- **Runtime logs:** Exact log paths, instances/assets, checks, actual findings, exceptions, warnings, and lifecycle evidence
- **Databases and output files:** Exact paths, timestamps, structural checks, baseline comparison, actual findings, and refresh evidence
- **Acceptance cases and metrics:** Expected versus observed results
- **Unexercised scenarios:** Rare or unavailable cases and why they remain open

### 5. Parameter And Debug Ledger

- **Existing defaults changed:** Tool, parameter, old value, requested value, workflow result, builds, persistence action, and final value
- **New parameters:** Declaration, default, purpose, and final line pointer
- **Debug parameters enabled:** Parameter and reason
- **Debug parameters reverted:** Parameter and final `false` evidence
- **Approved stay-on exceptions:** Parameter and user approval, or `None`
- **Final DEBUGGING zero-hit check:** Exact result

### 6. Outcome, Risks, And Next Gate

- **Implementation outcome:** What now works
- **Defects found and repaired:** Evidence and repair, or `None`
- **Remaining risks or pending evidence:**
- **User action required:** Exact action, or `None`
- **Next gate or continuation point:**

Use selective before/after blocks when:

- the user asks for them;
- a short block makes a replacement or deletion materially clearer;
- line pointers alone would hide an important behavioral change.

Do not dump full source files or every trivial diff hunk. For a large batch, group pointers by phase and file. Label every shown block `Before`, `After`, `Added`, or `Removed`.

Line numbers must be taken from the final synchronized files after edits, not estimated from an earlier copy.

## Verification Ladder

Use the strongest evidence currently available and label it honestly.

### Source-Level Verification

As relevant, check:

- exact diff and scope
- compile-sensitive syntax and signatures
- braces, regions, conflict markers, and whitespace
- stale fields, methods, calls, or signatures
- parameters, schemas, payloads, and public interfaces expected to remain unchanged
- live-cAlgo/workspace-mirror parity for every mapped pair

Static checks are not a successful build.

### Build Verification

For `user-build`:

- stop at the build gate in phased mode;
- tell the user exactly what to build and what evidence to return;
- do not claim compilation success until the user confirms it or supplies the build result; and
- after build confirmation, inspect the automatic restart/reload evidence immediately. Only if that evidence is absent after the bounded recheck may the agent ask the user for a targeted manual restart, run, or cTrader action.

For `agent-build`:

- run the real available build for every affected component;
- report each component separately;
- if the environment cannot perform the real build, say so and return the gate to the user instead of substituting a weaker check; and
- after a successful build, own the entire restart/reload and evidence-check continuation. Do not ask the user to restart or reload the affected cBot or indicator as a routine next step. Diagnose missing activity and report the actual blocker or defect instead of offloading that continuation to the user.

### Permitted User Gates

Waiting for the user is allowed only at these explicit gates:

1. **User-build gate** — the user owns the build. Wait for actual build evidence; then inspect the automatic restart/reload evidence immediately. A targeted request for a manual restart, run, attachment, or cTrader action is allowed only when the automatic evidence remains absent after the bounded recheck.
2. **User-controlled parameter gate** — meaningful runtime evidence requires a parameter or instance setting that only the user can turn on, turn off, or change in the running cTrader instance. State the exact tool, instance, asset, parameter, required value, why it is needed, whether a build or restart follows, and what confirmation will clear the gate.

Do not create a user gate when the agent is authorized and technically able to perform the action. Existing source `DefaultValue` transitions remain owned by `ecosystem-default-parameter-change`; they become user gates only when the user explicitly owns its parameter-cycle builds or when the required setting exists only in user-controlled runtime state. After either permitted gate clears, continue immediately into the automatic restart/reload check and the nested `inspect` evidence review.

### Automatic cTrader Restart And Evidence Window

In this Ecosystem environment, a successful build of a resolved live cAlgo project automatically reloads the affected running component:

- active cBot instances stop and start again, producing a new post-build lifecycle and a new log file or log sequence;
- active indicator instances reload and their logs reset, clearing or replacing the prior content before new startup and runtime lines appear; and
- databases, bridge files, and state files refresh as the restarted or reloaded instances write their post-build state.

This standing behavior applies whether the successful build is run by the user or by the agent. A successful build is therefore the start of the post-build runtime evidence window; a separate manual restart is not the default gate.

Immediately after build success is evidenced, the agent must:

1. record the build-completion time and the affected components, instances, and assets;
2. inspect the fixed log and output roots immediately for new, reset, truncated, or timestamp-refreshed evidence after that time;
3. correlate the cBot stop/start or indicator reload boundary with refreshed databases, bridge files, and state files;
4. recheck only as needed for bounded filesystem or startup latency, without first asking the user to restart the component; and
5. continue directly into the runtime, log, and database verification ladder.

Do not stop after a successful agent-owned build merely to ask the user to restart a cBot or indicator, rerun the instance, or tell the agent when it is ready. For a user-owned build, a targeted manual restart or cTrader request is allowed only after build confirmation, the immediate evidence check, and the bounded recheck show no post-build activity. Parameter-related waiting must satisfy the explicit user-controlled parameter gate above. Report unresolved conditions as missing runtime evidence, not as successful runtime checks.

### Required Inspect Evidence Review

After the build and automatic restart/reload check, invoke `inspect` as the nested read-only evidence-review workflow. The user does not need to invoke `inspect` separately; the explicit Ecosystem Greenlight run authorizes this bounded call. Use Inspect Mode B's Ecosystem runtime-evidence profile.

This is not a generic audit asking whether a log or database file is valid in isolation. Use the artifacts as evidence and context to determine whether the current fix, logic, phase, and implementation are behaving as intended or have introduced defects. Pass `inspect` the phase or batch objective, acceptance criteria, pre-change baseline, build time, selected tool/instance/asset, and resolved log/database/output paths.

`inspect` owns reading and correlating the selected evidence. `ecosystem-calgo-greenlight` retains ownership of asset selection, the defect and repair loop, and the compulsory six-part report. Fold the returned evidence packet into Verification Ledger sections for automatic restart/reload, runtime logs, databases/output files, acceptance cases, and unexercised scenarios.

### Runtime, Log, And Database Verification

Post-phase database verification is a standing obligation in both phased and full-run execution. After every completed phase or batch, once a successful build is evidenced—whether performed by the user or agent—and a post-build runtime sample exists, proactively open the relevant read-only output databases from `Tools\Outputs` and inspect the matching logs under the cAlgo `Data` root. Do not wait for the user to ask again, identify an asset again, or attach evidence that is already resolvable there.

Use the asset-resolution order under Evidence Locations. A suitable running instance may be selected automatically when that order produces one clear, representative choice. After a successful build, first apply the mandatory automatic-restart evidence check above. If no post-build sample appears after that immediate check and bounded recheck, diagnose the cTrader, deployment, instance, and asset state before asking a targeted question. In full-run mode, do not insert an approval gate merely because phases are preserved; perform each available post-batch check without asking, and account for unavailable runtime samples in the final report.

For each post-phase or post-batch check:

1. re-derive the metrics the phase was supposed to change and compare them with the pre-change baseline;
2. check the named worked cases or acceptance examples cited by the plan;
3. run structural integrity checks appropriate to the artifact, including duplicates, ordering, state counts, continuity between related records, and impossible values;
4. report what the data actually shows, including anything that worsened or did not change.

Inspect the relevant evidence together:

- logs for each affected instance or asset
- JSON or other database files
- timestamps and chronological ordering
- lifecycle transitions and state persistence
- duplicates, reversals, count mismatches, and stale state
- exceptions, warnings, operational errors, alert failures, and write failures
- expected cross-file or cross-instance consistency

Correlate evidence from the same runtime window when practical. Separate:

- behavior directly observed at runtime;
- behavior proven only from source;
- rare scenarios not exercised;
- accepted environmental errors;
- real defects requiring follow-up.

Never treat malformed parsing or a wrong database envelope as evidence. Discard the result, correct the inspection, and rerun it.

A phase or batch is not reportable as complete on source-level evidence alone when runtime data is available to check it. If the data contradicts the intended behavior, treat the contradiction as a defect under the Defect And Repair Loop, not as a reporting footnote.

## Defect And Repair Loop

If verification exposes a concrete defect:

1. explain the evidence and root cause;
2. distinguish it from a theoretical edge case;
3. identify the smallest reliable repair;
4. determine whether it stays inside the approved task;
5. apply it under the current mode when it is in scope;
6. otherwise stop and request the necessary scope decision;
7. repeat source, build, runtime, and persistence verification as applicable.

Do not mark a goal, phase, or plan complete merely because the planned edits were applied. Completion requires the evidence promised by its Definition of Done.

## Plans, Goals, And Finalization

When an active plan governs the work:

- preserve its phase/checklist structure;
- record only evidence actually obtained;
- keep incomplete runtime or user-build items pending;
- do not finalize it during implementation.

A Codex Goal may track a substantial run when the user explicitly requests the Goal feature. Do not create one merely because this skill was invoked.

Use `finalize-plan`, `finalize-prompt`, `finalize-task`, or `finalize-report` only when the user explicitly invokes the corresponding finalization workflow.

## Completion Report

At the end, use the complete mandatory report skeleton under Required Change Report and set **Report level** to `Completion`. In addition to the skeleton, account explicitly for:

- execution mode used
- ordinary phase build owner used
- parameter-cycle build owner used
- components and `.cs` files touched
- implementation outcome
- build and runtime evidence status
- logs/databases inspected
- per-file live-cAlgo/workspace-mirror parity
- every existing parameter default changed: tool, parameter, old value, and user-requested new value
- the parameter-change workflow outcome, including its builds, workspace diff, final synchronization, and any required cBot persistence action
- any temporary default changes and the final values requested by the user
- every debug parameter enabled and the reason for each
- every debug parameter reverted to `DefaultValue = false`
- every user-approved debug parameter deliberately left on
- the final zero-hit check for unapproved `Group = "DEBUGGING"` declarations combined with `DefaultValue = true`
- unresolved or deliberately deferred scenarios
- exact next action, if any

The task is complete only when every approved target is accounted for, every claimed check has evidence, and the user can navigate directly to the reported changes. When existing parameter defaults were in scope, every requested target value must be accounted for by the completed parameter-change workflow. It is not complete while an unapproved debug parameter remains at `DefaultValue = true`.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with the skill-creator install, running Python in UTF-8 mode (`-X utf8`). Also smoke-check that:

- `Mode = Eco-Greenlight` appears exactly;
- phased handoffs and runtime waits preserve the mode;
- successful user-build and agent-build evidence both trigger runtime checks;
- an unambiguous running asset may be inferred, while material ambiguity requires asking the user; and
- pre-change baseline evidence is captured when available and never fabricated;
- successful agent builds never create a routine user restart/reload gate;
- user builds allow a targeted manual restart request only after confirmed build success and a failed automatic-evidence check;
- user-controlled parameter gates name the exact parameter, value, runtime context, reason, and confirmation required;
- every post-build log/database/output review invokes `inspect` using its Ecosystem runtime-evidence profile; and
- every phase, batch, full-run, and completion response uses all six mandatory report sections, exact final line pointers, actual results, and explicit empty states instead of omitted fields.
