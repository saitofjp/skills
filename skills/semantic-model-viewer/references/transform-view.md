# Transform View: the gauge, the layers, the forms and the source ↔ model mapping

What [`assets/viewer.html`](../assets/viewer.html) does. Keep this file in step with the template when either changes.

The page shows one Semantic Model together with its text. The model is the text wrapped into chunks, with headlines, points, lines between chunks and a one-sentence summary. One control moves the page: a gauge that draws the meta-structure itself.

```
L0 Text ●━━━━ L1 Chunks ●━━━━ L2 Model ◉─┬─ Linear
                                          ├─ Table
                                          └─ Summary
```

- **The trunk** (focus out / in, meta-cognition): from the text, to the text wrapped into chunks, to the model. Moving right abstracts; moving left returns to the words.
- **The branches** (transform, representation): the model's forms. They are not there at first. They grow out of the model node as the knob comes near it, because a form is a representation of the model, not of the text.

## Concept

Rise through the layers of meaning. The text is the ground. Chunks lift off it as slabs, and are listed on the right. The model floats above, in a classical, unruly geometry composed from the model itself, which lies shattered near the text and comes together as you rise.

The look is flat, as on a printed manga page: solid fills, crisp lines, screentone dots and square, panel-like cards. There is no glow, blur or soft shadow. Motion is staged but plain. Pieces move in order, settle with a slight overshoot when you let go, and then hold.

## The gauge is continuous

Drag the knob, and the page stands at any point between two neighbouring stages. Every keyed piece (a chunk's card, its number, its headline, each point) is drawn between where it is in one stage and where it is in the other. Pieces start one after another in the notes' order. Letting go settles to the nearer stage. Clicking a label, or pressing ← / →, moves the knob there by the same path.

| Segment | As the knob moves right |
|---|---|
| Text → Chunks | The text column slides aside without reflowing and tilts back for a moment. Chunks wrap one after another: the bracket draws, the slab lifts with a brief wash, and the chunk's row comes out of its passage into the list on the right. The field's shards start to assemble. |
| Chunks → Model | Rows grow into cards and take their places in the structure. Then the lines grow, from the conclusion outward through its reasons (Formation). The forms begin to grow out of the model node. |
| Model → a form | The cards turn into that form: points come out of their cards into the linear notes, drop into table cells, or the cards fly into the phrases of the one sentence. The model's lines fade with it. |

A caption band names what is happening: the chunk being wrapped, the line being drawn (`6 ← 3.3 ２％に近づいたので`), or the form. With `prefers-reduced-motion`, a click jumps straight to the stage.

## Layers

| Layer | Shows |
|---|---|
| L0 Text | `sourceText` as written, centred. The field behind it is shattered. |
| L1 Chunks | The text on the left, wrapped. A bracket in the left margin and a slab behind each passage a chunk wraps, nested by `parent` and numbered. On the right, the chunks at a glance: number and headline, parts indented. |
| L2 Model | The text on the left and the model on the right, in one of its forms. This is the Two Pane view: the text and its notes side by side, with their pointers linked. |

## Forms

| Form | What it shows |
|---|---|
| Structure (the model itself) | Top-level chunks in columns that flow toward the conclusion. A chunk's column is its distance, in lines, from the conclusion, and the conclusion sits on the right. Parts sit inside their chunk as one-line cards. Lines run between cards. The labels of lines into the conclusion are always shown; the others appear on focus. |
| Linear | The notes in their order (`nodes` order, with parts under their parent). Each card has its headline and points. Lines are arcs in the right margin. |
| Table | One row per chunk, one column per `when` value (in order of first appearance), then a column for points without `when`. |
| Summary | The `summary` sentence, large. Each phrase is underlined with the numbers of the chunks it names. Chunks the sentence does not reach are chips below it. |

## Source ↔ model mapping

- **Segments.** The text is cut at every span boundary. A segment knows every chunk, point and relation whose spans cover it.
- **Text → model.** Hovering a segment picks the element with the smallest span over it: a point or a relation comes before the chunk that contains it.
- **Model → text.** Focusing a chunk washes its passages and marks its points' words. Focusing a point marks its words strongly. Focusing a relation underlines its words in the color of its sign.
- **The thread.** A line joins the hovered words to their note, or the note to the first of its words in view. The other side scrolls to keep the counterpart in view.
- **Following.** The chunk at the middle of the text view is marked. In the chunk list and in Linear, the right side scrolls with the text.
- **Nothing is derived from the text.** The page reads `sourceText` only to display it.

## Colors

| Color | Meaning |
|---|---|
| Yellow highlighter | The focus: what the pointer is on, or what is pinned. Also the knob and the path walked on the gauge. |
| Orange-red | `+`: raises, moves with |
| Blue | `−`: lowers, moves against |
| Grey | Related, no sign |
| Purple | What an inference rests on (`derivedFrom`) |
| Inverted card, yellow bar | `role: "conclusion"` |
| Dashed border or line | `inferred` / `uncertain`. Dotted means `abstracted`. |

## The field

The composition behind the model is built from the model:

- Top-level chunks are discs in screentone, parts are rings, and the conclusion is a heavy ring. They are placed by the golden angle.
- Chunks that bear on each other are joined by bands, and the conclusion's bands are heaviest. Every relation is a hairline.
- The summary is a hatched wedge from the conclusion toward the chunks it names.
- Shapes are filled even-odd, so they invert where they cross. A thin double frame closes the model's space.

Its assembly follows the knob: shattered into triangles at L0, half assembled at L1, whole at L2. Focusing a chunk traces its shapes in the composition.

## Interaction

| Action | Result |
|---|---|
| Drag the gauge's knob | Move continuously between stages; let go to settle |
| Click a label on the gauge, ← / → | Move to that stage, or the next one |
| ↑ / ↓ (at the model) | Go to the previous or next form |
| Hover text, a bracket, a row, a card, a point, a line, a phrase | Focus it on every layer at once, with the thread |
| Click | Pin it. The details card lists its passages (click to go there), points, lines, parts and evidence. |
| Click again, click the background, or Esc | Release |
| Double click a card | Go down to its passage |

## View options

| Option | Values |
|---|---|
| `stage` | Where the knob starts: `"text"` (default), `"chunks"`, `"model"`, `"linear"`, `"table"`, `"summary"` |
| `focus` | A node id to pin |
| `theme` | `"dark"` (default), `"light"`, `"auto"` |
| `follow` | `false` stops the right side from following the text |
| `lang` | `"ja"` / `"en"`. Defaults to `metadata.language`, then to the script of the text. |
