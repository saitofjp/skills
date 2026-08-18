# Persona test report template

Use this structure for the finished report unless the user asks for another format.

Keep the section headings and the fixed labels (`Yes / No / Partial`, `Low / Medium / High`, severity names) in English even when the report body is written in another language, so results stay comparable across runs.

Everything up to `Test Limitations` is Phase B and always applies. The final block is Phase C only — omit it entirely on a plain simulation-and-observation run.

```markdown
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
- **Severity:** Blocker / Major / Moderate / Minor
- **Why:** ...

### Suggested Investigation
- ...
```

`Suggested Investigation` should identify what the product team should investigate. Do not prescribe a design solution unless explicitly asked.
