#!/usr/bin/env python3
"""Semantic Model contract tool (semantic-model/1).

Shared by semantic-model-builder and semantic-model-viewer. This file is
copied verbatim into both skills; edit the builder copy and run
scripts/sync_semantic_shared.py from the repository root.

Standard library only.

  semantic_model.py sentences SOURCE.txt [--json]
      Number the sentences of a source text (use the numbers in draft spans).
  semantic_model.py resolve DRAFT.json [DRAFT2.json ...] --source SOURCE.txt -o MODEL.json
      Merge drafts written in parts, turn quote spans into offsets, validate.
      Writes nothing while there are errors.
  semantic_model.py validate MODEL.json [--json]
      Check the contract. Exit status 1 when there are errors.
  semantic_model.py outline MODEL.json
      Read the model aloud: from its conclusions through their reasons. It should
      explain the text to someone who has not read it. Also lists signs that the
      model copies the wording instead of the meaning.
  semantic_model.py summary MODEL.json
      A Markdown overview for checking the evidence against the text.
"""

import argparse
import json
import sys
from pathlib import Path

VERSION = "semantic-model/1"
PROVENANCE = ("explicit", "inferred", "abstracted", "uncertain")

_SENTENCE_END = set("。．！？!?")
_CLOSERS = set("」』）)】〕］]\"'”’")
_DIGITS = set("0123456789０１２３４５６７８９")
_DRAFT_KEYS = ("quote", "sentence", "occurrence")


class ContractError(Exception):
    pass


# ---------------------------------------------------------------- text


def normalize_text(text):
    """The canonical form of a source text: no BOM, \\n line endings, no trailing blanks."""
    return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").rstrip()


def split_sentences(text):
    """Code-point ranges [(start, end)] of sentences, trimmed of surrounding whitespace.

    A navigation aid for writing spans, not a linguistic analysis: it cuts after
    sentence-final punctuation (plus closing brackets) and at line breaks.
    """
    ranges = []
    start = i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\n":
            _push_range(text, start, i, ranges)
            start = i = i + 1
            continue
        heading_number = ch == "．" and i > 0 and text[i - 1] in _DIGITS     # 「１．見出し」
        if (ch in _SENTENCE_END and not heading_number) or (ch == "." and (i + 1 == n or text[i + 1].isspace())):
            j = i + 1
            while j < n and text[j] in _CLOSERS:
                j += 1
            _push_range(text, start, j, ranges)
            start = i = j
            continue
        i += 1
    _push_range(text, start, n, ranges)
    return ranges


def _push_range(text, s, e, out):
    while s < e and text[s].isspace():
        s += 1
    while e > s and text[e - 1].isspace():
        e -= 1
    if e > s:
        out.append((s, e))


def _sentence_of(offset, sentences):
    for k, (s, e) in enumerate(sentences, 1):
        if s <= offset < e:
            return k
    return None


def _find_all(text, needle, lo, hi):
    hits = []
    i = text.find(needle, lo, hi)
    while i != -1:
        hits.append(i)
        i = text.find(needle, i + 1, hi)
    return hits


def _clip(s, width=40):
    s = s.replace("\n", " ")
    return s if len(s) <= width else s[: width - 1] + "…"


# ---------------------------------------------------------------- resolve


def resolve_span(span, text, sentences):
    """Return a span with start/end/text; draft keys (quote, sentence, occurrence) are consumed."""
    if isinstance(span, str):
        span = {"quote": span}
    if not isinstance(span, dict):
        raise ContractError("a span must be an object or a quote string")
    extra = {k: v for k, v in span.items() if k not in ("start", "end", "text") + _DRAFT_KEYS}

    if "start" in span or "end" in span:
        s, e = span.get("start"), span.get("end")
        _check_offsets(s, e, len(text))
        actual = text[s:e]
        if "text" in span and span["text"] != actual:
            raise ContractError(
                f"text {span['text']!r} does not match sourceText[{s}:{e}] = {actual!r}"
            )
        return {"start": s, "end": e, "text": actual, **extra}

    quote = span.get("quote")
    if not isinstance(quote, str) or not quote:
        raise ContractError("a span needs start/end or a non-empty quote")
    lo, hi, where = 0, len(text), "the text"
    sentence = span.get("sentence")
    if sentence is not None:
        if not isinstance(sentence, int) or not 1 <= sentence <= len(sentences):
            raise ContractError(f"sentence {sentence!r} is not between 1 and {len(sentences)}")
        lo, hi = sentences[sentence - 1]
        where = f"sentence {sentence}"
    hits = _find_all(text, quote, lo, hi)
    occurrence = span.get("occurrence")
    if occurrence is not None:
        if not isinstance(occurrence, int) or not 1 <= occurrence <= len(hits):
            raise ContractError(
                f"occurrence {occurrence!r} requested, but {quote!r} occurs {len(hits)} time(s) in {where}"
            )
        start = hits[occurrence - 1]
    elif len(hits) == 1:
        start = hits[0]
    elif not hits:
        raise ContractError(f"{quote!r} not found in {where}{_not_found_hint(quote, text, sentences, sentence)}")
    else:
        found_in = sorted({_sentence_of(h, sentences) for h in hits} - {None})
        raise ContractError(
            f"{quote!r} occurs {len(hits)} times in {where} (sentences {found_in}); "
            'add "sentence" or "occurrence"'
        )
    return {"start": start, "end": start + len(quote), "text": quote, **extra}


