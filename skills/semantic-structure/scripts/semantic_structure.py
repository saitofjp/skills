#!/usr/bin/env python3
"""Semantic Structure contract tool (semantic-structure/1).

Standard library only.

  semantic_structure.py sentences SOURCE.txt [--json] [--after MODEL.json]
      Number the sentences of a source text (use the numbers in draft spans).
      --after shows only the sentences added since MODEL.json was built.
  semantic_structure.py resolve DRAFT.json [DRAFT2.json ...] --source SOURCE.txt -o MODEL.json
      Merge drafts written in parts, turn quote spans into offsets, validate.
      Writes nothing while there are errors.
  semantic_structure.py append MODEL.json DRAFT.json [...] --source SOURCE.txt (-o MODEL.json | --check)
      Add chunks and lines for text added at the end of the source, without
      re-cutting what is there. Quotes are looked up in the added text.
      --check writes nothing and reads back what would hold after it.
  semantic_structure.py validate MODEL.json [--json]
      Check the contract. Exit status 1 when there are errors.
  semantic_structure.py outline MODEL.json
      Read the notes back: the summary, then every chunk with its points and the
      relations to other chunks, in the order of the notes. It should explain the
      text to someone who has not read it.
  semantic_structure.py state MODEL.json
      What holds now: the chunks in force with what each overturned, the open
      questions, what is out and why, and the signs that a full review is due.
  semantic_structure.py summary MODEL.json
      A Markdown overview for checking the evidence against the text.
"""

import argparse
import json
import sys
from pathlib import Path

VERSION = "semantic-structure/1"
PROVENANCE = ("explicit", "inferred", "abstracted", "uncertain")
MOVES = ("replaces", "rejects", "answers")      # what a line does to its target as the text moves on
OVERTURN = ("replaces", "rejects")
LONG_TEXT = 10000                                # about what fits in one model

_SENTENCE_END = set("。．！？!?")
_CLOSERS = set("」』）)】〕］]\"'”’")
_DIGITS = set("0123456789０１２３４５６７８９")
_DRAFT_KEYS = ("quote", "sentence", "sentences", "occurrence")


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


def resolve_span(span, text, sentences, added=0):
    """Return a span with start/end/text; draft keys (quote, sentence(s), occurrence) are consumed.

    Draft forms: "quote", {"quote", "sentence"|"sentences", "occurrence"}, a whole sentence
    {"sentence": n}, or a passage of whole sentences {"sentences": [first, last]}.
    A quote without sentence numbers is looked up from offset `added` on: in an update, the added text.
    """
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
    within = _sentence_range(span, sentences)
    if quote is None and within is not None:
        s, e, _ = within
        return {"start": s, "end": e, "text": text[s:e], **extra}
    if not isinstance(quote, str) or not quote:
        raise ContractError("a span needs start/end, a non-empty quote, or sentence numbers")
    lo, hi, where = within or (added, len(text), "the added text" if added else "the text")
    sentence = span.get("sentence")
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
        hint = _not_found_hint(quote, text, sentences, sentence if within else (None if not added else 0))
        raise ContractError(f"{quote!r} not found in {where}{hint}")
    else:
        found_in = sorted({_sentence_of(h, sentences) for h in hits} - {None})
        raise ContractError(
            f"{quote!r} occurs {len(hits)} times in {where} (sentences {found_in}); "
            'add "sentence" or "occurrence"'
        )
    return {"start": start, "end": start + len(quote), "text": quote, **extra}


def _sentence_range(span, sentences):
    """(start, end, where) of {"sentence": n} or {"sentences": [first, last]} (inclusive), else None."""
    if "sentences" in span:
        pair = span["sentences"]
        if (not isinstance(pair, list) or len(pair) != 2 or not all(type(k) is int for k in pair)
                or not 1 <= pair[0] <= pair[1] <= len(sentences)):
            raise ContractError(f"sentences must be [first, last] between 1 and {len(sentences)} (got {pair!r})")
        return sentences[pair[0] - 1][0], sentences[pair[1] - 1][1], f"sentences {pair[0]}-{pair[1]}"
    if "sentence" in span:
        k = span["sentence"]
        if type(k) is not int or not 1 <= k <= len(sentences):
            raise ContractError(f"sentence {k!r} is not between 1 and {len(sentences)}")
        return sentences[k - 1][0], sentences[k - 1][1], f"sentence {k}"
    return None


