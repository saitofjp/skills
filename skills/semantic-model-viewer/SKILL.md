---
name: semantic-model-viewer
description: Shows a Semantic Model (from semantic-model-builder) as one self-contained interactive HTML page with two views of the same model. Two Pane puts the source text and the model side by side, synchronized both ways, with highlight by semantic distance and inferences traced back to their evidence. Formation shows the model forming step by step, from a focus or in reading order, each element rising out of its words. A scale control switches between overview and detail. Use it whenever the user wants to see, explore, visualize or present a semantic model or the structure of a text, read a text next to its structure, or watch that structure form. Triggers include "show the semantic model", "two pane view", "formation animation", "visualize this model", 「Semantic Modelを表示して」「原文とモデルを並べて見せて」「意味構造の形成過程を見せて」「Two Pane / Formationで見せて」.
---

# Semantic Model Viewer

One page, two views of one Semantic Model:

- **Two Pane:** see the text and its structure at the same time. Hover a word to find its place in the structure, or a node to find its words. The highlight fades with semantic distance from the current focus, and an inference can be walked back to the evidence in the text.
- **Formation:** watch the structure form. It grows from a focus outward (focus → direct relations → related nodes → secondary relations → overall structure), or in reading order. Each node rises out of the words it came from.

Both views read the same embedded model and place every node in the same spot, so switching keeps the reader's mental map.

The page is a fixed template, [`assets/viewer.html`](assets/viewer.html). It works with any model that follows the contract ([`references/semantic-model.md`](references/semantic-model.md)) and needs no network. The page never derives meaning from the text: the model is the only source of structure.

## Input

- A Semantic Model file (`semantic-model/1`). If the user has only a text, build the model first with [`semantic-model-builder`](../semantic-model-builder/SKILL.md). Do not work out the structure here.
- What the user wants to see, if they say: a view, a scale, a starting point.

## Steps

The tool is `scripts/build_viewer.py` in this skill's folder (Python 3, standard library only).

1. **Choose how the page opens.** These are presentation choices. Make them from the model; they never change it.
   - **View:** `two-pane` to read and explore. `formation` to show how the structure builds, for example in a presentation.
   - **Formation order:** `focus` for an argument or an explanation, where something sits at the center. `reading` for a narrative or a procedure, or when the order in which things are introduced matters.
   - **Focus node:** the node the text is about. By default the page starts from the model's conclusion (`role: "conclusion"`), so the structure forms the way the argument is built. Without a conclusion, choose the claim the rest supports, or what an explanation explains; otherwise the page uses the most connected node, which is not always the center of meaning.
   - **Scale:** for a model that uses `parent`, open at the overview (level `0`). The reader unfolds detail from there.
   - **Custom order (optional):** if neither order tells the story well, write the steps yourself (see View options).
2. **Build.**
   `python3 scripts/build_viewer.py model.json -o view.html --focus <node-id> [--mode formation] [--strategy reading] [--level 0]`
   It validates the model with the same checker as the builder and writes nothing while the model has errors. Save next to the model unless the user names another place: `.semantic/<YYYYMMDD>-<slug>/view.html`. Commit only when the user asks.
3. **Check it in a browser** if Node and Playwright are available:
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   It confirms that the page loads with no console errors, that hovering a word focuses the graph, that clicking pins and opens the details card and Escape releases it, and that Formation plays to the end in both orders. Then look at the page yourself: does the overview tell the story, and does the conclusion read as the conclusion?
4. **Deliver.** Give the path and how to use it: hover, click to pin, Esc to release, the scale buttons, Follow text, and in Formation Space / ← → / Home / End. If the user cannot open local files (for example in a remote session), publish the page as an Artifact; load the `artifact-design` skill before publishing.

## View options

Pass them as flags, or as a JSON file with `--view`. They live in their own block in the page, never in the model.

```json
{
  "mode": "two-pane",
  "level": 0,
  "follow": true,
  "lang": "ja",
  "formation": {
    "strategy": "focus",
    "focus": "node-id",
    "steps": [{ "add": ["node-or-relation-id"], "caption": "…", "phase": "focus" }]
  }
}
```

`steps` is used when `strategy` is `"custom"`. `lang` defaults to `metadata.language`, then to the script of the text.

## What not to do

- **Do not edit the model to improve the picture.** If the view is misleading, fix the model with the builder. If only the presentation is wrong, change the view options.
- **Do not add text analysis to the page.** Everything the page shows comes from the model.
- **Do not hand-write a new page per text.** The template is the implementation. If you improve it, keep [`references/two-pane.md`](references/two-pane.md) and [`references/formation.md`](references/formation.md) in step with it.

## Reference

- [references/semantic-model.md](references/semantic-model.md): the input contract (shared with the builder).
- [references/two-pane.md](references/two-pane.md): UI, interaction, highlight, and source ↔ model mapping.
- [references/formation.md](references/formation.md): formation order, animation rule, focus and expansion, controls.
- [assets/viewer.html](assets/viewer.html): the template. Opened as is, it shows the minimal example 「AはBを使ってCした。DはCに影響した。」.
