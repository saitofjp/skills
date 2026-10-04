# Transform View: the gauge, the layers, the forms and the source ↔ model mapping

What [`assets/viewer.html`](../assets/viewer.html) does. Keep this file in step with the template when either changes.

The page shows one Semantic Structure together with its text. The model is the text wrapped into chunks, with headlines, points, lines between chunks and a one-sentence summary. One control moves the page: a gauge that draws the meta-structure itself.

```
01 Text ■━━━ 02 Chunks ⬡━━━ 03 Model ◈━━┯━━━━━━━━━━━━ □ A Summary
                                        ├─ □ B Linear ── □ B2 Slides
                                        └─ □ C Table
```

The gauge is a compact game HUD at the top right (at the bottom on a phone), in English only:

- **The plate.** A flat panel with corner marks, one cut corner and hairline rules. The type is small, monospaced and widely spaced, and the focus colour is used sparingly.
- **The readout.** A large index (`01`–`03` for the levels; `A`, `B`, `B2`, `C` for the forms), the stage's name, and figures taken from the model (`13 NOTES · 11 LINKS`). The name decodes, letter by letter, when the knob reaches a new stage.
- **The play control.** `PLAY` / `PAUSE`, with a timecode: how long the play takes from here (`T-00:24`), and while it runs, the time elapsed (`00:07 / 00:24`).
- **The graph.** It is the control, and the model sits at its centre: a diamond in a ring, framed by turning lock brackets. The levels below it (text, chunks) run into it from the left along a ruled track; its forms leave it to the right as a tree, a series: A, the summary, straight on; B linear (and along its row on to B2 slides) and C table hanging from that line. The knob is a small diamond with a pulse.

The page's content starts below the HUD, and the text, centred at L0, keeps clear of it. The HUD takes no keyboard focus, so a stray Enter or a click cannot leave it ready to start or stop the play; Space and the arrow keys work from anywhere on the page.

- **The trunk** (focus out / in, meta-cognition): the levels, from the text, to the text wrapped into chunks, to the model. Moving right abstracts; moving left returns to the words.
- **The forms** (transform, representation): the model's forms, joined to the model by straight lines: A the summary in one sentence, B linear notes (which lead on to B2 slides), C a table. The only way to a form is through the model, because a form is a representation of the model, not of the text.
- **▶** plays the way to the summary from where the knob is, holds there for a moment, and goes back to the model. It starts from the text again when the knob is at the summary, or still at the model where the last play left it. It moves the knob for you, so what plays is exactly what dragging shows. Space does the same; PAUSE stops the knob where it is, and dragging takes over at once. The page plays by itself when it opens.

## Concept

Rise through the layers of meaning. The text is the ground. Chunks lift off it as slabs, and are listed on the right. The model floats above, in a classical, unruly geometry composed from the model itself, which lies shattered near the text and comes together as you rise.

The look is flat, as on a printed manga page, dark by default (black paper, white ink) with a light theme a click away: solid fills, crisp lines and square, panel-like cards. The dark theme uses screentone dots; the light theme leaves them out and stays plain. There is no glow, blur or soft shadow. Motion is staged but plain. Pieces move in order, settle with a slight overshoot when you let go, and then hold.

