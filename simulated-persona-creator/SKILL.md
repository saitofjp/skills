---
name: simulated-persona-creator
description: Create realistic, behavior-driven alpha-test personas that can be simulated consistently against a product or service. Use when you need synthetic test users before or alongside real alpha testers, need materially different user perspectives, or need a portable Persona Contract for an alpha-testing workflow. Produce assumption-aware behavioral models, not demographic profiles. Do not execute the product test itself.
---

# Simulated Persona Creator

## Purpose

Create a compact alpha-test persona that another tester can simulate consistently.

Treat the persona as a hypothesis, not as research evidence. Model the user's goals, prior knowledge, habits, expectations, trust, friction tolerance, recovery behavior, and abandonment conditions well enough that a tester can decide what this person would naturally do without asking the creator to intervene.

Do not optimize the persona to make the product look good.

## Core rules

1. Prefer behavior over demographics. Include age, occupation, location, family status, or other demographics only when they materially change product behavior.
2. Never invent research, interview quotes, analytics, support feedback, or market evidence.
3. Keep provided facts, assumptions, and unknowns distinguishable.
4. Give every persona realistic friction, limits, and failure behavior. Do not make every user patient, curious, technically capable, or willing to recover.
5. Keep multiple personas behaviorally distinct. Do not create clones that differ only by age or occupation.
6. Define what the persona knows before the test. Do not give the persona product knowledge merely because the model has it.
7. Produce a complete Persona Contract that can be handed directly to an alpha tester.

## Evidence discipline

Classify persona inputs into these categories:

- **Provided fact:** Explicitly supplied by the user, product brief, research, analytics, or another named source.
- **Assumption:** Plausible but not validated. Mark as `[ASSUMPTION-VALIDATE]` where the uncertainty matters to behavior.
- **Unknown:** Important information that cannot be inferred responsibly. Mark as `[UNKNOWN-NEEDS-RESEARCH]`.

If no user research is supplied, treat the persona as a synthetic hypothesis. Do not imply that generated characteristics represent actual customers.

Do not tag every sentence mechanically. Instead, make the evidence basis visible in the final contract and mark high-impact assumptions at the point where they affect behavior.

## Workflow

### 1. Establish the test context

Use the available information about:

- product or service
- intended audience
- intended use cases
- alpha-test goals
- starting platform or device
- known constraints
- existing research, analytics, or feedback
- current alternatives or competitors, if provided

If the product itself is unknown, do not invent one. State the gap.

### 2. Define only relevant identity and background

Create a memorable natural human name.

Include only details that affect behavior, such as:

- role or life stage
- relevant domain experience
- relevant technical experience
- device or usage context
- accessibility context, if relevant
- constraints such as time pressure, privacy sensitivity, or shared-device use

### 3. Define the relationship with the problem

Capture:

- primary goal
- motivation
- current pain
- current workaround
- what would make switching worthwhile

The current workaround is important because unfamiliar products are judged against existing habits.

### 4. Define the knowledge boundary

Explicitly state:

- **Knows:** Prior knowledge the persona may use at test start.
- **Does not know:** Product concepts, terminology, workflows, or conventions the persona should not be assumed to know.
- **May infer from:** Information sources the persona normally trusts, such as visible UI, familiar conventions, recommendations, documentation, or search.

The tester must be able to distinguish persona knowledge from model knowledge.

### 5. Define observable behavioral rules

Describe concrete tendencies for:

- discovery
- reading and comprehension
- decision-making
- exploration
- help-seeking
- recovery after mistakes or errors
- privacy and trust
- friction tolerance

Prefer rules such as:

> Skips onboarding paragraphs, scans headings and primary buttons, retries once after an unexplained error, then looks for a back path.

Avoid vague labels such as:

> Medium technical user.

### 6. Define initial state and state-change rules

Use these default state dimensions unless another dimension is clearly more relevant:

- **Trust**
- **Patience**
- **Confidence**
- **Confusion**

For each dimension, provide an initial level and concrete conditions that change it.

Examples:

- Trust decreases after an unexplained permission request.
- Patience decreases after repeated unclear steps.
- Confidence increases after a predictable successful action.
- Confusion accumulates when terminology remains unexplained.

Do not invent precise numerical psychology. Use simple levels or concrete conditions unless evidence supports more detail.

### 7. Define thresholds

Make stopping behavior reproducible. Define:

- retry threshold
- help-seeking threshold
- abandonment threshold
- trust-break conditions

A threshold may be a count or a condition. Use whichever better reflects the persona.

### 8. Define the persona voice

Describe communication style and typical vocabulary only to support consistent simulation.

Any illustrative quotation must be labeled `[REPRESENTATIVE-SYNTHETIC]`. Never present synthetic speech as an interview quote.

### 9. Define success and failure

State what would make the persona conclude:

- "This is useful enough to continue using."
- "This is not for me."

These criteria should reflect the persona's goal, not the product team's desired outcome.

## Persona Contract v1

Use this structure by default. Keep it compact, but do not omit fields that affect simulation.