def _not_found_hint(quote, text, sentences, sentence):
    if sentence is not None:
        elsewhere = sorted({_sentence_of(h, sentences) for h in _find_all(text, quote, 0, len(text))} - {None})
        if elsewhere:
            return f"; it occurs in sentence(s) {elsewhere}"
    squeeze = lambda s: "".join(s.split())
    if squeeze(quote) and squeeze(quote) in squeeze(text):
        return "; it matches only if whitespace or line breaks are ignored - quote the text exactly as it appears"
    return "; quote the source exactly (no paraphrase, same punctuation and digit width)"


def _check_offsets(s, e, length):
    if not isinstance(s, int) or not isinstance(e, int) or isinstance(s, bool) or isinstance(e, bool):
        raise ContractError("start and end must be integers")
    if not 0 <= s < e <= length:
        raise ContractError(f"offsets {s}..{e} are outside 0..{length} or empty")


def merge_drafts(drafts):
    """Merge drafts written in parts (e.g. one per section) into one; return (draft, warnings).

    Elements with the same id are one element: their sourceSpans and derivedFrom
    are combined, and for any other field the first value given wins.
    """
    merged = {"nodes": [], "relations": [], "metadata": {}}
    index, warnings = {}, []
    for n, draft in enumerate(drafts, 1):
        if not isinstance(draft, dict):
            raise ContractError(f"draft {n} must be a JSON object")
        for key, value in draft.items():
            if key in ("nodes", "relations", "metadata"):
                continue
            if key in merged and merged[key] != value:
                warnings.append(f"draft {n}: {key} differs from an earlier draft; kept the first")
            merged.setdefault(key, value)
        for key, value in (draft.get("metadata") or {}).items():
            merged["metadata"].setdefault(key, value)
        for kind in ("nodes", "relations"):
            for el in draft.get(kind) or []:
                eid = el.get("id") if isinstance(el, dict) else None
                if eid is None or eid not in index:
                    copy = dict(el) if isinstance(el, dict) else el
                    merged[kind].append(copy)
                    if eid is not None:
                        index[eid] = (kind, copy)
                    continue
                first_kind, first = index[eid]
                if first_kind != kind:
                    raise ContractError(f"draft {n}: id {eid!r} is used for both a node and a relation")
                for key, value in el.items():
                    if key == "sourceSpans":
                        first["sourceSpans"] = list(first.get("sourceSpans") or []) + list(value or [])
                    elif key == "states":
                        first["states"] = list(first.get("states") or []) + list(value or [])
                    elif key == "derivedFrom":
                        first["derivedFrom"] = list(dict.fromkeys(list(first.get("derivedFrom") or []) + list(value or [])))
                    elif key not in first:
                        first[key] = value
                    elif first[key] != value:
                        warnings.append(f"draft {n}: {eid}.{key} = {value!r} differs from {first[key]!r}; kept the first")
    return merged, warnings


def _dedupe_spans(spans):
    seen, out = set(), []
    for span in spans:
        key = (span["start"], span["end"])
        if key not in seen:
            seen.add(key)
            out.append(span)
    return sorted(out, key=lambda sp: (sp["start"], sp["end"]))


