---
name: semantic-model-viewer
description: Shows a Semantic Model (notes made by semantic-model-builder) next to its text as one self-contained, animated HTML page, the Transform View. A single gauge draws the meta-structure and is the control. Drag it from the text, to the text wrapped into chunks (with the chunks listed beside it), to the model, and on to the goal, the summary in one sentence, and every piece moves continuously between the stages; ▶ plays the way to the summary. Chunks wrap one by one, the list grows into cards, and lines grow from the conclusion outward. From the model, straight branches lead to linear notes (and on to 16:9 slides) and a table; at a form, the text, the form and the model (as a minimap in the corner) are shown and lit together. Use it whenever the user wants to see, explore, present or visualize a semantic model or the notes of a text, read a text next to its notes, watch a text turn into a structure and a summary, or plan slides from it. Triggers include "show the semantic model", "show the notes next to the text", "visualize this model", "transform view", 「Semantic Modelを表示して」「原文とノートを並べて見せて」「構造になっていく様子を見せて」「トランスフォームビューで見せて」.
---

# Semantic Model Viewer

One page shows one model and its text. One control moves it: a gauge that draws the meta-structure, with the model at its core. It is a compact HUD at the top right, in English.

- **The trunk, text ━ chunks ━ model ━ summary (focus out / in):**
  - Dragging the knob right abstracts, and dragging it left returns to the words.
  - The page can stand anywhere in between. Chunks wrap one by one, and their list on the right grows into cards. The cards take their places, and the lines grow from the conclusion outward (the Formation).
  - At the chunk and model layers, the text and its notes sit side by side, with their pointers linked (the Two Pane view).
  - The trunk ends at the goal, the summary in one sentence: the cards fly into the phrases that name them. **▶** plays the way there, from wherever the knob is, as a sequence: a title card for each stage, one beat per chunk with the text gliding to its passage, and the lines in waves from the conclusion.
- **The branches, linear (→ slides) / table (transform):**
  - These are representations of the model, so they branch from the model node, in straight lines, and are reached only through it.
  - Moving the knob into a branch turns the model into that form: points come out of their cards into linear notes, or drop into table cells. From the linear notes, the slides: each card grows into a 16:9 page, a plan for a presentation.
  - Meanwhile a copy of the structure recedes into the corner as a minimap, like the small map in a game. The text is on the left, the form in the centre and the model in the corner, and the focus lights all three.

The page is a fixed template, [`assets/viewer.html`](assets/viewer.html). It works with any model that follows the contract ([`references/semantic-model.md`](references/semantic-model.md)) and needs no network. It never derives meaning from the text: everything it shows comes from the model.

## Input

- A Semantic Model file (`semantic-model/1`). If the user has only a text, make the notes first with [`semantic-model-builder`](../semantic-model-builder/SKILL.md). Do not work out the structure here.
- Where the user wants to start, if they say.

## Steps

The tool is `scripts/build_viewer.py` in this skill's folder (Python 3, standard library only).

1. **Choose where the knob starts.** This is a presentation choice; it never changes the model.
   - To show how the text becomes a structure, start at the text (the default). The reader drags from there.
   - To read and explore, start at the model (`--stage model`) or at a form (`--stage summary`, `linear`, `slides`, `table`).
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage text|chunks|model|summary|linear|slides|table] [--focus ID] [--theme dark|light|auto]`
   - It validates the model with the builder's checker and writes nothing while the model has errors.
   - Save next to the model unless the user names another place: `.semantic/<YYYYMMDD>-<slug>/view.html`.
   - Commit only when the user asks.
3. **Check it in a browser** if Node and Playwright are available:
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   - It checks that the page loads with no errors and that dragging the knob moves the page between stages and settles when let go.
   - It checks that each form renders, that ▶ plays to the summary, and that hovering a word focuses the model.
   - It checks that pinning opens the details card and Esc releases it, and that nothing overflows a phone-width screen.

   Then look at it yourself: drag slowly from the text to the model. Do the headlines read as a story, and does the summary land?
4. **Deliver.** Give the path and how to use it:
   - ▶ (or Space) plays to the summary. Drag the gauge's knob, or click its labels (← → also move it).
   - At the model, drag into a branch for linear notes, slides or a table (↑ ↓ switch between the branches).
   - Hover to link the text and the notes, click to pin, Esc to release. Light / Dark in the header switches the theme.

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
