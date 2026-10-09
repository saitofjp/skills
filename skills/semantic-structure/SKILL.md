---
name: semantic-structure
description: Makes notes on what a text means, its Semantic Structure, made of chunks with message headlines and the points that matter, lines between them and a one-sentence summary, each traced to the words it rests on. Shows them beside the text as one animated HTML page that moves from the text to the model and on to a summary, linear notes, slides or a table. Use it whenever the user wants to understand, take notes on, structure, map or visualize a document or a conversation, read a text beside its notes, or plan slides from it. With no text named, it takes this conversation or a session the user names. Triggers include "make notes of this", "structure this text", "show the semantic structure", 「ノートにまとめて」「意味構造を作って」「意味構造を表示して」「この会話を意味構造にして」「意味構造をドパで見せて」.
---

# Semantic Structure

Build the semantic structure of a text, a model of what it means, written as the notes a good student makes from a textbook, and show it next to the text as one page. The work has two halves, joined by one file, `model.json` ([references/semantic-structure.md](references/semantic-structure.md)):

1. **Build the notes** when the user has a text and wants it understood, noted or structured. Report them, then offer the view.
2. **Show the notes** when the user wants to see them. If there is no model yet, build it first; never work out the structure in the page.

## What good notes do

Write the notes for someone who has not read the text. You are the one reading it, so you decide how to chunk it, what to call things and what to keep. This skill fixes the goal and the file format, not a procedure.

- **They are clear at a glance.** Each headline says the chunk's message in a few words, not its topic: "2026: oil weighs, growth continues", not "Outlook for 2026". The chunks, in order, tell the story. Someone could plan a presentation from them, one chunk per section, the way `dopagaki-generator` plans one message per slide.
- **They keep what matters.** Points hold the numbers, conditions, timing, actors and reasons that the message depends on. Nothing important is left only in the text.
- **They show how the chunks bear on each other.** A line says what one chunk does to another (raises, is the reason for, sets the pace of), with a sign when it has one. A connective in the text is evidence for a line, not its name.
- **They say what matters most.** Mark what the text concludes (`role: "conclusion"`). What matters most to a reader is not always the conclusion: a rule laid down on the way, a finding the text singles out, a turn against what came before. Mark that chunk `role: "key"`, and say in its `note` what in the text shows its weight: the space it gets, a general statement, a "however", being said although the conclusion did not need it. Give it its weight in the summary as well. A court that dismisses a claim on one ground after setting out a rule on another is the typical case: the dismissal is the conclusion, the rule is the key. Do not make the key the conclusion, and do not judge weight by anything outside the text.
- **They come to one sentence.** `summary` says what the whole text comes to, and each phrase names the chunks it stands for.
- **They can be checked.** Every headline, point and line points at the words it rests on. What the text states is `explicit`. What you inferred is `inferred`, with a `note` saying why. Nothing comes from outside the text.

Chunk at the size the text needs. A paragraph-sized passage is often one chunk; a section with distinct parts is a chunk with parts (`parent`). In a two-sentence text, a chunk may be a phrase. A summary at the top of a report and the section that develops it are the same chunk, with two passages.

## Build the notes

**Input and output.**

- The text comes from the arguments: pasted text, a file path, or a URL.
- If none is named, the text is a conversation session: this one, unless the user names another by title, id or link. Make the source text from its dialogue as [references/conversation.md](references/conversation.md) says. If the session has nothing to model yet, ask for a text.
- Up to about ten thousand characters fits in one model; for longer texts, ask which part to take, or make one model per part.
- Save the exact text to `source.txt` in the output folder, `.semantic/<YYYYMMDD>-<slug>/` unless the user names another place.
- From a PDF or a web page, keep the body text as it is. Remove only extraction debris: page numbers, running headers, and line breaks inside a sentence. Record what you removed in `metadata.source`. The spans point into this text, so never paraphrase it.

**The tool** is `scripts/semantic_structure.py` (Python 3, standard library only):

