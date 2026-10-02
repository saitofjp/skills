#!/usr/bin/env python3
"""Embed a Semantic Model (and optional view options) into the viewer template.

  build_viewer.py MODEL.json -o OUT.html [--view VIEW.json]
                  [--mode two-pane|formation] [--level N|detail]
                  [--strategy focus|reading|custom] [--focus NODE_ID] [--no-follow]

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


def check_view(view, model):
    """Return problems with view options that point at the model."""
    problems = []
    node_ids = {n["id"] for n in model["nodes"]}
    all_ids = node_ids | {r["id"] for r in model["relations"]}
    if view.get("mode") not in (None, "two-pane", "formation"):
        problems.append(f"mode must be two-pane or formation, not {view['mode']!r}")
    formation = view.get("formation") or {}
    if formation.get("strategy") not in (None, "focus", "reading", "custom"):
        problems.append(f"formation.strategy must be focus, reading or custom, not {formation['strategy']!r}")
    focus = formation.get("focus")
    if focus is not None and focus not in node_ids:
        problems.append(f"formation.focus {focus!r} is not a node id")
    for k, step in enumerate(formation.get("steps") or [], 1):
        for eid in step.get("add", []):
            if eid not in all_ids:
                problems.append(f"formation.steps[{k}]: unknown id {eid!r}")
    if formation.get("strategy") == "custom" and not formation.get("steps"):
        problems.append("formation.strategy is custom but formation.steps is empty")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--view", help="JSON file with view options")
    parser.add_argument("--mode", choices=["two-pane", "formation"])
    parser.add_argument("--level", help="initial scale: 0 (overview) … N, or 'detail'")
    parser.add_argument("--strategy", choices=["focus", "reading", "custom"])
    parser.add_argument("--focus", help="node id the focus formation starts from")
    parser.add_argument("--no-follow", action="store_true", help="do not follow the text scroll in Two Pane")
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
    if args.mode:
        view["mode"] = args.mode
    if args.level is not None:
        view["level"] = "detail" if args.level == "detail" else int(args.level)
    if args.no_follow:
        view["follow"] = False
    if args.strategy or args.focus:
        view.setdefault("formation", {})
        if args.strategy:
            view["formation"]["strategy"] = args.strategy
        if args.focus:
            view["formation"]["focus"] = args.focus
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
