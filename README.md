# skills

Agent Skills for testing and refining products and documents.

## Skills in this repo

- **[simulated-persona-creator](skills/simulated-persona-creator/SKILL.md)** — Create a behavior-driven test persona (a portable Persona Contract) that another tester can simulate consistently.
- **[simulated-persona-tester](skills/simulated-persona-tester/SKILL.md)** — Simulate how a supplied persona would naturally encounter and use a product, and report the result as a hypothesis-generating persona test.
- **[aidoc-less-is-more](skills/aidoc-less-is-more/SKILL.md)** — Restructure an AI-generated document by removing elements that compete for the reader's attention (conflict, duplication, decoration), verifying every deletion with a QA test.

Use the persona skills together: create a persona with `simulated-persona-creator`, then run it against your product with `simulated-persona-tester`.

## Install

Install with [`npx skills`](https://skills.sh):

```bash
npx skills add saitofjp/skills
```

Install a single skill:

```bash
npx skills add saitofjp/skills --skill simulated-persona-creator
npx skills add saitofjp/skills --skill simulated-persona-tester
npx skills add saitofjp/skills --skill aidoc-less-is-more
```

Or point directly at a skill's path in this repo:

```bash
npx skills add https://github.com/saitofjp/skills/tree/main/skills/simulated-persona-tester
```
