# skills

Agent Skills for testing and refining products and documents.

## Skills in this repo

- **[simulated-persona-creator](skills/simulated-persona-creator/SKILL.md)** — Create a behavior-driven test persona (a portable Persona Contract) that another tester can simulate consistently.
- **[simulated-persona-tester](skills/simulated-persona-tester/SKILL.md)** — Simulate how a supplied persona would naturally encounter and use a product, and report the result as a hypothesis-generating persona test.
- **[aidoc-less-is-more](skills/aidoc-less-is-more/SKILL.md)** — Restructure an AI-generated document by removing elements that compete for the reader's attention (conflict, duplication, decoration), verifying every deletion with a QA test.
- **[dopagaki-generator](skills/dopagaki-generator/SKILL.md)** — Turn content into an over-the-top, auto-playing 16:9 motion presentation (single HTML) in the Japanese "dopagaki" style (Japanese video games × pachinko × Japanese anime OP × short video); screen-record it to get a social media video. Japanese version: [SKILL.ja.md](skills/dopagaki-generator/SKILL.ja.md). Examples: [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html), [津田健次郎 対 TikTok 判決 ドパガキ版](https://saitofjp.github.io/skills/dopagaki/tsuda-tiktok-2609.html).
- **[semantic-structure-builder](skills/semantic-structure-builder/SKILL.md)** — Turn a text into a Semantic Structure written as notes: the text wrapped into chunks, each with a headline (its message) and the points that must not be lost, lines between chunks (+/−), and one sentence for the whole. Every piece is tied to the words it rests on and marked explicit / inferred / abstracted / uncertain. Japanese version: [SKILL.ja.md](skills/semantic-structure-builder/SKILL.ja.md).
- **[semantic-structure-viewer](skills/semantic-structure-viewer/SKILL.md)** — Show a Semantic Structure next to its text as one animated HTML page, the Transform View. One gauge, a compact HUD with the model at its centre, draws the meta-structure and is the control: drag it from the text, to the text wrapped passage by passage, to the model, and every piece moves continuously; ▶ plays the same animation on to the summary and back to the model, and starts by itself when the page opens. From the model, branches lead to its forms, A the summary in one sentence, B linear notes (and on to B2 slides) and C a table, with the model kept as a minimap. Themes are light, dark, dopa (the dopagaki look) and dopa/full, which also stages the play as a show (combos, cut-ins for the key and the conclusion, a question before the summary, the sentence lit up) to screen-record. Japanese version: [SKILL.ja.md](skills/semantic-structure-viewer/SKILL.ja.md). Example: [津田健次郎 対 TikTok 判決のノート](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).

Use the persona skills together: create a persona with `simulated-persona-creator`, then run it against your product with `simulated-persona-tester`.

Use the semantic skills together: make the notes with `semantic-structure-builder`, then look at them with `semantic-structure-viewer`. The two share one data contract ([semantic-structure.md](skills/semantic-structure-builder/references/semantic-structure.md)), so each can also be used on its own. After editing the contract or its tool in the builder, run `python3 scripts/sync_semantic_shared.py` to update the viewer's copy.

## Examples

Live examples are published with GitHub Pages from [`docs/`](docs/): <https://saitofjp.github.io/skills/>

- [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html) — made with `dopagaki-generator` from the Bank of Japan's Outlook Report (July 2026). It auto-plays in the browser and is an unofficial summary.
- [津田健次郎 対 TikTok 判決 ドパガキ版](https://saitofjp.github.io/skills/dopagaki/tsuda-tiktok-2609.html) — made with `dopagaki-generator` from the Tokyo District Court's ruling of 30 September 2026 on a request to delete videos narrated in a voice like the voice actor's (about 2 minutes in 13 stages). It shows the rule that a voice, like a likeness, is a symbol of the person apart from the conclusion, the dismissal because the videos were already deleted. It auto-plays in the browser and is an unofficial summary, not legal advice. The same ruling is also shown as notes below.
- [津田健次郎 対 TikTok 判決のノート](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html) — made with `semantic-structure-builder` and `semantic-structure-viewer` from the Tokyo District Court's ruling of 30 September 2026 on a request to delete videos narrated in a voice like the voice actor's (about 5,000 characters in 13 chunks, 11 lines, one sentence: the court held that a voice, like a likeness, is a symbol of the person and can be protected by the right of publicity, but dismissed the claim because the videos were already deleted). The rule is marked as the key, apart from the conclusion. Switch the header to dopa/full and press ▶ to see the same play as a show (a COMBO as the passages wrap, cut-ins as the key and the conclusion land, a question before the summary, and the sentence lit up). The model is in [`docs/semantic/`](docs/semantic/).

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
npx skills add saitofjp/skills --skill semantic-structure-builder
npx skills add saitofjp/skills --skill semantic-structure-viewer
```

Or point directly at a skill's path in this repo:

```bash
npx skills add https://github.com/saitofjp/skills/tree/main/skills/simulated-persona-tester
```