def resolve_model(draft, source_text=None):
    """Return (model, errors). Fills sourceText from source_text and resolves every span."""
    errors = []
    model = dict(draft)
    if source_text is not None:
        canonical = normalize_text(source_text)
        if "sourceText" in draft and normalize_text(str(draft["sourceText"])) != canonical:
            errors.append("draft sourceText differs from --source; drop it from the draft or fix it")
        model["sourceText"] = canonical
    text = model.get("sourceText")
    if not isinstance(text, str) or not text:
        return model, errors + ["no sourceText: pass --source SOURCE.txt"]
    model.setdefault("version", VERSION)
    model.setdefault("metadata", {})
    sentences = split_sentences(text)
    for kind in ("nodes", "relations"):
        for element in model.get(kind) or []:
            if not isinstance(element, dict):
                continue
            resolved = []
            for k, span in enumerate(element.get("sourceSpans") or [], 1):
                try:
                    resolved.append(resolve_span(span, text, sentences))
                except ContractError as exc:
                    errors.append(f"{element.get('id', '?')}: span {k}: {exc}")
            element["sourceSpans"] = _dedupe_spans(resolved)
            for n, state in enumerate(element.get("states") or [], 1):
                if not isinstance(state, dict):
                    continue
                spans = []
                for k, span in enumerate(state.get("sourceSpans") or [], 1):
                    try:
                        spans.append(resolve_span(span, text, sentences))
                    except ContractError as exc:
                        errors.append(f"{element.get('id', '?')}: state {n}: span {k}: {exc}")
                state["sourceSpans"] = _dedupe_spans(spans)
    head = ("version", "sourceText", "nodes", "relations", "metadata")
    ordered = {k: model[k] for k in head if k in model}
    ordered.update((k, v) for k, v in model.items() if k not in ordered)
    return ordered, errors


# ---------------------------------------------------------------- validate


def _check_spans(spans, name, text, errors):
    """Check a sourceSpans list; return the list (empty if unusable)."""
    if not isinstance(spans, list):
        errors.append(f"{name}: sourceSpans must be a list")
        return []
    for k, span in enumerate(spans, 1):
        if isinstance(span, str) or (isinstance(span, dict) and any(key in span for key in _DRAFT_KEYS)):
            errors.append(f"{name}: span {k} is a draft span; run `semantic_model.py resolve`")
            continue
        if not isinstance(span, dict):
            errors.append(f"{name}: span {k} must be an object")
            continue
        try:
            _check_offsets(span.get("start"), span.get("end"), len(text))
        except ContractError as exc:
            errors.append(f"{name}: span {k}: {exc}")
            continue
        if "text" in span and span["text"] != text[span["start"]:span["end"]]:
            errors.append(f"{name}: span {k}: text {span['text']!r} does not match its offsets")
    return spans


def all_spans(el):
    """An element's own spans plus those of its states."""
    out = list(el.get("sourceSpans") or [])
    for state in el.get("states") or []:
        if isinstance(state, dict):
            out += list(state.get("sourceSpans") or [])
    return out


