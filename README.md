# skills

Agent Skills for testing and refining products and documents.

## Skills in this repo

- **[simulated-persona-creator](skills/simulated-persona-creator/SKILL.md)** — Create a behavior-driven test persona (a portable Persona Contract) that another tester can simulate consistently.
- **[simulated-persona-tester](skills/simulated-persona-tester/SKILL.md)** — Simulate how a supplied persona would naturally encounter and use a product, and report the result as a hypothesis-generating persona test.
- **[aidoc-less-is-more](skills/aidoc-less-is-more/SKILL.md)** — Restructure an AI-generated document by removing elements that compete for the reader's attention (conflict, duplication, decoration), verifying every deletion with a QA test.
- **[dopagaki-generator](skills/dopagaki-generator/SKILL.md)** — Turn content into an over-the-top, auto-playing 16:9 motion presentation (single HTML) in the Japanese "dopagaki" style (Japanese video games × pachinko × Japanese anime OP × short video); screen-record it to get a social media video. Japanese version: [SKILL.ja.md](skills/dopagaki-generator/SKILL.ja.md). Example: [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html).
- **[semantic-model-builder](skills/semantic-model-builder/SKILL.md)** — Turn a text into a Semantic Model: the understanding a reader takes away, as a graph. It holds what the text is about (each thing once, with its states over time), how those things act on each other (+/−), and what the author concludes and why. Every element is tied to the words it rests on and marked explicit / inferred / abstracted / uncertain. It models the subject, not the sentences. Japanese version: [SKILL.ja.md](skills/semantic-model-builder/SKILL.ja.md).
- **[semantic-model-viewer](skills/semantic-model-viewer/SKILL.md)** — Show a Semantic Model as one interactive HTML page with two views: Two Pane (source and model side by side, synchronized, highlight by semantic distance, inferences traced to their evidence) and Formation (the structure forming from a focus or in reading order). Japanese version: [SKILL.ja.md](skills/semantic-model-viewer/SKILL.ja.md). Example: [日銀展望レポートの意味構造](https://saitofjp.github.io/skills/semantic/boj-outlook-2607.html).

Use the persona skills together: create a persona with `simulated-persona-creator`, then run it against your product with `simulated-persona-tester`.

Use the semantic skills together: build a model with `semantic-model-builder`, then look at it with `semantic-model-viewer`. The two share one data contract ([semantic-model.md](skills/semantic-model-builder/references/semantic-model.md)), so each can also be used on its own. After editing the contract or its tool in the builder, run `python3 scripts/sync_semantic_shared.py` to update the viewer's copy.

## Examples

Live examples are published with GitHub Pages from [`docs/`](docs/): <https://saitofjp.github.io/skills/>

- [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html) — made with `dopagaki-generator` from the Bank of Japan's Outlook Report (July 2026). It auto-plays in the browser and is an unofficial summary.
- [日銀展望レポートの意味構造](https://saitofjp.github.io/skills/semantic/boj-outlook-2607.html) — made with `semantic-model-builder` and `semantic-model-viewer` from the same report's Basic View (about 9,000 characters; 61 nodes, 104 relations, read from the conclusion "keep raising the policy rate" back to its reasons). Switch between Two Pane and Formation, and between overview and detail. An unofficial example; the model is in [`docs/semantic/`](docs/semantic/).

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
npx skills add saitofjp/skills --skill dopagaki-generator
npx skills add saitofjp/skills --skill semantic-model-builder
npx skills add saitofjp/skills --skill semantic-model-viewer
```

Or point directly at a skill's path in this repo:

```bash
npx skills add https://github.com/saitofjp/skills/tree/main/skills/simulated-persona-tester
```