def _not_found_hint(quote, text, sentences, sentence):
    """`sentence` is the sentence the quote was looked for in, 0 for the added text, None for the whole text."""
    if sentence is not None:
        elsewhere = sorted({_sentence_of(h, sentences) for h in _find_all(text, quote, 0, len(text))} - {None})
        if elsewhere and sentence == 0:
            return f'; it occurs in the earlier text, sentence(s) {elsewhere}: add "sentence" to point there'
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

    Elements with the same id are one element: their sourceSpans, points and
    derivedFrom are combined, and for any other field the first value given wins.
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
                    elif key == "points":
                        first["points"] = list(first.get("points") or []) + list(value or [])
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


def resolve_model(draft, source_text=None, added=0):
    """Return (model, errors). Fills sourceText from source_text and resolves every span.

    `added` is where the text added in an update starts; quotes are looked up from there on.
    """
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
                    resolved.append(resolve_span(span, text, sentences, added))
                except ContractError as exc:
                    errors.append(f"{element.get('id', '?')}: span {k}: {exc}")
            element["sourceSpans"] = _dedupe_spans(resolved)
            for n, point in enumerate(element.get("points") or [], 1):
                if not isinstance(point, dict):
                    continue
                spans = []
                for k, span in enumerate(point.get("sourceSpans") or [], 1):
                    try:
                        spans.append(resolve_span(span, text, sentences, added))
                    except ContractError as exc:
                        errors.append(f"{element.get('id', '?')}: point {n}: span {k}: {exc}")
                point["sourceSpans"] = _dedupe_spans(spans)
    head = ("version", "sourceText", "summary", "nodes", "relations", "metadata")
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
            errors.append(f"{name}: span {k} is a draft span; run `semantic_structure.py resolve`")
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
    """An element's own spans plus those of its points."""
    out = list(el.get("sourceSpans") or [])
    for point in el.get("points") or []:
        if isinstance(point, dict):
            out += list(point.get("sourceSpans") or [])
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

    node_by_id = {el["id"]: el for kind, el in elements if kind == "node"}
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

        points = el.get("points")
        if points is not None:
            if kind != "node":
                errors.append(f"{name}: points are for nodes only")
            elif not isinstance(points, list):
                errors.append(f"{name}: points must be a list")
            else:
                for n, point in enumerate(points, 1):
                    where = f"{name}: point {n}"
                    if not isinstance(point, dict) or not isinstance(point.get("label"), str) or not point["label"].strip():
                        errors.append(f"{where} needs a non-empty label")
                        continue
                    if "when" in point and not isinstance(point["when"], str):
                        errors.append(f"{where}: when must be a string")
                    pprov = point.get("provenance", prov)
                    if pprov not in PROVENANCE:
                        errors.append(f"{where}: provenance must be one of {', '.join(PROVENANCE)}")
                    if not _check_spans(point.get("sourceSpans", []), where, text, errors) and pprov == "explicit":
                        warnings.append(f"{where} ({point['label']!r}) has no sourceSpans - point at the words that state it")
        if "polarity" in el and (kind != "relation" or el["polarity"] not in ("+", "-")):
            errors.append(f"{name}: polarity is for relations and must be \"+\" or \"-\"")
        if "move" in el and (kind != "relation" or el["move"] not in MOVES):
            errors.append(f"{name}: move is for relations and must be one of {', '.join(MOVES)}")
        if "targetPoints" in el:
            picked = el["targetPoints"]
            target = node_by_id.get(el.get("target"), {})
            count = len(target.get("points") or []) if isinstance(target.get("points"), list) else 0
            if kind != "relation" or el.get("move") not in OVERTURN:
                errors.append(f"{name}: targetPoints is for replaces and rejects lines")
            elif (not isinstance(picked, list) or not picked or len(set(map(repr, picked))) != len(picked)
                  or not all(type(k) is int and 1 <= k <= count for k in picked)):
                errors.append(f"{name}: targetPoints must list numbers of the target's points, 1 to {count}")
        if "question" in el and (kind != "node" or not isinstance(el["question"], bool)):
            errors.append(f"{name}: question is for nodes and must be true or false")
        if "update" in el and (type(el["update"]) is not int or el["update"] < 1):
            errors.append(f"{name}: update must be a positive integer (append writes it)")
        if "role" in el and not isinstance(el["role"], str):
            errors.append(f"{name}: role must be a string")
        elif el.get("role") == "key" and not el.get("note"):
            warnings.append(f"{name}: a key chunk should say in its note what in the text shows its weight")

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
            if el.get("move") == "answers" and node_by_id.get(el.get("target"), {}).get("question") is not True:
                warnings.append(f"{name}: answers {el.get('target')!r}, which is not marked question: true")
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

    summary = model.get("summary")
    if summary is not None:
        if not isinstance(summary, list) or not summary:
            errors.append("summary must be a non-empty list of {text, refs} parts")
        else:
            for k, part in enumerate(summary, 1):
                if not isinstance(part, dict) or not isinstance(part.get("text"), str) or not part["text"]:
                    errors.append(f"summary part {k} needs a non-empty text")
                    continue
                refs = part.get("refs", [])
                if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
                    errors.append(f"summary part {k}: refs must be a list of node ids")
                    continue
                for r in refs:
                    if kinds.get(r) != "node":
                        errors.append(f"summary part {k}: refs {r!r} must be a node id")
            if not any(isinstance(p, dict) and p.get("refs") for p in summary):
                warnings.append("summary refers to no node - point each phrase at the chunks it stands for")

    parents = {el["id"]: el.get("parent") for kind, el in elements if kind == "node"}
    for start in parents:
        seen, cur = set(), start
        while cur is not None and cur in parents and cur not in seen:
            seen.add(cur)
            cur = parents.get(cur)
        if cur is not None and cur in seen and cur == start:
            errors.append(f"node {start}: parent chain loops back to itself")

    if not errors:
        loop = _overturn_loop(model)
        if loop:
            errors.append("replaces/rejects lines loop: " + " → ".join(loop) + " - a chunk cannot be taken out by "
                          "what it takes out; to go back to an earlier chunk, add a chunk for the return that "
                          "replaces the one in force")
    if not errors and any(isinstance(r, dict) and r.get("move") for r in lists["relations"]):
        st = model_state(model)
        for nid in list(st["out"]) + list(st["outWith"]):
            if node_by_id[nid].get("role") in ("conclusion", "key"):
                warnings.append(f"node {nid}: marked {node_by_id[nid]['role']} but it is out; "
                                "mark what holds now (append can move a role)")
        for k, part in enumerate(summary or [], 1):
            gone = [r for r in part.get("refs") or [] if r in st["out"] or r in st["outWith"]]
            if gone:
                warnings.append(f"summary part {k} refers to {', '.join(gone)}, which is out; say what holds now")

    if text and not errors:
        covered = [False] * len(text)
        for _, el in elements:
            for span in all_spans(el):
                for p in range(span["start"], span["end"]):
                    covered[p] = True
        gaps = [f"S{k} {_clip(text[s:e], 20)!r}" for k, (s, e) in enumerate(split_sentences(text), 1)
                if not any(covered[s:e])]
        if gaps:
            warnings.append(f"{len(gaps)} sentence(s) no span touches - a prompt to check for something lost, "
                            f"not a quota: " + ", ".join(gaps))
    return errors, warnings


