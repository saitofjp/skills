---
name: semantic-model-viewer
description: Shows a Semantic Model (notes made by semantic-model-builder) next to its text as one self-contained, animated HTML page, the Transform View. It moves along two axes. Focus out and in rises from the text to its chunks to the model and back. Transform turns the model into structure, linear notes, a table or one sentence. Every piece flies from where it was to where it goes, so the reader never loses their place. The text and the notes are linked by a thread under the pointer, and a story mode plays the whole rise: text, chunks wrapped with cut-ins, notes, structure, links, one sentence. Use it whenever the user wants to see, explore, present or visualize a semantic model or the notes of a text, read a text next to its notes, or watch a text turn into a structure. Triggers include "show the semantic model", "show the notes next to the text", "visualize this model", "transform view", 「Semantic Modelを表示して」「原文とノートを並べて見せて」「構造になっていく様子を見せて」「トランスフォームビューで見せて」.
---

# Semantic Model Viewer

One page, one model, two moves:

- **Focus out / in:** from the text (L0), to the text wrapped into chunks (L1), to the model (L2), and back. Rising abstracts; descending returns to the words. At L2 the text and the notes sit side by side with their pointers linked: the Two Pane view.
- **Transform:** at L2, the same notes become structure, linear notes, a table or one sentence.

Every change is animated so the reader keeps their place: a tag grows into a card, a card flies into its phrase in the summary, a point drops into its table cell, and back. ▶ plays the whole rise as a story (the Formation): the text, each chunk wrapped with a cut-in, the notes, the structure, the links from the conclusion outward, and the one sentence.

The page is a fixed template, [`assets/viewer.html`](assets/viewer.html). It works with any model that follows the contract ([`references/semantic-model.md`](references/semantic-model.md)) and needs no network. It never derives meaning from the text: everything it shows comes from the model.

## Input

- A Semantic Model file (`semantic-model/1`). If the user has only a text, make the notes first with [`semantic-model-builder`](../semantic-model-builder/SKILL.md). Do not work out the structure here.
- What the user wants to see, if they say: a layer, a form, whether to play the story.

## Steps

The tool is `scripts/build_viewer.py` in this skill's folder (Python 3, standard library only).

1. **Choose how the page opens.** These are presentation choices; they never change the model.
   - To read and explore: the model layer with linear notes (the default).
   - To present, or to show how the text becomes a structure: `--play`. Use `--order reading` when the order in which things appear in the text matters (a narrative, a procedure).
   - A specific starting point: `--stop`, `--rep`, `--focus <node-id>`.
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--play] [--stop text|chunks|model] [--rep structure|linear|table|summary] [--order notes|reading] [--focus ID] [--theme dark|light|auto]`
   It validates the model with the builder's checker and writes nothing while the model has errors. Save next to the model unless the user names another place: `.semantic/<YYYYMMDD>-<slug>/view.html`. Commit only when the user asks.
3. **Check it in a browser** if Node and Playwright are available:
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   It checks that the page loads with no errors, that hovering a word focuses the model, that pinning opens the details card and Esc releases it, that every layer and form renders, that the story plays to the end in both orders, and that nothing overflows a phone-width screen. Then look at it yourself: do the headlines read as a story, and does the summary land?
4. **Deliver.** Give the path and how to use it: hover to link text and notes, click to pin, Esc to release, the Focus and Form buttons (↑ ↓, 1–4), ▶ / Space for the story, ← → to step. If the user cannot open local files (for example in a remote session), publish the page as an Artifact; load the `artifact-design` skill first.

## View options

Pass them as flags, or as a JSON file with `--view`. They live in their own block in the page, never in the model.

```json
{ "stop": "model", "rep": "linear", "play": false, "order": "notes", "focus": "node-id", "theme": "dark", "follow": true, "lang": "ja" }
```

## What not to do

- **Do not edit the model to improve the picture.** If the notes are unclear, fix them with the builder. If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page.** Everything it shows comes from the model.
- **Do not hand-write a new page per text.** The template is the implementation. If you improve it, keep [`references/transform-view.md`](references/transform-view.md) in step with it.

## Reference

- [references/semantic-model.md](references/semantic-model.md): the input contract (shared with the builder).
- [references/transform-view.md](references/transform-view.md): layers, forms, the story, the motion rules, the field, the source ↔ model mapping, controls.
- [assets/viewer.html](assets/viewer.html): the template. Opened as is, it shows a short example (a shopping street in three chunks).
