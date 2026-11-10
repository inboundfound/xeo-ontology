#!/usr/bin/env python3
"""Generate schemes.json — the reference schemes as plain JSON.

xeo-schemes.ttl is the source of truth: SKOS concept schemes filling the slots
the ontology leaves open (gapType, atPriority, inIntervention, status, ...).
Nobody should parse Turtle at boot to build a JSON Schema enum, so this
projects the same schemes to JSON, the way context.jsonld ships a
machine-friendly projection beside the TTL.

Every concept's ``code`` is its skos:notation — the exact string a system
stores or sends. ``label`` is skos:prefLabel, what an operator reads.
Ordered schemes (a lifecycle, a priority ladder) come out in their
skos:OrderedCollection order and carry ``"ordered": true``.

Two files are read. xeo-schemes.ttl holds the reference fillings and comes out
under ``"schemes"``. xeo-vendor-schemes.ttl holds the per-vendor crosswalks and
comes out under ``"vendorSchemes"``, where each concept also carries the slot it
fills, its match, a scope note, its source and its mapping confidence.

A concept gains further keys only where the Turtle states them, so a concept
with nothing extra reads exactly as it always has:
    "altLabels"       skos:altLabel
    "status"          xeo:termStatus ("extension")
    "matches"         {"exactMatch": [...], "closeMatch": [...], ...}
    "editorialNote"   skos:editorialNote
    "metric"          for an xeo:Metric: its type, unit, direction, additivity
                      and what it is computed from, as codes

Requires rdflib (``pip install rdflib``).
Usage:  python tools/gen_schemes.py        # writes schemes.json
"""
import json
import os

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, SKOS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "xeo-schemes.ttl")
VENDOR_SRC = os.path.join(HERE, "xeo-vendor-schemes.ttl")
DEST = os.path.join(HERE, "schemes.json")

XEO = Namespace("https://xeoontology.org/xeo#")
XEOS = Namespace("https://xeoontology.org/schemes#")


def local(iri: URIRef) -> str:
    return str(iri).split("#", 1)[1]


def curie(iri: URIRef) -> str:
    s = str(iri)
    if s.startswith(str(XEO)):
        return "xeo:" + local(iri)
    if s.startswith(str(XEOS)):
        return "xeos:" + local(iri)
    return s


def text(g: Graph, s: URIRef, p: URIRef) -> str | None:
    v = g.value(s, p)
    return str(v) if v is not None else None


MATCHES = ("exactMatch", "closeMatch", "narrowMatch", "broadMatch", "relatedMatch")
# The definition properties of an xeo:Metric, in the order they are written out.
METRIC_SLOTS = ("metricType", "aggregation", "readsSlot", "numerator", "denominator",
                "inputMetric", "expression", "metricFilter", "timeAnchor", "unit",
                "betterDirection", "additivity", "minDenominator")


def extras(g: Graph, c: URIRef) -> dict:
    """The optional keys of a concept: only what the Turtle states."""
    out: dict = {}
    alts = sorted(str(o) for o in g.objects(c, SKOS.altLabel))
    if alts:
        out["altLabels"] = alts
    status = text(g, c, XEO.termStatus)
    if status:
        out["status"] = status
    matches = {m: sorted(curie(o) for o in g.objects(c, SKOS[m])) for m in MATCHES}
    matches = {m: v for m, v in matches.items() if v}
    if matches:
        out["matches"] = matches
    note = text(g, c, SKOS.editorialNote)
    if note:
        out["editorialNote"] = note
    if (c, RDF.type, XEO.Metric) in g:
        metric = {}
        for slot in METRIC_SLOTS:
            values = []
            for o in sorted(g.objects(c, XEO[slot]), key=str):
                code = g.value(o, SKOS.notation) if isinstance(o, URIRef) else None
                if code is not None:
                    values.append(str(code))        # a concept: its code
                elif isinstance(o, URIRef):
                    values.append(curie(o))         # a property: its CURIE
                else:
                    values.append(o.toPython())     # a literal
            if values:
                metric[slot] = values[0] if len(values) == 1 else values
        out["metric"] = metric
    return out


def read_schemes(g: Graph, lookup: Graph, vendor: bool) -> dict[str, dict]:
    """Every scheme declared in ``g``; ``lookup`` also holds what its concepts point at."""
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
            # Vendor schemes may repeat a notation, so the IRI breaks the tie.
            members.sort(key=lambda c: (str(g.value(c, SKOS.notation)), str(c)))

        concepts = []
        for c in members:
            entry = {
                "code": text(g, c, SKOS.notation),
                "iri": str(c),
                "label": text(g, c, SKOS.prefLabel),
                "definition": text(g, c, SKOS.definition),
                "note": text(g, c, SKOS.note),
            }
            if vendor:
                entry["fillsSlot"] = sorted(curie(o) for o in g.objects(c, XEO.fillsSlot))
                entry["scopeNote"] = text(g, c, SKOS.scopeNote)
                entry["source"] = text(g, c, DCTERMS.source)
                entry["mappingConfidence"] = text(g, c, XEO.mappingConfidence)
            entry.update(extras(lookup, c))
            concepts.append(entry)

        entry = {
            "iri": str(scheme),
            "label": text(g, scheme, SKOS.prefLabel),
            "description": text(g, scheme, DCTERMS.description),
            "source": text(g, scheme, DCTERMS.source),
            "ordered": ordered,
            "concepts": concepts,
        }
        if not vendor:
            fills = g.value(scheme, XEO.fillsSlot)
            entry = {"iri": entry.pop("iri"), "label": entry.pop("label"),
                     "fillsSlot": curie(fills) if fills is not None else None, **entry}
            status = text(g, scheme, XEO.termStatus)
            if status:
                entry["status"] = status
        schemes[local(scheme)] = entry
    return schemes


def build() -> dict:
    """The schemes.json document, as a dict."""
    g = Graph()
    g.parse(SRC, format="turtle")
    vg = Graph()
    vg.parse(VENDOR_SRC, format="turtle")
    both = g + vg

    module = g.value(predicate=RDF.type, object=OWL.Ontology)
    version = text(g, module, OWL.versionInfo) if module else None

    return {
        "$comment": "Generated from xeo-schemes.ttl and xeo-vendor-schemes.ttl by tools/gen_schemes.py — do not edit by hand.",
        "namespace": str(XEOS),
        "ontology": str(XEO),
        "version": version,
        "schemes": read_schemes(g, both, vendor=False),
        "vendorSchemes": read_schemes(vg, both, vendor=True),
    }


def render() -> str:
    """schemes.json exactly as written to disk (tools/validate.py diffs against this)."""
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write(render())

    doc = build()
    for key in ("schemes", "vendorSchemes"):
        n = sum(len(s["concepts"]) for s in doc[key].values())
        print(f"wrote {DEST}  {key}: {len(doc[key])} schemes, {n} concepts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