# ---------------------------------------------------------------- state


def _takes_out(r):
    """A replaces or rejects line that takes out its whole target (not only some of its points)."""
    return r.get("move") in OVERTURN and not r.get("targetPoints")


def _overturn_loop(model):
    """A loop of lines that take chunks out (with parts falling with their parent), as a list of ids, or None."""
    step = {}
    for n in model["nodes"]:
        if n.get("parent"):
            step.setdefault(n["parent"], []).append(n["id"])
    for r in model["relations"]:
        if _takes_out(r):
            step.setdefault(r["source"], []).append(r["target"])
    color, path = {}, []

    def visit(v):
        color[v] = 1
        path.append(v)
        for w in step.get(v, []):
            if color.get(w) == 1:
                return path[path.index(w):] + [w]
            if not color.get(w):
                found = visit(w)
                if found:
                    return found
        path.pop()
        color[v] = 2
        return None

    for n in model["nodes"]:
        if not color.get(n["id"]):
            found = visit(n["id"])
            if found:
                return found
    return None


def model_state(model):
    """What holds now, from the lines that move the text on (`move`: replaces, rejects, answers).

    A chunk is out once a replaces or rejects line comes into it, and its parts go with it. It stays out
    even if what took it out is out later: to go back to it, a chunk for the return replaces the one in
    force. A line with targetPoints takes out only those points. A question is open while no chunk in
    force answers it. Returns
      out       {node id: [ids of the lines that took it out]}
      outWith   {node id: the id of the out chunk it is part of}
      outPoints {node id in force: {point index from 0: [line ids]}}
      inForce   [node ids, in model order]
      open      [ids of the questions in force that nothing in force answers]
    """
    nodes = {n["id"]: n for n in model["nodes"]}
    out, out_points = {}, {}
    for r in model["relations"]:
        if r.get("move") not in OVERTURN:
            continue
        if r.get("targetPoints"):
            for k in r["targetPoints"]:
                out_points.setdefault(r["target"], {}).setdefault(k - 1, []).append(r["id"])
        else:
            out.setdefault(r["target"], []).append(r["id"])
    out_with = {}
    for nid, n in nodes.items():
        if nid in out:
            continue
        seen, up = set(), n.get("parent")
        while up in nodes and up not in seen:
            if up in out:
                out_with[nid] = up
                break
            seen.add(up)
            up = nodes[up].get("parent")
    gone = set(out) | set(out_with)
    in_force = [nid for nid in nodes if nid not in gone]
    answered = {r["target"] for r in model["relations"] if r.get("move") == "answers" and r["source"] not in gone}
    return {
        "out": out,
        "outWith": out_with,
        "outPoints": {nid: pts for nid, pts in out_points.items() if nid not in gone},
        "inForce": in_force,
        "open": [nid for nid in in_force if nodes[nid].get("question") is True and nid not in answered],
    }


