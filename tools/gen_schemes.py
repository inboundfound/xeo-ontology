#!/usr/bin/env python3
"""Generate schemes.json — the reference schemes as plain JSON.

weo-schemes.ttl is the source of truth: SKOS concept schemes filling the slots
the ontology leaves open (gapType, atPriority, inIntervention, status, ...).
Nobody should parse Turtle at boot to build a JSON Schema enum, so this
projects the same schemes to JSON, the way context.jsonld ships a
machine-friendly projection beside the TTL.

Every concept's ``code`` is its skos:notation — the exact string a system
stores or sends. ``label`` is skos:prefLabel, what an operator reads.
Ordered schemes (a lifecycle, a priority ladder) come out in their
skos:OrderedCollection order and carry ``"ordered": true``.

Requires rdflib (``pip install rdflib``).
Usage:  python tools/gen_schemes.py        # writes schemes.json
"""
import json
import os

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, SKOS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "weo-schemes.ttl")
DEST = os.path.join(HERE, "schemes.json")

WEO = Namespace("https://inboundfound.github.io/weo-ontology/weo#")
WEOS = Namespace("https://inboundfound.github.io/weo-ontology/schemes#")


def local(iri: URIRef) -> str:
    return str(iri).split("#", 1)[1]


def curie(iri: URIRef) -> str:
    s = str(iri)
    if s.startswith(str(WEO)):
        return "weo:" + local(iri)
    if s.startswith(str(WEOS)):
        return "weos:" + local(iri)
    return s


def text(g: Graph, s: URIRef, p: URIRef) -> str | None:
    v = g.value(s, p)
    return str(v) if v is not None else None


def main() -> int:
    g = Graph()
    g.parse(SRC, format="turtle")

    module = g.value(predicate=RDF.type, object=OWL.Ontology)
    version = text(g, module, OWL.versionInfo) if module else None

    schemes: dict[str, dict] = {}
    for scheme in sorted(g.subjects(RDF.type, SKOS.ConceptScheme), key=local):
        # Concepts: every skos:inScheme member that is a Concept (collections
        # also point inScheme, so filter on type).
        members = [
            c for c in g.subjects(SKOS.inScheme, scheme)
            if (c, RDF.type, SKOS.Concept) in g
        ]
        ordered = False
        for coll in g.subjects(SKOS.inScheme, scheme):
            if (coll, RDF.type, SKOS.OrderedCollection) in g:
                head = g.value(coll, SKOS.memberList)
                listed = list(Collection(g, head)) if head is not None else []
                if listed:
                    # Keep list order; append any straggler not in the list.
                    rest = [c for c in members if c not in listed]
                    members = listed + sorted(rest, key=local)
                    ordered = True
                break
        if not ordered:
            members.sort(key=lambda c: str(g.value(c, SKOS.notation)))

        concepts = []
        for c in members:
            concepts.append({
                "code": text(g, c, SKOS.notation),
                "iri": str(c),
                "label": text(g, c, SKOS.prefLabel),
                "definition": text(g, c, SKOS.definition),
                "note": text(g, c, SKOS.note),
            })

        fills = g.value(scheme, WEO.fillsSlot)
        schemes[local(scheme)] = {
            "iri": str(scheme),
            "label": text(g, scheme, SKOS.prefLabel),
            "fillsSlot": curie(fills) if fills is not None else None,
            "description": text(g, scheme, DCTERMS.description),
            "source": text(g, scheme, DCTERMS.source),
            "ordered": ordered,
            "concepts": concepts,
        }

    out = {
        "$comment": "Generated from weo-schemes.ttl by tools/gen_schemes.py — do not edit by hand.",
        "namespace": str(WEOS),
        "ontology": str(WEO),
        "version": version,
        "schemes": schemes,
    }
    with open(DEST, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    n = sum(len(s["concepts"]) for s in schemes.values())
    print(f"wrote {DEST}  ({len(schemes)} schemes, {n} concepts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
