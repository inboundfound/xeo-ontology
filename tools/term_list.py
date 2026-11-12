#!/usr/bin/env python3
"""Compare the ontology's terms, and everything said about them, with another version.

A repackaging moves terms between module files and must change nothing else.
This proves it. It reads every xeo-*.ttl module here and at a git ref, and
reports three things:

  TERMS     every xeo: IRI declared with a type (class, property, individual),
            with its type. Must be identical on both sides, after renames.
  TRIPLES   every statement in every module, except the module headers (the
            owl:Ontology nodes, which name the file and not a term). Compared
            as graphs, so blank nodes and statement order do not matter.
  MOVES     which file each term's declaration sits in on each side. Reported,
            never a failure: moving terms is the point of a repackaging.

    python tools/term_list.py                        # print the term list
    python tools/term_list.py --against origin/main  # compare with a ref
    python tools/term_list.py --against v0.6 --rename epistemicLayer=xeoLayer
    python tools/term_list.py --against v0.6 --terms-only   # terms, not triples

--rename old=new treats xeo:old on the other side as xeo:new on this side, so a
deliberate rename is not reported as one term removed and another added.
--terms-only skips the triple comparison, for a change that edits what a term
says but neither adds nor removes a term.

Exits non-zero when the terms differ, or (without --terms-only) the triples do.
Requires rdflib.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys

from rdflib import Graph, Literal, OWL, RDF, URIRef
from rdflib.compare import graph_diff, to_isomorphic

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XEO = "https://xeoontology.org/xeo#"


def sources_here() -> dict[str, str]:
    """{file name: Turtle} for every module in the working tree."""
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, "xeo-*.ttl"))):
        with open(path, encoding="utf-8") as fh:
            out[os.path.basename(path)] = fh.read()
    return out


def sources_at(ref: str) -> dict[str, str]:
    """{file name: Turtle} for every module at a git ref."""
    names = subprocess.run(["git", "-C", HERE, "ls-tree", "--name-only", ref],
                           check=True, capture_output=True, text=True).stdout.split()
    out = {}
    for name in sorted(n for n in names if n.startswith("xeo-") and n.endswith(".ttl")):
        out[name] = subprocess.run(["git", "-C", HERE, "show", f"{ref}:{name}"],
                                   check=True, capture_output=True, text=True).stdout
    return out


def renamer(renames: dict[str, str]):
    def fix(t):
        if isinstance(t, URIRef) and str(t).startswith(XEO):
            local = str(t)[len(XEO):]
            if local in renames:
                return URIRef(XEO + renames[local])
        return t
    return fix


def load(sources: dict[str, str], renames: dict[str, str]):
    """(graph without module headers, {term: kinds}, {term: declaring files})."""
    fix = renamer(renames)
    merged, kinds, home = Graph(), {}, {}
    for name, text in sources.items():
        g = Graph()
        g.parse(data=text, format="turtle")
        headers = set(g.subjects(RDF.type, OWL.Ontology))
        for s, p, o in g:
            if s in headers:
                continue
            s, p, o = fix(s), fix(p), fix(o)
            merged.add((s, p, o))
            if p == RDF.type and isinstance(s, URIRef) and str(s).startswith(XEO):
                kinds.setdefault(s, set()).add(o)
                home.setdefault(s, set()).add(name)
    return merged, kinds, home


def short(t) -> str:
    s = str(t)
    for prefix, ns in (("xeo:", XEO), ("owl:", str(OWL)), ("rdf:", str(RDF))):
        if s.startswith(ns):
            return prefix + s[len(ns):]
    return s


def term_lines(kinds) -> list[str]:
    return sorted(f"{short(t)}  {' '.join(sorted(short(k) for k in ks))}" for t, ks in kinds.items())


def show(triple) -> str:
    s, p, o = triple
    obj = repr(str(o))[:90] if isinstance(o, Literal) else short(o)
    return f"{short(s)} {short(p)} {obj}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--against", metavar="REF", help="git ref to compare with")
    ap.add_argument("--rename", action="append", default=[], metavar="OLD=NEW",
                    help="a deliberate rename of a term (repeatable)")
    ap.add_argument("--terms-only", action="store_true", help="compare the term list only")
    a = ap.parse_args()

    here_graph, here_kinds, here_home = load(sources_here(), {})
    if not a.against:
        print("\n".join(term_lines(here_kinds)))
        print(f"\n{len(here_kinds)} terms")
        return 0

    renames = dict(r.split("=", 1) for r in a.rename)
    there_graph, there_kinds, there_home = load(sources_at(a.against), renames)
    failures = 0

    # TERMS
    here_lines, there_lines = set(term_lines(here_kinds)), set(term_lines(there_kinds))
    gone, new = sorted(there_lines - here_lines), sorted(here_lines - there_lines)
    if gone or new:
        failures += 1
        print(f"FAIL  terms: {len(gone)} only at {a.against}, {len(new)} only here")
        for line in gone:
            print(f"        - {line}")
        for line in new:
            print(f"        + {line}")
    else:
        print(f"ok    terms: the same {len(here_lines)} terms as {a.against}"
              + (f", after renaming {', '.join(a.rename)}" if a.rename else ""))

    # TRIPLES
    if not a.terms_only:
        _, only_there, only_here = graph_diff(to_isomorphic(there_graph), to_isomorphic(here_graph))
        if len(only_there) or len(only_here):
            failures += 1
            print(f"FAIL  triples: {len(only_there)} only at {a.against}, {len(only_here)} only here")
            for t in sorted(show(t) for t in only_there)[:40]:
                print(f"        - {t}")
            for t in sorted(show(t) for t in only_here)[:40]:
                print(f"        + {t}")
        else:
            print(f"ok    triples: the same {len(here_graph)} statements as {a.against}, module headers aside")

    # MOVES
    moves = sorted((short(t), ",".join(sorted(there_home[t])), ",".join(sorted(here_home[t])))
                   for t in here_home if t in there_home and here_home[t] != there_home[t])
    print(f"note  {len(moves)} terms declared in a different file than at {a.against}")
    for term, before, after in moves:
        print(f"        {term}: {before} -> {after}")

    print("\nFAILED" if failures else "\nPASSED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