def review_signs(model, st=None):
    """Signs that the structure no longer fits what holds now and should be rebuilt from the whole."""
    st = st or model_state(model)
    nodes = {n["id"]: n for n in model["nodes"]}
    gone = set(st["out"]) | set(st["outWith"])
    signs = []
    moved = [nid for nid in st["out"] if nodes[nid].get("question") is True]
    if moved:
        signs.append("the question moved: " + "; ".join(f"{nodes[q]['label']!r} is out" for q in moved))
    last = max((n.get("update", 0) for n in model["nodes"] if type(n.get("update")) is int), default=0)
    if last:
        added = {nid for nid, n in nodes.items() if n.get("update") == last}
        earlier = set(nodes) - added
        touches = any((r["source"] in added) != (r["target"] in added) for r in model["relations"]
                      if r["source"] in nodes and r["target"] in nodes)
        touches = touches or any(nodes[nid].get("parent") in earlier for nid in added)
        if added and earlier and not touches:
            signs.append(f"update {last} added {len(added)} chunk(s) with no line to the earlier ones: "
                         "the session may have moved to another question")
    if len(nodes) >= 4 and len(gone) * 2 > len(nodes):
        signs.append(f"{len(gone)} of {len(nodes)} chunks are out: the chunks follow the history more than what holds now")
    for nid, pts in st["outPoints"].items():
        total = len(nodes[nid].get("points") or [])
        if len(pts) >= 2 and len(pts) * 2 >= total:
            signs.append(f"{len(pts)} of the {total} points of {nodes[nid]['label']!r} are out: the chunk no longer fits")
    if len(model["sourceText"]) > LONG_TEXT:
        signs.append(f"the text is {len(model['sourceText']):,} characters, over about {LONG_TEXT:,}")
    return signs