- `sentences source.txt` numbers the sentences, so a draft can say `{"sentences": [31, 39]}` for a passage, `{"sentence": 2}` for one sentence, or quote the words for a point.
- `resolve draft*.json --source source.txt -o model.json` merges drafts, turns quotes and sentence numbers into offsets, and checks the contract. It writes nothing while there are errors.
- `outline model.json` reads the notes back: the summary, then each chunk with its passages (S31–39), points and lines. Read it as someone who has not seen the text. If it does not explain the text, or something important is missing, change the notes.
- `summary model.json` lists the evidence: every element with its quotes, everything not stated explicitly, and the sentences no span touches.

For a conversation session, `scripts/session_transcript.py` reads its transcript, shows it turn by turn and checks the excerpt word for word; see [references/conversation.md](references/conversation.md).

**Report** the path to `model.json`, the outline, and what is `inferred` or `uncertain` so the user can check it. Say which chunk is the conclusion and which is the key, and what in the text shows the key's weight; if they are the same chunk, say so. Then offer the view.

## Show the notes

The page is a fixed template, [assets/viewer.html](assets/viewer.html), filled with the model by `scripts/build_viewer.py`. What it does (the gauge from the text through the chunks to the model and its forms, ▶, the marks for the conclusion and the key, the themes) is in [references/transform-view.md](references/transform-view.md).

1. **Choose the view.** These are presentation choices; they never change the model.
   - `--stage`: where the knob starts. `text` (default) shows how the text becomes a structure; `model`, `summary`, `linear`, `slides` or `table` start there for reading and exploring.
   - `--anchor`: which way the structure runs. Leave it at `auto`. Set `end` (from the conclusion, for reasons gathering into it, such as a ruling) or `start` (from the chunks no line comes into, for a text branching out from a question) only when the picture reads the wrong way.
   - `--theme`: `dark` (default), `light`, `auto` or `dopa`. Use `dopa` for the dopagaki look, for a show to screen-record, or when the user asks for dopa or dopagaki.
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage …] [--focus ID] [--theme …] [--anchor …] [--no-autoplay]`
   It validates the model and writes nothing while it has errors. Save next to the model unless the user names another place. Options can also come as a JSON file with `--view`.
3. **Check** in a browser if Node and Playwright are available: `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`. It loads the page and exercises the gauge, ▶, every form, hover, the themes and a phone-width screen. Then drag slowly from the text to the model yourself: do the headlines read as a story, and does the summary land?
4. **Deliver** the path and how to use it:
   - It plays by itself when it opens; ▶ (or Space) plays from the text to the summary and back to the model. Drag the gauge's knob to watch every piece move; click its labels (or ← →) to switch at once; at the model, ↑ ↓ switch between the forms.
   - Hover to link the text and the notes; click to bring the other side to it. light / dark / dopa in the header switches the theme.
   - In dopa, ▶ is a show: to make a video, show the page full screen, press ▶ and screen-record it.

   If the user cannot open local files (for example in a remote session), publish the page as an Artifact. Load the `artifact-design` skill first.

## What not to do

- **Do not edit the model to improve the picture.** If the notes are unclear, fix the notes. If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page, or hand-write a page per text.** Everything the page shows comes from the model, and the template is the implementation. If you improve the template, keep [references/transform-view.md](references/transform-view.md) in step with it.
- **Commit only when the user asks.**

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the format (chunks, points, summary, spans, provenance, validation).
- [references/conversation.md](references/conversation.md): a conversation session as the text.
- [references/transform-view.md](references/transform-view.md): the page (gauge, layers, forms, motion, dopa theme, source ↔ model mapping, controls, view options).
- [examples/notes.model.json](examples/notes.model.json): a short text as three chunks; the template shows it when opened as is. [examples/minimal.model.json](examples/minimal.model.json): one sentence at word scale.
- A full-size example: a ruling of the Tokyo District Court (30 September 2026, a voice actor against TikTok), about 5,000 characters in 13 chunks, with a conclusion (the claim is dismissed) and a key (a voice, like a likeness, can be protected by the right of publicity). See the [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json) and the [view](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).
