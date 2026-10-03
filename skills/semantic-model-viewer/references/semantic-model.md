# Semantic Model contract (`semantic-model/1`)

The Semantic Model is the only thing `semantic-model-builder` and `semantic-model-viewer` share. The builder writes it; the viewer only reads it.

The model is a set of **notes on a text**. The text is wrapped into chunks. Each chunk becomes a note with a headline (its message) and points (what in it must not be lost). Lines between chunks say how they bear on each other, and one sentence says what the whole comes to. Every piece points back to the words it rests on.

The contract is small on purpose. It fixes what a view needs in order to draw the notes and trace them back to the text. How to chunk, what to call things, and what to keep are left to the modeler.

> This file is copied verbatim into both skills. Edit the copy in `semantic-model-builder`, then run `python3 scripts/sync_semantic_shared.py` from the repository root.

## Shape

```json
{
  "version": "semantic-model/1",
  "sourceText": "駅前の商店街では、昨年から空き店舗が増えている。…",
  "summary": [
    { "text": "商店街は、" },
    { "text": "大型店に客を奪われて空き店舗が増えたが、", "refs": ["vacancy"] },
    { "text": "家賃補助とイベントで育てる。", "refs": ["plan"] }
  ],
  "nodes": [
    { "id": "vacancy", "label": "空き店舗が増えている", "type": "現状", "provenance": "explicit",
      "sourceSpans": [{ "start": 0, "end": 50, "text": "駅前の商店街では、…流れたためだ。" }],
      "points": [
        { "label": "昨年から増加", "when": "昨年から", "sourceSpans": [{ "start": 9, "end": 23, "text": "昨年から空き店舗が増えている" }] },
        { "label": "原因：郊外の大型店に客が流れた", "sourceSpans": [{ "start": 24, "end": 46, "text": "郊外に大型店ができ、買い物客がそちらに流れた" }] }
      ] }
  ],
  "relations": [
    { "id": "vacancy-newcomers", "source": "vacancy", "target": "newcomers", "type": "enables", "label": "安く借りられる",
      "polarity": "+", "provenance": "explicit", "sourceSpans": [{ "start": 55, "end": 66, "text": "家賃が下がった空き店舗" }] }
  ],
  "metadata": { "title": "駅前商店街の空き店舗（作例）", "language": "ja" }
}
```

(Shortened.) Complete examples: [`examples/notes.model.json`](../examples/notes.model.json), a short text in three chunks, embedded in the viewer template; and [`examples/minimal.model.json`](../examples/minimal.model.json), one sentence at word scale. The contract does not fix the scale.

## Required fields

| Where | Field | Meaning |
|---|---|---|
| Document | `sourceText` | The exact text that was modeled. Line endings are `\n`. Never paraphrased or cleaned. |
| | `nodes`, `relations` | Lists (may be empty). |
| | `metadata` | Object, free-form. Use `{}` when there is nothing to record. |
| Node | `id` | Unique among **all** nodes and relations (one namespace). |
| | `label` | The headline: what this chunk says, in the language of the source. |
| | `type` | Free text: what kind of note it is (現状, 見通し, リスク, 方針, …). |
| | `provenance` | `explicit` / `inferred` / `abstracted` / `uncertain` (below). |
| | `sourceSpans` | The passage the chunk wraps (below). May be empty unless `explicit`. |
| Relation | `id`, `type`, `provenance`, `sourceSpans` | As for nodes. `type` is free text: how the two bear on each other. |
| | `source`, `target` | Node ids. Read as `source —type→ target`. |

There is no type vocabulary.

## Optional fields the viewer understands

