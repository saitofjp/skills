# skills

Agent Skills for testing and refining products and documents.

## Skills in this repo

- **[simulated-persona-creator](skills/simulated-persona-creator/SKILL.md)** — Create a behavior-driven test persona (a portable Persona Contract) that another tester can simulate consistently.
- **[simulated-persona-tester](skills/simulated-persona-tester/SKILL.md)** — Simulate how a supplied persona would naturally encounter and use a product, and report the result as a hypothesis-generating persona test.
- **[aidoc-less-is-more](skills/aidoc-less-is-more/SKILL.md)** — Restructure an AI-generated document by removing elements that compete for the reader's attention (conflict, duplication, decoration), verifying every deletion with a QA test.
- **[dopagaki-generator](skills/dopagaki-generator/SKILL.md)** — Turn content into an over-the-top, auto-playing 16:9 motion presentation (single HTML) in the Japanese "dopagaki" style (Japanese video games × pachinko × Japanese anime OP × short video); screen-record it to get a social media video. Japanese version: [SKILL.ja.md](skills/dopagaki-generator/SKILL.ja.md). Examples: [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html), [津田健次郎 対 TikTok 判決 ドパガキ版](https://saitofjp.github.io/skills/dopagaki/tsuda-tiktok-2609.html).
- **[semantic-structure](skills/semantic-structure/SKILL.md)** — Map what a text or a Claude Code conversation means as a diagram of chunks of meaning and the lines between them, each traced to the words it rests on, and show it beside the text as one animated HTML page that also turns it into a one-sentence summary, notes, slides or a table. Japanese version: [SKILL.ja.md](skills/semantic-structure/SKILL.ja.md). Example: [津田健次郎 対 TikTok 判決のノート](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).
- **[review-birds-eye](skills/review-birds-eye/SKILL.md)** — Review a change from a bird's-eye view, the way a senior engineer does, rather than line by line: read from the code up to the design it implies, and judge whether the change is sound in its design (is it carried through consistently in the related code) and in its non-functional requirements (side effects, compatibility, failure, concurrency, operation, security). Japanese version: [SKILL.ja.md](skills/review-birds-eye/SKILL.ja.md).
- **[review-modeling](skills/review-modeling/SKILL.md)** — Review a specification or design document by modeling it: choose the models the document calls for (state transitions, permissions, domain rules, structure and data ownership, interface contracts, failure, concurrency, trust boundaries, migration and so on), try to write each one from the text, and report what could not be written as gaps and what does not hold as contradictions and risks, each traced to the text and put as a question for the author. At the end it offers to turn the models into a checklist of what to confirm. Japanese version: [SKILL.ja.md](skills/review-modeling/SKILL.ja.md). Example: [施設予約システムの仕様・設計レビュー](examples/review-modeling/).
- **[orchestrator-mode](skills/orchestrator-mode/SKILL.md)** — Turn the session into an orchestrator that does no work itself: it keeps the conversation with the user moving, hands the work to other sessions or agents with short instructions a good manager would give, keeps their order and consistency as the conversation changes, and reports where things stand as a tree of large, medium and small cases. Called explicitly only. Japanese version: [SKILL.ja.md](skills/orchestrator-mode/SKILL.ja.md).

Use the persona skills together: create a persona with `simulated-persona-creator`, then run it against your product with `simulated-persona-tester`. Example: [AIQ のペルソナテスト](examples/aiq-personas/).

## Examples

- [AIQ のペルソナテスト](examples/aiq-personas/) — made with `simulated-persona-creator` and `simulated-persona-tester` for [AIQ](https://aiqtry.com), a web app that measures how people handle an AI that is wrong on purpose. Four Persona Contracts, split by behavior rather than demographics, and one report per persona from runs against the real screens. The personas are synthetic hypotheses, not research.
- [施設予約システムの仕様・設計レビュー](examples/review-modeling/) — made with `review-modeling` from a made-up specification and design document for a facility booking system, with defects planted on purpose (they are also this skill's evals). The review traces each finding to the sections it rests on, puts it as a question for the author, appends the models it wrote, with the cells the documents leave open marked `?`, and ends by offering a checklist; the checklist written after a yes is included.

Live examples are published with GitHub Pages from [`docs/`](docs/): <https://saitofjp.github.io/skills/>

- [日銀展望レポート ドパガキ版](https://saitofjp.github.io/skills/dopagaki/boj-outlook-2607.html) — made with `dopagaki-generator` from the Bank of Japan's Outlook Report (July 2026). It auto-plays in the browser and is an unofficial summary.
- [津田健次郎 対 TikTok 判決 ドパガキ版](https://saitofjp.github.io/skills/dopagaki/tsuda-tiktok-2609.html) — made with `dopagaki-generator` from the Tokyo District Court's ruling of 30 September 2026 on a request to delete videos narrated in a voice like the voice actor's (about 2 minutes in 13 stages). It shows the rule that a voice, like a likeness, is a symbol of the person apart from the conclusion, the dismissal because the videos were already deleted. It auto-plays in the browser and is an unofficial summary, not legal advice. The same ruling is also shown as notes below.
- [津田健次郎 対 TikTok 判決のノート](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html) — made with `semantic-structure` from the same ruling, about 5,000 characters in 13 chunks and 11 lines. The rule that a voice, like a likeness, is a symbol of the person is marked as the key, apart from the conclusion, the dismissal. Switch the header to dopa and press ▶ to watch it as a show. The model is in [`docs/semantic/`](docs/semantic/).

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
npx skills add saitofjp/skills --skill semantic-structure
npx skills add saitofjp/skills --skill review-birds-eye
npx skills add saitofjp/skills --skill review-modeling
npx skills add saitofjp/skills --skill orchestrator-mode
```

Or point directly at a skill's path in this repo:

```bash
npx skills add https://github.com/saitofjp/skills/tree/main/skills/simulated-persona-tester
```
