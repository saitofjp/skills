#!/usr/bin/env python3
"""Reconstruct a text from its Semantic Structure, in the flow of the model.

Part of semantic-structure-reconstructor. It uses semantic_structure.py, the contract
tool shared by the semantic skills, from the same folder. Standard library only.

  reconstruct.py flow MODEL.json
      The chunks in the order of the notes, what brings each one in from what came
      before, and the questions to settle with the user.
  reconstruct.py blueprint MODEL.json [--style TEXT] [-o BLUEPRINT.md]
      The plan of the text: for each chunk, its message, points, the turn from what
      came before, its weight, and its passage of the original as the material.
  reconstruct.py check MODEL.json DRAFT.md [-o CHECK.md]
      The draft chunk by chunk against the blueprint: chunks missing or out of order,
      numbers in the notes that a paragraph lacks, numbers from neither the notes nor
      the original, the [?: ...] left open, the lengths.
  reconstruct.py export DRAFT.md [-o TEXT.md]
      The draft without its chunk markers: the reconstructed text.
  reconstruct.py diff BEFORE.json AFTER.json [-o DIFF.md]
      What changed in the model.
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

MARKER = re.compile(r"^[ \t]*<!--\s*(\S+?)\s*-->[ \t]*$", re.M)
QUESTION = re.compile(r"\[\?:\s*(.*?)\s*\]", re.S)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


# ---------------------------------------------------------------- reading the notes


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


def _blockquote(text):
    return "\n".join("> " + line if line.strip() else ">" for line in text.strip().split("\n"))


class Notes:
    """A valid model read in the order of its notes (parts under their chunk, numbered 2, 2.1, …)."""

    def __init__(self, model):
        self.model = model
        self.text = model["sourceText"]
        self.sentences = ss.split_sentences(self.text)
        self.nodes = {n["id"]: n for n in model["nodes"]}
        self.order = ss.note_order(model)
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

    def passage_texts(self, nid):
        return [self.text[s:e].strip() for s, e in self.own_passages(nid)]

    def own_length(self, nid):
        return sum(_chars(p) for p in self.passage_texts(nid))

    def where(self, nid):
        spans = self.nodes[nid].get("sourceSpans") or []
        return ss._sentence_list(spans, self.sentences) or "no passage of its own"

    def arrow(self, r, nid):
        """How a line looks from one of its chunks: ← it comes in, → it goes out, — no direction."""
        if r.get("directed", True) is False:
            return "—"
        return "←" if r["target"] == nid else "→"

    def line(self, r, nid):
        """A line as seen from one of its chunks: `← 2 X: label (type, +, inferred, confirmed)`."""
        extra = []
        if r.get("label") and r["label"] != r["type"]:
            extra.append(r["type"])
        if r.get("polarity"):
            extra.append(r["polarity"])
        if r["provenance"] != "explicit":
            extra.append(r["provenance"])
            if r.get("confirmed"):
                extra.append("confirmed")
        tail = f" ({', '.join(extra)})" if extra else ""
        return f"{self.arrow(r, nid)} {self.name(self.other(r, nid))}: {r.get('label') or r['type']}{tail}"

    def mark(self, nid):
        role = self.nodes[nid].get("role")
        return "★ " if role == "conclusion" else "◆ " if role == "key" else ""

    def roles(self):
        out = []
        for nid, _, _ in self.order:
            role = self.nodes[nid].get("role")
            if role == "conclusion":
                out.append(f"★ conclusion: {self.name(nid)}")
            elif role == "key":
                out.append(f"◆ key: {self.name(nid)}")
        return out


def _prov(el, default="explicit"):
    prov = el.get("provenance", default)
    if prov == "explicit":
        return ""
    return f" [{prov}{', confirmed' if el.get('confirmed') else ''}]"


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


def flow(model):
    notes = Notes(model)
    qs = _questions(notes)
    qnum = {(kind, subject): f"Q{k}" for k, (kind, subject, _) in enumerate(qs, 1) if subject is not None}
    out = ["# Flow: the chunks in the order the text will follow", "",
           "Each chunk should be brought in by what comes before it: a line to an earlier chunk,",
           "the chunk it is part of, or a transition (↪). Where nothing brings a chunk in, the text",
           "cannot say why it comes there. Each line is shown once, at its later end.", "",
           " ".join([f"{len(notes.order)} chunks, {len(model['relations'])} lines."] + notes.roles()), ""]
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


# ---------------------------------------------------------------- blueprint

RULES = """\
1. Write the chunks in the order below, one paragraph each; a long chunk may take a few, and
   with headings a top-level chunk's headline may become its heading. Put each chunk's marker,
   exactly as given (`<!-- id -->`), on a line of its own before it.
