---
name: semantic-structure-reconstructor
description: Refines a Semantic Structure (the notes semantic-structure-builder makes of a text) together with the user until the relations between its chunks are clear, then writes the text back from the notes alone and lays it beside the original, chunk by chunk, to see whether the model carries the text (text → model → text). It asks first where the flow breaks (chunks nothing before them brings in, lines that rest on an inference); then a writer who has not read the text writes it back from a brief without the text's words, and what comes back lost, added, turned the other way or weighed differently becomes the next question. Use it when the user wants to review, fix or refine a semantic structure or its notes with them, make the relations between chunks clear, rebuild or rewrite a text from its notes or model, or test whether notes capture a text (a round trip). Triggers include "refine the semantic structure with me", "rebuild the text from the notes", 「意味構造を一緒に手直しして」「関係をはっきりさせて」「ノートから元の文章を再構築して」「モデルから文章を書き戻して」.
---

# Semantic Structure Reconstructor

A model of a text is good enough when the text can be written back from it. This skill gets the model there together with the user, and shows how close it is. Make the relations between the chunks clear, write the text back from the model alone, lay it beside the original chunk by chunk, and turn each difference into a fix or a question.

```
text ──builder──▶ model ──this skill──▶ text again
                    ▲                      │
                    └── fixes, questions ◀─┘
```

[`semantic-structure-builder`](../semantic-structure-builder/SKILL.md) makes the model and [`semantic-structure-viewer`](../semantic-structure-viewer/SKILL.md) shows it. This skill changes the model with the user, and writes from it.

The model is the user's as much as yours. You find where it breaks and propose; the user decides. It stays a model of the text: a reading the user agrees with is still a reading, and the text does not come to say more because of it.

## What makes a text come back

- **A flow.** Read in order, each chunk is brought in by what comes before it: a line to an earlier chunk (a reason, a contrast, a consequence, an example), the chunk it is part of, or a `transition` when the text simply moves on (`ここから争点`). Where nothing brings a chunk in, the writer has to guess the turn, and often guesses wrong. These are the first questions.
- **Lines the user has looked at.** A line the text does not state is the modeler's reading. Show the user the words it rests on and ask. When they agree, set `confirmed: true`; it stays `inferred`. When they pick one reading of something `uncertain`, make it `inferred` and put the reading in its `note`. When they say it is wrong, change its direction, sign, type or label, or remove it.
- **Points that carry the message.** What a chunk says has to be in its headline and points: the numbers, conditions, timing, who and why. A writer cannot bring back what the notes leave in the text.
- **Weight.** The conclusion, the key and the one sentence say what matters. If the rebuilt text puts the weight somewhere else, the text has not come back.

## The tool

`scripts/reconstruct.py` in this skill's folder (Python 3, standard library only). It reads the model with `scripts/semantic_structure.py`, the contract tool the semantic skills share, and refuses a model with errors.

- `flow model.json` lists the chunks in the order the text will be written back, what brings each one in, and the questions to settle with the user (Q1, Q2, …).
- `brief model.json -o brief-1.md` writes the brief: the one sentence, then for each chunk its headline, marker, role, length in the text, what brings it in, its points and its lines, with the rules for writing at the top. It has no words of the text except those the notes use. `--style "判決文、である調"` says how the text should read; style is not meaning, and nothing checks it.
- `compare model.json rebuilt-1.md -o compare-1.md` puts each rebuilt paragraph under its passage, with the chunk's points, the writer's `[?: …]` questions, the lengths, and the numbers one side has and the other lacks:
  - in the text but nowhere in the notes: the notes left them out;
  - in a chunk's notes but not in its paragraph: the writer dropped them;
  - in the rebuilt text but in neither: the writer invented them;
  - in the rebuilt text and only in the text: did the writer see the text?

  The numbers are hints. Read the pairs.
- `diff model.before.json model.json` lists what changed: chunks, points, lines, the one sentence, the order.
- `--order text` on `flow`, `brief` and `compare` writes the text back in the order its passages come in the text instead of the order of the notes. Use the same order for all three.

To change the model, edit `model.json`, then run `python3 scripts/semantic_structure.py resolve model.json --source source.txt -o model.json`. It turns quotes and sentence numbers into offsets (`"原油価格"`, `{"sentences": [3, 4]}`), checks the contract, and writes nothing while there are errors.

The skill uses two fields of the contract that the viewer ignores:

- `transition` on a chunk: how it is brought in when no line says so.
- `confirmed: true` on a chunk, point or line: the user has checked it and agrees. Its provenance does not change.

## Files

Work in the model's folder, usually `.semantic/<YYYYMMDD>-<slug>/` from the builder, with `source.txt` next to `model.json` (if there is no `source.txt`, `resolve` uses the model's own `sourceText`). If the model is somewhere it should not change, such as a committed example, copy it into a new `.semantic/` folder first and say so. Commit only when the user asks.