The dopa theme is the one exception: the same page and the same play, staged as a show (see [The dopa theme](#the-dopa-theme)).

## The gauge is continuous

Drag the knob, and the page stands at any point between two neighbouring stages. Every keyed piece (a chunk's card, its number, its headline, each point) is drawn between where it is in one stage and where it is in the other. Pieces start one after another: passages in the text's order, notes in the notes' order. Letting go settles to the nearer stage. Only dragging and ▶ move through the frames: clicking a label, or pressing an arrow key, switches to that stage at once.

| Segment | As the knob moves right |
|---|---|
| Text → Chunks | The text column slides aside without reflowing and tilts back for a moment. The passages wrap one after another, in the text's order: the bracket draws, the slab lifts with a brief wash, and the passage's row comes out of it into the list on the right. The field's shards start to assemble. |
| Chunks → Model | The structuring. Rows of the same chunk merge into its card, the cards nest their parts and take their places in the notes' order, and the numbers turn from the text's order (`07`) into the notes' (`4.1`). Then the lines grow, from the conclusion outward through its reasons (Formation). |
| Model → summary, linear or table | The model splits in two. A copy of the whole structure recedes into the corner and becomes the minimap, while its cards turn into the form: points come out of their cards into the linear notes, drop into table cells, or the cards fly into the phrases of the one sentence. |

A caption band names what is happening: the chunk being wrapped, the line being drawn (`7 ← 6 削除済みだから理由がない`), or the form. It cuts in afresh each time it changes.

## The play

▶ is the drag, played: the knob travels along the gauge by itself, through the same frames, as a steady hand would move it. It moves at a constant pace (about 0.47 s for each chunk, and 0.27 s for each line as it grows, with at least 4 s per segment) and stops for a moment at each stage. At the summary it holds for 2.6 s, so the sentence can be read, then plays back down to the model and stops there, with the text and the notes side by side to explore. For the ruling example, the play takes about 22 seconds; the timecode in the HUD shows where it is.

The page starts the play by itself when it opens: once the fonts are in (or after 1.5 s) and the page is in view, unless the reader has already taken the knob. `autoplay: false` (`--no-autoplay`) turns that off.

Dragging, ▶ and the play on opening always animate, even with `prefers-reduced-motion`, because the movement is what the page shows. That setting stops only the decoration: the HUD's pulse and turning lock, the decoding readout, cut-ins and sweeps.

## The dopa theme

`theme: "dopa"` (`--theme dopa`) stages the same play as a show in the dopagaki style of [`dopagaki-generator`](../../dopagaki-generator/SKILL.md): game × pachinko × anime OP × short video. Built with it, the page plays the show when it opens, and a screen recording of the play is a short video.

It adds nothing to what the page shows. Every event is a moment the drag or the play already passes through, fired as the knob passes it going forward (once a segment; going back only runs the counters down), and every number on screen is counted from the model. The stronger the moment, the bigger the show: the conclusion and the result get the most.

| Moment | Show |
|---|---|
| ▶ from the text | A hook first (2.7 s): the text's length counting up (`4,987字`), what it becomes (`→ 1文に。`), the title on a slanted band, `GO!!`. Taking the knob or PAUSE cuts it short. |
| A passage wraps | Sparks off its bracket and a ring on its slab; a COMBO counter (`×07`, with a bar to the last passage). The last one is a `FULL COMBO!!`, with a flash and a shake. |
| Text → chunks → model begins | Speed lines and a light flash. |
| The key lands | A hot pink band across the screen with `◆ KEY` and its headline, a flash, a shake, sparks where its card lands (at the edge of the view when the card is out of it). |
| The conclusion lands | The same in gold, with `CONCLUSION`: the biggest moment before the result. The big moments take turns, so two never cover each other. |
| A line is drawn | Sparks at its arrow, in the colour of its sign; the counter turns to `LINK ×n`. |
| The model is reached | `STAGE CLEAR · MODEL COMPLETE!!`, with its notes and links counting up. |
| Model → summary | The build-up: the stage darkens around the middle, a bubble asks (`一言でいうと……？`), and `3`, `2`, `1` punch in, following the knob. |
| The summary arrives | `MISSION COMPLETE`: a burst, a gold flash and a shake; the text's length counted down to the sentence's (`4,987 → 120字`), its notes and links, and how much smaller it is (`圧縮 1/42`). Then the panel leaves and the sentence lights up, phrase by phrase. |
| A form is reached | `FORM CHANGE` and the form's name. |

- **The stage behind the page** keeps moving: rays turning slowly from the model's centre and sparks rising, stronger as the knob rises. Over the page lie scanlines and a vignette. The HUD's figures count up as the knob reaches a stage.
- **The look.** A black stage in neon: cyan is the focus, gold the conclusion, hot pink the key, and cards and lines glow. The text keeps its plain type, so it can still be read.
- **Timing.** The show takes a little longer than the plain play: the hook, 1.1 s at each stage, 3.5 s for the build-up from the model to a form, and 5.6 s at the summary before going back to the model. The timecode counts it all.
- **Limits.** Flashes come at most about three a second. The show never takes the pointer, and the HUD stays above it. On a phone, it centres above the HUD and the counter moves to the top right.
- **`prefers-reduced-motion`** keeps the colours and drops the show: no hook, cut-ins, flashes, shakes, sparks or moving stage. The play itself still runs, as in the other themes.
- **Not remembered.** dopa is a show the page is built for, not a reading preference: a page built with it always opens in it, and choosing it in the header is never remembered. Light or dark, chosen there, is.

## Layers

| Layer | Shows |
|---|---|
| L0 Text | `sourceText` as written, centred. The field behind it is shattered. |
| L1 Chunks | The text on the left, wrapped passage by passage: a bracket in the left margin and a slab behind each passage, numbered in the text's order. On the right, a row for each passage, in the same order, with its chunk's headline. Nothing is merged, nested or moved yet: a chunk the text comes back to has a row each time. |
| L2 Model | The text on the left and the model (its structure) on the right. This is the Two Pane view: the text and its notes side by side, with their pointers linked. |
| A form | Three at once: the text on the left, the form in the centre, and the model as a minimap in the bottom-right corner, like the small map in a game. The chunks in view in the form are framed on the minimap, and the focus lights it as it lights the other two. The details card sits beside the minimap, so the two line up along the bottom. |

## The details card

The details of what is in focus are docked along the bottom of the model's side, never over the top of it:

- **On focus.** Hovering anything that can be focused shows its details at once (`FOCUS`), and moving off clears them. Nothing is pinned. The card lets the pointer through, and it fades away while the pointer is under it, so what it covers can still be hovered and read. When the details are longer than the card, the bottom fades out.
- **Where.** At the chunks and the model, it spans the bottom of the model's side. At a form, it sits to the left of the minimap, at least as tall as it. Where the side is too narrow for both, the minimap shrinks first, then the card goes above it. On a phone it sits just above the HUD. It hides while the knob moves.
- **Inside.** The headline, then its provenance and note, then its passages, points, lines, parts and evidence in columns that fill the card's width. It is for reading, with no buttons.

## Forms

| Form | What it shows |
|---|---|
| Structure (the model itself) | Top-level chunks in columns that flow toward the conclusion. A chunk's column is its distance, in lines, from the conclusion, and the conclusion sits on the right. Parts sit inside their chunk as one-line cards. Lines run between cards. The labels of lines into the conclusion are always shown; the others appear on focus. |
| B Linear | The notes in their order (`nodes` order, with parts under their parent). Each card has its headline and points. Lines are arcs in the right margin. |
| C Table | One row per chunk, one column per `when` value (in order of first appearance), then a column for points without `when`. |
| A Summary | The `summary` sentence, large. Each phrase is underlined with the numbers of the chunks it names. Chunks the sentence does not reach are chips below it. |
| B2 Slides (from Linear) | Each note on a 16:9 page. The deck opens with a cover (the title and the one sentence) and has a section page for each chunk with parts and a page for each other chunk, with its headline large and its points. The conclusion's page is inverted, and the one sentence closes the deck. The linear cards grow into the pages. It is a plan for a presentation, such as one made with `dopagaki-generator`. |

## Source ↔ model mapping

- **Segments.** The text is cut at every span boundary. A segment knows every chunk, point and relation whose spans cover it.
- **Text → model.** Hovering a segment picks the element with the smallest span over it: a point or a relation comes before the chunk that contains it.
- **Model → text.** Focusing a chunk washes its passages and marks its points' words. Focusing a point marks its words strongly. Focusing a relation underlines its words in the color of its sign.
- **The thread.** A line joins the hovered words to their note, or the note to the first of its words in view. At a form, the focus also lights the chunk on the minimap, so text, form and model point at each other. The other sides scroll to keep the counterparts in view.
- **Following.** The chunk at the middle of the text view is marked. In the chunk list and in Linear, the right side scrolls with the text.
- **Nothing is derived from the text.** The page reads `sourceText` only to display it.

## Colors

| Color | Meaning |
|---|---|
| Teal (blue-green), with a thick outline | The focus: what the pointer is on. In the text, a light wash and an underline. Also the knob and the path walked on the gauge. Not yellow: yellow reads as a warning. |
| Orange-red | `+`: raises, moves with |
| Blue | `−`: lowers, moves against |
| Grey | Related, no sign |
| Purple | What an inference rests on (`derivedFrom`) |
| Inverted card | `role: "conclusion"` |
| Heavy frame, ◆ KEY (注目) | `role: "key"`: what matters most to a reader when that is not the conclusion |
| Dashed border or line | `inferred` / `uncertain`. Dotted means `abstracted`. |

In the dopa theme the meanings stay and the colours change: cyan is the focus, red `+`, blue `−`, violet the basis; the conclusion is a gold card and the key has a hot pink frame.

## The field

The composition behind the model is built from the model:

- Top-level chunks are discs (in screentone in the dark theme), parts are rings, and the conclusion is a heavy ring. They are placed by the golden angle.
- Chunks that bear on each other are joined by bands, and the conclusion's bands are heaviest. Every relation is a hairline.
- The summary is a hatched wedge from the conclusion toward the chunks it names.
- Shapes are filled even-odd, so they invert where they cross. A thin double frame closes the model's space.

Its assembly follows the knob: shattered into triangles at L0, half assembled at L1, whole at L2. Focusing a chunk traces its shapes in the composition.

## Interaction

| Action | Result |
|---|---|
| Drag the gauge's knob | Move continuously between stages; let go to settle |
| Hover or click a box on the minimap | Focus that chunk; the form and the text scroll to it |
| Click a label on the gauge | Switch to that stage at once |
| ▶ PLAY or Space | Play to the summary and back to the model: the knob moves by itself, as in dragging; again (PAUSE) to stop where it is |
| ← / → | Switch toward the text / toward the summary (from Linear, on to Slides) |
| ↑ / ↓ (at the model or a form) | Switch between A summary, B linear and C table, as they lie on the gauge |
| Hover text, a bracket, a row, a card, a point, a line, a phrase | Focus it on every layer at once, with the thread, and show its details along the bottom |
| Click | Bring the other side to it at once: a word scrolls the model to its note, a note scrolls the text to its words. Nothing is pinned. |
| Move off, or Esc | Clear the focus |
| Double click a card | Go down to its passage |
| light / dark / dopa (header) | Switch the theme. Dark is the default; a choice of light or dark is remembered in the browser. dopa turns the show on and off, and is not remembered. |

## View options

| Option | Values |
|---|---|
| `stage` | Where the knob starts: `"text"` (default), `"chunks"`, `"model"`, `"summary"`, `"linear"`, `"slides"`, `"table"` |
| `focus` | A node id to focus when the page opens, until the pointer moves onto something else |
| `theme` | The starting theme: `"dark"` (default), `"light"`, `"auto"`, `"dopa"`. The reader can still switch. A page built with `"dopa"` always opens in it. |
| `follow` | `false` stops the right side from following the text |
| `autoplay` | `false` stops the page from playing by itself when it opens (default `true`) |
| `lang` | `"ja"` / `"en"`. Defaults to `metadata.language`, then to the script of the text. |
