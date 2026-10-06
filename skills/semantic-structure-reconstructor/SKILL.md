---
name: semantic-structure-reconstructor
description: Reconstructs a text from its Semantic Structure (the notes semantic-structure-builder makes of a text or a conversation), in the flow the notes make clear. First it works through the model with the user until the relations between its chunks are clear (how each chunk follows from what comes before, which lines the text only implies, what the conclusion and the key are, in what order they go). Then it uses the model as a blueprint and writes the text again, one paragraph per chunk, taking the order, the turns and the weight from the model and the facts and wording from the original, and checks that every point is carried and nothing is added. Use it when the user wants to rebuild, rewrite or restructure a text or a conversation from its semantic structure or notes, make the relations between its parts clear with them, or turn notes back into a clear text. Triggers include "reconstruct the text from the model", "rewrite this along its structure", 「意味構造から文章を再構築して」「関係をはっきりさせて書き直して」「ノートから文章に戻して」「この会話を文章に再構築して」.
---

# Semantic Structure Reconstructor

Reconstruct a text from its semantic structure. The model says what the text means: its chunks, what each one says, how they bear on each other, and what it all comes to. Work through it with the user until the relations are clear, then write the text again in that flow. The content stays the same, but every chunk is in its place and every turn is said.

```
text ──builder──▶ model ──refined with the user──▶ blueprint ──▶ the text, reconstructed
```

The model is the blueprint. The order, the turns and the weight come from it; the facts and the wording come from the original. [`semantic-structure-builder`](../semantic-structure-builder/SKILL.md) makes the model and [`semantic-structure-viewer`](../semantic-structure-viewer/SKILL.md) shows it. This skill changes it with the user and writes from it. The text can be a conversation: the builder makes notes of a conversation session, and this skill turns them into a text that says what the conversation came to, in its flow.

The model is the user's as much as yours. You find where the flow breaks and propose; the user decides.

## What a reconstructed text does

- **It goes in the flow of the notes.** Read in order, each chunk is brought in by what comes before it: a line to an earlier chunk (a reason, a contrast, a consequence, an example), the chunk it is part of, or a `transition` when the text simply moves on (`ここから争点`). Where nothing brings a chunk in, the text cannot say why it comes there. Settle that with the user before you write.
- **It says the turns.** A line the original states, or one the user has confirmed, is said in the text, so the reader sees why each part comes where it does. A line the original only implies, and nobody has confirmed, is carried by the order, not stated. What is `uncertain` stays open.
- **It keeps the facts.** Every point of the notes is in it, with the numbers, dates, names and conditions exactly as the original has them. It adds nothing that neither the notes nor the original says.
- **It puts the weight where the notes put it.** The conclusion and the key get the room and the place they need, and the key does not disappear behind the conclusion. The whole comes to the one sentence of the summary.

## The tool

`scripts/reconstruct.py` in this skill's folder (Python 3, standard library only). It reads the model with `scripts/semantic_structure.py`, the contract tool the semantic skills share, and refuses a model with errors.

- `flow model.json` lists the chunks in the order of the notes, what brings each one in, and the questions to settle with the user (Q1, Q2, …).
- `blueprint model.json --style "…" -o blueprint.md` writes the plan of the text. The rules for writing come first, then the one sentence, then each chunk: its marker, headline, role, length in the original, what brings it in, its points, its lines, and its passage of the original as the material. `--style` says whom the text is for and how it should read (its form, register and length). It goes in the blueprint, never in the model.
- `check model.json draft.md -o check.md` puts each paragraph of the draft under its chunk's points, with its passage of the original. It lists the chunks that are missing or out of order, the numbers in a chunk's notes that its paragraph lacks, the numbers from neither the notes nor the original, the `[?: …]` still open, and the lengths. The numbers are hints. Read the paragraphs.
- `export draft.md -o reconstructed.md` writes the text without its chunk markers, and warns about any `[?: …]` still open.
- `diff model.before.json model.json` lists what changed in the model: chunks, points, lines, the one sentence, the order.

To change the model, edit `model.json`, then run `python3 scripts/semantic_structure.py resolve model.json --source source.txt -o model.json`. It turns quotes and sentence numbers into offsets (`"原油価格"`, `{"sentences": [3, 4]}`), checks the contract, and writes nothing while there are errors.

The skill uses two fields of the contract that the viewer ignores:

