#!/usr/bin/env python3
"""Write a text back from its Semantic Structure and lay it beside the original.

Part of semantic-structure-reconstructor. It uses semantic_structure.py, the contract
tool shared by the semantic skills, from the same folder. Standard library only.

  reconstruct.py flow MODEL.json [--order notes|text]
      The chunks in the order the text is written back, what brings each one in
      from what came before, and the questions to settle with the user.
  reconstruct.py brief MODEL.json [--order notes|text] [--style TEXT] [-o BRIEF.md]
      The model without the text: what a writer who has not read the text needs
      to write it back, with the rules for writing it.
  reconstruct.py compare MODEL.json REBUILT.md [--order notes|text] [-o COMPARE.md]
      The text written back next to the original, chunk by chunk, with the numbers
      one side has and the other lacks, the writer's [?: ...] questions and the lengths.
  reconstruct.py diff BEFORE.json AFTER.json [-o DIFF.md]
      What changed in the model.

--order notes (the default) writes the text back in the order of the notes;
--order text in the order the chunks' passages start in the text.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import semantic_structure as ss  # noqa: E402  (shared contract tool, copied from semantic-structure-builder)

ORDERS = ("notes", "text")
MARKER = re.compile(r"^[ \t]*<!--\s*(\S+?)\s*-->[ \t]*$", re.M)
QUESTION = re.compile(r"\[\?:\s*(.*?)\s*\]", re.S)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


# ---------------------------------------------------------------- reading order


def reading_order(model, order="notes"):
    """The chunks in the order the text is written back: [(id, number, depth)].

    notes: the order of the notes, parts under their chunk, numbered as the outline
    and the viewer number them. text: the same tree, with the chunks under each
    parent sorted by where their passages (or their parts' passages) start.
    """
    if order == "notes":
        return ss.note_order(model)
    by_id = {n["id"]: n for n in model["nodes"]}
    children, roots = {}, []
    for n in model["nodes"]:
        (children.setdefault(n["parent"], []) if n.get("parent") in by_id else roots).append(n["id"])
    first = {}

    def start(nid):
        if nid not in first:
            starts = [sp["start"] for sp in by_id[nid].get("sourceSpans") or []]
            starts += [s for s in (start(c) for c in children.get(nid, [])) if s is not None]
            first[nid] = min(starts) if starts else None
        return first[nid]

    def ordered(ids):
        keyed, last = [], -1
        for nid in ids:
            s = start(nid)
            last = s if s is not None else last      # a chunk with no passage stays after the one before it
            keyed.append((last, nid))
        return [nid for _, nid in sorted(keyed, key=lambda kv: kv[0])]

    out = []

    def walk(nid, number, depth):
        out.append((nid, number, depth))
        for k, child in enumerate(ordered(children.get(nid, [])), 1):
            walk(child, f"{number}.{k}", depth + 1)

    for k, root in enumerate(ordered(roots), 1):
        walk(root, str(k), 0)
    return out


def _merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [(s, e) for s, e in out]


def _subtract(intervals, holes):
    out = []
    for s, e in intervals:
        cur = s
        for hs, he in holes:
            if he <= cur or hs >= e:
                continue
            if hs > cur:
                out.append((cur, hs))
            cur = max(cur, he)
        if cur < e:
            out.append((cur, e))
    return out


def _chars(text):
    return sum(1 for ch in text if not ch.isspace())


def _numbers(text):
    """The numbers in a text, full-width digits folded, thousands separators dropped."""
    return {m.group().replace(",", "") for m in NUMBER.finditer(unicodedata.normalize("NFKC", text))}


def _quote(s, width=40):
    return f"「{ss._clip(s, width)}」"


class Notes:
    """A valid model read in one reading order."""

    def __init__(self, model, order="notes"):
        self.model = model
        self.text = model["sourceText"]
        self.sentences = ss.split_sentences(self.text)
        self.nodes = {n["id"]: n for n in model["nodes"]}
        self.order = reading_order(model, order)
        self.number = {nid: num for nid, num, _ in self.order}
        self.position = {nid: k for k, (nid, _, _) in enumerate(self.order)}
        self.children = {}
        for n in model["nodes"]:
            if n.get("parent") in self.nodes:
                self.children.setdefault(n["parent"], []).append(n["id"])
        self.lines = {nid: [] for nid in self.nodes}
        for r in model["relations"]:
            self.lines[r["source"]].append(r)
            if r["target"] != r["source"]:
                self.lines[r["target"]].append(r)

    def name(self, nid):
        return f"{self.number[nid]} {self.nodes[nid]['label']}"

    def other(self, r, nid):
        return r["target"] if r["source"] == nid else r["source"]

    def earlier_lines(self, nid):
        """Lines between the chunk and a chunk before it. Each line is shown once, at its later end."""
        return [r for r in self.lines[nid] if self.position[self.other(r, nid)] < self.position[nid]]

    def later_lines(self, nid):
        return [r for r in self.lines[nid] if self.position[self.other(r, nid)] > self.position[nid]]

    def descendants(self, nid):
        out = []
        for child in self.children.get(nid, []):
            out += [child] + self.descendants(child)
        return out

    def brought_in(self, nid):
        """What brings the chunk in: (parent, transition, lines to earlier chunks)."""
        n = self.nodes[nid]
        parent = n.get("parent") if n.get("parent") in self.nodes else None
        return parent, n.get("transition"), self.earlier_lines(nid)

    def own_passages(self, nid):
        """The chunk's passages without its parts' passages, as [(start, end)]."""
        own = _merge((sp["start"], sp["end"]) for sp in self.nodes[nid].get("sourceSpans") or [])
        parts = _merge((sp["start"], sp["end"]) for d in self.descendants(nid)
                       for sp in self.nodes[d].get("sourceSpans") or [])
        return [(s, e) for s, e in _subtract(own, parts) if self.text[s:e].strip()]

    def own_length(self, nid):
        return sum(_chars(self.text[s:e]) for s, e in self.own_passages(nid))

    def where(self, nid):
        spans = self.nodes[nid].get("sourceSpans") or []
        return ss._sentence_list(spans, self.sentences) or "no passage of its own"

    def arrow(self, r, nid):
        """How a line looks from one of its chunks: ← it comes in, → it goes out, — no direction."""
        if r.get("directed", True) is False:
            return "—"
        return "←" if r["target"] == nid else "→"

    def line(self, r, nid, for_writer=False):
        """A line as seen from one of its chunks: `← 2 X: label (type, +, inferred)`."""
        extra = []
        if r.get("label") and r["label"] != r["type"]:
            extra.append(r["type"])
        if r.get("polarity"):
            extra.append(r["polarity"])
        if r["provenance"] != "explicit":
            extra.append(r["provenance"])
        if r.get("confirmed") and not for_writer:
            extra.append("confirmed")
        tail = f" ({', '.join(extra)})" if extra else ""
        return f"{self.arrow(r, nid)} {self.name(self.other(r, nid))}: {r.get('label') or r['type']}{tail}"

    def mark(self, nid):
        role = self.nodes[nid].get("role")
        return "★ " if role == "conclusion" else "◆ " if role == "key" else ""


def _prov(el, default="explicit", confirmed=True):
    prov = el.get("provenance", default)
    if prov == "explicit":
        return ""
    return f" [{prov}{', confirmed' if confirmed and el.get('confirmed') else ''}]"


def _roles(notes):
    out = []
    for nid, _, _ in notes.order:
        role = notes.nodes[nid].get("role")
        if role == "conclusion":
            out.append(f"★ conclusion: {notes.name(nid)}")
        elif role == "key":
            out.append(f"◆ key: {notes.name(nid)}")
    return out


# ---------------------------------------------------------------- flow


def _ask(prov):
    if prov == "uncertain":
        return " Which reading is right? Pick one (it becomes inferred, with the reading in its note), or leave it open."
    return " Confirm it, change it, or drop it."


def _questions(notes):
    """The questions to settle with the user, flow gaps first: [(kind, subject, text)]."""
    qs = []
    previous = None
    for nid, _, _ in notes.order:
        parent, transition, lines = notes.brought_in(nid)
        if previous is not None and not (parent or transition or lines):
            parts = notes.descendants(nid)
            via = [f"{notes.number[d]} {notes.arrow(r, d)} {notes.number[notes.other(r, d)]}"
                   for d in parts for r in notes.lines[d]
                   if notes.other(r, d) not in parts and notes.position[notes.other(r, d)] < notes.position[nid]]
            text = (f"{notes.name(nid)} comes after {notes.name(previous)}, but nothing before it brings it in: "
                    f"no line to an earlier chunk, no chunk it is part of, no transition. How does it follow? "
                    f"Add a line with the words it rests on, or give it a `transition`.")
            if via:
                text += f" Only its parts are tied to what came before ({', '.join(via)})."
            qs.append(("gap", nid, text))
        previous = nid

    nodes = notes.nodes
    if not any(n.get("role") == "conclusion" for n in nodes.values()):
        qs.append(("role", None, "No chunk is marked as the conclusion (`role: \"conclusion\"`). What does the text come to?"))
    summary = notes.model.get("summary")
    if not summary:
        qs.append(("summary", None, "There is no summary. What does the whole text come to, in one sentence?"))
    else:
        named = {r for part in summary for r in part.get("refs") or []}
        for nid, _, _ in notes.order:
            if nodes[nid].get("role") == "key" and nid not in named:
                qs.append(("summary", nid, f"The key {notes.name(nid)} is not in the summary. Give it its weight there?"))

    for r in notes.model["relations"]:
        if r["provenance"] in ("inferred", "uncertain") and not r.get("confirmed"):
            later = max((r["source"], r["target"]), key=notes.position.get)
            words = " / ".join(_quote(sp["text"]) for sp in r.get("sourceSpans") or []) or "no words of the text"
            text = (f"The line {notes.name(r['source'])} → {notes.name(r['target'])}: "
                    f"{r.get('label') or r['type']} ({r['type']}{', ' + r['polarity'] if r.get('polarity') else ''}, "
                    f"{r['provenance']}). It rests on {words}.")
            if r.get("note"):
                text += f" Note: {r['note']}"
            text += _ask(r["provenance"])
            qs.append(("line", (later, r["id"]), text))

    for nid, _, _ in notes.order:
        n = nodes[nid]
        if n["provenance"] in ("inferred", "uncertain") and not n.get("confirmed"):
            text = f"The chunk {notes.name(nid)} [{n['provenance']}]."
            if n.get("note"):
                text += f" Note: {n['note']}"
            text += _ask(n["provenance"])
            qs.append(("node", nid, text))
        for k, pt in enumerate(n.get("points") or []):
            prov = pt.get("provenance", n["provenance"])
            if prov in ("inferred", "uncertain") and not pt.get("confirmed") and not n.get("confirmed"):
                text = f"The point 「{pt['label']}」 of {notes.name(nid)} [{prov}]."
                if pt.get("note"):
                    text += f" Note: {pt['note']}"
                text += _ask(prov)
                qs.append(("point", (nid, k), text))
    return qs


def flow(model, order="notes"):
    notes = Notes(model, order)
    qs = _questions(notes)
    qnum = {(kind, subject): f"Q{k}" for k, (kind, subject, _) in enumerate(qs, 1) if subject is not None}
    out = ["# Flow: the chunks in the order the text is written back", "",
           "Each chunk should be brought in by what comes before it: a line to an earlier chunk,",
           "the chunk it is part of, or a transition (↪). Where nothing brings a chunk in, a writer",
           "has to guess the turn. Each line is shown once, at its later end.", "",
           " ".join([f"{len(notes.order)} chunks in the order of the {order}, "
                     f"{len(model['relations'])} lines."] + _roles(notes)), ""]
    if model.get("summary"):
        out += ["The whole: " + "".join(part["text"] for part in model["summary"]), ""]
    out += ["## Flow", ""]
    for k, (nid, num, depth) in enumerate(notes.order):
        n = notes.nodes[nid]
        pad, inner = "    " * depth, "    " * (depth + 1)
        ask = qnum.get(("node", nid))
        out.append(f"{pad}{notes.mark(nid)}{num} {n['label']}{_prov(n)}  ({notes.where(nid)})"
                   + (f"  [{ask}]" if ask else ""))
        parent, transition, lines = notes.brought_in(nid)
        if k == 0:
            out.append(f"{inner}the text starts here")
        if parent:
            out.append(f"{inner}part of {notes.number[parent]}")
        if transition:
            out.append(f"{inner}↪ {transition}")
        for r in lines:
            ask = qnum.get(("line", (nid, r["id"])))
            out.append(f"{inner}{notes.line(r, nid)}" + (f"  [{ask}]" if ask else ""))
        if ("gap", nid) in qnum:
            out.append(f"{inner}?? nothing before it brings it in  [{qnum[('gap', nid)]}]")
        for j, pt in enumerate(n.get("points") or []):
            ask = qnum.get(("point", (nid, j)))
            if ask:
                out.append(f"{inner}- {pt['label']}{_prov(pt, n['provenance'])}  [{ask}]")
    out += ["", "## Questions for the user", ""]
    if qs:
        out += [f"Q{k}. {text}" for k, (_, _, text) in enumerate(qs, 1)]
    else:
        out.append("None: every chunk is brought in, and every line the text does not state has been confirmed.")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- brief

RULES = """\
1. Write one paragraph per chunk, in the order below; a long chunk may take a few. Put its
   marker, exactly as given (`<!-- id -->`), on a line of its own before it, and write
   nothing before the first marker. Parts (2.1, 2.2) follow their chunk.
2. Say each chunk's headline as a statement, and carry every point. Keep numbers, dates and
   names exactly as given.
3. Bring each chunk in as "Brought in by" says. `← X: words` means X does that to this chunk,
   `→ X: words` that this chunk does it to X, `— X: words` that they go together. `+` means
   raises or goes the same way, `-` lowers or goes against. `↪` is a transition: the text
   moves on. Choose your own connecting words.
4. `inferred` means the text implies it but does not say it: let the order and the context
   carry it, and do not state it outright. `uncertain` means the text can be read more than
   one way: do not settle it.
5. Give the ★ conclusion and the ◆ key the weight the text gives them. The lengths say
   roughly how much room each chunk had in the text. A chunk with no passage of its own gets
   at most a short lead-in to its parts.
6. Add nothing the notes do not say: no facts, reasons, examples or judgements of your own.
   Where you need something the notes do not give, write [?: what is missing] and go on.
7. Reply with the text only."""


def brief(model, order="notes", style=None):
    notes = Notes(model, order)
    meta = model.get("metadata") or {}
    title, language = meta.get("title"), meta.get("language")
    out = [f"# Brief: {title}" if title else "# Brief", "",
           "These are notes on a text you have not seen. Write the text back from them.", "",
           f"- Language: {language}." if language else "- Language: the language of the notes.",
           *([f"- Style: {style}"] if style else []),
           f"- Length: about {_chars(model['sourceText']):,} characters in all.",
           "- " + " ".join([f"{len(notes.order)} chunks and {len(model['relations'])} lines."] + _roles(notes)),
           "", "## How to write it", "", RULES, ""]
    if model.get("summary"):
        out += ["## The whole, in one sentence", "", "".join(part["text"] for part in model["summary"]), ""]
    out += ["## The chunks", ""]
    for k, (nid, num, _) in enumerate(notes.order):
        n = notes.nodes[nid]
        facts = [f"`<!-- {nid} -->`", n["type"]]
        if n.get("role") == "conclusion":
            facts.append("★ conclusion")
        elif n.get("role") == "key":
            facts.append("◆ key")
        length = notes.own_length(nid)
        facts.append(f"about {length:,} characters" if length else "no passage of its own")
        if n["provenance"] != "explicit":
            facts.append(n["provenance"])
        out += [f"### {notes.mark(nid)}{num} {n['label']}", "", " · ".join(facts), ""]
        parent, transition, lines = notes.brought_in(nid)
        brought = ["the text starts here"] if k == 0 else []
        if parent:
            brought.append(f"part of {notes.name(parent)}")
        if transition:
            brought.append(f"↪ {transition}")
        brought += [notes.line(r, nid, for_writer=True) for r in lines]
        out += ["Brought in by:", ""] + [f"- {b}" for b in brought or ["nothing in the notes"]] + [""]
        if n.get("points"):
            out += ["Points:", ""]
            for pt in n["points"]:
                when = f"{pt['when']}: " if pt.get("when") else ""
                out.append(f"- {when}{pt['label']}{_prov(pt, n['provenance'], confirmed=False)}")
            out.append("")
        later = notes.later_lines(nid)
        if later:
            out += ["Lines to later chunks:", ""] + [f"- {notes.line(r, nid, for_writer=True)}" for r in later] + [""]
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------- compare


def parse_rebuilt(text):
    """Split a rebuilt text at its markers: (text before the first marker, [(id, body)])."""
    parts = MARKER.split(text.replace("\r\n", "\n"))
    return parts[0].strip(), [(parts[k], parts[k + 1].strip()) for k in range(1, len(parts) - 1, 2)]


def _blockquote(text):
    return "\n".join("> " + line if line.strip() else ">" for line in text.strip().split("\n"))


def compare(model, rebuilt, order="notes"):
    notes = Notes(model, order)
    text = notes.text
    preamble, chunks = parse_rebuilt(rebuilt)
    bodies, seen, unknown, repeated = {}, [], [], []
    for cid, body in chunks:
        if cid not in notes.nodes:
            unknown.append(cid)
            continue
        if cid in bodies:
            repeated.append(cid)
            bodies[cid] += "\n\n" + body
        else:
            bodies[cid] = body
            seen.append(cid)
    missing = [nid for nid, _, _ in notes.order if nid not in bodies]
    out_of_order = seen != sorted(seen, key=notes.position.get)

    def note_words(nid):
        n = notes.nodes[nid]
        return " ".join([n["label"]] + [pt["label"] + " " + pt.get("when", "") for pt in n.get("points") or []])

    def without_questions(s):
        return QUESTION.sub(" ", s)

    passages = {nid: [text[s:e].strip() for s, e in notes.own_passages(nid)] for nid in notes.nodes}
    in_text = {nid: _numbers(" ".join(p)) for nid, p in passages.items()}
    in_notes = {nid: _numbers(note_words(nid)) for nid in notes.nodes}
    in_rebuilt = {nid: _numbers(without_questions(bodies.get(nid, ""))) for nid in notes.nodes}
    all_text, all_notes = _numbers(text), set().union(*in_notes.values()) if in_notes else set()
    asked = {nid: [q for q in QUESTION.findall(bodies.get(nid, ""))] for nid in notes.nodes}

    def nums(values):
        return ", ".join(sorted(values, key=lambda v: (len(v), v)))

    findings = {}
    totals = {"left": 0, "dropped": 0, "invented": 0, "seen": 0}
    for nid in notes.nodes:
        left = in_text[nid] - all_notes
        dropped = (in_notes[nid] - in_rebuilt[nid]) if nid in bodies else set()
        invented = in_rebuilt[nid] - all_notes - all_text
        seen_text = (in_rebuilt[nid] & all_text) - all_notes
        findings[nid] = (left, dropped, invented, seen_text)
        for key, values in zip(("left", "dropped", "invented", "seen"), findings[nid]):
            totals[key] += len(values)

    meta = model.get("metadata") or {}
    rebuilt_chars = sum(_chars(without_questions(b)) for b in bodies.values())
    n_asked = sum(len(v) for v in asked.values())
    out = [f"# Round trip{': ' + meta['title'] if meta.get('title') else ''}", "",
           "The text written back from the notes, next to the original, chunk by chunk. Judge each",
           "pair by meaning, not wording: is anything lost, added, turned the other way (a different",
           "turn from the chunk before) or weighed differently? The numbers are only hints.", ""]
    status = f"- Chunks written back: {len(seen)} of {len(notes.order)}"
    status += f", in the order of the {order}." if not out_of_order else \
        ", in another order: " + ", ".join(notes.number[c] for c in seen) + "."
    out.append(status)
    if missing:
        out.append("- Missing: " + "; ".join(notes.name(c) for c in missing) + ".")
    if unknown:
        out.append("- Markers that are not chunks: " + ", ".join(f"`{c}`" for c in unknown) + ".")
    if repeated:
        out.append("- Chunks written more than once (joined): " + ", ".join(notes.number[c] for c in repeated) + ".")
    if preamble:
        out.append(f"- Text before the first marker ({_chars(preamble)} characters) is not compared.")
    out.append(f"- The writer asked {n_asked} question(s) ([?: …]).")
    out.append(f"- Numbers: {totals['left']} in the text that the notes nowhere give; "
               f"{totals['dropped']} in a chunk's notes that its rebuilt paragraph lacks; "
               f"{totals['invented']} in the rebuilt text from neither the notes nor the text; "
               f"{totals['seen']} in the rebuilt text that only the text gives (did the writer see the text?).")
    out.append(f"- Length: {_chars(text):,} → {rebuilt_chars:,} characters.")

    wrapped = [False] * len(text)
    for n in notes.nodes.values():
        for sp in ss.all_spans(n):
            for p in range(sp["start"], sp["end"]):
                wrapped[p] = True
    gaps = [(k, s, e) for k, (s, e) in enumerate(notes.sentences, 1) if not any(wrapped[s:e])]
    if gaps:
        out.append(f"- Sentences no chunk wraps, which cannot come back: "
                   + ", ".join(f"S{k}" for k, _, _ in gaps) + ".")
    out.append("")

    for nid, num, _ in notes.order:
        n = notes.nodes[nid]
        out += [f"## {notes.mark(nid)}{num} {n['label']}  `{nid}`  ({notes.where(nid)})", ""]
        parent, transition, lines = notes.brought_in(nid)
        brought = ([f"part of {notes.number[parent]}"] if parent else []) + \
                  ([f"↪ {transition}"] if transition else []) + [notes.line(r, nid) for r in lines]
        if brought:
            out += ["Brought in by: " + "; ".join(brought), ""]
        if n.get("points"):
            out += ["Points: " + " / ".join(pt["label"] for pt in n["points"]), ""]
        out += ["**Original**", ""]
        out += [("\n>\n> …\n>\n".join(_blockquote(p) for p in passages[nid])) if passages[nid]
                else "(no passage of its own)", ""]
        out += ["**Rebuilt**", ""]
        out += [_blockquote(bodies[nid]) if bodies.get(nid) else "(not written back)", ""]
        left, dropped, invented, seen_text = findings[nid]
        hints = []
        if left:
            hints.append(f"Numbers in the text that the notes nowhere give: {nums(left)}")
        if dropped:
            hints.append(f"Numbers in the notes that the rebuilt paragraph lacks: {nums(dropped)}")
        if invented:
            hints.append(f"Numbers in the rebuilt paragraph from neither the notes nor the text: {nums(invented)}")
        if seen_text:
            hints.append(f"Numbers in the rebuilt paragraph that only the text gives: {nums(seen_text)}")
        hints += [f"The writer asked: {q}" for q in asked[nid]]
        hints.append(f"Length: {notes.own_length(nid):,} → {_chars(without_questions(bodies.get(nid, ''))):,} characters")
        out += [f"- {h}" for h in hints] + [""]
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------- diff

NODE_FIELDS = ("label", "type", "role", "parent", "provenance", "transition", "confirmed", "note", "derivedFrom")
RELATION_FIELDS = ("source", "target", "type", "label", "polarity", "directed", "provenance", "confirmed", "note",
                   "derivedFrom")
POINT_FIELDS = ("when", "provenance", "confirmed", "note")


def _show(value):
    if value is None:
        return "(none)"
    if isinstance(value, str):
        return _quote(value, 60)
    return json.dumps(value, ensure_ascii=False)


def _field_changes(a, b, fields):
    return [f"{f}: {_show(a.get(f))} → {_show(b.get(f))}" for f in fields if a.get(f) != b.get(f)]


def _span_change(a, b, before, after):
    sa = [(sp["start"], sp["end"]) for sp in a.get("sourceSpans") or []]
    sb = [(sp["start"], sp["end"]) for sp in b.get("sourceSpans") or []]
    if sa == sb and before["sourceText"] == after["sourceText"]:
        return []
    wa = ss._sentence_list(a.get("sourceSpans") or [], ss.split_sentences(before["sourceText"])) or "none"
    wb = ss._sentence_list(b.get("sourceSpans") or [], ss.split_sentences(after["sourceText"])) or "none"
    if sa == sb or wa == wb:
        return [f"words: {' / '.join(_quote(sp['text'], 24) for sp in b.get('sourceSpans') or []) or '(none)'}"]
    return [f"passages: {wa} → {wb}"]


def _point_changes(a, b):
    pa = {pt["label"]: pt for pt in a.get("points") or []}
    pb = {pt["label"]: pt for pt in b.get("points") or []}
    out = [f"point added 「{label}」" for label in pb if label not in pa]
    out += [f"point removed 「{label}」" for label in pa if label not in pb]
    for label in pa:
        if label in pb:
            changes = _field_changes(pa[label], pb[label], POINT_FIELDS)
            if [(sp["start"], sp["end"]) for sp in pa[label].get("sourceSpans") or []] != \
                    [(sp["start"], sp["end"]) for sp in pb[label].get("sourceSpans") or []]:
                changes.append("its words")
            if changes:
                out.append(f"point 「{label}」: " + ", ".join(changes))
    if [pt["label"] for pt in a.get("points") or [] if pt["label"] in pb] != \
            [pt["label"] for pt in b.get("points") or [] if pt["label"] in pa]:
        out.append("points reordered")
    return out


def diff(before, after):
    nb, na = {n["id"]: n for n in before["nodes"]}, {n["id"]: n for n in after["nodes"]}
    rb, ra = {r["id"]: r for r in before["relations"]}, {r["id"]: r for r in after["relations"]}
    numbers = {nid: num for nid, num, _ in ss.note_order(after)}
    old_numbers = {nid: num for nid, num, _ in ss.note_order(before)}

    def node_name(nid):
        return f"{numbers.get(nid) or old_numbers.get(nid)} {(na.get(nid) or nb.get(nid))['label']}"

    def rel_name(r, nodes):
        src = nodes.get(r["source"], {}).get("label", r["source"])
        tgt = nodes.get(r["target"], {}).get("label", r["target"])
        arrow = "—" if r.get("directed", True) is False else "→"
        return f"{src} {arrow} {tgt}: {r.get('label') or r['type']}"

    node_lines, changed_nodes = [], 0
    for nid in na:
        if nid not in nb:
            node_lines.append(f"- added `{nid}` {node_name(nid)} ({na[nid]['type']}, {na[nid]['provenance']})")
    for nid in nb:
        if nid not in na:
            node_lines.append(f"- removed `{nid}` {old_numbers[nid]} {nb[nid]['label']}")
    for nid in na:
        if nid in nb:
            changes = _field_changes(nb[nid], na[nid], NODE_FIELDS) + \
                _span_change(nb[nid], na[nid], before, after) + _point_changes(nb[nid], na[nid])
            if changes:
                changed_nodes += 1
                node_lines.append(f"- `{nid}` {node_name(nid)}: " + "; ".join(changes))

    rel_lines, changed_rels = [], 0
    for rid in ra:
        if rid not in rb:
            rel_lines.append(f"- added `{rid}` {rel_name(ra[rid], na)} ({ra[rid]['type']}, {ra[rid]['provenance']})")
    for rid in rb:
        if rid not in ra:
            rel_lines.append(f"- removed `{rid}` {rel_name(rb[rid], nb)}")
    for rid in ra:
        if rid in rb:
            changes = _field_changes(rb[rid], ra[rid], RELATION_FIELDS) + _span_change(rb[rid], ra[rid], before, after)
            if changes:
                changed_rels += 1
                rel_lines.append(f"- `{rid}` {rel_name(ra[rid], na)}: " + "; ".join(changes))

    def sentence(model):
        return "".join(part["text"] for part in model.get("summary") or []) or "(none)"

    def summary_refs(model):
        return [(part["text"], part.get("refs") or []) for part in model.get("summary") or []]

    summary_changed = summary_refs(before) != summary_refs(after)
    common = [nid for nid, _, _ in ss.note_order(after) if nid in nb]
    reordered = common != [nid for nid, _, _ in ss.note_order(before) if nid in na]
    meta_changed = (before.get("metadata") or {}) != (after.get("metadata") or {})

    out = ["# Changes in the model", ""]
    if before["sourceText"] != after["sourceText"]:
        out += ["- The source texts differ, so the passages may not be comparable.", ""]
    out += [f"- Chunks: {len(nb)} → {len(na)}: {sum(i not in nb for i in na)} added, "
            f"{sum(i not in na for i in nb)} removed, {changed_nodes} changed.",
            f"- Lines: {len(rb)} → {len(ra)}: {sum(i not in rb for i in ra)} added, "
            f"{sum(i not in ra for i in rb)} removed, {changed_rels} changed.",
            f"- Summary: {'changed' if summary_changed else 'unchanged'}.",
            f"- Order of the notes: {'changed' if reordered else 'unchanged'}."]
    if meta_changed:
        out.append("- Metadata: changed.")
    if node_lines:
        out += ["", "## Chunks", ""] + node_lines
    if rel_lines:
        out += ["", "## Lines", ""] + rel_lines
    if summary_changed:
        out += ["", "## Summary", "", f"- before: {sentence(before)}", f"- after: {sentence(after)}"]
    if reordered:
        out += ["", "## Order of the notes", "",
                "The chunks in their new order, by their old numbers: " + ", ".join(old_numbers[i] for i in common)]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- CLI


def _load(path):
    try:
        model = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"{path}: not valid JSON: {exc}")
    errors, _ = ss.validate_model(model)
    if errors:
        for e in errors:
            print(f"ERROR   {e}")
        sys.exit(f"{path} does not follow the contract; fix it first (semantic_structure.py validate)")
    return model


def _emit(text, path):
    if path:
        Path(path).write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    else:
        sys.stdout.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("flow", help="the chunks in order, what brings each one in, and the questions")
    p.add_argument("model")
    p.add_argument("--order", choices=ORDERS, default="notes")
    p.add_argument("-o", "--output")
    p = sub.add_parser("brief", help="the model without the text, for a writer who has not read it")
    p.add_argument("model")
    p.add_argument("--order", choices=ORDERS, default="notes")
    p.add_argument("--style", help="how the text should read, e.g. its genre and register")
    p.add_argument("-o", "--output")
    p = sub.add_parser("compare", help="the rebuilt text next to the original, chunk by chunk")
    p.add_argument("model")
    p.add_argument("rebuilt")
    p.add_argument("--order", choices=ORDERS, default="notes")
    p.add_argument("-o", "--output")
    p = sub.add_parser("diff", help="what changed between two versions of a model")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    if args.command == "diff":
        _emit(diff(_load(args.before), _load(args.after)), args.output)
        return 0
    model = _load(args.model)
    if args.command == "flow":
        _emit(flow(model, args.order), args.output)
    elif args.command == "brief":
        _emit(brief(model, args.order, args.style), args.output)
    else:
        rebuilt = Path(args.rebuilt).read_text(encoding="utf-8")
        if not MARKER.search(rebuilt):
            sys.exit(f"{args.rebuilt} has no chunk markers (<!-- chunk-id --> on a line of its own)")
        _emit(compare(model, rebuilt, args.order), args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