| File | What it is |
|---|---|
| `model.json` | The model, refined in place. |
| `model.before.json` | The model as it was before this skill changed it. Save it before the first change. |
| `brief-<n>.md` | Round n: the brief the writer was given. |
| `rebuilt-<n>.md` | Round n: the text written back, one paragraph per chunk, each after its marker `<!-- chunk-id -->`. The markers are HTML comments, so they do not show when the Markdown is rendered. |
| `compare-<n>.md` | Round n: the original and the rebuilt text side by side. |

## Steps

1. **Find the model.** If the user has only a text, make the notes first with `semantic-structure-builder`. Save `model.before.json`.
2. **Show the flow and ask.** Run `flow`. Give the user the chunks in order in a few lines, then the questions.
   - Ask three or four at a time, those that change the most first: the gaps in the flow, then the lines, then the rest.
   - For each, give the chunks by number and headline, the words of the text that bear on it (short quotes), your proposal and the other readings. If you have a tool for multiple-choice questions, use it, with your proposal first.
   - Do not ask what the text settles. Fix that yourself and say so.
   - Ask in the user's language. The tool's output is in English; translate as you present it.
3. **Change the model** with the answers, `resolve`, and show what changed in the flow. A new line needs the words it rests on, or `inferred` with a `note` that says whose reading it is. Go back to 2 until the flow has no gaps, or until the user wants to see the text.
4. **Write it back, blind.** Run `brief`, and give the brief to a writer who has not read the text. If the writer has read it, they fill the model's gaps from memory, and the test shows nothing.
   - The best writer is a fresh subagent. Put the brief in its prompt, and nothing else (not the text, not the model file, not this conversation), and ask for the text as its reply. Save the reply as `rebuilt-<n>.md`.
   - If you cannot start one, write it yourself from the brief alone, and say in your report that the writer had read the text, so the test is weaker.
   - Do not correct the rebuilt text against the original. It shows what the model carries; correcting it hides that.
5. **Compare.** Run `compare`, read every pair, and sort what differs (below). Show the user the main differences, with the words of the text and of the rebuilt text side by side, and ask about the ones that are the model's.
6. **Go round again** from 3. Stop when every chunk comes back (its message, its points and its turn from the chunk before, in other words), when the user is content, or when what is left is not meaning. Two or three rounds are usually enough. Say what is left and why.

## Reading the comparison

Judge each pair by meaning, not wording. Before changing the model, decide whose difference it is: the model's, or the writer's.

| What you see | Whose it is | What to do |
|---|---|---|
| **Lost:** the text says it, the rebuilt text does not. | The model's if the notes do not have it. The writer's if they do, unless the point is worded so that it reads as something else. | Ask the user whether it matters; if it does, add a point. Reword a point that misleads. |
| **Added:** the rebuilt text says what the text does not. | The model's if the notes say it: a headline that overstates, an inferred line stated outright. Otherwise the writer's. | Fix the headline, the point or the line. |
| **Turned:** a chunk follows the one before differently, a "therefore" where the text has "however". | The model's: a line is missing, points the wrong way, has the wrong sign, or has a type too vague to write from. | Make the line clear with the user. This is what the skill is for. |
| **Weighed:** the minor made major, or the reverse. | The model's: the conclusion, the key, or the one sentence. | Ask the user what matters most. |
| **Asked:** a `[?: …]` in the rebuilt text. | The model's. | A question for the user, or a point. |

These do not count: wording, sentence length, rhythm, the order of the points inside a chunk, and what the notes leave out on purpose (case numbers, citations of evidence, boilerplate). If the user wants those back too, add them as points.

## Report

- The paths to `model.json` and to the last `rebuilt-<n>.md` and `compare-<n>.md`.
- What changed in the model (`diff`), in a few lines, and which changes were the user's decisions.
- Chunk by chunk, what still does not come back and why, or that everything does.
- The rebuilt text itself if it is short, or else its first chunks.
- Then offer `semantic-structure-viewer` to see the refined model.

## What not to do

- **Do not rebuild the model from scratch.** Change what the questions and the comparison show. If the chunking itself is wrong, say so and offer `semantic-structure-builder`.
- **Do not let the writer see the text**, and do not correct the rebuilt text from it.
- **Do not make the text say more.** If the user wants something in the model that the text does not say, it goes in as `inferred`, with a `note` that it is the user's; the comparison will then show it as added, as it should. Nothing becomes `explicit` because the user said it.

## Reference

- [references/semantic-structure.md](references/semantic-structure.md): the contract, shared with the builder and the viewer (chunks, points, lines, summary, spans, provenance, `transition`, `confirmed`).
- A model to try it on: the Tokyo District Court's ruling of 30 September 2026 (a voice actor against TikTok), [model](https://github.com/saitofjp/skills/blob/main/docs/semantic/tsuda-tiktok-2609.model.json). `flow` finds two chunks nothing brings in (the claim after the case, the issues after the facts) and asks about three inferences.
