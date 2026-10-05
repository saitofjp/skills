---
name: semantic-structure-viewer
description: Shows the Semantic Structure of a text (a model of what it means, written as notes by semantic-structure-builder) next to the text as one self-contained, animated HTML page, the Transform View. A single gauge, a compact HUD with the model at its centre, draws the meta-structure and is the control. Drag it from the text, to the text wrapped into chunks passage by passage (listed beside it in the text's order), to the model, where the chunks merge and take their places, and every piece moves continuously between the stages; ▶ plays the same animation to the summary and back to the model, and starts by itself when the page opens. From the model, straight branches lead to its forms, A the summary in one sentence, B linear notes (and on to B2, 16:9 slides) and C a table; at a form, the text, the form and the model (as a minimap in the corner) are shown and lit together. The dopa theme dresses it in the dopagaki style of dopagaki-generator, and while ▶ plays, stages the play as a show (combos, cut-ins for the key and the conclusion, a question before the summary, the sentence lit up), ready to screen-record. Use it whenever the user wants to see, explore, present or visualize the semantic structure or the notes of a text, read a text next to its notes, watch a text turn into a structure and a summary, or plan slides from it. Triggers include "show the semantic structure", "show the notes next to the text", "visualize this model", "transform view", 「意味構造を表示して」「原文とノートを並べて見せて」「構造になっていく様子を見せて」「トランスフォームビューで見せて」「ドパで見せて」「意味構造をドパガキ風に見せて」.
---

# Semantic Structure Viewer

One page shows one model and its text. One control moves it: a gauge that draws the meta-structure, with the model at its centre. It is a compact HUD at the top right, in English.

- **The trunk, text ━ chunks ━ model (focus out / in):**
  - Dragging the knob right abstracts, and dragging it left returns to the words.
  - The page can stand anywhere in between. At the chunk layer the text is wrapped passage by passage, and the list on the right follows the text's order: nothing is restructured yet. Moving on to the model, the rows of each chunk merge into its card, the cards nest and take their places, and the lines grow from the conclusion outward (the Formation).
  - At the chunk and model layers, the text and its notes sit side by side, with their pointers linked (the Two Pane view).
  - **▶** always plays from the start, the text, to the summary, wherever the knob is, holds there for a moment and goes back to the model: it moves the knob by itself, so it plays exactly the animation dragging shows. The page starts it by itself when it opens.
- **The forms, A summary / B linear (→ B2 slides) / C table (transform):**
  - These are representations of the model, so they branch from the model, in straight lines, and are reached only through it.
  - Moving the knob into a branch turns the model into that form: the cards fly into the phrases of the one sentence, points come out of their cards into linear notes, or drop into table cells. From the linear notes, the slides: each card grows into a 16:9 page, a plan for a presentation.
  - Meanwhile a copy of the structure recedes into the corner as a minimap, like the small map in a game. The text is on the left, the form in the centre and the model in the corner, and the focus lights all three.
- **The conclusion and the key:** the chunk the text concludes with is the inverted card. The key (`role: "key"`, ◆ KEY), what matters most to a reader when that is not the conclusion, has a heavy frame in every form, so it is not lost behind the conclusion.
- **Themes, light / dark / dopa:** dark is the default and light a click away. **dopa** dresses the page in the dopagaki style of [`dopagaki-generator`](../dopagaki-generator/SKILL.md) (game × pachinko × anime OP × short video): a black stage in neon, the conclusion gold and the key hot pink.
  - While ▶ plays (and in the play on opening), the play is staged as a show. As the passages wrap, a COMBO counts them; the key and the conclusion land with cut-ins (hot pink and gold), flashes and a shake; before the summary the stage darkens and asks 「一言でいうと……？」; the summary arrives with the biggest burst, and the sentence lights up phrase by phrase.
  - Moving the knob by hand, clicking a label or pressing a key stages nothing: the show is the play's alone, and stops when it does.
  - The show plays even when the system asks for less motion (on some machines that setting is on without the reader knowing). It only decorates what the gauge already does, and every number it shows is counted from the model. Screen-record the play and it is a short video.

The page is a fixed template, [`assets/viewer.html`](assets/viewer.html). It works with any model that follows the contract ([`references/semantic-structure.md`](references/semantic-structure.md)) and needs no network. It never derives meaning from the text: everything it shows comes from the model.

## Input

- A Semantic Structure file (`semantic-structure/1`). If the user has only a text, make the notes first with [`semantic-structure-builder`](../semantic-structure-builder/SKILL.md). Do not work out the structure here.
- Where the user wants to start, if they say.

## Steps

The tool is `scripts/build_viewer.py` in this skill's folder (Python 3, standard library only).

1. **Choose where the knob starts.** This is a presentation choice; it never changes the model.
   - To show how the text becomes a structure, start at the text (the default). The reader drags from there.
   - To read and explore, start at the model (`--stage model`) or at a form (`--stage summary`, `linear`, `slides`, `table`).
   - **Which way the structure runs** (`--anchor`) is a presentation choice too. With `end` the columns run from the conclusion, on the right: for a text whose reasons gather into it, such as a ruling. With `start` they run from where the lines start, on the left: for a text that branches out from a question, such as a research memo. Leave it at `auto` (the default), which takes `start` when more than half of the chunks with lines never reach the conclusion. Set it only when the picture reads the wrong way.
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage text|chunks|model|summary|linear|slides|table] [--focus ID] [--theme dark|light|auto|dopa] [--anchor auto|end|start] [--no-autoplay]`
   - It validates the model with the builder's checker and writes nothing while the model has errors.
   - For the dopagaki look, a show to screen-record, or when the user asks for dopa or dopagaki, build with `--theme dopa`. A page built with it always opens in it.
   - Save next to the model unless the user names another place: `.semantic/<YYYYMMDD>-<slug>/view.html`.
   - Commit only when the user asks.
3. **Check it in a browser** if Node and Playwright are available:
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   - It checks that the page loads with no errors and that dragging the knob moves the page between stages and settles when let go.
   - It checks that the structure and the minimap run the same way, and that the columns follow the shape of the text: a question branching out runs from the start, reasons gathering into a conclusion run from it, and `anchor` overrides that.
   - It checks that the page plays by itself when it opens, that each form renders, that ▶ plays from the text to the summary and back to the model, and that hovering a word, or anywhere inside a chunk's frame, focuses the model.
   - It checks that hovering shows the details along the bottom and Esc clears them, that at a form the card and the minimap sit side by side, and that nothing overflows a phone-width screen.
   - It checks that the theme switches between light, dark and dopa: in dopa, moving the knob by hand stages nothing, ▶ stages the show (the build-up and the summary's arrival once) and it stops with the play, the show plays even when the system asks for less motion, and it stops when the theme changes.

   Then look at it yourself: drag slowly from the text to the model. Do the headlines read as a story, and does the summary land?
4. **Deliver.** Give the path and how to use it:
   - It plays by itself when it opens; ▶ (or Space) plays from the start to the summary and back to the model. Drag the gauge's knob to watch every piece move; click its labels (or press ← →) to switch at once.
   - At the model, drag into a branch for linear notes, slides or a table (↑ ↓ switch between the branches).
   - Hover to link the text and the notes and show the details along the bottom; click to bring the other side to it. light / dark / dopa in the header switches the theme.
   - In dopa, the play is the show: to make a video, show the page full screen, press ▶ and screen-record it.

   If the user cannot open local files (for example in a remote session), publish the page as an Artifact. Load the `artifact-design` skill first.

## View options

Pass them as flags, or as a JSON file with `--view`. They live in their own block in the page, never in the model.

```json
{ "stage": "text", "focus": "node-id", "theme": "dark", "anchor": "auto", "follow": true, "autoplay": true, "lang": "ja" }
```

`theme` is `dark` (default), `light`, `auto` (follows the system) or `dopa`.

`anchor` is `auto` (default), `end` (the structure runs from the conclusion, on the right) or `start` (from the chunks no line comes into, on the left).

## What not to do

- **Do not edit the model to improve the picture.** If the notes are unclear, fix them with the builder, or with the user through [`semantic-structure-reconstructor`](../semantic-structure-reconstructor/SKILL.md). If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page.** Everything it shows comes from the model.
- **Do not hand-write a new page per text.** The template is the implementation. If you improve it, keep [`references/transform-view.md`](references/transform-view.md) in step with it.

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the input contract (shared with the builder).
- [references/transform-view.md](references/transform-view.md): the gauge, the layers, the forms, the motion, the field, the dopa theme, the source ↔ model mapping and the controls.
- [assets/viewer.html](assets/viewer.html): the template. Opened as is, it shows a short example (a shopping street in three chunks).
