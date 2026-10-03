---
name: semantic-model-viewer
description: Shows a Semantic Model (notes made by semantic-model-builder) next to its text as one self-contained, animated HTML page, the Transform View. A single gauge draws the meta-structure and is the control. Drag it from the text, to the text wrapped into chunks (with the chunks listed beside it), to the model, and every piece moves continuously between the stages. Chunks wrap one by one, the list grows into cards, and lines grow from the conclusion outward. At the model, its forms (linear notes, a table, one sentence) grow out of it as branches of the gauge. The text and the notes are linked by a thread under the pointer. Use it whenever the user wants to see, explore, present or visualize a semantic model or the notes of a text, read a text next to its notes, or watch a text turn into a structure. Triggers include "show the semantic model", "show the notes next to the text", "visualize this model", "transform view", 「Semantic Modelを表示して」「原文とノートを並べて見せて」「構造になっていく様子を見せて」「トランスフォームビューで見せて」.
---

# Semantic Model Viewer

One page shows one model and its text. One control moves it: a gauge that draws the meta-structure.

- **The trunk, text ━ chunks ━ model (focus out / in):**
  - Dragging the knob right abstracts, and dragging it left returns to the words.
  - The page can stand anywhere in between. Chunks wrap one by one, and their list on the right grows into cards. The cards take their places, and the lines grow from the conclusion outward (the Formation).
  - At the chunk and model layers, the text and its notes sit side by side, with their pointers linked (the Two Pane view).
- **The branches, linear / table / summary (transform):**
  - These are representations of the model, so they appear only once the knob reaches it, growing out of the model node.
  - Moving the knob into a branch turns the model into that form: points come out of their cards, drop into table cells, or the cards fly into the phrases of the one sentence.

The page is a fixed template, [`assets/viewer.html`](assets/viewer.html). It works with any model that follows the contract ([`references/semantic-model.md`](references/semantic-model.md)) and needs no network. It never derives meaning from the text: everything it shows comes from the model.

## Input

- A Semantic Model file (`semantic-model/1`). If the user has only a text, make the notes first with [`semantic-model-builder`](../semantic-model-builder/SKILL.md). Do not work out the structure here.
- Where the user wants to start, if they say.

## Steps

The tool is `scripts/build_viewer.py` in this skill's folder (Python 3, standard library only).

1. **Choose where the knob starts.** This is a presentation choice; it never changes the model.
   - To show how the text becomes a structure, start at the text (the default). The reader drags from there.
   - To read and explore, start at the model (`--stage model`) or at a form (`--stage linear`).
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage text|chunks|model|linear|table|summary] [--focus ID] [--theme dark|light|auto]`
   - It validates the model with the builder's checker and writes nothing while the model has errors.
   - Save next to the model unless the user names another place: `.semantic/<YYYYMMDD>-<slug>/view.html`.
   - Commit only when the user asks.
3. **Check it in a browser** if Node and Playwright are available:
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   - It checks that the page loads with no errors and that dragging the knob moves the page between stages and settles when let go.
   - It checks that the forms grow out of the model and each one renders, and that hovering a word focuses the model.
   - It checks that pinning opens the details card and Esc releases it, and that nothing overflows a phone-width screen.

   Then look at it yourself: drag slowly from the text to the model. Do the headlines read as a story, and does the summary land?
4. **Deliver.** Give the path and how to use it:
   - Drag the gauge's knob, or click its labels (← → also move it).
   - At the model, drag into a branch for linear notes, a table or the one sentence (↑ ↓ switch between them).
   - Hover to link the text and the notes, click to pin, Esc to release.

   If the user cannot open local files (for example in a remote session), publish the page as an Artifact. Load the `artifact-design` skill first.

## View options

Pass them as flags, or as a JSON file with `--view`. They live in their own block in the page, never in the model.

```json
{ "stage": "text", "focus": "node-id", "theme": "dark", "follow": true, "lang": "ja" }
```

## What not to do

- **Do not edit the model to improve the picture.** If the notes are unclear, fix them with the builder. If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page.** Everything it shows comes from the model.
- **Do not hand-write a new page per text.** The template is the implementation. If you improve it, keep [`references/transform-view.md`](references/transform-view.md) in step with it.

## Reference

- [references/semantic-model.md](references/semantic-model.md): the input contract (shared with the builder).
- [references/transform-view.md](references/transform-view.md): the gauge, the layers, the forms, the motion, the field, the source ↔ model mapping and the controls.
- [assets/viewer.html](assets/viewer.html): the template. Opened as is, it shows a short example (a shopping street in three chunks).
