# Transform View: the gauge, the layers, the forms and the source ↔ model mapping

What [`assets/viewer.html`](../assets/viewer.html) does. Keep this file in step with the template when either changes.

The page shows one Semantic Model together with its text. The model is the text wrapped into chunks, with headlines, points, lines between chunks and a one-sentence summary. One control moves the page: a gauge that draws the meta-structure itself.

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

The page's content starts below the HUD, and the text, centred at L0, keeps clear of it.

- **The trunk** (focus out / in, meta-cognition): the levels, from the text, to the text wrapped into chunks, to the model. Moving right abstracts; moving left returns to the words.
- **The forms** (transform, representation): the model's forms, joined to the model by straight lines: A the summary in one sentence, B linear notes (which lead on to B2 slides), C a table. The only way to a form is through the model, because a form is a representation of the model, not of the text.
- **▶** plays the way to the summary, from where the knob is (from the text again when it is already there). It moves the knob for you, so what plays is exactly what dragging shows. Space does the same; PAUSE stops the knob where it is, and dragging takes over at once.

## Concept

Rise through the layers of meaning. The text is the ground. Chunks lift off it as slabs, and are listed on the right. The model floats above, in a classical, unruly geometry composed from the model itself, which lies shattered near the text and comes together as you rise.

The look is flat, as on a printed manga page, dark by default (black paper, white ink) with a light theme a click away: solid fills, crisp lines and square, panel-like cards. The dark theme uses screentone dots; the light theme leaves them out and stays plain. There is no glow, blur or soft shadow. Motion is staged but plain. Pieces move in order, settle with a slight overshoot when you let go, and then hold.

## The gauge is continuous

Drag the knob, and the page stands at any point between two neighbouring stages. Every keyed piece (a chunk's card, its number, its headline, each point) is drawn between where it is in one stage and where it is in the other. Pieces start one after another: passages in the text's order, notes in the notes' order. Letting go settles to the nearer stage. Only dragging and ▶ move through the frames: clicking a label, or pressing an arrow key, switches to that stage at once.

| Segment | As the knob moves right |
|---|---|
| Text → Chunks | The text column slides aside without reflowing and tilts back for a moment. The passages wrap one after another, in the text's order: the bracket draws, the slab lifts with a brief wash, and the passage's row comes out of it into the list on the right. The field's shards start to assemble. |
| Chunks → Model | The structuring. Rows of the same chunk merge into its card, the cards nest their parts and take their places in the notes' order, and the numbers turn from the text's order (`07`) into the notes' (`4.1`). Then the lines grow, from the conclusion outward through its reasons (Formation). |
| Model → summary, linear or table | The model splits in two. A copy of the whole structure recedes into the corner and becomes the minimap, while its cards turn into the form: points come out of their cards into the linear notes, drop into table cells, or the cards fly into the phrases of the one sentence. |

A caption band names what is happening: the chunk being wrapped, the line being drawn (`7 ← 6 削除済みだから理由がない`), or the form. It cuts in afresh each time it changes.

## The play

▶ is the drag, played: the knob travels along the gauge by itself, through the same frames, as a steady hand would move it. It moves at a constant pace (about 0.47 s for each chunk, and 0.27 s for each line as it grows, with at least 4 s per segment) and stops for a moment at each stage. For the ruling example, the play takes about 16 seconds; the timecode in the HUD shows where it is.

Dragging and ▶ always animate, even with `prefers-reduced-motion`, because the movement is what the page shows. That setting stops only the decoration: the HUD's pulse and turning lock, the decoding readout, cut-ins and sweeps.

## Layers

| Layer | Shows |
|---|---|
| L0 Text | `sourceText` as written, centred. The field behind it is shattered. |
| L1 Chunks | The text on the left, wrapped passage by passage: a bracket in the left margin and a slab behind each passage, numbered in the text's order. On the right, a row for each passage, in the same order, with its chunk's headline. Nothing is merged, nested or moved yet: a chunk the text comes back to has a row each time. |
| L2 Model | The text on the left and the model (its structure) on the right. This is the Two Pane view: the text and its notes side by side, with their pointers linked. |
| A form | Three at once: the text on the left, the form in the centre, and the model as a minimap in the bottom-right corner, like the small map in a game. The chunks in view in the form are framed on the minimap, and the focus lights it as it lights the other two. |

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
| Teal (blue-green), with a thick outline | The focus: what the pointer is on, or what is pinned. In the text, a light wash and an underline. Also the knob and the path walked on the gauge. Not yellow: yellow reads as a warning. |
| Orange-red | `+`: raises, moves with |
| Blue | `−`: lowers, moves against |
| Grey | Related, no sign |
| Purple | What an inference rests on (`derivedFrom`) |
| Inverted card | `role: "conclusion"` |
| Heavy frame, ◆ KEY (注目) | `role: "key"`: what matters most to a reader when that is not the conclusion |
| Dashed border or line | `inferred` / `uncertain`. Dotted means `abstracted`. |

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
| Hover or click a box on the minimap | Focus or pin that chunk; the form and the text scroll to it |
| Click a label on the gauge | Switch to that stage at once |
| ▶ PLAY or Space | Play to the summary: the knob moves by itself, as in dragging; again (PAUSE) to stop where it is |
| ← / → | Switch toward the text / toward the summary (from Linear, on to Slides) |
| ↑ / ↓ (at the model or a form) | Switch between A summary, B linear and C table, as they lie on the gauge |
| Hover text, a bracket, a row, a card, a point, a line, a phrase | Focus it on every layer at once, with the thread |
| Click | Pin it. The details card (top left) lists its passages (click to go there), points, lines, parts and evidence. |
| Click again, click the background, or Esc | Release |
| Double click a card | Go down to its passage |
| Light / Dark (header) | Switch the theme. Dark is the default; the reader's choice is remembered in the browser. |

## View options

| Option | Values |
|---|---|
| `stage` | Where the knob starts: `"text"` (default), `"chunks"`, `"model"`, `"summary"`, `"linear"`, `"slides"`, `"table"` |
| `focus` | A node id to pin |
| `theme` | The starting theme: `"dark"` (default), `"light"`, `"auto"`. The reader can still switch. |
| `follow` | `false` stops the right side from following the text |
| `lang` | `"ja"` / `"en"`. Defaults to `metadata.language`, then to the script of the text. |