def validate_model(model):
    """Return (errors, warnings) as lists of strings."""
    errors, warnings = [], []
    if not isinstance(model, dict):
        return ["the model must be a JSON object"], []

    text = model.get("sourceText")
    if not isinstance(text, str) or not text.strip():
        errors.append("sourceText must be a non-empty string")
        text = ""
    version = model.get("version")
    if version is not None and version != VERSION:
        warnings.append(f"version is {version!r}; this tool checks {VERSION!r}")
    if "metadata" not in model:
        warnings.append("metadata is missing (use {} when there is nothing to record)")
    elif not isinstance(model["metadata"], dict):
        errors.append("metadata must be an object")

    lists = {}
    for kind in ("nodes", "relations"):
        value = model.get(kind)
        if not isinstance(value, list):
            errors.append(f"{kind} must be a list")
            value = []
        lists[kind] = value

    kinds = {}
    elements = []
    for kind, items in (("node", lists["nodes"]), ("relation", lists["relations"])):
        for i, el in enumerate(items, 1):
            if not isinstance(el, dict):
                errors.append(f"{kind} #{i} must be an object")
                continue
            eid = el.get("id")
            if not isinstance(eid, str) or not eid:
                errors.append(f"{kind} #{i}: id must be a non-empty string")
                continue
            if eid in kinds:
                errors.append(f"{kind} {eid}: duplicate id (nodes and relations share one id space)")
                continue
            kinds[eid] = kind
            elements.append((kind, el))

    seen_edges = {}
    for kind, el in elements:
        eid = el["id"]
        name = f"{kind} {eid}"
        fields = ("label", "type") if kind == "node" else ("type",)
        for field in fields:
            if not isinstance(el.get(field), str) or not el[field].strip():
                errors.append(f"{name}: {field} must be a non-empty string")
        prov = el.get("provenance")
        if prov not in PROVENANCE:
            errors.append(f"{name}: provenance must be one of {', '.join(PROVENANCE)} (got {prov!r})")

        spans = _check_spans(el.get("sourceSpans"), name, text, errors)

        states = el.get("states")
        if states is not None:
            if kind != "node":
                errors.append(f"{name}: states are for nodes only")
            elif not isinstance(states, list):
                errors.append(f"{name}: states must be a list")
            else:
                for n, state in enumerate(states, 1):
                    where = f"{name}: state {n}"
                    if not isinstance(state, dict) or not isinstance(state.get("label"), str) or not state["label"].strip():
                        errors.append(f"{where} needs a non-empty label")
                        continue
                    if "when" in state and not isinstance(state["when"], str):
                        errors.append(f"{where}: when must be a string")
                    sprov = state.get("provenance", prov)
                    if sprov not in PROVENANCE:
                        errors.append(f"{where}: provenance must be one of {', '.join(PROVENANCE)}")
                    if not _check_spans(state.get("sourceSpans", []), where, text, errors) and sprov == "explicit":
                        warnings.append(f"{where} ({state['label']!r}) has no sourceSpans - point at the words that state it")
        if "polarity" in el and (kind != "relation" or el["polarity"] not in ("+", "-")):
            errors.append(f"{name}: polarity is for relations and must be \"+\" or \"-\"")
        if "role" in el and not isinstance(el["role"], str):
            errors.append(f"{name}: role must be a string")

        derived = el.get("derivedFrom")
        if derived is not None:
            if not isinstance(derived, list) or not all(isinstance(d, str) for d in derived):
                errors.append(f"{name}: derivedFrom must be a list of ids")
                derived = []
            for d in derived:
                if d == eid:
                    errors.append(f"{name}: derivedFrom refers to itself")
                elif d not in kinds:
                    errors.append(f"{name}: derivedFrom refers to unknown id {d!r}")
        derived = derived or []

        if "parent" in el:
            parent = el["parent"]
            if kind != "node":
                errors.append(f"{name}: parent is for nodes only")
            elif kinds.get(parent) != "node":
                errors.append(f"{name}: parent {parent!r} must be a node id")
            elif parent == eid:
                errors.append(f"{name}: parent refers to itself")

        if kind == "relation":
            for end in ("source", "target"):
                ref = el.get(end)
                if kinds.get(ref) != "node":
                    what = "a relation" if kinds.get(ref) == "relation" else "unknown"
                    errors.append(f"{name}: {end} {ref!r} must be a node id ({what})")
            if el.get("source") == el.get("target"):
                warnings.append(f"{name}: source and target are the same node")
            if "directed" in el and not isinstance(el["directed"], bool):
                errors.append(f"{name}: directed must be true or false")
            key = (el.get("source"), el.get("target"), el.get("type"))
            if key in seen_edges:
                warnings.append(f"{name}: same source, target and type as {seen_edges[key]}")
            else:
                seen_edges[key] = eid

        if prov == "explicit" and not spans:
            errors.append(f"{name}: explicit but has no sourceSpans - point at the words that state it")
        if prov == "abstracted" and not derived:
            errors.append(f"{name}: abstracted but has no derivedFrom - list the members it groups")
        if prov in ("inferred", "uncertain") and not spans and not derived:
            warnings.append(f"{name}: {prov} with neither sourceSpans nor derivedFrom cannot be traced to the text")
        if prov == "uncertain" and not el.get("note"):
            warnings.append(f"{name}: uncertain without a note - say what the competing readings are")

    parents = {el["id"]: el.get("parent") for kind, el in elements if kind == "node"}
    for start in parents:
        seen, cur = set(), start
        while cur is not None and cur in parents and cur not in seen:
            seen.add(cur)
            cur = parents.get(cur)
        if cur is not None and cur in seen and cur == start:
            errors.append(f"node {start}: parent chain loops back to itself")

    if text and not errors:
        covered = [False] * len(text)
        for _, el in elements:
            for span in all_spans(el):
                for p in range(span["start"], span["end"]):
                    covered[p] = True
        for k, (s, e) in enumerate(split_sentences(text), 1):
            if not any(covered[s:e]):
                warnings.append(f"sentence {k} is not referenced by any span: {_clip(text[s:e])!r}")
    return errors, warnings


