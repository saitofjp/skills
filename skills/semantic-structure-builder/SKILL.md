---
name: semantic-structure-builder
description: Builds the Semantic Structure of a text, a model of what the text means, and writes it down as notes the way a good student turns a textbook into a notebook. The text is wrapped into chunks; each chunk gets a headline that says its message and points that keep what must not be lost (numbers, conditions, timing, who, why); lines between chunks say how they bear on each other; one sentence says what the whole comes to. Every headline, point and line points back to the words it rests on and says whether the text states it. The notes are meant to be clear enough to plan a presentation from, one chunk per section. Use it when the user wants to understand, summarize into notes, structure, or map a document, or prepare input for semantic-structure-viewer. With no text named, it takes this conversation or a session the user names. Triggers include "make notes of this", "build the semantic structure of this", "structure this text", 「ノートにまとめて」「意味構造を作って」「意味構造にして」「この文章を構造化して」「この会話を意味構造にして」.
---

# Semantic Structure Builder

Build the semantic structure of a text, a model of what it means, and write it down as the notes a good student makes from a textbook: the text wrapped into chunks, each chunk with a headline and the points that matter, lines between the chunks, and one sentence for the whole. Write them for someone who has not read the text.

You are the one reading the text, so you decide how to chunk it, what to call things and what to keep. This skill only fixes the goal and the file format. It does not prescribe a procedure.

## What good notes do

- **They are clear at a glance.** Each headline says the chunk's message in a few words, not its topic: "2026: oil weighs, growth continues", not "Outlook for 2026". The chunks, in order, tell the story. Someone could plan a presentation from them, one chunk per section, the way [`dopagaki-generator`](../dopagaki-generator/SKILL.md) plans one message per slide.
- **They keep what matters.** Points hold the numbers, conditions, timing, actors and reasons that the message depends on. Nothing important is left only in the text.
- **They show how the chunks bear on each other.** A line says what one chunk does to another (raises, is the reason for, sets the pace of), with a sign when it has one. A connective in the text is evidence for a line, not its name.
- **They say what matters most.** Mark what the text concludes (`role: "conclusion"`). What matters most to a reader is not always the conclusion: a rule laid down on the way, a finding the text singles out, a turn against what came before. Mark that chunk `role: "key"`, and say in its `note` what in the text shows its weight: the space it gets, a general statement, a "however", being said although the conclusion did not need it. Give it its weight in the summary as well. A court that dismisses a claim on one ground after setting out a rule on another is the typical case: the dismissal is the conclusion, the rule is the key. Do not make the key the conclusion, and do not judge weight by anything outside the text.
- **They come to one sentence.** `summary` says what the whole text comes to, and each phrase names the chunks it stands for.
- **They can be checked.** Every headline, point and line points at the words it rests on. What the text states is `explicit`. What you inferred is `inferred`, with a `note` saying why. Nothing comes from outside the text.

Chunk at the size the text needs. A paragraph-sized passage is often one chunk; a section with distinct parts is a chunk with parts (`parent`). In a two-sentence text, a chunk may be a phrase. A summary at the top of a report and the section that develops it are the same chunk, with two passages.

The format is [references/semantic-structure.md](references/semantic-structure.md). [`semantic-structure-viewer`](../semantic-structure-viewer/SKILL.md) shows the notes next to the text and turns them into structure, linear notes, a table or the one sentence.

## Input and output

- The text comes from the arguments: pasted text, a file path, or a URL.
- If none is named, the text is a conversation session: this one, unless the user names another by title, id or link. Make the source text from its dialogue as [references/conversation.md](references/conversation.md) says: the user's messages whole and the sentences of Claude's replies that carry each turn, copied word for word. If the session has nothing to model yet, ask for a text.
- Up to about ten thousand characters fits in one model; for longer texts, ask which part to take, or make one model per part.
- Save the exact text to `source.txt` in the output folder, `.semantic/<YYYYMMDD>-<slug>/` unless the user names another place. Commit only when the user asks.
- From a PDF or a web page, keep the body text as it is. Remove only extraction debris: page numbers, running headers, and line breaks inside a sentence. Record what you removed in `metadata.source`. The spans point into this text, so never paraphrase it.

## The tool

`scripts/semantic_structure.py` in this skill's folder (Python 3, standard library only):

- `sentences source.txt` numbers the sentences, so a draft can say `{"sentences": [31, 39]}` for a passage, `{"sentence": 2}` for one sentence, or quote the words for a point.
- `resolve draft*.json --source source.txt -o model.json` merges drafts, turns quotes and sentence numbers into offsets, and checks the contract. It writes nothing while there are errors.
- `outline model.json` reads the notes back: the summary, then each chunk with its passages (S31–39), points and lines. Read it as someone who has not seen the text. If it does not explain the text, or something important is missing, change the notes.
- `summary model.json` lists the evidence: every element with its quotes, everything not stated explicitly, and the sentences no span touches.

For a conversation session, `scripts/session_transcript.py` reads its transcript (`current`, `sessions`, `collect`), shows it turn by turn (`turns`, `dialogue`) and checks that every line of an excerpt is in the dialogue word for word (`check`). See [references/conversation.md](references/conversation.md).

When you report, give the path to `model.json`, the outline, and what is `inferred` or `uncertain` so the user can check it. Say which chunk is the conclusion and which is the key, and what in the text shows the key's weight; if they are the same chunk, say so. Then offer `semantic-structure-viewer` to see the notes, and [`semantic-structure-reconstructor`](../semantic-structure-reconstructor/SKILL.md) to refine them with the user and write the text back from them.

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the format (chunks, points, summary, spans, provenance, validation).
- [references/conversation.md](references/conversation.md): a conversation session as the text (getting the dialogue, making the excerpt, notes on a conversation).
- [examples/notes.model.json](examples/notes.model.json): a short text as three chunks with points, lines and a summary.
- [examples/minimal.model.json](examples/minimal.model.json): one sentence at word scale. The format does not fix the scale.
- A full-size example: a ruling of the Tokyo District Court (30 September 2026, a voice actor against TikTok), about 5,000 characters in 13 chunks, with a conclusion (the claim is dismissed) and a key (a voice, like a likeness, can be protected by the right of publicity). See the [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json) and the [view](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).
