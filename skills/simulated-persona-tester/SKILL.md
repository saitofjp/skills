---
name: simulated-persona-tester
description: Act as a simulated alpha tester using a supplied persona or Persona Contract to discover, use, and react to a product as that user would. Use for first-impression, task-completion, free-exploration, or recovery tests before or alongside real alpha testing. Preserve the persona's knowledge limits, behavior rules, state changes, friction tolerance, and abandonment thresholds. For visual interfaces, discover and judge UI from screenshots or other rendered user-visible output, not from DOM inspection. Do not create the persona or switch into expert-reviewer mode during simulation.
---

# Simulated Persona Tester

## Purpose

Simulate how a supplied persona would naturally encounter and use a product or service.

The objective is not to find the optimal path or to review the product as an expert. The objective is to observe whether this persona would naturally understand, trust, attempt, recover, continue, succeed, or abandon.

Treat the result as a simulation that generates hypotheses, not as evidence of actual user behavior.

## Core rules

1. Use the supplied persona as the primary decision model.
2. Do not become a UX designer, product manager, developer, usability expert, or ideal user during the simulation phase.
3. Do not silently rescue the persona with model knowledge.
4. Do not invent missing UI, hidden features, developer intent, or undocumented behavior.
5. Do not optimize for task completion. If the persona would stop, stop.
6. Follow the persona's reading, exploration, recovery, help-seeking, trust, and friction rules even when another path would be more efficient.
7. Keep observed system behavior separate from simulated user interpretation.
8. Update persona state only from events the persona actually experiences.
9. Do not silently fill missing persona rules. Treat material gaps as unknown.

## Knowledge boundary

The simulated user may use only:

- prior knowledge explicitly granted by the persona
- information exposed to the persona during the current test
- information the persona naturally obtains through an allowed help-seeking action

Treat model knowledge about the product as unavailable to the persona.

Do not infer product intent from information the persona has not seen. Do not use hidden product knowledge to interpret unfamiliar terminology, predict navigation, or recover from mistakes.

If the supplied persona lacks a rule needed for a decision, do not invent a detailed personality trait. Use an explicitly stated general rule from the persona if one applies. If the missing information materially determines the next action and no rule applies, record the simulation as limited by an insufficient persona definition.

## Visual interaction boundary

For graphical interfaces, treat the user's visible rendered experience as the source of truth.

### Discover UI visually

Use, in order of preference when available:

- screenshots
- rendered page or app images
- video frames or screen captures
- other user-visible visual output from the test environment

Base recognition of buttons, links, fields, menus, messages, hierarchy, and state changes on what is visibly rendered.

### Do not discover controls from the DOM

Do not inspect or search the DOM, HTML, page source, CSS, element IDs, test IDs, framework internals, hidden text, network payloads, application state, or accessibility tree to discover what actions are available or where to click.

Do not use selectors, DOM queries, or accessibility labels as a shortcut for understanding a screen the persona has not visually understood.

If the automation environment requires a DOM handle or selector only to execute an action on a target that was already identified from the visible screen, the handle may be used strictly as an execution mechanism. It must not reveal, select, rank, or interpret targets that were not first identified visually.

After a meaningful action, capture or inspect a fresh rendered visual state before deciding what happened next whenever the environment supports it.

If a visual state cannot be obtained, do not silently fall back to DOM inspection. Record the environment limitation and stop or continue only with information genuinely visible to the persona.

### Assistive-technology exception

Use an accessibility representation only when the test explicitly models an assistive-technology user and that representation is part of the user's actual interface under test. Do not use it merely as a hidden source of UI metadata.

## Inputs

A test should use:

1. **Persona / Persona Contract**
2. **Product or service**
3. **Starting point**
4. **Task or scenario**, if one exists
5. **Optional success criteria**
6. **Optional constraints**

Do not create a new persona inside this skill merely to make the test possible.

If no task is supplied, follow the persona's natural first-time exploration behavior instead of inventing a business objective.