2. Make each chunk's message, its headline, plain, and carry every point.
3. Take the facts from the material, the chunk's passage of the original: numbers, dates,
   names, conditions and the wording of what is decided, exactly as it has them. Keep its
   sentences where they already say it well; rewrite where the flow needs it. Use what the
   notes leave out only where a sentence needs it to make sense.
4. Bring each chunk in as "Brought in by" says, so that the reader sees why it comes here.
   `← X: words` means X does that to this chunk, `→ X: words` that this chunk does it to X,
   `— X: words` that they go together; `+` raises or goes the same way, `-` lowers or goes
   against; `↪` moves on. Say the lines that are stated or confirmed. Let an `inferred` line or
   point that is not confirmed be carried by the order, with a light connective at most. Do
   not settle what is `uncertain`.
5. Give the ★ conclusion and the ◆ key the room and the place they need; do not let the key
   disappear behind the conclusion. The whole must come to the one sentence above.
6. Add nothing that neither the notes nor the material says. Where you need something they do
   not give, write [?: what is missing] and go on."""


def blueprint(model, style=None):
    notes = Notes(model)
    meta = model.get("metadata") or {}
    title, language = meta.get("title"), meta.get("language")
    out = [f"# Blueprint: {title}" if title else "# Blueprint", "",
           "The plan for writing the text again, in the flow of its notes: the order, the turns and",
           "the weight come from the notes, the facts and the wording from the original.", "",
           f"- Language: {language}." if language else "- Language: the language of the original.",
           *([f"- Style: {style}"] if style else []),
           f"- The original: about {_chars(model['sourceText']):,} characters.",
           "- " + " ".join([f"{len(notes.order)} chunks and {len(model['relations'])} lines."] + notes.roles()),
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
        facts.append(f"about {length:,} characters in the original" if length else "no passage of its own")
        if n["provenance"] != "explicit":
            facts.append(n["provenance"] + (", confirmed" if n.get("confirmed") else ""))
        out += [f"### {notes.mark(nid)}{num} {n['label']}", "", " · ".join(facts), ""]
        parent, transition, lines = notes.brought_in(nid)
        brought = ["the text starts here"] if k == 0 else []
        if parent:
            brought.append(f"part of {notes.name(parent)}")
        if transition:
            brought.append(f"↪ {transition}")
        brought += [notes.line(r, nid) for r in lines]
        out += ["Brought in by:", ""] + [f"- {b}" for b in brought or ["nothing in the notes"]] + [""]
        if n.get("points"):
            out += ["Points:", ""]
            for pt in n["points"]:
                when = f"{pt['when']}: " if pt.get("when") else ""
                out.append(f"- {when}{pt['label']}{_prov(pt, n['provenance'])}")
            out.append("")
        later = notes.later_lines(nid)
        if later:
            out += ["Lines to later chunks:", ""] + [f"- {notes.line(r, nid)}" for r in later] + [""]
        passages = notes.passage_texts(nid)
        if passages:
            out += ["Material:", "", "\n>\n> …\n>\n".join(_blockquote(p) for p in passages), ""]
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------- check


def parse_draft(text):
    """Split a draft at its markers: (text before the first marker, [(id, body)])."""
    parts = MARKER.split(text.replace("\r\n", "\n"))
    return parts[0].strip(), [(parts[k], parts[k + 1].strip()) for k in range(1, len(parts) - 1, 2)]


def check(model, draft):
    notes = Notes(model)
    preamble, chunks = parse_draft(draft)
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
        return " ".join([n["label"]] + [pt["label"] for pt in n.get("points") or []])  # `when` only places a point in time

    def plain(s):
        return QUESTION.sub(" ", s)

    in_notes = {nid: _numbers(note_words(nid)) for nid in notes.nodes}
    in_draft = {nid: _numbers(plain(bodies.get(nid, ""))) for nid in notes.nodes}
    all_notes = set().union(*in_notes.values()) if in_notes else set()
    all_original = _numbers(notes.text)
    asked = {nid: QUESTION.findall(bodies.get(nid, "")) for nid in notes.nodes}
    dropped = {nid: (in_notes[nid] - in_draft[nid]) if nid in bodies else set() for nid in notes.nodes}
    invented = {nid: in_draft[nid] - all_notes - all_original for nid in notes.nodes}

    def nums(values):
        return ", ".join(sorted(values, key=lambda v: (len(v), v)))

    meta = model.get("metadata") or {}
    n_asked = sum(len(v) for v in asked.values())
    out = [f"# Check{': ' + meta['title'] if meta.get('title') else ''}", "",
           "The draft against its blueprint, chunk by chunk. Read each paragraph: does it make the",
           "chunk's message plain, carry every point, come in as its lines say, and add nothing that",
           "neither the notes nor the original says? The numbers are only hints.", ""]
    status = f"- Chunks written: {len(seen)} of {len(notes.order)}"
    status += ", in the order of the notes." if not out_of_order else \
        ", in another order: " + ", ".join(notes.number[c] for c in seen) + "."
    out.append(status)
    if missing:
        out.append("- Missing: " + "; ".join(notes.name(c) for c in missing) + ".")
    if unknown:
        out.append("- Markers that are not chunks: " + ", ".join(f"`{c}`" for c in unknown) + ".")
    if repeated:
        out.append("- Chunks written more than once (joined): " + ", ".join(notes.number[c] for c in repeated) + ".")
    if preamble:
        out.append(f"- Text before the first marker: {_chars(preamble)} characters (kept in the export, not checked).")
    out.append(f"- Open questions [?: …]: {n_asked}.")
    out.append(f"- Numbers: {sum(len(v) for v in dropped.values())} in a chunk's notes that its paragraph lacks; "
               f"{sum(len(v) for v in invented.values())} in the draft from neither the notes nor the original.")
    out.append(f"- Length: the original {_chars(notes.text):,} → the draft "
               f"{sum(_chars(plain(b)) for b in bodies.values()):,} characters.")
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
        out += ["**Draft**", "", _blockquote(bodies[nid]) if bodies.get(nid) else "(not written)", ""]
        passages = notes.passage_texts(nid)
        out += ["**Original**", "", "\n>\n> …\n>\n".join(_blockquote(p) for p in passages) if passages
                else "(no passage of its own)", ""]
        hints = []
        if dropped[nid]:
            hints.append(f"Numbers in the notes that the paragraph lacks: {nums(dropped[nid])}")
        if invented[nid]:
            hints.append(f"Numbers from neither the notes nor the original: {nums(invented[nid])}")
        hints += [f"Open: {q}" for q in asked[nid]]
        hints.append(f"Length: {notes.own_length(nid):,} → {_chars(plain(bodies.get(nid, ''))):,} characters")
        out += [f"- {h}" for h in hints] + [""]
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------- export


def export(draft):
    """The draft without its markers, blank lines collapsed; and the [?: …] still open."""
    text = MARKER.sub("", draft.replace("\r\n", "\n"))
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, QUESTION.findall(text)


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


def _read_draft(path):
    draft = Path(path).read_text(encoding="utf-8")
    if not MARKER.search(draft):
        sys.exit(f"{path} has no chunk markers (<!-- chunk-id --> on a line of its own)")
    return draft


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
    p.add_argument("-o", "--output")
    p = sub.add_parser("blueprint", help="the plan of the text: messages, points, turns, weight and material")
    p.add_argument("model")
    p.add_argument("--style", help="how the text should read: its reader, form, register, length")
    p.add_argument("-o", "--output")
    p = sub.add_parser("check", help="the draft chunk by chunk against the blueprint")
    p.add_argument("model")
    p.add_argument("draft")
    p.add_argument("-o", "--output")
    p = sub.add_parser("export", help="the draft without its markers")
    p.add_argument("draft")
    p.add_argument("-o", "--output")
    p = sub.add_parser("diff", help="what changed between two versions of a model")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    if args.command == "diff":
        _emit(diff(_load(args.before), _load(args.after)), args.output)
    elif args.command == "export":
        text, open_questions = export(_read_draft(args.draft))
        _emit(text, args.output)
        for q in open_questions:
            print(f"WARNING [?: {q}] is still open", file=sys.stderr)
    elif args.command == "flow":
        _emit(flow(_load(args.model)), args.output)
    elif args.command == "blueprint":
        _emit(blueprint(_load(args.model), args.style), args.output)
    else:
        _emit(check(_load(args.model), _read_draft(args.draft)), args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
