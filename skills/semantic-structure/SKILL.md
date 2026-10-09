---
name: semantic-structure
description: Maps what a text means as a diagram of its meanings and how they relate, its Semantic Structure. The text is wrapped into chunks of meaning, each with a headline that says its message and the points that matter, joined by lines that say how one bears on another, every piece traced to the words it rests on. Shows the diagram beside the text as one animated HTML page that moves from the text to the structure and on to a one-sentence summary, linear notes, slides or a table. Use it whenever the user wants to see how the parts of a document or a conversation relate, structure or map it, or read a text beside its structure. With no text named, it takes this conversation or a session the user names. Triggers include "map this text", "show the semantic structure", 「意味構造を作って」「意味構造を表示して」「関係図にして」「この文章を構造化して」「この会話を意味構造にして」「意味構造をドパで見せて」.
---

# Semantic Structure

Map what a text means: write it down the way a skilled reader makes notes from a text, and draw it as a diagram that someone who has not read the text can follow and check against its words. Each item of the notes is a chunk and each arrow between items is a line; the format is in [references/semantic-structure.md](references/semantic-structure.md). The result, the Semantic Structure, is kept in `model.json` and shown next to the text as one page. You decide how to write the notes.

1. **Grasp the meaning first.** Read all of it, closely, then look over the whole, and say in your own words what the text is about, what it comes to and why, and what matters most in it.
2. **Group it roughly, from the whole.** From that view, sort the text into a few large groups; where the text's own large divisions sort its meaning, use them. The groups are the top chunks of the notes.
3. **Chunk it, and check the chunks against the groups.** Within each group, say in a few words what each part means in the whole, with the points it rests on, as chunks under the group (`parent`). Do not copy the text: who said what goes into the points. Where the chunks do not fit the groups, regroup or re-cut, going back and forth until they agree.
4. **Draw the lines from the relations.** Between chunks, say what one meaning does to another, toward what the text comes to.
5. **Ground it in the text.** Every headline, point and line points at the words it rests on; what you inferred is `inferred`, with a `note` saying why.

Mark what the text concludes `role: "conclusion"`. If something else matters most to a reader, mark it `role: "key"` and say in its `note` where the text shows its weight. Say what the whole comes to in one sentence in `summary`, each phrase naming the chunks it stands for.

Read the notes back as someone who has not read the text: do they tell what it means, or retell it part by part?

The skill does two things:

1. **Build the structure** when the user has a text and wants to see how it holds together. Report it, then offer the page.
2. **Show the structure** when the user wants to see it. If there is no `model.json` yet, build it first; never work out the structure in the page.

## Build the structure

Read [references/semantic-structure.md](references/semantic-structure.md), the format of `model.json`, before writing the first draft.

**Input and output.**

- The text comes from the arguments: pasted text, a file path, or a URL.
- If none is named, the text is a conversation session: this one, unless the user names another by title, id or link. Make the source text from its dialogue as [references/conversation.md](references/conversation.md) says. If the session has nothing to map yet, ask for a text.
- Up to about ten thousand characters fits in one `model.json`; for longer texts, ask which part to take, or make one per part.
- Save the exact text to `source.txt` in the output folder, `.semantic/<YYYYMMDD>-<slug>/` unless the user names another place.
- From a PDF or a web page, keep the body text as it is. Remove only extraction debris: page numbers, running headers, and line breaks inside a sentence. Record what you removed in `metadata.source`. The spans point into this text, so never paraphrase it.

**The tool** is `scripts/semantic_structure.py` (Python 3, standard library only):

- `sentences source.txt` numbers the sentences, so a draft can say `{"sentences": [31, 39]}` for a passage, `{"sentence": 2}` for one sentence, or quote the words for a point.
- `resolve draft*.json --source source.txt -o model.json` merges drafts, turns quotes and sentence numbers into offsets, and checks the contract. It writes nothing while there are errors.
- `outline model.json` reads the structure back: the summary, then each chunk with its passages (S31–39), points and lines. Read it as someone who has not seen the text. If it retells the text part by part instead of telling what it means, or something important is missing, change the structure.
- `summary model.json` lists the evidence: every element with its quotes, everything not stated explicitly, and the sentences no span touches (a prompt to check for something lost, not a quota).