# ---------------------------------------------------------------- summary


def summarize(model):
    text = model["sourceText"]
    nodes, relations = model["nodes"], model["relations"]
    by_id = {el["id"]: el for el in nodes + relations}
    covered = [False] * len(text)
    for el in nodes + relations:
        for span in all_spans(el):
            for p in range(span["start"], span["end"]):
                covered[p] = True
    meaningful = [p for p, ch in enumerate(text) if not ch.isspace()]
    ratio = sum(covered[p] for p in meaningful) / max(1, len(meaningful))
    sentences = split_sentences(text)

    def count(items):
        tally = {p: 0 for p in PROVENANCE}
        for el in items:
            tally[el.get("provenance")] = tally.get(el.get("provenance"), 0) + 1
        return ", ".join(f"{p} {n}" for p, n in tally.items() if n)

    def quotes(el):
        return " / ".join(f"「{_clip(s['text'], 24)}」" for s in el.get("sourceSpans", [])) or "-"

    def cell(s):
        return str(s).replace("|", "\\|").replace("\n", " ")

    def describe(eid):
        el = by_id.get(eid)
        if el is None:
            return eid
        if "source" not in el:
            return el.get("label", eid)
        src = by_id.get(el.get("source"), {}).get("label", el.get("source"))
        tgt = by_id.get(el.get("target"), {}).get("label", el.get("target"))
        return f"{src} —{el.get('label') or el.get('type')}→ {tgt}"

    title = model.get("metadata", {}).get("title")
    out = [f"# Semantic Model summary{': ' + title if title else ''}", ""]
    out.append(f"- Source: {len(text)} characters, {len(sentences)} sentences; "
               f"{ratio:.0%} of non-space characters fall inside some span")
    out.append(f"- Nodes: {len(nodes)} ({count(nodes)})")
    out.append(f"- Relations: {len(relations)} ({count(relations)})")
    out += ["", "## Nodes", "", "| id | label | type | parent | provenance | spans |", "|---|---|---|---|---|---|"]
    for n in nodes:
        out.append(f"| {cell(n['id'])} | {cell(n['label'])} | {cell(n['type'])} | {cell(n.get('parent', ''))} "
                   f"| {n['provenance']} | {cell(quotes(n))} |")
    staged = [n for n in nodes if n.get("states")]
    if staged:
        out += ["", "## States", "", "| node | when | state | provenance | spans |", "|---|---|---|---|---|"]
        for n in staged:
            for st in n["states"]:
                out.append(f"| {cell(n['label'])} | {cell(st.get('when', ''))} | {cell(st['label'])} "
                           f"| {st.get('provenance', n['provenance'])} | {cell(quotes(st))} |")
    out += ["", "## Relations", "", "| id | relation | provenance | spans |", "|---|---|---|---|"]
    for r in relations:
        src = by_id.get(r["source"], {}).get("label", r["source"])
        tgt = by_id.get(r["target"], {}).get("label", r["target"])
        arrow = "—" if r.get("directed", True) is False else "→"
        word = r.get("label") or r["type"]
        out.append(f"| {cell(r['id'])} | {cell(src)} —{cell(word)}{arrow} {cell(tgt)} | {r['provenance']} | {cell(quotes(r))} |")
    review = [el for el in nodes + relations if el["provenance"] != "explicit"]
    if review:
        out += ["", "## Not stated in the text (review these)", ""]
        for el in review:
            basis = "; ".join(describe(d) for d in el.get("derivedFrom", []))
            label = describe(el["id"])
            line = f"- **{cell(label)}** (`{el['id']}`, {el['provenance']})"
            if basis:
                line += f" ← {cell(basis)}"
            if el.get("note"):
                line += f": {cell(el['note'])}"
            out.append(line)
    gaps = [(k, s, e) for k, (s, e) in enumerate(sentences, 1) if not any(covered[s:e])]
    if gaps:
        out += ["", "## Sentences no span touches", ""]
        out += [f"- {k}: {_clip(text[s:e], 80)}" for k, s, e in gaps]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- outline