- `transition` on a chunk: how it is brought in when no line says so.
- `confirmed: true` on a chunk, point or line: the user has checked it and agrees. Its provenance does not change, but the text may now say it.

## Files

Work in the model's folder, usually `.semantic/<YYYYMMDD>-<slug>/` from the builder, with `source.txt` next to `model.json` (if there is no `source.txt`, `resolve` uses the model's own `sourceText`). If the model is somewhere it should not change, such as a committed example, copy it into a new `.semantic/` folder first and say so. Commit only when the user asks.

| File | What it is |
|---|---|
| `model.json` | The model, refined in place. |
| `model.before.json` | The model before this skill changed it. Save it before the first change. |
| `blueprint.md` | The plan of the text. |
| `draft.md` | The text as it is written: each chunk's paragraph after its marker, `<!-- chunk-id -->` on a line of its own. |
| `check.md` | The draft checked against the blueprint. |
| `reconstructed.md` | The reconstructed text, without markers. This is what the user gets. |

## Steps

1. **Find the model.** If the user has only a text or a conversation, make the notes first with `semantic-structure-builder`. Save `model.before.json`. If it is not clear, ask whom the text is for and how it should read: for the original's readers or plainer, prose or with headings, how long. That becomes `--style`.
2. **Shape the flow with the user.** Run `flow`. Give the user the chunks in order in a few lines, then the questions.
   - Ask three or four at a time, those that change the text most first: the gaps in the flow, then the lines, then the rest.
   - For each, give the chunks by number and headline, the words of the original that bear on it (short quotes), your proposal and the other readings. If you have a tool for multiple-choice questions, use it, with your proposal first.
   - Settle the order too. The text follows the notes. If the user wants another order (the conclusion first, say), move the chunks in `nodes` (parts go with their parent), and see that each chunk is still brought in.
   - Settle what to leave out. The text carries what the notes carry, so to leave something out, take it out of the notes.
   - Do not ask what the original settles. Fix that yourself and say so.
   - Ask in the user's language. The tool's output is in English; translate as you present it.
3. **Change the model** with the answers, `resolve`, and show what changed in the flow. When the user decides a relation the original does not state, add it as `inferred` and `confirmed`, with a `note` saying it is the user's reading. Go back to 2 until `flow` has no questions left, or until the user wants to see the text.
4. **Make the blueprint** with `blueprint`.
5. **Write `draft.md`** from the blueprint, chunk by chunk, in order. Write it yourself: the turns depend on what the user decided. Before each chunk, read what brings it in, so that its paragraph opens with that turn. Take the facts from the material, and keep the original's sentences where they already say it well. Where you need something the notes and the material do not give, write `[?: what is missing]` and go on.
6. **Check** with `check`, and read every paragraph against its chunk. Is the message plain? Is every point there? Does it come in as its lines say? Is the weight right, and is nothing added? Fix the draft where the writing is at fault. Where you could not write a turn, or left a `[?: …]`, the model is at fault: ask the user, fix the model, and rewrite those chunks.
7. **Export** with `export`, and show the user the text.

## Report

- The path to `reconstructed.md`, and the text itself: all of it if it is short, otherwise its beginning.
- What changed in the model (`diff`), in a few lines, and which changes were the user's decisions. Name the turns the original only implied that the text now says.
- Anything left open, and why.
- Then offer `semantic-structure-viewer` to see the refined model.

## What not to do

- **Do not add content.** The content stays the same, and the flow becomes clearer. Even a reason that seems obvious goes in only if the notes or the original give it.
- **Do not put the style in the model.** Whom the text is for and how it reads are options of the blueprint.
- **Do not make the original say more.** A relation the user decides is the user's reading. It is `inferred` and `confirmed` in the model, and the report says that the text now states it.
- **Do not rebuild the model from scratch.** Change what the questions show. If the chunking itself is wrong, say so and offer `semantic-structure-builder`.

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the contract, shared with the builder and the viewer (chunks, points, lines, summary, spans, provenance, `transition`, `confirmed`).
- A model to try it on: the Tokyo District Court's ruling of 30 September 2026 (a voice actor against TikTok), [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json). `flow` finds two chunks that nothing brings in (the claim after the case, the issues after the facts) and asks about three inferences. Reconstructed for general readers once those are settled, the ruling's 4,861 characters come back as about 2,000.
