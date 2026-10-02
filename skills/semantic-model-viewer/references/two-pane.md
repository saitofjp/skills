# Two Pane — UI, interaction, highlight and source ↔ model mapping

What [`assets/viewer.html`](../assets/viewer.html) does in its Two Pane view. Keep this file in step with the template when either changes.

Two Pane puts the source text and the Semantic Model side by side and keeps them synchronized in both directions. Its job is not to hide anything. It makes the current focus of meaning obvious, and it lets the reader go from any word to the structure and from any part of the structure back to the words.

## Layout

| Area | Content |
|---|---|
| Header | Title and source (`metadata.title`, `metadata.source`), the view switch (Two Pane / Formation), the scale control (only when the model uses `parent`) |
| Left pane | `sourceText` exactly as stored, with line breaks kept. Text that some span covers is a hover target and has a faint dotted underline. A strip on the right edge marks where the highlighted spans are in the whole text; clicking a mark scrolls there |
| Right pane | The graph. Overlays: details card (top right), legend and usage hint (bottom left), tools (follow text, zoom, fit; bottom right), chips for highlighted nodes that are outside the view |
| Narrow screens (< 860 px) | Text above, graph below |

### Colors

Each data color has one meaning, the same in the text and in the graph. Controls use a neutral ink so they never read as data.

| Color | Meaning |
|---|---|
| Yellow highlighter, ink underline / ink border | The focus: what the cursor points at, or what is pinned |
| Orange-red | `+`: moves with the focus (raises it, or is raised by it) |
| Blue | `−`: moves against the focus (lowers it, or is lowered by it) |
| Grey | Related without a sign (support, condition, part) |
| Purple | What an inference rests on (`derivedFrom`) |
| Brown, dashed with "?" | `uncertain` |

Orange-red and blue were chosen so that the sign stays legible with the common forms of color blindness; the sign is also written on the edge label (＋ / −).

### Graph encoding

Every visual variable carries information. None is decoration.

