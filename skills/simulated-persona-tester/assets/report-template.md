# Persona test report template

Use this structure for the finished report unless the user asks for another format.

Keep the section headings and the fixed labels (`Yes / No / Partial`, `Low / Medium / High`, severity names) in English even when the report body is written in another language, so results stay comparable across runs.

The two top headings are part of that: the file opens with `# [Persona name] — [Scenario]`, and the report itself always opens with `## Persona Test Result`. Earlier runs drifted to other wordings and to hand-rolled metadata blocks, which is exactly what makes a set of runs hard to read side by side.

Everything up to `Test Limitations` is Phase B and always applies. The final block is Phase C only — omit it entirely on a plain simulation-and-observation run.

```markdown
# [Persona name] — [Scenario in a few words]

- **Date:** YYYY-MM-DD
- **Persona file:** .simulated-personas/persona-NN…/persona.md
- **Environment:** production / local / preview, with the URL, the device or viewport, and the auth state
- **Side effects:** real data this run created (sessions, consumed credits, saved content, anything now publicly visible) — write "none" when there are none

## Persona Test Result

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

<!-- Phase C only. Delete this whole block when severity, prioritization,
     cross-persona comparison, or investigation areas were not requested. -->

### Analyst Classification

One entry per finding, most severe first — a run normally produces several at different severities.

- **Severity: Major** — [the finding in one sentence]
  - **Why:** [the persona rule, threshold, or observed reaction that sets this severity]
- **Severity: Moderate** — ...
  - **Why:** ...

### Suggested Investigation
- ...
```

`Suggested Investigation` should identify what the product team should investigate. Do not prescribe a design solution unless explicitly asked.