# Heuristics for "the model copies the wording": connectives used as relation names,
# relations and nodes about the document rather than its subject.
_CONNECTIVES = {
    "こうしたもとで", "そうしたもとで", "こうしたもと", "こうしたなか", "そうしたなか", "そのうえで", "この間", "一方",
    "これに加え", "これらに加え", "加え", "に加え", "ことから", "ため", "ので", "から", "なか", "もとで", "のもとで",
    "踏まえると", "を踏まえると", "背景に", "を背景に", "もあって", "こともあり", "なかにあっては", "続き", "続くなか",
    "therefore", "thus", "hence", "so", "because", "since", "meanwhile", "in addition", "given", "under", "then", "and",
}
_TEXT_RELATIONS = {"describes", "mentions", "refers_to", "concerns", "examines", "summarizes", "restates", "elaborates",
                   "elaborated_by", "details", "introduces", "lists"}
_TEXT_NODE_TYPES = {"section", "heading", "chapter", "paragraph", "sentence", "topic", "summary", "examination", "framework"}


def outline(model):
    nodes = {n["id"]: n for n in model["nodes"]}
    order = {n["id"]: k for k, n in enumerate(model["nodes"])}
    incoming, children = {}, {}
    for r in model["relations"]:
        incoming.setdefault(r["target"], []).append(r)
    for n in model["nodes"]:
        if n.get("parent"):
            children.setdefault(n["parent"], []).append(n["id"])

    def states(n):
        parts = [(f"{st['when']}: " if st.get("when") else "") + st["label"] for st in n.get("states") or []]
        return f"  ｜ {' / '.join(parts)}" if parts else ""

    def word(r):
        w = r.get("label") or r["type"]
        return w + (f" ({r['polarity']})" if r.get("polarity") else "")

    # How much explanation hangs below a node: everything reachable back through its reasons,
    # without passing through a conclusion (a feedback loop would otherwise count everything).
    weights = {}
    stops = {n["id"] for n in model["nodes"] if n.get("role") == "conclusion"}

    def weight(nid):
        if nid not in weights:
            todo, found = [nid], set()
            while todo:
                for r in incoming.get(todo.pop(), []):
                    src = r["source"]
                    if src not in found and src not in stops:
                        found.add(src)
                        todo.append(src)
            weights[nid] = len(found)
        return weights[nid]

    lines, seen, later = [], set(), []

    def walk(nid, depth, line):
        n = nodes[nid]
        pad = "  " * depth
        if nid in seen:
            lines.append(f"{pad}- {line}  (see above)")
            return
        if depth > 3 and (incoming.get(nid) or children.get(nid)):
            lines.append(f"{pad}- {line}{states(n)}  (continued below)")
            later.append(nid)
            return
        seen.add(nid)
        lines.append(f"{pad}- {line}{states(n)}")
        for r in sorted(incoming.get(nid, []), key=lambda r: (-weight(r["source"]), order.get(r["source"], 0))):
            src = nodes[r["source"]]
            arrow = "—" if r.get("directed", True) is False else "→"
            walk(src["id"], depth + 1, f"{src['label']} —{word(r)}{arrow} {n['label']}")
        for c in children.get(nid, []):
            if c in seen:
                continue
            if depth < 1:
                walk(c, depth + 1, f"⊂ {nodes[c]['label']}")
            else:
                lines.append(f"{pad}  - ⊂ {nodes[c]['label']}{states(nodes[c])}")
                if incoming.get(c) or children.get(c):
                    later.append(c)

    roots = [n for n in model["nodes"] if n.get("role") == "conclusion"]
    out = ["# Outline: the model read aloud", "",
           "Read this without the text. It should explain what the text says and why, more plainly than the",
           "text does. If it reads like the text reworded sentence by sentence, the model holds the wording,",
           "not the meaning.", ""]
    if not roots:
        best = max(model["nodes"], key=lambda n: len(incoming.get(n["id"], [])), default=None)
        roots = [best] if best else []
        out.append("(No node has role \"conclusion\"; starting from the node with the most incoming relations.)")
        out.append("")
    for n in roots:
        walk(n["id"], 0, f"**{n['label']}**")
    # what the conclusion does not reach, largest stories first
    rest = later + sorted((n["id"] for n in model["nodes"] if n["id"] not in seen and not n.get("parent")),
                          key=lambda nid: (-weight(nid), order[nid]))
    first = True
    for nid in rest:
        if nid in seen:
            continue
        if first:
            lines += ["", "Further:"]
            first = False
        walk(nid, 0, nodes[nid]["label"])
    out += lines

    smells = []
    conn = [r for r in model["relations"] if (r.get("label") or "").strip().lower() in _CONNECTIVES]
    if conn:
        smells.append(f"{len(conn)} relation(s) are named by a connective, not by what they do: "
                      + ", ".join(f"{r['id']} ({r['label']})" for r in conn[:6]) + (" …" if len(conn) > 6 else ""))
    textual = [r for r in model["relations"] if r["type"] in _TEXT_RELATIONS]
    if textual:
        smells.append(f"{len(textual)} relation(s) are about the text rather than its subject: "
                      + ", ".join(f"{r['id']} ({r['type']})" for r in textual[:6]) + (" …" if len(textual) > 6 else ""))
    doc_nodes = [n for n in model["nodes"] if n["type"].lower() in _TEXT_NODE_TYPES]
    if doc_nodes:
        smells.append(f"{len(doc_nodes)} node(s) look like document structure: " + ", ".join(n["label"] for n in doc_nodes[:6]))
    heads = {}
    for n in model["nodes"]:
        for sep in ("：", ":"):
            if sep in n["label"]:
                heads.setdefault(n["label"].split(sep, 1)[0].strip(), []).append(n["label"])
                break
    split = {h: ls for h, ls in heads.items() if len(ls) > 1}
    if split:
        smells.append("the same subject is split over several nodes (one node with states instead?): "
                      + "; ".join(f"{h} ×{len(ls)}" for h, ls in list(split.items())[:6]))
    out += ["", "## Signs of modeling the words", ""]
    out += [f"- {s}" for s in smells] if smells else ["- none found"]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- JSON output


