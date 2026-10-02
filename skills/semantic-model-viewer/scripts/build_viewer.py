#!/usr/bin/env python3
"""Embed a Semantic Model (and optional view options) into the viewer template.

  build_viewer.py MODEL.json -o OUT.html [--view VIEW.json]
                  [--stop text|chunks|model] [--rep structure|linear|table|summary]
                  [--play] [--order notes|reading] [--focus NODE_ID]
                  [--theme dark|light|auto] [--no-follow]

The model is validated with semantic_model.py first; nothing is written while
it has errors. View options are presentation only and never change the model.
Standard library only.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import semantic_model  # noqa: E402  (shared contract tool, copied from semantic-model-builder)

TEMPLATE = HERE.parent / "assets" / "viewer.html"
BLOCK = r'(<script type="application/json" id="{id}">)(.*?)(</script>)'


def embed_json(value):
    """JSON that is safe inside a <script> element."""
    text = json.dumps(value, ensure_ascii=False, indent=1)
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def replace_block(page, block_id, value):
    pattern = re.compile(BLOCK.format(id=re.escape(block_id)), re.S)
    if not pattern.search(page):
        sys.exit(f"template has no <script id={block_id!r}> block")
    return pattern.sub(lambda m: m.group(1) + "\n" + embed_json(value) + "\n" + m.group(3), page, count=1)


STOPS = ("text", "chunks", "model")
REPS = ("structure", "linear", "table", "summary")


def check_view(view, model):
    """Return problems with the view options."""
    problems = []
    node_ids = {n["id"] for n in model["nodes"]}
    for key, allowed in (("stop", STOPS), ("rep", REPS), ("order", ("notes", "reading")), ("theme", ("dark", "light", "auto"))):
        if view.get(key) not in (None,) + allowed:
            problems.append(f"{key} must be one of {', '.join(allowed)}, not {view[key]!r}")
    if view.get("focus") is not None and view["focus"] not in node_ids:
        problems.append(f"focus {view['focus']!r} is not a node id")
    for key in ("play", "follow"):
        if key in view and not isinstance(view[key], bool):
            problems.append(f"{key} must be true or false")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--view", help="JSON file with view options")
    parser.add_argument("--stop", choices=STOPS, help="the layer it opens on (default model)")
    parser.add_argument("--rep", choices=REPS, help="the form of the model it opens on (default linear)")
    parser.add_argument("--play", action="store_true", help="play the story from the text up when it opens")
    parser.add_argument("--order", choices=["notes", "reading"], help="order in which the story wraps the chunks")
    parser.add_argument("--focus", help="node id to pin when it opens")
    parser.add_argument("--theme", choices=["dark", "light", "auto"], help="default dark")
    parser.add_argument("--no-follow", action="store_true", help="do not move the notes with the text scroll")
    parser.add_argument("--template", default=str(TEMPLATE))
    args = parser.parse_args(argv)

    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    errors, warnings = semantic_model.validate_model(model)
    for w in warnings:
        print(f"WARNING {w}")
    if errors:
        for e in errors:
            print(f"ERROR   {e}")
        sys.exit(f"{len(errors)} error(s) in {args.model}; {args.output} not written")

    view = json.loads(Path(args.view).read_text(encoding="utf-8")) if args.view else {}
    for key in ("stop", "rep", "order", "focus", "theme"):
        if getattr(args, key):
            view[key] = getattr(args, key)
    if args.play:
        view["play"] = True
    if args.no_follow:
        view["follow"] = False
    problems = check_view(view, model)
    if problems:
        for p in problems:
            print(f"ERROR   {p}")
        sys.exit(f"{args.output} not written")

    page = Path(args.template).read_text(encoding="utf-8")
    page = replace_block(page, "semantic-model", model)
    page = replace_block(page, "semantic-view", view)
    title = (model.get("metadata") or {}).get("title")
    if title:
        page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)} — Semantic Model Viewer</title>", page, count=1)
    Path(args.output).write_text(page, encoding="utf-8")
    print(f"wrote {args.output} ({len(model['nodes'])} nodes, {len(model['relations'])} relations)")


if __name__ == "__main__":
    main()
