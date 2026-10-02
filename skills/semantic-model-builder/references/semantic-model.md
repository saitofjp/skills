# Semantic Model contract (`semantic-model/1`)

The Semantic Model is the only thing `semantic-model-builder` and `semantic-model-viewer` share. The builder writes it; the viewer only reads it. Any future view (table, timeline, …) reads the same file.

The model describes the **subject** of a text (what it is about, how those things act on each other, what the author concludes), not the text's sentences. The text is the evidence, reached through spans.

The contract is deliberately small. It fixes what a view needs in order to draw the model and trace it back to the text. Everything about *how* to model (granularity, type names, when to abstract) is left to the modeler's judgment.

> This file is copied verbatim into both skills. Edit the copy in `semantic-model-builder`, then run `python3 scripts/sync_semantic_shared.py` from the repository root.

## Shape

```json
{
  "version": "semantic-model/1",
  "sourceText": "…原油価格上昇が、エネルギーや財を中心に価格を押し上げる…",
  "nodes": [
    { "id": "oil", "label": "原油価格", "type": "quantity", "provenance": "explicit",
      "sourceSpans": [{ "start": 120, "end": 126, "text": "原油価格上昇" }],
      "states": [
        { "when": "2026年春〜", "label": "上昇", "sourceSpans": [{ "start": 120, "end": 126, "text": "原油価格上昇" }] },
        { "when": "見通し期間終盤", "label": "緩やかに低下（前提）", "sourceSpans": [{ "start": 3510, "end": 3527, "text": "緩やかに低下していく前提としている" }] }
      ] }
  ],
  "relations": [
    { "id": "oil-raises-cpi", "source": "oil", "target": "cpi", "type": "raises", "label": "押し上げ", "polarity": "+",
      "provenance": "explicit", "sourceSpans": [{ "start": 140, "end": 145, "text": "押し上げる" }] }
  ],
  "metadata": { "title": "…", "language": "ja" }
}
```

(Offsets shortened for the example.)

A complete example is in [`examples/minimal.model.json`](../examples/minimal.model.json) (builder) or embedded in [`assets/viewer.html`](../assets/viewer.html) (viewer).

## Required fields

| Where | Field | Meaning |
|---|---|---|
| Document | `sourceText` | The exact text that was modeled. Line endings are `\n`. Never paraphrased or cleaned. |
| | `nodes`, `relations` | Lists (may be empty). |
| | `metadata` | Object, free-form. Use `{}` when there is nothing to record. |
| Node | `id` | Unique among **all** nodes and relations (one namespace). |
| | `label` | Short display text, in the language of the source. |
| | `type` | Free text: what this unit is. |
| | `provenance` | `explicit` / `inferred` / `abstracted` / `uncertain` (below). |
| | `sourceSpans` | Where the text says it (below). May be empty unless `explicit`. |
| Relation | `id`, `type`, `provenance`, `sourceSpans` | As for nodes. `type` is free text: how the two relate. |
| | `source`, `target` | Node ids. Read as `source —type→ target`. |

There is no type vocabulary. Pick the word that says it best, and reuse the same word for the same kind of thing within one model.

## Optional fields the viewer understands

| Field | On | Use |
|---|---|---|
| `version` | Document | `"semantic-model/1"`. |
| `label` | Relation | The wording to show on the edge (e.g. `押し上げ`). Falls back to `type`. |
| `directed` | Relation | `false` when direction carries no meaning. Default `true`. |
| `states` | Node | How the thing stands or changes, and when: a list of `{ "label", "when"?, "sourceSpans", "provenance"? }`. A state's provenance defaults to its node's. Use states instead of a new node per period or per sentence. |
| `polarity` | Relation | `"+"` or `"-"`: the relation raises or lowers its target. |
| `role` | Node | `"conclusion"` marks what the text concludes. The viewer starts Formation there, and `outline` reads the model from there. Other values are free. |
| `parent` | Node | The id of a larger node this one is part of in the subject: a component of an index, a measure in a policy package, a link in a mechanism. It lets one model hold several scales at once. The viewer draws a node larger the more it contains, and can fold children into their parent for an overview. Not for the document's sections. |
| `derivedFrom` | Node, Relation | Ids of the elements this one was inferred or abstracted from. The viewer uses it to walk an inference back to the text. |
| `note` | Node, Relation | Why: how it was inferred, what the competing readings are. |