def state_report(model):
    st = model_state(model)
    nodes = {n["id"]: n for n in model["nodes"]}
    gone = set(st["out"]) | set(st["outWith"])
    order = note_order(model)
    number = {nid: num for nid, num, _ in order}
    outgoing = {}
    for r in model["relations"]:
        outgoing.setdefault(r["source"], []).append(r)
    last = max((n.get("update", 0) for n in model["nodes"] if type(n.get("update")) is int), default=0)

    def name(nid):
        return f"{number[nid]} {nodes[nid]['label']}"

    def took(r):
        what = name(r["target"])
        if r.get("targetPoints"):
            pts = nodes[r["target"]].get("points") or []
            what += ": " + " / ".join(pts[k - 1]["label"] for k in r["targetPoints"])
        return f"{what} ({r.get('label') or r['type']})"

    out = ["# State: what holds now", "",
           "Read this as someone who will act on it: what holds, what was set aside and why, what is still open.", "",
           f"{len(st['inForce'])} of {len(nodes)} chunks in force, {len(st['open'])} open question(s), {len(gone)} out.", ""]
    if model.get("summary"):
        out += ["## Summary", "", "".join(part["text"] for part in model["summary"]), ""]
    out += ["## In force", ""]
    for nid, num, depth in order:
        if nid in gone:
            continue
        n, pad = nodes[nid], "    " * depth
        mark = ("★ " if n.get("role") == "conclusion" else "◆ " if n.get("role") == "key" else "") \
            + ("? " if nid in st["open"] else "")
        new = "  [new]" if last and n.get("update") == last else ""
        out.append(f"{pad}{mark}{num} {n['label']}{new}")
        struck = st["outPoints"].get(nid, {})
        for k, pt in enumerate(n.get("points") or []):
            out.append(f"{pad}    - {'✕ ' if k in struck else ''}{pt['label']}")
        for r in outgoing.get(nid, []):
            if r.get("move") in OVERTURN:
                out.append(f"{pad}    ✕ {r['move']} {took(r)}")
            elif r.get("move") == "answers":
                out.append(f"{pad}    ✓ answers {name(r['target'])}")
    if st["open"]:
        out += ["", "## Open questions", ""] + [f"- {name(q)}" for q in st["open"]]
    if gone:
        out += ["", "## Out", ""]
        rels = {r["id"]: r for r in model["relations"]}
        for nid, num, _ in order:
            if nid in st["out"]:
                done = {"replaces": "replaced", "rejects": "rejected"}
                by = "; ".join(f"{done[rels[rid]['move']]} by {name(rels[rid]['source'])} ({rels[rid].get('label') or rels[rid]['type']})"
                               for rid in st["out"][nid])
                out.append(f"- ✕ {name(nid)}: {by}")
            elif nid in st["outWith"]:
                out.append(f"- ✕ {name(nid)}: with {name(st['outWith'][nid])}")
    signs = review_signs(model, st)
    out += ["", "## Review", ""]
    out += [f"- {s}" for s in signs] if signs else ["No sign that a full review is due."]
    if signs:
        out += ["", "Rebuild from the whole when the user agrees, or when they ask to sum up."]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- append


