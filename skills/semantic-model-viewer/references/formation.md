# Formation — formation rule, animation rule, focus and expansion

What [`assets/viewer.html`](../assets/viewer.html) does in its Formation view. Keep this file in step with the template when either changes.

Formation does not show the finished model at once. It shows the structure forming: what is at the center, and what connects to it, in what order. Every motion stands for a step in that order. Nothing moves for effect.

## Formation order

The plan is computed in the page from the model at the current scale. It is a list of steps, and each step adds some nodes and relations. Elements already formed stay on screen; elements not yet formed are hidden.

### From a focus (default)

| Phase | What a step adds | Steps |
|---|---|---|
| Focus | The focus node | 1 |
| Direct relations | One relation of the focus, and the node at its other end, in text order | up to 14 (more are grouped) |
| Secondary relations | For each node reached in the previous phase: all of its remaining relations and the nodes they reach | up to 12 |
| Overall structure | Further rings; then parts not connected to the focus, each starting from its most connected node | up to 8 |
| Complete | Nothing new: everything at full strength, the camera fits the whole | 1 |

A part-of link (`parent`) counts as a relation for expansion. The focus is, in this order: `formation.focus` from the view options, the node pinned in Two Pane when switching, the first node with `role: "conclusion"`, or the most connected node (ties go to the one earlier in the text). It can be changed from the focus menu. Starting from the conclusion, the first ring is its reasons, the second ring their reasons, and so on: the structure forms the way the argument is built.

### In reading order

One step per sentence, in text order. The page cuts reading units after sentence-final punctuation and at line breaks. This sets the pace only; it is not an analysis of the text.

- A sentence adds every node whose first mention is in it.
- A relation mentioned in the sentence appears as soon as both of its ends are on screen. Otherwise it waits and appears in the first later step where both ends are there.
- A node mentioned again pulses: the same thing, met again in a new place.
- A node with no words of its own appears together with the first relation that needs it. Anything still missing appears in a final Overall step.

Use it when the order of introduction matters (narratives, procedures), or to show how a reader builds the structure while reading.

### Custom

With `formation.strategy: "custom"`, `formation.steps` gives the order: `[{"add": [ids], "caption": "…", "phase": "…"}]`. Ids are model ids and are mapped to what shows them at the current scale. Anything left out is added in a final step.

## Animation rule

| Motion | Meaning |
|---|---|
| The words light up in the text, a copy of them flies to the node's place, and the node appears | This node comes from these words |
| Members pulse, then the node condenses | A node without words of its own (abstracted, or derived from others) |
| A line grows from the node already on screen toward the new one | The expansion order: from the known to the new |
| The arrowhead and the label appear after the line has grown | The direction of the relation is part of its meaning and can differ from the expansion order |
| The node at the end of the line appears | Reached through that relation |
| A ring pulses around a node | Mentioned again (reading order) |
| This step's elements in the accent color; earlier ones dimmed; later ones absent | What is new now, against the context already built |
| The camera starts close on the focus and widens as the structure grows; in reading order it follows the current sentence; at Complete it fits everything | From the center to the overall structure |

Within a step, items start one after another (120–260 ms apart) and overlap. A relation waits until both of its ends are on screen. Up to six text-to-node flights run per step; further nodes appear in place. With `prefers-reduced-motion`, nothing flies or grows: the same steps appear directly.

## Keeping the source in view

- The current step's spans are highlighted strongly, spans already formed faintly, and the rest of the text is muted. In reading order the current sentence is in full ink.
- The text scrolls so that the current spans stay in view.
- The caption shows the phase, then the relation (`A —label（＋）→ B`) or the names of what was added (with its state when a single node with one state appears), then a quote of the words.

## Controls

| Control | Key |
|---|---|
| Play / pause | Space |
| Previous / next step | ← / → |
| Back to the start | Home |
| Show everything | End |
| Order: from a focus / in reading order | — |
| Focus node | — |
| Speed 0.5× to 4× (picked automatically so a run takes about two to three minutes) | — |
| Step list (jump to any step) | — |

Formation plays automatically when opened. It uses the current scale: at Overview it forms the large units, at Detail every node.

## View options used by Formation

`mode: "formation"` opens it first. `formation.strategy` is `"focus"`, `"reading"` or `"custom"`; `formation.focus` is a node id; `formation.steps` is the custom order; `level` sets the scale.