| Field | On | Use |
|---|---|---|
| `version` | Document | `"semantic-model/1"`. |
| `points` | Node | What in the chunk must not be lost: numbers, conditions, timing, who, the reason. A list of `{ "label", "when"?, "sourceSpans", "provenance"?, "note"? }`. A point's spans are the words that say it. Its provenance defaults to its node's. `when` places the point in time; the viewer's table uses it for columns. |
| `summary` | Document | What the text comes to, in one sentence, as parts: `[{ "text", "refs"? }]`. `refs` are the node ids a phrase stands for, so each phrase leads back to its notes and from there to the text. |
| `parent` | Node | The chunk this one is part of. Nodes are numbered in their order in `nodes`, with parts under their parent (2, 2.1, 2.2). Put them in the order the notes should be read. |
| `role` | Node | `"conclusion"` marks what the text concludes. The viewer gives it the strongest card and links toward it. `"key"` marks what matters most to a reader when that is not the conclusion: a rule laid down on the way, a finding the text singles out, a turn. Say in `note` what in the text shows its weight. The viewer marks it ◆ KEY. |
| `label` | Relation | The words to show on the line (e.g. `削除済みだから理由がない`). Falls back to `type`. |
| `polarity` | Relation | `"+"` or `"-"`: the source raises or lowers the target. |
| `directed` | Relation | `false` when direction carries no meaning. Default `true`. |
| `derivedFrom` | Node, Relation | Ids of the elements this one was inferred or abstracted from. The viewer walks an inference back to the text through it. |
| `note` | Node, Relation, Point | Why: how it was inferred, what the competing readings are. |

Any other field is allowed. The viewer ignores fields it does not know.

## Provenance

| Value | Use when | Trace back through |
|---|---|---|
| `explicit` | The text states it. | `sourceSpans` (required). |
| `inferred` | It follows from the text but is not stated: an implied cause, a link the text makes only by ordering. | `sourceSpans` of the evidence and/or `derivedFrom`; `note` says how. |
| `abstracted` | A grouping made while modeling. | `derivedFrom` (required): what it groups. |
| `uncertain` | The text allows more than one reading. | `sourceSpans` of the ambiguous words; `note` gives the readings. |

When torn between `explicit` and `inferred`, choose `inferred`. The text's own hedging (「〜とみられる」) is not uncertainty in the model.

## Source spans

```json
{ "start": 12, "end": 16, "text": "原油価格" }
```

- `start` and `end` are offsets into `sourceText` in Unicode code points (Python string indices; in JavaScript use `Array.from(text)`), 0-based and end-exclusive.
- `text` is `sourceText[start:end]`. The tool writes it; validation uses it to catch drifted offsets.
- A chunk's spans are the passages it wraps. A chunk may wrap several passages, for example a summary sentence at the top of a report and the section that develops it.
- A point's spans, and a relation's, are the words that say it.

### Writing spans without counting characters

Write drafts with quotes and sentence numbers, and let `semantic_model.py resolve` turn them into offsets:

```jsonc
"sourceSpans": [{ "sentences": [31, 39] }]                 // a passage: sentences 31 to 39
"sourceSpans": [{ "sentence": 2 }]                         // one whole sentence
"sourceSpans": ["原油価格"]                                 // a quote that occurs once
"sourceSpans": [{ "quote": "原油価格", "sentence": 3 }]      // a quote inside sentence 3
"sourceSpans": [{ "quote": "原油価格", "occurrence": 2 }]    // its 2nd occurrence
```

Sentence numbers come from `semantic_model.py sentences`. Spans that already have `start`/`end` are checked, not moved. A long text can be drafted in several files; elements with the same id are merged (spans, points and `derivedFrom` are combined; for other fields the first value wins).

## What a view may and may not do

- A view never derives meaning from `sourceText`. It displays the text and highlights spans.
- A view never changes the model. Presentation choices live in a separate view config.
- A view tolerates missing optional fields, empty spans and unknown fields.

## Validation

```bash
python3 scripts/semantic_model.py validate model.json
```

Errors: a bad shape, duplicate ids, a relation endpoint that is not a node, an unknown provenance, an offset out of range or not matching its `text`, an unresolved draft span, `explicit` without spans, `abstracted` without `derivedFrom`, an unknown id in `derivedFrom` or `summary`, a `parent` that is not a node or that loops, a point without a label, a `polarity` other than `+` / `-`.

Warnings: something that cannot be traced to the text, `uncertain` without a `note`, a duplicate relation, a summary that names no node, and sentences no span touches. An untouched sentence is a prompt to check for something lost, not a quota.
