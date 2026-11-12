#!/usr/bin/env python3
"""Generate the Neo4j profile — XEO as a property graph reads it.

The Turtle is the source of truth. A property graph does not speak IRIs, so this
projects the ontology onto the three names Neo4j has, by one rule:

    class               ->  node label            URL, SerpSnapshot      (the local name)
    object property     ->  relationship type     linksTo -> LINKS_TO    (UPPER_SNAKE)
    datatype property   ->  property key          avgPosition            (the local name)

and writes three files:

    neo4j-profile.json      every label, relationship type and property key with
                            its IRI, layer and module; the reference
                            schemes as plain code lists. What a consumer vendors
                            and checks its own graph against.
    context.neo4j.jsonld    a JSON-LD @context keyed the way Neo4j names things
                            (labels, UPPER_SNAKE relationship types, property
                            keys), so a Neo4j JSON export lifts to RDF.
    docs/neo4j-profile.md   the mapping tables, between the GENERATED markers.

A concept slot (an object property whose range is skos:Concept) appears twice,
on purpose: as a relationship type, for a graph that keeps concepts as nodes,
and as a property key, for a graph that stores the concept's code on the node
or edge. Both are conformant.

A controlled string (a datatype property with a published scheme: sentiment,
device, metric, dealOutcome) is a property key that lists its schemes. The code
it stores is the skos:notation of a concept in one of them, which is how
MetricTarget.metric names an xeo:Metric without being an object property.

Two optional markers, present only where the Turtle states them, so an entry
without them is a current core term:
    "status": "extension"     the term carries xeo:termStatus "extension"
    "deprecated": true        the term carries owl:deprecated true; advisory,
                              with "replacedBy" naming what rdfs:seeAlso points at

Vendor crosswalks (mappings/, one file per tool) are not in the profile: they map a
vendor's field names to slots and are not values a graph stores. schemes.json
carries them under "vendorSchemes".

Output is deterministic (sorted keys, no timestamps), so tools/validate.py can
regenerate in memory and fail the build when a checked-in file is stale.

Requires rdflib.
Usage:  uv run --no-project --with rdflib python tools/gen_profile.py
"""
from __future__ import annotations

import json
import os
import re

from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, SKOS, XSD

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XEO = Namespace("https://xeoontology.org/xeo#")
XEOS = Namespace("https://xeoontology.org/schemes#")

# Modules that declare terms: core first, then the add-ons, each of which needs only core. xeo-align only bridges and
# xeo-schemes only fills slots; neither declares a class or property a graph
# would carry, so they are read for alignment and values, not for terms.
TERM_MODULES = [
    "xeo-core.ttl", "xeo-visibility.ttl", "xeo-analysis.ttl",
    "xeo-sales.ttl", "xeo-attribution.ttl", "xeo-attribution-sales.ttl",
    "xeo-work.ttl", "xeo-decision.ttl",
]
SCHEMES_MODULE = "xeo-schemes.ttl"
LAYERS = ["entity", "episode", "observation", "derivation", "interpretation", "norm"]

PROFILE_JSON = "neo4j-profile.json"
NEO4J_CONTEXT = "context.neo4j.jsonld"
PROFILE_DOC = os.path.join("docs", "neo4j-profile.md")
BEGIN = "<!-- BEGIN GENERATED: tools/gen_profile.py -->"
END = "<!-- END GENERATED -->"


def local(iri) -> str:
    return str(iri).split("#", 1)[1]