def append_model(model, drafts, source_text):
    """Return (model, errors, warnings, report): the model with the drafts' new chunks and lines added.

    The source must be the model's text with text added at its end, so the spans already there stay
    put. Nothing in the model is re-cut: an id it already has is an error, except a node entry with
    only `id` and `role`, which moves a role (null removes it). The drafts' summary replaces the
    model's, and their metadata is merged over it. Every element added gets `update`: the count of updates.
    """
    old = model["sourceText"]
    text = normalize_text(source_text)
    if not text.startswith(old):
        return model, ["the source must be the model's text with new text added at its end; "
                       "to change the text before it, rebuild with resolve"], [], ""
    try:
        draft, warnings = merge_drafts(drafts)
    except ContractError as exc:
        return model, [str(exc)], [], ""
    errors = []
    kinds = {el["id"]: kind for kind in ("nodes", "relations") for el in model[kind]}
    fresh, roles = {"nodes": [], "relations": []}, []
    for kind in ("nodes", "relations"):
        for el in draft[kind]:
            eid = el.get("id") if isinstance(el, dict) else None
            if eid not in kinds:
                fresh[kind].append(el)
            elif kind == "nodes" and kinds[eid] == "nodes" and set(el) == {"id", "role"}:
                roles.append((eid, el["role"]))
            else:
                errors.append(f"{eid}: already in the model. append adds chunks and lines and never changes them "
                              "(a node entry with only id and role moves a role); to re-cut, rebuild with resolve")
    added, errs = resolve_model({**fresh, "metadata": {}}, text, added=len(old))
    errors += errs
    update = 1 + max((el.get("update", 0) for kind in ("nodes", "relations") for el in model[kind]
                      if type(el.get("update")) is int), default=0)
    result = json.loads(json.dumps(model, ensure_ascii=False))
    result["sourceText"] = text
    for kind in ("nodes", "relations"):
        for el in added[kind]:
            if isinstance(el, dict):
                el["update"] = update
            result[kind].append(el)
    by_id = {n["id"]: n for n in result["nodes"]}
    for eid, role in roles:
        if role is None:
            by_id[eid].pop("role", None)
        else:
            by_id[eid]["role"] = role
    if "summary" in draft:
        result["summary"] = draft["summary"]
    elif result.get("summary"):
        warnings.append("the summary is the one from before this update; say what the whole comes to now")
    result.setdefault("metadata", {}).update(draft.get("metadata") or {})
    for key, value in draft.items():
        if key not in ("nodes", "relations", "metadata", "summary", "sourceText", "version"):
            result[key] = value
    if not errors:
        more_errors, more = validate_model(result)
        errors += more_errors
        warnings += more
    n_nodes, n_rels = len(fresh["nodes"]), len(fresh["relations"])
    report = (f"update {update}: {len(text) - len(old):,} characters of text added; "
              f"{n_nodes} chunk(s) and {n_rels} line(s) added" + (f"; {len(roles)} role(s) moved" if roles else ""))
    if not (n_nodes or n_rels or roles or len(text) > len(old)):
        warnings.append("nothing was added")
    return result, errors, warnings, report


# ---------------------------------------------------------------- summary


def _coverage(model):
    covered = [False] * len(model["sourceText"])
    for el in model["nodes"] + model["relations"]:
        for span in all_spans(el):
            for p in range(span["start"], span["end"]):
                covered[p] = True
    return covered


def summarize(model):
    text = model["sourceText"]
    nodes, relations = model["nodes"], model["relations"]
    by_id = {el["id"]: el for el in nodes + relations}
    covered = _coverage(model)
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
    out = [f"# Semantic Structure summary{': ' + title if title else ''}", ""]
    out.append(f"- Source: {len(text)} characters, {len(sentences)} sentences; "
               f"{ratio:.0%} of non-space characters fall inside some span")
    out.append(f"- Nodes: {len(nodes)} ({count(nodes)})")
    out.append(f"- Relations: {len(relations)} ({count(relations)})")
    if model.get("summary"):
        out.append(f"- Summary: {''.join(part['text'] for part in model['summary'])}")
    out += ["", "## Nodes", "", "| id | label | type | parent | provenance | spans |", "|---|---|---|---|---|---|"]
    for n in nodes:
        out.append(f"| {cell(n['id'])} | {cell(n['label'])} | {cell(n['type'])} | {cell(n.get('parent', ''))} "
                   f"| {n['provenance']} | {cell(quotes(n))} |")
    noted = [n for n in nodes if n.get("points")]
    if noted:
        out += ["", "## Points", "", "| node | when | point | provenance | spans |", "|---|---|---|---|---|"]
        for n in noted:
            for pt in n["points"]:
                out.append(f"| {cell(n['label'])} | {cell(pt.get('when', ''))} | {cell(pt['label'])} "
                           f"| {pt.get('provenance', n['provenance'])} | {cell(quotes(pt))} |")
    out += ["", "## Relations", "", "| id | relation | provenance | spans |", "|---|---|---|---|"]
    for r in relations:
        src = by_id.get(r["source"], {}).get("label", r["source"])
        tgt = by_id.get(r["target"], {}).get("label", r["target"])
        arrow = "—" if r.get("directed", True) is False else "→"
        word = (r.get("label") or r["type"]) + (f" [{r['move']}]" if r.get("move") else "")
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