## Test modes

### Mode 1: First impression

Use for landing pages, onboarding, positioning, navigation, or initial comprehension.

Start with only the prior knowledge allowed by the persona.

Observe:

- what the persona thinks the product is
- what they think they can do
- what they notice first
- what they expect to happen
- whether they know what to do next

### Mode 2: Task completion

Use when a concrete task is supplied.

Do not reveal or seek the optimal path. Let the persona choose the path that follows naturally from the visible interface and their knowledge.

### Mode 3: Free exploration

Let the persona explore until they:

- understand enough to reach a meaningful outcome
- become stuck
- lose interest
- satisfy their curiosity
- abandon

### Mode 4: Recovery test

Observe or introduce a relevant friction point only when the scenario allows it.

Do not give the persona the solution. Follow the persona's normal recovery and help-seeking behavior.

## Execution phases

### Phase A: Simulation

Stay inside the persona's behavioral model.

For each meaningful step, internally apply:

```text
Observe visible state
-> Interpret using persona knowledge
-> Form expectation
-> Choose natural action
-> Observe rendered result
-> React
-> Update persona state
-> Continue, recover, seek help, or abandon
```

At each decision point, preserve these distinctions:

- **Observed:** What was visibly or explicitly presented.
- **Expected:** What the persona expected before acting.
- **Action:** What the persona naturally chose.
- **Result:** What the product actually presented next.
- **Reaction:** How the result affected the persona.
- **State change:** Any supported change to trust, patience, confidence, or confusion.

Do not expose hidden chain-of-thought. If a detailed trace is requested, report concise externally observable reasoning such as expectations, actions, reactions, and state changes.

### Phase B: Observation report

After simulation ends, step out of the persona only enough to summarize what occurred.

Describe behavior and mismatches without prescribing product changes.

### Phase C: Analyst classification

Use this phase only when the requested output calls for severity, prioritization, cross-persona comparison, or investigation areas.

Keep analyst judgments clearly labeled and separate from persona feedback.

Do not retroactively change what the persona experienced because the intended design becomes obvious later.

## State handling

If the Persona Contract includes initial states and update rules, follow them consistently.

Typical state dimensions are:

- trust
- patience
- confidence
- confusion

Apply only changes supported by experienced events and persona rules.

Examples:

- An unexplained permission request may reduce trust if the persona is privacy-sensitive.
- A predictable successful action may increase confidence.
- Repeated unclear steps may reduce patience.
- Undefined terminology may increase confusion.

Do not invent precise numerical changes unless the persona contract defines them.

When a persona threshold is reached, follow the defined behavior even if the task remains incomplete.

## Interaction rules

### Clear instruction

Follow it naturally if the persona understands it.

### Ambiguous instruction

Choose the interpretation most consistent with the persona and visible context. Do not ask the product owner what the UI was intended to mean.

### Confusion

Follow the persona's normal sequence, such as:

- infer from visible context
- try an action
- go back
- look for visible help
- search externally, only if allowed and natural for the persona
- ask another person, only if the scenario supports it
- abandon

Do not jump directly to expert documentation unless the persona would.

### Failure

Retry only within the persona's retry tolerance. Do not keep trying solely to make the test succeed.

### Positive surprise

Record unexpectedly clear, trustworthy, efficient, or satisfying moments as well as problems.

## Completion criteria

End the simulation when one of these occurs:

- the persona achieves the scenario's natural goal
- the persona reaches a meaningful stopping point
- the persona abandons according to their rules
- the test environment prevents further meaningful visual interaction
- a missing persona rule makes further simulation materially arbitrary

Do not continue indefinitely.

## Default result format

Use this structure unless the user asks for another format.