| Variable | Meaning |
|---|---|
| Vertical position | Where in the text the node is discussed: the median of its mentions (its members' mentions when folded). The graph reads top to bottom like the text |
| Horizontal position | Structure: related nodes are pulled together. The layout is deterministic, so Two Pane and Formation place every node in the same spot |
| Node size and weight | How large the unit is: it grows with the number of nodes it contains (`parent`) and, slightly, with its number of relations |
| Border / line style | Provenance: solid `explicit`, dashed `inferred`, dotted (double border on nodes) `abstracted`, dashed orange with "?" `uncertain` |
| Arrowhead | Direction of the relation (`directed: false` has none) |
| Edge label | `label`, else `type`. When the current scale has more than 36 edges, labels show only for edges in focus |
| Small mono text above a label | The node's `type` (hidden when zoomed out) |
| Lines under a label | The node's `states`: when (bold) and how it stands. Up to two in the box; the hover card and the details card list all |
| Edge color | `polarity`: orange-red for `+` (raises), blue for `-` (lowers), grey without a sign. The label is prefixed with ＋ or − |
| Bold double border | `role: "conclusion"`: what the text concludes |
| Badge `+n` | Parts folded into this node at the current scale |
| Dotted grey connector | Part of (`parent`) |
| Dotted purple connector | Derived from (`derivedFrom`), shown while tracing evidence |
| Dot instead of a box | The node is too small to read at this zoom (it becomes a box again when zoomed in) |

## Source ↔ model mapping

- **Segments.** The text is cut at every span boundary. Each segment knows every element whose spans cover it. A state's spans count as spans of its node.
- **Text → model.** Hovering a segment picks the element with the smallest span covering it, preferring a node when spans tie. Small units inside a large one stay reachable this way.
- **What shows an element.** At the current scale, a node is shown by itself or by its nearest visible ancestor. A relation is shown by the edge between the visible nodes of its two ends, and several relations between the same pair share one edge. If both ends fold into the same node, that node shows it.
- **Model → text.** Focusing an element lights the spans of every element it stands for: for a folded node, its members; for a shared edge, all its relations. The spans of the exact element under the cursor are underlined.
- **Nothing is derived from the text.** The page reads `sourceText` only to display it. All structure comes from the model.

## Highlight: semantic distance

Distance is measured on the graph at the current scale. A step between a node and one of its relations counts 0.5, and a step along a part-of link counts 1.

| Distance from the focus | Example | Intensity |
|---|---|---|
| 0 | the focus itself | 100% |
| 0.5 | its relations, or the two ends of a focused relation | 80% |
| 1 | directly related nodes | 60% |
| 1.5 | their other relations | 40% |
| 2 | second-order nodes | 25% |
| more | unrelated | 0% highlight; still drawn faintly, never hidden |

- In the graph, nodes and edges fade with the intensity. The focus gets the highlighter and an ink border. Directly related nodes are outlined in the color of the sign that connects them, and edges keep their sign color. The graph shows the whole neighborhood; the text shows only where the focus is written.
- In the text, the weights are local, so that a factor mentioned twenty times does not color the whole document:

  | Spans of | Weight |
  |---|---|
  | the element under the cursor (or pinned) | 100%, underlined |
  | the relations of the focus: the words that state them | 60%, in the color of the relation's sign |
  | parts folded into the focus, and relations inside it | 30% |
  | the nodes at the other end of those relations | 25% (40% when the focus is a relation), only in sentences where the focus or one of its relations is written, in the color of the sign that connects them (grey when the relations disagree or have none) |
  | anything further away | not tinted in the text |

  A span longer than 60 characters counts at 45% of its weight, so a paragraph-sized unit does not drown the words inside it. "Sentence" here is a reading unit cut at sentence-final punctuation and line breaks, used only to keep highlights local.
- **Evidence.** If the focused element has `derivedFrom`, everything it was derived from, followed recursively, is marked purple in the graph and in the text, with dotted purple connectors. An inference can be walked back to the words it rests on.

## Interaction

| Action | Result |
|---|---|
| Hover a span in the text | Focus on its element (transient). A compact card names it |
| Hover a node or an edge | Focus on it; its spans light up in the text, and the tick strip shows where they are |
| Move away | Back to the pinned focus, or to the idle state |
| Click (text, node or edge) | Pin the focus. The full details card opens: kind, type, provenance, note, states (click one to jump to its words), every mention, derived from, basis for, part of, contains, relations, other fields. × hides the card and keeps the pin. The camera frames the focus and its neighborhood at a readable scale |
| Click the same element, click the background, or press Esc | Release the pin |
| While pinned | Hover only outlines what is under the cursor; the focus does not move, and scrolling the text does not move the camera |
| Click an item in the details card | Select that element (pin it) |
| Tab / Enter / Space | Move between nodes; pin; Esc releases |
| Scale control | Fold or unfold parts (see below) |
| Follow text (on by default above 1,500 characters) | The camera follows the part of the text on screen, and the nodes shown there get a faint fill |
| Wheel / drag / double-click | Zoom / pan / fit (any of these turns Follow text off) |
| Chip at the graph edge | Pan to a highlighted node that is out of view |
| "Form from here" (details card of a node) | Open Formation with this node as the focus |

## Scale

When the model uses `parent`, the header shows one button per depth: Overview (only nodes without a parent) up to Detail (every node). At a coarser scale, a node's parts fold into it. Relations between folded parts are drawn between the visible nodes and labelled `first label +n`. Every level has its own deterministic layout, seeded from the detailed one so positions stay comparable. Hover, pin and evidence work the same at every scale.

## View options used by Two Pane

`mode` (`"two-pane"`), `level` (number or `"detail"`), `follow` (`false` turns following off), `lang` (`"ja"` / `"en"`; defaults to `metadata.language`, then to the script of the text).