```markdown
# [Persona Name]

## Snapshot
- **Role / context:** ...
- **Primary goal:** ...
- **Current workaround:** ...
- **Relevant experience:** ...
- **Why this product might matter:** ...

## Evidence Basis
- **Provided facts:** ...
- **High-impact assumptions:** [ASSUMPTION-VALIDATE] ...
- **Important unknowns:** [UNKNOWN-NEEDS-RESEARCH] ...

## Background
...

## Goals & Motivation
- ...

## Pains & Current Workarounds
- ...

## Knowledge Boundary
- **Knows:** ...
- **Does not know:** ...
- **May infer from:** ...

## Knowledge & Confidence
- **Domain knowledge:** ...
- **Digital literacy:** ...
- **Product-category familiarity:** ...
- **Terminology familiarity:** ...
- **Unfamiliar-software confidence:** ...

## Behavioral Rules
- **Discovery:** ...
- **Comprehension / reading:** ...
- **Decision-making:** ...
- **Exploration:** ...
- **Help-seeking:** ...
- **Recovery:** ...
- **Privacy / trust:** ...
- **Friction tolerance:** ...

## Initial State
- **Trust:** Low / Medium / High - ...
- **Patience:** Low / Medium / High - ...
- **Confidence:** Low / Medium / High - ...
- **Confusion:** Low / Medium / High - ...

## State Update Rules
- **Trust increases when:** ...
- **Trust decreases when:** ...
- **Patience decreases when:** ...
- **Confidence increases when:** ...
- **Confidence decreases when:** ...
- **Confusion increases when:** ...
- **Confusion decreases when:** ...

## Thresholds
- **Retry threshold:** ...
- **Help-seeking threshold:** ...
- **Abandonment threshold:** ...
- **Trust-break conditions:** ...

## Voice
- **Style:** ...
- **Typical reaction:** "[REPRESENTATIVE-SYNTHETIC] ..."

## Alpha Testing Rules
- **First action:** ...
- **What they notice first:** ...
- **What they usually ignore:** ...
- **How far they explore without guidance:** ...
- **When they seek help:** ...
- **When they retry:** ...
- **When they abandon:** ...
- **What builds trust:** ...
- **What breaks trust:** ...
- **Definition of success:** ...
- **Definition of failure:** ...
```

## Saving personas

Save each finished Persona Contract as a Markdown file by default; skip only for an explicit throwaway.

- **Location:** fixed at `.simulated-personas/` in the repo root. Each persona gets its own numbered folder, with a sibling `test-results/` folder that `simulated-persona-tester` writes into:

  ```text
  .simulated-personas/
  ├─ persona-01/
  │  ├─ persona.md
  │  └─ test-results/
  ├─ persona-02/
  │  ├─ persona.md
  │  └─ test-results/
  └─ ...
  ```

- **Numbering:** scan `.simulated-personas/` for existing `persona-NN` folders and continue the sequence (start at `persona-01`).
- **Filename:** always `persona.md`, saved inside the persona's own `persona-NN/` folder.
- Create the sibling `test-results/` folder alongside `persona.md` even if empty, so it exists before `simulated-persona-tester` needs to write into it.
- Report the saved path to the user.

## Multiple personas

When asked for several personas:

1. Start with 2-4 materially different users unless the user specifies another number.
2. Run the same evidence discipline for each persona.
3. Differentiate by behavior, motivation, knowledge, context, trust, or friction tolerance rather than demographics alone.
4. Include a primary persona when the product has a clear target.
5. Include an edge-case persona only when it can expose a meaningful usability risk.
6. Do not create extra personas merely to fill a quota.

Useful differentiation axes include:

- novice vs expert
- fast vs cautious
- high trust vs low trust
- high friction tolerance vs low friction tolerance
- self-directed vs help-seeking
- frequent vs occasional use
- problem-aware vs problem-unaware
- buyer vs user
- mobile-first vs desktop-first

## Quality checks

Before finalizing, verify that:

- the persona has a plausible reason to use the product
- demographics are not carrying the persona
- current workarounds are explicit
- prior knowledge and non-knowledge are explicit
- behavioral rules are observable rather than generic traits
- state-change rules are concrete enough to simulate
- retry, help-seeking, and abandonment thresholds are defined
- trust-building and trust-breaking conditions are defined
- the persona can make decisions without creator intervention
- synthetic quotations are clearly labeled
- important assumptions and unknowns are visible
- no research, analytics, or customer feedback was invented
- another tester could use the contract and produce reasonably consistent behavior

## Anti-patterns

### Generic persona

Avoid: "A 30-year-old professional who wants an easy-to-use product."

Prefer: "Scans the first screen rather than reading onboarding, expects one obvious next action, retries once when a step fails, and leaves if the recovery path is unclear."

### Idealized user

Do not make the persona behave as the product designer hopes.

### Expert-user leakage

Do not give the persona terminology, product knowledge, or intended navigation they have not plausibly learned.

### Perfect recovery

Do not assume the persona will patiently read documentation or keep retrying.

### Fake evidence

Never attribute generated characteristics to interviews, analytics, reviews, surveys, or support data unless that evidence was actually supplied.

### Biography without behavioral value

Omit details that do not change how the persona would use or judge the product.