Repeat `resolve` and `outline` until `resolve` reports no errors and the outline tells someone who has not read the text what it means.

For a conversation session, `scripts/session_transcript.py` reads its transcript, shows it turn by turn and checks the excerpt word for word; see [references/conversation.md](references/conversation.md).

**Report** what the text means in a few sentences, then the path to `model.json`, the outline, and what is `inferred` or `uncertain` so the user can check it. Say which chunk is the conclusion and which is the key, and what in the text shows the key's weight; if they are the same chunk, say so. Then offer the page.

## Show the structure

The page is a fixed template, [assets/viewer.html](assets/viewer.html), filled with `model.json` by `scripts/build_viewer.py`. On the page, a gauge moves from the text through the chunks to the model, where the chunks take their places and the lines grow between them, and on to its forms. Read [references/transform-view.md](references/transform-view.md) when the user asks how a part of the page works, or before you change the template.

1. **Choose how the page opens.** These are presentation choices; they never change the structure.
   - `--stage`: where the knob starts. `text` (default) shows how the text becomes a structure; `model`, `summary`, `linear`, `slides` or `table` start there for reading and exploring.
   - `--anchor`: which way the structure runs. Leave it at `auto`. Set `end` (from the conclusion, for reasons gathering into it, such as a ruling) or `start` (from the chunks no line comes into, for a text branching out from a question) only when the picture reads the wrong way.
   - `--theme`: `dark` (default), `light`, `auto` or `dopa`. Use `dopa` for the dopagaki look, for a show to screen-record, or when the user asks for dopa or dopagaki.
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage …] [--focus ID] [--theme …] [--anchor …] [--no-autoplay]`
   It validates `model.json` and writes nothing while it has errors. Save next to `model.json` unless the user names another place. Options can also come as a JSON file with `--view`.
3. **Check** in a browser if Node and Playwright are available: `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`. It loads the page and exercises the gauge, ▶, every form, hover, the themes and a phone-width screen. Then drag slowly from the text to the model yourself: do the lines show how the text holds together, and does the summary land?
4. **Deliver** the path and how to use it:
   - It plays by itself when it opens; ▶ (or Space) plays from the text to the summary and back to the model. Drag the gauge's knob to watch every piece move; click its labels (or ← →) to switch at once; at the model, ↑ ↓ switch between the forms.
   - Hover to link the text and the structure; click to bring the other side to it. light / dark / dopa in the header switches the theme.
   - In dopa, ▶ is a show: to make a video, show the page full screen, press ▶ and screen-record it.

   If the user cannot open local files (for example in a remote session), publish the page as an Artifact. Load the `artifact-design` skill first.

## What not to do

- **Do not edit the structure to improve the picture.** If the structure is unclear, fix the structure. If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page, or hand-write a page per text.** Everything the page shows comes from `model.json`, and the template is the implementation. If you improve the template, keep [references/transform-view.md](references/transform-view.md) in step with it.
- **Commit only when the user asks.**

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the format (chunks, points, lines, summary, spans, provenance, validation).
- [references/conversation.md](references/conversation.md): a conversation session as the text.
- [references/transform-view.md](references/transform-view.md): the page (gauge, layers, forms, motion, dopa theme, source ↔ model mapping, controls, view options).
- [examples/notes.model.json](examples/notes.model.json): a short text as three chunks and three lines; the template shows it when opened as is. [examples/minimal.model.json](examples/minimal.model.json): one sentence at word scale.
- A full-size example: a ruling of the Tokyo District Court (30 September 2026, a voice actor against TikTok), about 5,000 characters in 9 chunks (three of them parts of one) and 7 lines, with a conclusion (the claim is dismissed) and a key (a voice, like a likeness, can be protected by the right of publicity). See the [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json) and the [view](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).
