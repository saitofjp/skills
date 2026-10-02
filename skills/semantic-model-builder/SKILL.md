---
name: semantic-model-builder
description: Turns a text into a Semantic Model, the understanding a careful reader takes away from it, written down as a graph. The model holds what the text is about (the things, quantities, actors and events it reasons about, each once, with how they stand and change over time), how they act on each other, and what the author concludes and on what grounds. Every element points back to the words it rests on and says whether the text states it (explicit), implies it (inferred), groups it (abstracted) or leaves it open (uncertain). It models the subject, not the sentences: it is neither a summary nor a map of the text. Use it when the user wants to understand, map, model or structure a document, see what drives what and why, extract entities and relations with their sources, or prepare input for semantic-model-viewer. Triggers include "build a semantic model of this", "map the structure of this text", "what drives what here", 「意味構造を作って」「Semantic Modelにして」「この文章を構造化して」「関係を抽出して」.
---

# Semantic Model Builder

A Semantic Model is what a careful reader understands from a text, written down. It has three parts:

- **what the text is about:** the things, quantities, actors and events it reasons about, and how each one stands and changes over time;
- **how they act on each other:** the mechanism;
- **what the author concludes, and why.**

Every piece points back to the words it rests on.

It is a model of the **subject**, not of the **text**. The text is the evidence. Its sentences, connectives and sections are how the author delivered the understanding; they are not the understanding. A model that mirrors them, with one node per phrase, one relation per 「こうしたもとで」, and the document's chapters as nodes, has captured the wording and left the reader to do the understanding.

**The test.** Read the model from its conclusion back through its reasons (`semantic_model.py outline` does this). It should explain the text to someone who has not read it, more plainly than the text itself: what is happening, what drives it, what follows. If it sounds like the text reworded sentence by sentence, start again from step 1 below.

The output is one JSON file that follows [references/semantic-model.md](references/semantic-model.md). The contract fixes only what a view needs. Everything else is your judgment.

[`semantic-model-viewer`](../semantic-model-viewer/SKILL.md) shows the file as HTML (Two Pane and Formation).

## Input

- Take the text from the arguments: pasted text, a file path, or a URL. If there is none, ask for it.
- Anything from a few sentences up to about ten thousand characters (a report of ten or so pages) fits in one model. For anything longer, ask which part to model, or build one model per part.
- Save the exact text to `source.txt` in the output folder. Unless the user names another place, use `.semantic/<YYYYMMDD>-<slug>/`. Commit only when the user asks.
- From a PDF or a web page, keep the body text as it is. Remove only extraction debris: page numbers, running headers, footnote markers, and line breaks inside a sentence (in Japanese, join the lines with no space). Record what you removed in `metadata.source`. Never paraphrase it; the spans point into this text.

## Build it in this order

Understand first, map back last. Starting from the sentences produces a model of the sentences.

1. **Say what the text says.** Read the whole text. Then, without looking back, write in a few lines what it concludes and why. This is what the model has to be able to tell. Keep it for the report; it does not go into the model.
2. **List what the text is about.** These are the things it reasons about: quantities, actors, objects, events, mechanisms. Name each once, the way a reader would name it, however many ways the text words it. Oil prices are one node whether the text says 「原油高」, 「原油価格上昇」 or 「原油価格の下落」.
3. **Give each thing its states.** How it stands and how it changes, and when: "now: near 2%", "FY2026 H2 – FY2027: consistent with the target", "risk: overshooting 2%". A state belongs to its thing (`states`); it is not a new node. Three sentences about capital spending in three periods are one node with three states.
4. **Connect them.** Say how things act on each other, in the subject's terms: raises, lowers, causes, enables, offsets, requires. Give a direction, and a sign (`polarity`) where it has one. Name the relation by what it does. A connective (「こうしたもとで」, 「踏まえると」, "therefore") is evidence that a relation exists. It is never the relation's name.
5. **Say what the author concludes.** The outlooks, judgments, risks and decisions the text argues for, as a few claim nodes. Link each to what supports it. Mark the main conclusion or conclusions with `"role": "conclusion"`.
6. **Attach the evidence.** Only now go back to the text. Give every element and every state its spans: every mention, including paraphrases and pronouns. Mark how each was obtained (`provenance`).
7. **Run the test.** Read the outline cold. Fix the model, not the outline.

## Scale

The size of a node follows the size of the text. Information is not only in small pieces. In two sentences, the units are words and phrases. In a ten-page report, they are the subjects the report reasons about and the few claims it makes. A mechanism or an argument can be a large node with its parts as children (`parent`). Use `parent` for part and whole in the subject (a price index and its components; a policy package and its measures; a mechanism and its links). Do not use it for the document's chapters.

## What does not go in

- **The document:** sections, headings, "the first pillar", "as stated in the summary". Put them in `metadata` if they matter.
- **Relations about the text:** "describes", "mentions", "examines".
- **Restatements:** a claim made in the summary and again in the body is one claim with two spans.
- **Every sentence:** framing, hedges and repetition need no element of their own. A model that touches every sentence is suspicious, not thorough.

## What never changes

- **Do not add facts the text does not contain.** Your knowledge helps you read; it is not a source. What the model asserts comes from the text: anything else is `inferred` with its basis shown, or it stays out.
- **Do not present an inference as explicit.** If in doubt, use `inferred`. If the text allows two readings, use `uncertain` and give both in `note`.
- **Do not drop meaning to make the picture tidy.** If the text says something matters, it is in the model.
- **Everything traces back.** An `explicit` element or state has spans. Anything else has spans or `derivedFrom`.

## Steps with the tool

The tool is `scripts/semantic_model.py` in this skill's folder (Python 3, standard library only).

1. `python3 scripts/semantic_model.py sentences source.txt`: numbers the sentences. Use it to locate quotes, not to drive the model.
2. Write `draft.json` with `nodes` (with `states`), `relations` and `metadata`, and without `sourceText`. Write spans as quotes: `"sourceSpans": ["原油高"]`. When a quote repeats, add the sentence number: `{"quote": "原油高", "sentence": 3}`. A long text can be drafted in several files that reuse the same ids; they are merged.
3. `python3 scripts/semantic_model.py resolve draft*.json --source source.txt -o model.json`: merges the drafts, turns quotes into offsets and checks the contract. It writes nothing while there are errors.
4. `python3 scripts/semantic_model.py outline model.json`: the test. It reads the model from its conclusions and lists signs of modeling the words (connectives as relation names, relations about the text, document-structure nodes, one subject split over several nodes). Compare the outline with what you wrote in step 1 of "Build it in this order".
5. `python3 scripts/semantic_model.py summary model.json`: checks the evidence. It lists every element and state with its quotes, everything not stated explicitly, and the sentences no span touches. For each untouched sentence, ask whether it says something the model lacks; most will be framing or repetition.
6. **Report.** Give the path to `model.json`, the few lines from step 1, the outline, the counts by provenance, and the list of what is not stated in the text, which the user should check. Offer `semantic-model-viewer` to look at it.

## Reference

- [references/semantic-model.md](references/semantic-model.md): the contract (fields, states, provenance, spans, validation).
- [examples/minimal.model.json](examples/minimal.model.json): 「AはBを使ってCした。DはCに影響した。」 as a model, with one inferred relation.
- A full-size example: the Bank of Japan's Outlook Report (July 2026), Basic View, about 9,000 characters. See the [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/boj-outlook-2607.model.json) and the [view](https://saitofjp.github.io/skills/semantic/boj-outlook-2607.html).