def note_order(model):
    """The notes in reading order: [(id, number, depth)].

    Nodes keep their order in `nodes`; a node's parts follow it and are numbered
    under it (2, 2.1, 2.2). The viewer numbers the cards the same way.
    """
    ids = {n["id"] for n in model["nodes"]}
    children, roots = {}, []
    for n in model["nodes"]:
        if n.get("parent") in ids:
            children.setdefault(n["parent"], []).append(n["id"])
        else:
            roots.append(n["id"])
    out = []

    def walk(nid, number, depth):
        out.append((nid, number, depth))
        for k, child in enumerate(children.get(nid, []), 1):
            walk(child, f"{number}.{k}", depth + 1)

    for k, root in enumerate(roots, 1):
        walk(root, str(k), 0)
    return out


def _sentence_list(spans, sentences):
    """Which sentences some span touches, as "S2, S31-39"."""
    hit = [k for k, (s, e) in enumerate(sentences, 1) if any(sp["start"] < e and s < sp["end"] for sp in spans)]
    runs = []
    for k in hit:
        if runs and k == runs[-1][1] + 1:
            runs[-1][1] = k
        else:
            runs.append([k, k])
    return ", ".join(f"S{a}" if a == b else f"S{a}-{b}" for a, b in runs)


def outline(model):
    text = model["sourceText"]
    sentences = split_sentences(text)
    nodes = {n["id"]: n for n in model["nodes"]}
    order = note_order(model)
    number = {nid: num for nid, num, _ in order}
    incoming, outgoing = {}, {}
    for r in model["relations"]:
        outgoing.setdefault(r["source"], []).append(r)
        incoming.setdefault(r["target"], []).append(r)

    def prov(el):
        return "" if el.get("provenance", "explicit") == "explicit" else f" [{el['provenance']}]"

    def word(r):
        move = f" [{r['move']}]" if r.get("move") else ""
        return (r.get("label") or r["type"]) + {"+": " (+)", "-": " (-)"}.get(r.get("polarity"), "") + move + prov(r)

    st = model_state(model)
    gone = set(st["out"]) | set(st["outWith"])
    covered = _coverage(model)
    out = ["# Notes: the model read back", "",
           "Read this without the text. It should tell what the text means, not retell it part by part:",
           "the summary says what the text comes to in one sentence; each chunk says one meaning and keeps",
           "what it rests on (numbers, conditions, timing, who); the arrows say how the meanings bear on",
           "each other, toward what the text comes to.", "",
           f"{len(nodes)} nodes, {len(model['relations'])} relations."
           + (f" ✕ marks what is out, ? an open question; `state` reads back only what holds now." if gone or st["open"] else ""), ""]

    summary = model.get("summary")
    if summary:
        out += ["## Summary", "", "".join(part["text"] for part in summary), ""]
        out += [f"- 「{part['text']}」 → " + ", ".join(f"{number[r]} {nodes[r]['label']}" for r in part["refs"])
                for part in summary if part.get("refs")]
        out.append("")

    out += ["## Notes", ""]
    for nid, num, depth in order:
        n = nodes[nid]
        pad = "    " * depth
        where = _sentence_list(n.get("sourceSpans") or [], sentences) or "no words of its own"
        star = "★ " if n.get("role") == "conclusion" else "◆ " if n.get("role") == "key" else ""
        star = ("✕ " if nid in gone else "? " if nid in st["open"] else "") + star
        out.append(f"{pad}{star}{num} {n['label']}{prov(n)}  ({where})")
        for k, pt in enumerate(n.get("points") or []):
            when = f"{pt['when']}: " if pt.get("when") else ""
            struck = "✕ " if k in st["outPoints"].get(nid, {}) else ""
            out.append(f"{pad}    - {struck}{when}{pt['label']}{prov(pt)}")
        for r in incoming.get(nid, []):
            arrow = "—" if r.get("directed", True) is False else "←"
            out.append(f"{pad}    {arrow} {number[r['source']]} {nodes[r['source']]['label']}: {word(r)}")
        for r in outgoing.get(nid, []):
            arrow = "—" if r.get("directed", True) is False else "→"
            out.append(f"{pad}    {arrow} {number[r['target']]} {nodes[r['target']]['label']}: {word(r)}")

    gaps = [(k, s, e) for k, (s, e) in enumerate(sentences, 1) if not any(covered[s:e])]
    if gaps:
        out += ["", "## Sentences no span touches", "",
                "Look here only for something that matters and is missing; a sentence need not be covered.", ""]
        out += [f"- S{k}: {_clip(text[s:e], 80)}" for k, s, e in gaps]
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
    p.add_argument("--after", metavar="MODEL", help="show only the sentences added since MODEL was built")
    p = sub.add_parser("resolve", help="merge drafts, turn quote spans into offsets and validate")
    p.add_argument("drafts", nargs="+")
    p.add_argument("--source", help="the source text file (sets sourceText)")
    p.add_argument("-o", "--output", required=True)
    p = sub.add_parser("append", help="add chunks and lines for text added at the end of the source")
    p.add_argument("model")
    p.add_argument("drafts", nargs="+")
    p.add_argument("--source", required=True, help="the source text: the model's text with the new text at its end")
    out = p.add_mutually_exclusive_group(required=True)
    out.add_argument("-o", "--output")
    out.add_argument("--check", action="store_true", help="write nothing; read back what would hold after the update")
    p = sub.add_parser("validate", help="check a model against the contract")
    p.add_argument("model")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("outline", help="read the notes back: summary, chunks, points, relations")
    p.add_argument("model")
    p = sub.add_parser("state", help="what holds now, what is out and why, the open questions, and whether to review")
    p.add_argument("model")
    p = sub.add_parser("summary", help="print a Markdown overview of a model")
    p.add_argument("model")
    args = parser.parse_args(argv)

    if args.command == "sentences":
        text = normalize_text(Path(args.source).read_text(encoding="utf-8"))
        ranges = list(enumerate(split_sentences(text), 1))
        if args.after:
            built = _read_json(args.after).get("sourceText") or ""
            if not text.startswith(built):
                sys.exit(f"{args.source} does not start with the text {args.after} was built on")
            ranges = [(k, (s, e)) for k, (s, e) in ranges if s >= len(built)]
        if args.json:
            print(json.dumps([{"sentence": k, "start": s, "end": e, "text": text[s:e]}
                              for k, (s, e) in ranges], ensure_ascii=False, indent=2))
        else:
            for k, (s, e) in ranges:
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

    if args.command == "append":
        model = _read_json(args.model)
        errors, warnings = validate_model(model)
        if errors:
            _report(errors, warnings)
            print(f"{args.model} has errors; {args.output} not written")
            return 1
        drafts = [_read_json(path) for path in args.drafts]
        model, errors, warnings, report = append_model(model, drafts, Path(args.source).read_text(encoding="utf-8"))
        _report(errors, warnings)
        if errors:
            print("nothing written" if args.check else f"{args.output} not written")
            return 1
        if args.check:
            print(f"{report}; nothing written\n")
            sys.stdout.write(state_report(model))
            return 0
        Path(args.output).write_text(dumps(model) + "\n", encoding="utf-8")
        print(f"{report}\nwrote {args.output}")
        return 0

    model = _read_json(args.model)
    errors, warnings = validate_model(model)
    if args.command == "validate":
        _report(errors, warnings, args.json)
        return 1 if errors else 0
    if errors:
        _report(errors, warnings)
        return 1
    sys.stdout.write({"outline": outline, "state": state_report, "summary": summarize}[args.command](model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