def dumps(value, indent=0, width=100):
    """JSON with small objects and arrays kept on one line, so spans stay readable."""
    flat = json.dumps(value, ensure_ascii=False)
    if not isinstance(value, (dict, list)) or len(flat) + indent <= width:
        return flat
    pad, inner = " " * indent, " " * (indent + 2)
    if isinstance(value, list):
        items = [inner + dumps(v, indent + 2, width) for v in value]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]" if items else "[]"
    items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent + 2, width)}" for k, v in value.items()]
    return "{\n" + ",\n".join(items) + "\n" + pad + "}" if items else "{}"


# ---------------------------------------------------------------- CLI


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"{path}: not valid JSON: {exc}")


def _report(errors, warnings, as_json=False):
    if as_json:
        print(json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
        return
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("sentences", help="number the sentences of a source text")
    p.add_argument("source")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("resolve", help="merge drafts, turn quote spans into offsets and validate")
    p.add_argument("drafts", nargs="+")
    p.add_argument("--source", help="the source text file (sets sourceText)")
    p.add_argument("-o", "--output", required=True)
    p = sub.add_parser("validate", help="check a model against the contract")
    p.add_argument("model")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("outline", help="read the model aloud, from its conclusions")
    p.add_argument("model")
    p = sub.add_parser("summary", help="print a Markdown overview of a model")
    p.add_argument("model")
    args = parser.parse_args(argv)

    if args.command == "sentences":
        text = normalize_text(Path(args.source).read_text(encoding="utf-8"))
        ranges = split_sentences(text)
        if args.json:
            print(json.dumps([{"sentence": k, "start": s, "end": e, "text": text[s:e]}
                              for k, (s, e) in enumerate(ranges, 1)], ensure_ascii=False, indent=2))
        else:
            for k, (s, e) in enumerate(ranges, 1):
                print(f"{k:>3} [{s}:{e}] {text[s:e]}")
        return 0

    if args.command == "resolve":
        source = Path(args.source).read_text(encoding="utf-8") if args.source else None
        try:
            draft, warnings = merge_drafts([_read_json(path) for path in args.drafts])
        except ContractError as exc:
            sys.exit(f"ERROR   {exc}")
        model, errors = resolve_model(draft, source)
        if not errors:
            errors, more = validate_model(model)
            warnings += more
        _report(errors, warnings)
        if errors:
            print(f"{args.output} not written")
            return 1
        Path(args.output).write_text(dumps(model) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
        return 0

    model = _read_json(args.model)
    errors, warnings = validate_model(model)
    if args.command == "validate":
        _report(errors, warnings, args.json)
        return 1 if errors else 0
    if errors:
        _report(errors, warnings)
        return 1
    sys.stdout.write(outline(model) if args.command == "outline" else summarize(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
