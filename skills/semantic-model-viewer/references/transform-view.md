# Transform View — layers, forms, motion and the source ↔ model mapping

What [`assets/viewer.html`](../assets/viewer.html) does. Keep this file in step with the template when either changes.

The page shows one Semantic Model (a text wrapped into chunks, with headlines, points, lines between chunks and a one-sentence summary) together with its text. It moves along two axes, and every move is animated so the reader never loses their place:

- **Focus out / in** (meta-cognition): from the text, up to its chunks, up to the model. Going up abstracts; going down returns to the words.
- **Transform** (representation): at the model layer, the same notes are shown as structure, linear notes, a table or one sentence.

## Concept

Rise through the layers of meaning. The text is the ground. Chunks lift off it as slabs, each with its headline in the margin. The model floats above, in a classical, unruly geometry composed from the model itself, which lies shattered near the text and comes together as you rise. One sentence sits at the top.

The look is flat, as on a printed manga page: solid fills, crisp lines, screentone dots, square panel-like cards. No glow, blur or soft shadow. Motion has staging but no gimmicks: things enter fast, overshoot slightly and settle, then hold. Cut-ins, like those of an anime opening, mark the chunks as they are wrapped; nothing shakes or flashes.

## Layers (Focus)

| Layer | Shows |
|---|---|
| L0 Text | `sourceText`, as written, centered. The field behind it is shattered. |
| L1 Chunks | The text wrapped: a bracket in the left margin and a slab behind each passage a chunk wraps (nested by `parent`, numbered), and the headline as a tag in the right margin next to its passage. |
| L2 Model | Text on the left (with brackets and numbers) and the model on the right, in one of four forms. This is the Two Pane view: the text and its notes side by side, with their pointers linked. |

Rising: the text column slides aside without reflowing and tilts back for a moment; tags grow into cards along an upward arc; the field's shards fly into the composition. Descending reverses it: cards shrink into their tags or passages, and the field breaks up again. ↑ / ↓ rise and descend; "Down to the text" in the details card (or a double click on a card) descends to that chunk's passage.

## Forms (Transform)

| Form | What it shows |
|---|---|
| Structure | Top-level chunks in columns that flow toward the conclusion: a chunk's column is its distance (in lines) from the conclusion, the conclusion on the right. Parts sit inside their chunk as one-line cards. Lines are drawn between cards; the labels of lines into the conclusion are always shown, the rest on focus. |
| Linear | The notes in their order (`nodes` order, parts under their parent), each card with its headline and points. Lines are arcs in the right margin. |
| Table | One row per chunk; one column per `when` value (in order of first appearance), then a column for points without `when`. |
| Summary | The `summary` sentence, large, each phrase underlined with the numbers of the chunks it names. Chunks the sentence does not reach are chips below it. |

Every piece has an identity across layers and forms: a chunk's card, its number, its headline and each point. On a change, each piece flies from where it was to where it goes, crossfading between its two looks. A piece with nowhere to go flies into its chunk (a point into its card, a part into its parent, a card into its phrase in the summary, or into its passage when the model is put away); a new piece comes out of the same place. Pieces move with a short stagger and a slight overshoot.

## The story (Formation)

▶ plays the whole move as one sequence:

1. **Text:** the text as written.
2. **Wrap:** each chunk in turn (notes order, or reading order: by first position in the text). The text scrolls to the passage, a cut-in shows the chunk's number, type and headline (top-level chunks and the conclusion large, parts small; the conclusion inverted), the bracket draws, the slab lifts and the tag comes out of the passage.
3. **Notes:** rise to the model; tags grow into the linear notes.
4. **Structure:** the notes take their places in columns.
5. **Link:** lines grow, grouped by the chunk they lead to, starting from the conclusion and moving outward through its reasons. The conclusion stamps when its reasons are in.
6. **One sentence:** the cards fly into the phrases that name them, and the phrases underline one by one.

A caption names the phase and what is happening. A slate names the form at each change. Space plays or pauses, ← → step, ⏮ returns to the start. Speed is 0.5× to 2×. With `prefers-reduced-motion`, every change is immediate.

## Source ↔ model mapping

- **Segments.** The text is cut at every span boundary. A segment knows every chunk, point and relation whose spans cover it.
- **Text → model.** Hovering a segment picks the element with the smallest span over it (a point or a relation before the chunk that contains it).
- **Model → text.** Focusing a chunk washes its passages and marks its points' words; focusing a point marks its words strongly; focusing a relation underlines its words in the color of its sign.
- **The thread.** A line joins the hovered words to their note (or the note to the first of its words in view). The other side scrolls to keep the counterpart in view.
- **Following.** At the model layer, the card of the passage at the middle of the text view is marked; in Linear, the notes scroll with the text.
- **Nothing is derived from the text.** The page reads `sourceText` only to display it.

## Colors

| Color | Meaning |
|---|---|
| Yellow highlighter | The focus: what the pointer is on, or what is pinned |
| Orange-red | `+`: raises, moves with |
| Blue | `−`: lowers, moves against |
| Grey | Related, no sign |
| Purple | What an inference rests on (`derivedFrom`) |
| Inverted card, yellow bar | `role: "conclusion"` |
| Dashed border or line | `inferred` / `uncertain`; dotted: `abstracted` |

## The field

The composition behind the model is built from the model, never decoration:

- top-level chunks are discs (in screentone), parts are rings, the conclusion is a heavy ring, placed by the golden angle;
- chunks that bear on each other are joined by bands, the conclusion's heaviest; every relation is a hairline;
- the summary is a hatched wedge from the conclusion toward the chunks it names;
- shapes are filled even-odd, so they invert where they cross; a thin double frame closes the model's space.

At L0 it is cut into triangular shards, scattered; at L1 half assembled; at L2 whole. Focusing a chunk traces its shapes in the composition. The cut-in bands carry a print of the same composition.

## Interaction

| Action | Result |
|---|---|
| Hover text, a bracket, a tag, a card, a point, a line, a phrase | Focus it on every layer at once, with the thread |
| Click | Pin; the details card lists its passages (click to go there), points, lines, parts, evidence |
| Click again, click the background, Esc | Release |
| Double click a card | Descend to its passage |
| ↑ / ↓ | Rise / descend |
| 1–4 | Structure / Linear / Table / Summary |
| Space, ← → | Play or pause the story, step |

## View options

`stop` (`"text"`, `"chunks"`, `"model"`; default `model`), `rep` (`"structure"`, `"linear"`, `"table"`, `"summary"`; default `linear`), `play` (open playing the story), `order` (`"notes"` or `"reading"`), `focus` (a node id to pin), `theme` (`"dark"` default, `"light"`, `"auto"`), `follow` (`false` stops the notes from following the text), `lang` (`"ja"` / `"en"`; defaults to `metadata.language`, then to the script of the text).