```markdown
## Alpha Test Result

### Simulation Status
- **Nature of result:** Simulated behavior, not real-user evidence
- **Persona:** [Persona name]
- **Scenario:** [Task / starting context]

### Outcome
- **Completed:** Yes / No / Partial
- **Effort impression:** Low / Medium / High
- **Would use again:** Yes / Maybe / No
- **Stopping reason:** ...

### Observed Behavior
- ...

### Expectation Mismatches
- **Expected:** ...
- **Observed:** ...
- **Reaction:** ...

### Confusion / Friction
- ...

### Positive Moments
- ...

### Trust Signals
- ...

### Drop-off Signals
- ...

### State Changes
- **Trust:** ...
- **Patience:** ...
- **Confidence:** ...
- **Confusion:** ...

### Unexpected Behavior
- ...

### Persona Feedback
> [REPRESENTATIVE-SYNTHETIC] ...

### Test Limitations
- ...

### Analyst Classification
- **Severity:** Blocker / Major / Moderate / Minor, if requested or useful
- **Why:** ...

### Suggested Investigation
- ...
```

`Suggested Investigation` should identify what the product team should investigate. Do not prescribe a design solution unless explicitly asked.

## Saving results

Save the finished report (Phase B, plus Phase C if run) as a Markdown file by default; skip only if the user says not to.

- **Location:** fixed at `.simulated-personas/persona-NN/test-results/`, where `persona-NN` is the folder of the persona under test (create the folder, and a `persona-NN/test-results/` subfolder, if the persona wasn't created via `simulated-persona-creator` and doesn't already have one). If the persona wasn't file-based at all, fall back to `.simulated-personas/ad-hoc/test-results/`.
- **Filename:** `YYYY-MM-DD-<scenario-slug>.md`, e.g. `2026-08-17-travel-plan-pitfall.md`. Append `-2`, `-3` on same-day reruns instead of overwriting.
- **Content:** a short metadata header (date, persona file, product/environment tested) followed by the report exactly as produced.
- Report the saved path to the user; don't repeat the full report in chat afterward.

## Severity guidance

Use severity only in the analyst phase.

- **Blocker:** The persona cannot continue toward the scenario goal.
- **Major:** The issue is likely to cause abandonment, failure, or a materially wrong outcome for this persona.
- **Moderate:** The issue causes significant hesitation, confusion, or extra effort but recovery remains plausible.
- **Minor:** The issue is noticeable but unlikely to alter the outcome for this persona.

Do not generalize severity from one simulated persona to all users.

## Multi-persona testing

When several personas are supplied:

1. Reset product assumptions and persona state before each run.
2. Run each persona independently.
3. Do not let one persona's discoveries leak into another persona's prior knowledge.
4. Use the same scenario and observation categories where possible.
5. Compare results only after all individual simulations are complete.

Useful comparison fields include:

- first impression
- first action
- comprehension
- primary path
- confusion
- trust shifts
- friction tolerance
- completion
- abandonment trigger

Separate:

- common simulated problems
- persona-specific simulated problems
- contradictory expectations
- different successful paths
- different abandonment points

## Anti-patterns

### Reviewer mode during simulation

Avoid: "The navigation is poorly designed."

Prefer: "This persona looked under Profile for saved items because they expected personal content to be there."

### DOM shortcut

Avoid discovering a hidden or unlabeled control through DOM inspection and then clicking it.

Prefer identifying available actions from the screenshot and acting only on what the persona could visually discover.

### Expert rescue

Do not explain the intended flow after the persona becomes stuck.

### Hindsight bias

Do not say the persona should obviously have selected an option they did not understand.

### Over-optimization

Do not keep trying until the task succeeds.

### Fake emotion

Do not manufacture dramatic reactions that are unsupported by the persona.

### Generic feedback

Avoid: "The UX could be improved."

Prefer: "After the second unclear step, this persona reaches their abandonment threshold and leaves rather than opening help."

## Epistemic boundary

Always distinguish among:

- simulated persona behavior
- observed system behavior
- actual user research
- product analytics
- analyst interpretation

Never present simulated alpha-persona behavior as proof that real users will behave the same way. Use it to generate hypotheses, expose obvious usability risks, and decide what deserves validation with real users.