Any other field is allowed (`modality`, `time`, `attributes`, `confidence`, `abstractionLevel`, …). Add one when the text needs it. The viewer shows unknown fields in its detail panel and otherwise ignores them.

## Provenance

| Value | Use when | Trace back through |
|---|---|---|
| `explicit` | The text states it. | `sourceSpans` (required): the words that state it. |
| `inferred` | It follows from the text but is not stated: a resolved reference, an implied cause, an unstated agent. | `sourceSpans` of the evidence and/or `derivedFrom` of the premises; `note` says how. |
| `abstracted` | A grouping or generalization made while modeling. The members stay in the model. | `derivedFrom` (required): the members. |
| `uncertain` | The text allows more than one reading, or it is unclear whether it says this at all. | `sourceSpans` of the ambiguous words; `note` gives the readings. |

When torn between `explicit` and `inferred`, choose `inferred`.

The text's own hedging is not uncertainty in the model. 「〜とみられる」 states an outlook explicitly: the element is `explicit`, and the hedge can be recorded in a field such as `"modality": "見通し"`.

## Source spans

```json
{ "start": 12, "end": 16, "text": "原油価格" }
```

- `start` and `end` are offsets into `sourceText`, counted in Unicode code points (Python string indices; in JavaScript use `Array.from(text)`). 0-based and end-exclusive.
- `text` is `sourceText[start:end]`. The tool writes it, and validation uses it to catch offsets that have drifted.
- One span per mention. A node mentioned three times, including through a pronoun or a paraphrase, has three spans. A state's spans are the words that state that state.
- Point a relation at the words that carry it (a verb, a particle, a connective such as 「ため」 or 「一方」), not at the whole sentence, when such words exist.

### Writing spans without counting characters

Do not count offsets by hand. In a draft, write a quote and let `semantic_model.py resolve` find it:

```jsonc
"sourceSpans": ["原油価格"]                                  // the quote occurs once
"sourceSpans": [{ "quote": "原油価格", "sentence": 3 }]       // inside sentence 3
"sourceSpans": [{ "quote": "原油価格", "occurrence": 2 }]     // its 2nd occurrence
```

Sentence numbers come from `semantic_model.py sentences`. Spans that already have `start`/`end` are checked, not moved.

A long text can be drafted in parts, one file per section. Pass all of them to `resolve`. Elements with the same id are merged: their spans and `derivedFrom` are combined, and for other fields the first value wins (a warning names any conflict).

## What a view may and may not do

- A view never derives meaning from `sourceText`. It displays the text and highlights spans; nothing more.
- A view never changes the model. View-specific choices (layout, mode, formation focus, step order) live in a separate view config.
- A view tolerates missing optional fields, empty `sourceSpans`, unknown types and unknown fields.

## Validation

```bash
python3 scripts/semantic_model.py validate model.json
```

Errors (the model is broken): bad JSON shape, duplicate ids, a relation endpoint that is not a node, an unknown provenance, an offset out of range or not matching its `text`, an unresolved draft span, `explicit` without spans, `abstracted` without `derivedFrom`, a `derivedFrom` id that does not exist, a `parent` that is not a node or that loops, a state without a label, a `polarity` other than `+` / `-`.

Warnings (look, then decide): an element or state that cannot be traced back to the text, an `uncertain` element without a `note`, a duplicate relation, and sentences that no span touches. An untouched sentence is a prompt to check for something missing. It is not a quota to fill.

`semantic_model.py outline model.json` reads the model from its conclusions and lists signs that it copies the wording rather than the meaning.