def upper_snake(name: str) -> str:
    """linksTo -> LINKS_TO, hasCanonical -> HAS_CANONICAL, coversUrl -> COVERS_URL."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).upper()


def short(iri) -> str:
    """A class as the profile names it: the local name for XEO, a CURIE otherwise."""
    s = str(iri)
    if s.startswith(str(XEO)):
        return local(iri)
    if s.startswith(str(SKOS)):
        return "skos:" + s[len(str(SKOS)):]
    if s.startswith(str(XSD)):
        return "xsd:" + s[len(str(XSD)):]
    return s


def load():
    """Parse the term modules. Returns (merged graph, {term: module name})."""
    g = Graph()
    origin: dict[URIRef, str] = {}
    for name in TERM_MODULES:
        mg = Graph()
        mg.parse(os.path.join(HERE, name), format="turtle")
        for kind in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty):
            for s in mg.subjects(RDF.type, kind):
                if str(s).startswith(str(XEO)):
                    origin.setdefault(s, name[len("xeo-"):-len(".ttl")])
        g += mg
    return g, origin


def load_schemes():
    """{scheme name: {"codes": [...], "fillsSlot": local name or None}} in stated order."""
    g = Graph()
    g.parse(os.path.join(HERE, SCHEMES_MODULE), format="turtle")
    out = {}
    for scheme in g.subjects(RDF.type, SKOS.ConceptScheme):
        members = [c for c in g.subjects(SKOS.inScheme, scheme)
                   if (c, RDF.type, SKOS.Concept) in g]
        ordered = None
        for coll in g.subjects(SKOS.inScheme, scheme):
            if (coll, RDF.type, SKOS.OrderedCollection) in g:
                head = g.value(coll, SKOS.memberList)
                ordered = list(Collection(g, head)) if head is not None else None
                break
        if ordered:
            rest = sorted((c for c in members if c not in ordered), key=local)
            members = ordered + rest
        else:
            members.sort(key=lambda c: str(g.value(c, SKOS.notation)))
        slot = g.value(scheme, XEO.fillsSlot)
        out[local(scheme)] = {
            "codes": [str(g.value(c, SKOS.notation)) for c in members],
            "fillsSlot": local(slot) if slot is not None else None,
        }
    return out


def build():
    """Return (profile dict, neo4j context dict)."""
    g, origin = load()
    schemes = load_schemes()
    slot_schemes: dict[str, list[str]] = {}
    for name, s in schemes.items():
        if s["fillsSlot"]:
            slot_schemes.setdefault(s["fillsSlot"], []).append(name)
    for names in slot_schemes.values():
        names.sort()

    def text(s, p):
        v = g.value(s, p)
        return str(v) if v is not None else None

    def classes_of(s, hard, hint):
        found = set(g.objects(s, hard)) | set(g.objects(s, hint))
        return sorted(short(c) for c in found)

    def terms(kind):
        return sorted((s for s in set(g.subjects(RDF.type, kind))
                       if str(s).startswith(str(XEO))), key=local)

    def mark(entry, s):
        """Add the optional status / deprecation markers to a profile entry."""
        status = text(s, XEO.termStatus)
        if status and status != "core":
            entry["status"] = status
        if str(g.value(s, OWL.deprecated)).lower() == "true":
            entry["deprecated"] = True
            entry["replacedBy"] = sorted(
                short(o) if str(o).startswith(str(XEO)) else
                ("xeos:" + local(o) if str(o).startswith(str(XEOS)) else str(o))
                for o in g.objects(s, RDFS.seeAlso))
        return entry

    labels = {}
    for c in terms(OWL.Class):
        entry = {
            "iri": str(c),
            "layer": text(c, XEO.xeoLayer),
            "module": origin[c],
            "definition": text(c, DCTERMS.description),
        }
        parents = sorted(local(p) for p in g.objects(c, RDFS.subClassOf)
                         if str(p).startswith(str(XEO)))
        if parents:
            entry["subClassOf"] = parents
        labels[local(c)] = mark(entry, c)

    relationship_types = {}
    properties = {}
    for p in terms(OWL.ObjectProperty):
        name = local(p)
        rng = classes_of(p, RDFS.range, XEO.rangeIncludes)
        entry = {
            "iri": str(p),
            "term": name,
            "layer": text(p, XEO.xeoLayer),
            "module": origin[p],
            "domain": classes_of(p, RDFS.domain, XEO.domainIncludes),
            "range": rng,
        }
        parents = sorted(local(x) for x in g.objects(p, RDFS.subPropertyOf)
                         if str(x).startswith(str(XEO)))
        if parents:
            entry["subPropertyOf"] = parents
        # A concept slot: the range is skos:Concept and nothing else.
        if set(g.objects(p, RDFS.range)) == {SKOS.Concept}:
            entry["conceptSlot"] = True
            entry["schemes"] = slot_schemes.get(name, [])
            properties[name] = mark({
                "iri": str(p),
                "layer": entry["layer"],
                "module": entry["module"],
                "datatype": "xsd:string",
                "conceptSlot": True,
                "schemes": slot_schemes.get(name, []),
            }, p)
        elif name in slot_schemes:
            entry["schemes"] = slot_schemes[name]
        key = upper_snake(name)
        if key in relationship_types:
            raise SystemExit(f"relationship type collision: {key}")
        relationship_types[key] = mark(entry, p)

    for p in terms(OWL.DatatypeProperty):
        name = local(p)
        rng = g.value(p, RDFS.range)
        entry = {
            "iri": str(p),
            "layer": text(p, XEO.xeoLayer),
            "module": origin[p],
            "datatype": short(rng) if rng is not None else None,
        }
        dom = classes_of(p, RDFS.domain, XEO.domainIncludes)
        if dom:
            entry["domain"] = dom
        if name in slot_schemes:
            entry["schemes"] = slot_schemes[name]
        if name in properties:
            raise SystemExit(f"property key collision: {name}")
        properties[name] = mark(entry, p)

    version = text(URIRef(str(XEO)), OWL.versionInfo)
    profile = {
        "$comment": "Generated from the xeo-*.ttl modules by tools/gen_profile.py — do not edit by hand.",
        "version": version,
        "namespace": str(XEO),
        "schemesNamespace": str(XEOS),
        "generatedFrom": TERM_MODULES + [SCHEMES_MODULE],
        "conventions": {
            "label": "the class local name, PascalCase",
            "relationshipType": "UPPER_SNAKE of the object property local name",
            "propertyKey": "the datatype property local name, camelCase",
            "tenancyKey": "websiteId",
            "layerKey": "xeoLayer",
            "layers": LAYERS,
        },
        "labels": labels,
        "relationshipTypes": relationship_types,
        "properties": properties,
        "schemes": {name: s["codes"] for name, s in schemes.items()},
    }

    ctx: dict = {
        "xeo": str(XEO),
        "xeos": str(XEOS),
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xsd": str(XSD),
        "id": "@id",
        "type": "@type",
        # An edge that carries properties has no direct RDF form. Lift it as a
        # reified statement beside (not instead of) the plain triple.
        "Edge": "rdf:Statement",
        "start": {"@id": "rdf:subject", "@type": "@id"},
        "edge": {"@id": "rdf:predicate", "@type": "@vocab"},
        "end": {"@id": "rdf:object", "@type": "@id"},
    }
    reserved = set(ctx)
    clash = reserved & (set(labels) | set(relationship_types) | set(properties))
    if clash:
        raise SystemExit(f"context key collides with an XEO name: {sorted(clash)}")
    for name in labels:
        ctx[name] = "xeo:" + name
    for key, entry in relationship_types.items():
        ctx[key] = {"@id": "xeo:" + entry["term"], "@type": "@id"}
    for name, entry in properties.items():
        if entry.get("conceptSlot"):
            if len(entry["schemes"]) == 1:
                # Stored as the concept's code: resolve it inside the one
                # scheme that fills the slot (xeos:<scheme>-<code>).
                ctx[name] = {
                    "@id": "xeo:" + name, "@type": "@vocab",
                    "@context": {"@vocab": str(XEOS) + entry["schemes"][0] + "-"},
                }
            else:
                # No single published scheme: the value must already be an IRI.
                ctx[name] = {"@id": "xeo:" + name, "@type": "@id"}
        elif entry["datatype"] in (None, "xsd:string"):
            ctx[name] = "xeo:" + name
        else:
            ctx[name] = {"@id": "xeo:" + name, "@type": entry["datatype"]}
    context = {
        "$comment": "Generated from the xeo-*.ttl modules by tools/gen_profile.py — do not edit by hand.",
        "@context": ctx,
    }
    return profile, context


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def mapping_tables(profile) -> str:
    """The generated section of docs/neo4j-profile.md."""
    def cell(values):
        return " · ".join(f"`{v}`" for v in values) if values else "open"

    def tag(e):
        """' (extension)' / ' (deprecated)' after a name, where the Turtle says so."""
        marks = ([e["status"]] if e.get("status") else []) + (["deprecated"] if e.get("deprecated") else [])
        return f" ({', '.join(marks)})" if marks else ""

    out = [BEGIN, "",
           f"Generated from XEO {profile['version']}. Do not edit between the markers; "
           "run `tools/gen_profile.py`.", ""]
    out += [f"### Node labels ({len(profile['labels'])})", "",
            "| Label | XEO class | Layer | Module |", "|---|---|---|---|"]
    for name, e in profile["labels"].items():
        out.append(f"| `{name}`{tag(e)} | `xeo:{name}` | {e['layer']} | {e['module']} |")
    out += ["", f"### Relationship types ({len(profile['relationshipTypes'])})", "",
            "`open` means the ontology leaves that side unconstrained. A concept slot may "
            "also be stored as a property key holding the concept's code.", "",
            "| Relationship type | XEO property | From | To | Layer | Module |",
            "|---|---|---|---|---|---|"]
    for key, e in profile["relationshipTypes"].items():
        to = cell(e["range"])
        if e.get("conceptSlot"):
            to += " (concept slot)"
        out.append(f"| `{key}`{tag(e)} | `xeo:{e['term']}` | {cell(e['domain'])} | {to} | "
                   f"{e['layer']} | {e['module']} |")
    out += ["", f"### Property keys ({len(profile['properties'])})", "",
            "| Property key | Datatype | Values from | Layer | Module |", "|---|---|---|---|---|"]
    for name, e in profile["properties"].items():
        dt = "concept code" if e.get("conceptSlot") else f"`{e['datatype']}`"
        out.append(f"| `{name}`{tag(e)} | {dt} | {cell(e.get('schemes', [])) if e.get('schemes') else ''} | "
                   f"{e['layer']} | {e['module']} |")
    out += ["", f"### Reference schemes ({len(profile['schemes'])})", "",
            "| Scheme | Codes |", "|---|---|"]
    for name, codes in sorted(profile["schemes"].items()):
        out.append(f"| `{name}` | {' · '.join(f'`{c}`' for c in codes)} |")
    out += ["", END]
    return "\n".join(out)


def render_doc(existing: str, profile) -> str:
    """Replace the generated section of the doc, leaving the prose around it."""
    if BEGIN not in existing or END not in existing:
        raise SystemExit(f"{PROFILE_DOC} has no GENERATED markers")
    head = existing[:existing.index(BEGIN)]
    tail = existing[existing.index(END) + len(END):]
    return head + mapping_tables(profile) + tail


def outputs() -> dict[str, str]:
    """{relative path: expected content} for every generated file."""
    profile, context = build()
    files = {PROFILE_JSON: dumps(profile), NEO4J_CONTEXT: dumps(context)}
    doc_path = os.path.join(HERE, PROFILE_DOC)
    if os.path.exists(doc_path):
        with open(doc_path, encoding="utf-8") as fh:
            files[PROFILE_DOC] = render_doc(fh.read(), profile)
    return files


def main() -> int:
    for rel, content in outputs().items():
        with open(os.path.join(HERE, rel), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"wrote {rel}")
    profile, _ = build()
    print(f"  {len(profile['labels'])} labels · {len(profile['relationshipTypes'])} relationship types · "
          f"{len(profile['properties'])} property keys · {len(profile['schemes'])} schemes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
