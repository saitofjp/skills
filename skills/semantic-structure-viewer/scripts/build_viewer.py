#!/usr/bin/env python3
"""Embed a Semantic Structure (and optional view options) into the viewer template.

  build_viewer.py MODEL.json -o OUT.html [--view VIEW.json]
                  [--stage text|chunks|model|summary|linear|slides|table]
                  [--focus NODE_ID] [--theme dark|light|auto|dopa] [--no-follow] [--no-autoplay]

The model is validated with semantic_structure.py first; nothing is written while
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
import semantic_structure  # noqa: E402  (shared contract tool, copied from semantic-structure-builder)

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


STAGES = ("text", "chunks", "model", "summary", "linear", "slides", "table")
THEMES = ("dark", "light", "auto", "dopa")


def check_view(view, model):
    """Return problems with the view options."""
    problems = []
    node_ids = {n["id"] for n in model["nodes"]}
    for key, allowed in (("stage", STAGES), ("theme", THEMES)):
        if view.get(key) not in (None,) + allowed:
            problems.append(f"{key} must be one of {', '.join(allowed)}, not {view[key]!r}")
    if view.get("focus") is not None and view["focus"] not in node_ids:
        problems.append(f"focus {view['focus']!r} is not a node id")
    for key in ("follow", "autoplay"):
        if key in view and not isinstance(view[key], bool):
            problems.append(f"{key} must be true or false")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--view", help="JSON file with view options")
    parser.add_argument("--stage", choices=STAGES, help="where the gauge starts (default text)")
    parser.add_argument("--focus", help="node id to focus when it opens")
    parser.add_argument("--theme", choices=THEMES, help="default dark; dopa is the dopagaki look, and stages ▶ as a show")
    parser.add_argument("--no-follow", action="store_true", help="do not move the notes with the text scroll")
    parser.add_argument("--no-autoplay", action="store_true", help="do not play by itself when the page opens")
    parser.add_argument("--template", default=str(TEMPLATE))
    args = parser.parse_args(argv)

    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    errors, warnings = semantic_structure.validate_model(model)
    for w in warnings:
        print(f"WARNING {w}")
    if errors:
        for e in errors:
            print(f"ERROR   {e}")
        sys.exit(f"{len(errors)} error(s) in {args.model}; {args.output} not written")

    view = json.loads(Path(args.view).read_text(encoding="utf-8")) if args.view else {}
    for key in ("stage", "focus", "theme"):
        if getattr(args, key):
            view[key] = getattr(args, key)
    if args.no_follow:
        view["follow"] = False
    if args.no_autoplay:
        view["autoplay"] = False
    problems = check_view(view, model)
    if problems:
        for p in problems:
            print(f"ERROR   {p}")
        sys.exit(f"{args.output} not written")

    page = Path(args.template).read_text(encoding="utf-8")
    page = replace_block(page, "semantic-structure", model)
    page = replace_block(page, "semantic-view", view)
    title = (model.get("metadata") or {}).get("title")
    if title:
        page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)} — Semantic Structure Viewer</title>", page, count=1)
    Path(args.output).write_text(page, encoding="utf-8")
    print(f"wrote {args.output} ({len(model['nodes'])} nodes, {len(model['relations'])} relations)")


if __name__ == "__main__":
    main()
