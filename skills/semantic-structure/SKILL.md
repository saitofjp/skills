---
name: semantic-structure
description: Maps what a text means as a diagram of its meanings and how they relate, its Semantic Structure. The text is wrapped into chunks of meaning, each with a headline that says its message and the points that matter, joined by lines that say how one bears on another, every piece traced to the words it rests on. Shows the diagram beside the text as one animated HTML page that moves from the text to the structure and on to a one-sentence summary, linear notes, slides or a table. Use it whenever the user wants to see how the parts of a document or a conversation relate, structure or map it, or read a text beside its structure. With no text named, it takes this conversation or a session the user names. Triggers include "map this text", "show the semantic structure", 「意味構造を作って」「意味構造を表示して」「関係図にして」「この文章を構造化して」「この会話を意味構造にして」「意味構造をドパで見せて」.
---

# Semantic Structure

Map what a text means: its meanings and how they bear on each other, as a diagram that someone who has not read the text can follow and check against its words. That diagram is the Semantic Structure, kept in `model.json`. Then show it next to the text as one page.

Make it the way a skilled reader makes notes from a text: understand what it means, then write that meaning down, with items under headings, each item a message with the points it rests on, and arrows from what leads to what the text comes to. Each item of the notes is a chunk, and each arrow drawn on them is a line; the notes with their arrows are the structure. (Linear notes are also one of the page's forms.)

- **Grasp the meaning first.** Read all of it, closely, then look over the whole; you can take in the whole text at once, so you can do both. Say to yourself, in your own words, what the text is about, what it comes to and why, and what matters most in it.
- **Write that meaning down as notes.** The text's own large divisions are clues to what it means: where they sort it, use them as the headings of the notes, and write under them what each part means. What you do not copy is the text's wording and its turn-taking; who said what goes into the points. A novice goes part by part, deletes what seems unneeded and copies the rest, so the notes keep the text's wording and its back-and-forth; a skilled reader writes what each part means in the whole (Brown & Day, 1983).
- **Ground it in the text.** Point every headline, point and line at the words it rests on, and mark what you inferred. The words check the meaning; they do not decide it.

The skill does two things:

1. **Build the structure** when the user has a text and wants to see how it holds together. Report it, then offer the page.
2. **Show the structure** when the user wants to see it. If there is no `model.json` yet, build it first; never work out the structure in the page.

## What good notes look like

Write them for someone who has not read the text. You are the one reading it, so you decide what the items are, what to call them and what to keep. This skill fixes the goal and the file format, not a procedure: what follows describes good notes, to check yours against, not steps to follow.

- **Each chunk is one message, readable at a glance.** Its headline says the message in a few words, not the topic: "2026: oil weighs, growth continues", not "Outlook for 2026". Read in order, the headlines tell the story, so a presentation can be planned from them, one chunk per section.
- **The chunks are the text's meanings, gathered as notes gather them.** Start from the text's own headings and sections, and keep them where they fit what it means (after the macrostructure of Kintsch & van Dijk, 1978); when its large divisions sort what it means, they are the top items of the notes. What plays one part in the whole is one chunk; what plays different parts is different chunks, even when it says much the same. The parts of one section sit under it as sub-items (`parent`), so the top of the notes stays a few items. Fit the size to the whole text: in a two-sentence text a chunk may be a phrase. A summary at the top of a report and the section that develops it are the same chunk, with two passages.
- **The points keep what the message rests on**: the numbers, conditions, timing, actors and reasons, so nothing important is left only in the text. An exchange within a chunk, such as one side's claim and the other's reply, goes into its points, as it would in a note.
- **The lines carry the structure.** A line is an arrow on the notes: it says what one meaning does to another (raises, is the reason for, sets the pace of, leads to), with a sign when it has one, and it runs the way the notes read, toward what the text comes to. Followed along the lines, the notes explain why the text comes to what it comes to. The order in which the text takes things up is not a line, and a connective in the text is evidence for a line, not its name. Mentioning the same thing is a clue to a relation, not the relation. A line the reader supplies is part of the structure too, marked as inferred. A chunk with no lines is a prompt to look again; background can stand alone.
- **It says what matters most.** Mark what the text concludes (`role: "conclusion"`). What matters most to a reader is not always the conclusion: a rule laid down on the way, a finding the text singles out, a turn against what came before. Mark that chunk `role: "key"`, and say in its `note` what in the text shows its weight: the space it gets, a general statement, a "however", being said although the conclusion did not need it. Give it its weight in the summary as well. A court that dismisses a claim on one ground after setting out a rule on another is the typical case: the dismissal is the conclusion, the rule is the key. Do not make the key the conclusion, and do not judge weight by anything outside the text.
- **It comes to one sentence.** `summary` says what the whole text comes to, the meaning you grasped first, and each phrase names the chunks it stands for.
- **It can be checked.** Every headline, point and line points at the words it rests on. What the text states is `explicit`. What you inferred is `inferred`, with a `note` saying why. Nothing comes from outside the text.

Look back over the notes as someone who has not read the text. Do they tell what it means, or retell what it says, part by part? Does the summary run through the central chunks? Has the first impression bent the reading of what comes later?

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
