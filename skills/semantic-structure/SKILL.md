---
name: semantic-structure
description: Maps what a text means as a diagram of chunks of meaning joined by lines that say how one bears on another, its Semantic Structure, every piece traced to the words it rests on. Shows it beside the text as one animated HTML page that also turns it into a one-sentence summary, notes, slides or a table. Use it whenever the user wants to see how the parts of a document or a conversation relate, or to structure or map a text; with no text named, it takes this conversation or a session the user names, and can keep that map up to date as the session goes on, showing what holds now. Triggers include "map this text", "show the semantic structure", 「意味構造を作って」「関係図にして」「この文章を構造化して」「この会話を意味構造にして」「意味構造を更新して」「意味構造をドパで見せて」.
# Claude Code: keeps a session's structure up to date in the background, only once .semantic/*/auto.json is written
# for the session (see "Keep it up to date by itself" in references/conversation.md). Does nothing otherwise.
hooks:
  Stop:
    - hooks:
        - type: command
          async: true
          command: >-
            [ -z "$SEMANTIC_STRUCTURE_AUTO" ] && ls "${CLAUDE_PROJECT_DIR:-.}"/.semantic/*/auto.json >/dev/null 2>&1 &&
            python3 -c 'import glob, json, os, subprocess, sys; d = sys.stdin.read();
            [subprocess.run([sys.executable, os.path.join(json.load(open(f))["skill"], "scripts", "auto_update.py"), f], input=d, text=True)
            for f in glob.glob(os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".semantic", "*", "auto.json"))]'; exit 0
---

# Semantic Structure

Structure what a text means the way notes are made: the text is broken into chunks of meaning, each an item of the notes, and the relations between items are the lines. From every item you can trace back to the words of the text it rests on. This is the Semantic Structure, kept in `model.json` and shown next to the text as one page; the format is in [references/semantic-structure.md](references/semantic-structure.md). You decide how to write the notes.

1. **Grasp the meaning first.** Read all of it, closely, then look over the whole, and say in your own words what the text is about, what it comes to and why, and what matters most in it.
2. **Group it roughly, from the whole.** From that view, sort the text into a few large groups; where the text's own large divisions sort its meaning, use them. The groups are the top chunks of the notes.
3. **Chunk it, and check the chunks against the groups.** Within each group, say in a few words what each part means in the whole, with the points it rests on, as chunks under the group (`parent`); do not copy the text. Split or merge by the part each plays in the whole: parts that bear differently on the rest are separate chunks; parts that play one part are one chunk, with their differences in its points. Where the chunks do not fit the groups, regroup or re-cut, going back and forth until they agree.
4. **Draw the lines from the relations.** Between chunks, say what one meaning does to another, toward what the text comes to.
5. **Ground it in the text.** Every headline, point and line points at the words it rests on; what you inferred is `inferred`, with a `note` saying why.

Mark what the text concludes `role: "conclusion"`. If something else matters most to a reader, mark it `role: "key"` and say in its `note` where the text shows its weight. Give it its weight in the summary, and in the headline of the group it sits in. Say what the whole comes to in one sentence in `summary`, each phrase naming the chunks it stands for.

Read the notes back as someone who has not read the text: do they tell what it means, or retell it part by part?

The skill does three things:

1. **Build the structure** when the user has a text and wants to see how it holds together. Report it, then offer the page.
2. **Update the structure** when the conversation it maps goes on: add the new turns without re-cutting, so it shows what holds now.
3. **Show the structure** when the user wants to see it. If there is no `model.json` yet, build it first; never work out the structure in the page.

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
- `append model.json draft.json --source source.txt -o model.json` adds chunks and lines for text added at the end of the source, without re-cutting; with `--check` in place of `-o` it writes nothing and reads back what would hold after it. `sentences source.txt --after model.json` numbers only the added sentences.
- `state model.json` reads back what holds now, for a model whose lines replace, reject or answer earlier chunks (`move`): the chunks in force with what each took out, the open questions, what is out and why, and the signs that a full review is due.

Repeat `resolve` and `outline` until `resolve` reports no errors and the outline tells someone who has not read the text what it means.

For a conversation session, `scripts/session_transcript.py` reads its transcript, shows it turn by turn and checks the excerpt word for word; see [references/conversation.md](references/conversation.md).

**Report** what the text means in a few sentences, then the path to `model.json`, the outline, and what is `inferred` or `uncertain` so the user can check it. Say which chunk is the conclusion and which is the key, and what in the text shows the key's weight; if they are the same chunk, say so. For a model with `move`, say from `state` what was set aside and what is still open. Then offer the page.

## Update the structure

A conversation moves on: it corrects itself, sets options aside and answers its questions. Map those moves as lines with `move` (`replaces`, `rejects`, `answers`) and mark questions `question: true`; the page and `state` then show what holds now (the chunks in force, what was set aside and why, the open questions) instead of the order it was said in. See [references/conversation.md](references/conversation.md#the-structure-of-a-conversation).

When the user asks to update the structure of a session that has gone on, follow "Update the structure" in [references/conversation.md](references/conversation.md#update-the-structure). In short: add the new turns' excerpt at the end of `source.txt`; draft only what they add, with a line carrying `move` wherever they change what the model holds; say again where the session ends up (the summary, and the conclusion if it moved); read back what would hold with `append --check`, then `append`; rebuild the page. Never re-cut in an update. Rebuild from the whole only when the user asks to sum up, or when `state` reports a sign and the user agrees ("Review the whole" in the same file).

**Keep it up to date by itself** (Claude Code only; an option). When the user asks for it, say that each update is a separate Claude run on their account, then write `auto.json` in the output folder, which must be under the project's `.semantic/`:

```json
{"session": "${CLAUDE_SESSION_ID}", "skill": "${CLAUDE_SKILL_DIR}", "every": 3, "tz": "+09:00", "model": null, "view": []}
```

`every` is how many turns the user types between updates; `tz` is their UTC offset; `model` names the model for the updates (`null` for the default); `view` lists the `build_viewer.py` options the page was built with. From then on, the `Stop` hook in this skill's frontmatter updates the structure in the background every `every` turns and reports at the next turn; tell the user then in one line, and republish the page if it was published as an Artifact. Delete `auto.json` to stop. How it works, and what the update may do: "Keep it up to date by itself" in [references/conversation.md](references/conversation.md#keep-it-up-to-date-by-itself).

## Show the structure

The page is a fixed template, [assets/viewer.html](assets/viewer.html), filled with `model.json` by `scripts/build_viewer.py`. On the page, a gauge moves from the text through the chunks to the model, where the chunks take their places and the lines grow between them, and on to its forms. Read [references/transform-view.md](references/transform-view.md) when the user asks how a part of the page works, or before you change the template.

1. **Choose how the page opens.** These are presentation choices; they never change the structure.
   - `--stage`: where the knob starts. `text` (default) shows how the text becomes a structure; `model`, `summary`, `linear`, `slides` or `table` start there for reading and exploring.
   - `--anchor`: which way the structure runs. Leave it at `auto`. Set `end` (from the conclusion, for reasons gathering into it, such as a ruling) or `start` (from the chunks no line comes into, for a text branching out from a question) only when the picture reads the wrong way.
   - `--theme`: `dark` (default), `light`, `auto` or `dopa`. Use `dopa` for the dopagaki look, for a show to screen-record, or when the user asks for dopa or dopagaki.
   - `--state`: for a model with `move`, `now` (default) opens on what holds now, `all` on everything with what is out struck. The reader can switch in the header.
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html [--stage …] [--focus ID] [--theme …] [--anchor …] [--state …] [--no-autoplay]`
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
- [references/conversation.md](references/conversation.md): a conversation session as the text, its updates, the review, and the option to keep it up to date by itself.
- [references/transform-view.md](references/transform-view.md): the page (gauge, layers, forms, motion, dopa theme, source ↔ model mapping, controls, view options).
- [examples/notes.model.json](examples/notes.model.json): a short text as three chunks and three lines; the template shows it when opened as is. [examples/minimal.model.json](examples/minimal.model.json): one sentence at word scale. [examples/session.model.json](examples/session.model.json): three exchanges of a conversation, built from the first two and updated with the third, in which a decision replaces the candidates, answers the question and leaves a new one open.
- A full-size example: a ruling of the Tokyo District Court (30 September 2026, a voice actor against TikTok), about 5,000 characters in 13 chunks and 11 lines, with a conclusion (the claim is dismissed) and a key (a voice, like a likeness, can be protected by the right of publicity). See the [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json) and the [view](https://saitofjp.github.io/skills/semantic/tsuda-tiktok-2609.html).
