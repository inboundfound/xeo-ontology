#!/usr/bin/env python3
"""Generate the xeoontology.org site files from this ontology checkout.

Usage (from the ontology repo root):

    uv run --no-project --python 3.12 --with rdflib \\
        python tools/gen_site.py [SITE] [--no-copy] [--freeze]

SITE is a checkout of the site repo. Without it, everything is written into
``site-bundle/`` here (git-ignored), laid out as the site repo lays it out, so
the folder can be copied over a site checkout as it is.

It does three things, and a fourth on request:

1. Copies the files the ontology publishes into ``public/``: every
   ``xeo-*.ttl`` module, ``schemes.json``, ``context.jsonld``,
   ``context.neo4j.jsonld``, ``neo4j-profile.json``, ``schema.cypher``,
   ``shapes/xeo-shapes.ttl``, the ``mappings/`` folder (minus ``_``-prefixed
   templates) and ``LICENSE``.
2. Regenerates ``src/lib/xeo-terms.json`` (drives /xeo) and
   ``src/lib/xeo-schemes.json`` (drives /schemes) from the Turtle, with rdflib.
3. Writes ``src/lib/xeo-release.json``: the version, the module list and every
   count the pages state, so no page hard-codes a number.
4. With ``--freeze``: writes the frozen copy of this release to
   ``public/releases/<version>/`` (the module files, ``schemes.json``,
   ``context.jsonld``, ``neo4j-profile.json``). A frozen copy is never
   rewritten: if the folder exists the run stops, unless ``--force``.

``--no-copy`` skips step 1. ``--onto DIR`` reads another ontology checkout
instead of this one (an older release, say); files that release does not have
are skipped with a note.

Moved here from the site repo's ``tools/sync_from_ontology.py`` (decision W3:
the generator lives in the ontology and runs on every release). The term
reference follows tools/gen_docs.py: the same groups, the same per-term rows,
in the same order. Values are plain text with prefixed names (``xeo:Gap``),
several values joined by `` · ``; the site's markdown.ts links them at build
time.
"""
import argparse
import json
import os
import re
import shutil
import sys

from rdflib import Graph, Literal, RDF, RDFS, OWL, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, SKOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "site-bundle")
NS = "https://xeoontology.org/xeo#"
XEOS = "https://xeoontology.org/schemes#"

# Core first, then the add-ons. A term's "module" is the first file in this order
# that states anything about it (the rule gen_docs.py uses), so a module that
# only adds triples about an older term (align, a deprecation) never claims it.
MODULE_ORDER = [
    "xeo-core", "xeo-visibility", "xeo-analysis", "xeo-sales", "xeo-work",
    "xeo-decision", "xeo-strategy", "xeo-schemes", "xeo-align",
]

# Files and folders copied into public/ as-is, if the release has them.
PUBLIC_FILES = [
    "schemes.json", "context.jsonld", "context.neo4j.jsonld",
    "neo4j-profile.json", "schema.cypher", "LICENSE",
    os.path.join("shapes", "xeo-shapes.ttl"),
]

EPI = URIRef(NS + "xeoLayer")
GROUNDED = URIRef(NS + "groundedIn")
STORE = URIRef(NS + "canonicalStore")
DOMAIN_INCLUDES = URIRef(NS + "domainIncludes")
RANGE_INCLUDES = URIRef(NS + "rangeIncludes")
TERM_STATUS = URIRef(NS + "termStatus")
FILLS_SLOT = URIRef(NS + "fillsSlot")
CLOSE_MATCH = SKOS.closeMatch

PREFIXES = {
    NS: "xeo:",
    XEOS: "xeos:",
    "https://schema.org/": "schema:",
    "http://www.w3.org/ns/prov#": "prov:",
    "http://www.w3.org/2004/02/skos/core#": "skos:",
    "http://www.w3.org/2001/XMLSchema#": "xsd:",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
    "http://www.w3.org/2002/07/owl#": "owl:",
    "http://purl.org/dc/terms/": "dct:",
}

GROUPS = [
    ("Classes", OWL.Class),
    ("Object properties", OWL.ObjectProperty),
    ("Datatype properties", OWL.DatatypeProperty),
    ("Annotation properties", OWL.AnnotationProperty),
    ("Individuals", None),
    ("Modules", OWL.Ontology),
]


def qname(node):
    s = str(node)
    if isinstance(node, Literal):
        return s
    for base, pre in PREFIXES.items():
        if s.startswith(base):
            return pre + s[len(base):]
    return s


def local(node):
    return str(node).split("#")[-1].split("/")[-1]


def join(nodes, key=str):
    # rdflib keeps no statement order, so several values are sorted to keep
    # the output stable from run to run (by IRI, as gen_docs.py sorts seeAlso).
    return " · ".join(qname(n) for n in sorted(nodes, key=key))


def module_files(onto):
    """The module files of this release, in MODULE_ORDER (unknown ones last)."""
    found = sorted(f[:-4] for f in os.listdir(onto)
                   if f.startswith("xeo-") and f.endswith(".ttl"))
    known = [m for m in MODULE_ORDER if m in found]
    return known + [m for m in found if m not in known]


def load(onto, modules):
    g = Graph()
    origin = {}
    for m in modules:
        mg = Graph()
        mg.parse(os.path.join(onto, m + ".ttl"), format="turtle")
        for s in mg.subjects():
            if str(s).startswith(NS) and s not in origin:
                origin[s] = m
        g += mg
    return g, origin


# ---------------------------------------------------------------------------
# xeo-terms.json


def term_fields(g, term, module, group):
    def val(p):
        o = g.value(term, p)
        return str(o) if o is not None else None

    def objs(p):
        return list(g.objects(term, p))

    fields = []
    label = val(DCTERMS.title) if group == "Modules" else val(RDFS.label)
    if label:
        fields.append(("label", label))
    fields.append(("module", module))
    layer = val(EPI)
    if layer:
        fields.append(("layer", layer))
    # v0.6: release status of a term. "extension" (declared and usable, not
    # expected of every implementation) and/or "deprecated" (still valid; the
    # seeAlso row names what to write instead).
    status = []
    if val(TERM_STATUS):
        status.append(val(TERM_STATUS))
    if str(g.value(term, OWL.deprecated)).lower() == "true":
        status.append("deprecated")
    if status:
        fields.append(("status", " · ".join(status)))
    if group == "Individuals":
        # The XEO class first, then owl:NamedIndividual.
        fields.append(("type", join(objs(RDF.type),
                                    key=lambda t: (not str(t).startswith(NS), str(t)))))
    rows = [
        ("domain", objs(RDFS.domain)),
        ("expected on", objs(DOMAIN_INCLUDES)),
        ("range", objs(RDFS.range)),
        ("expected to point at", objs(RANGE_INCLUDES)),
        ("subclass of", objs(RDFS.subClassOf)),
        ("subproperty of", objs(RDFS.subPropertyOf)),
        ("closeMatch", objs(CLOSE_MATCH)),
        ("seeAlso", objs(RDFS.seeAlso)),
    ]
    fields += [(k, join(v)) for k, v in rows if v]
    for key, p in (("grounded in", GROUNDED), ("canonical store", STORE)):
        if val(p):
            fields.append((key, val(p)))
    if group == "Modules":
        for key, p in (("creator", DCTERMS.creator), ("version", OWL.versionInfo)):
            if val(p):
                fields.append((key, val(p)))
    desc = val(DCTERMS.description) or val(RDFS.comment)
    if desc:
        fields.append(("description", desc))
    return [[k, v] for k, v in fields]


def build_terms(g, origin):
    ours = {s for s in origin if str(s) != NS}
    typed = {}
    for title, cls in GROUPS:
        if cls is not None:
            typed[title] = {s for s in ours if (s, RDF.type, cls) in g}
    meta = set().union(*(typed[t] for t in typed if t != "Modules"))
    typed["Individuals"] = {
        s for s in ours if s not in meta and s not in typed["Modules"]
        and any(str(o).startswith(NS) for o in g.objects(s, RDF.type))
    }
    groups = []
    for title, _ in GROUPS:
        terms = sorted(typed[title], key=lambda s: local(s).lower())
        groups.append({
            "title": title,
            "declared": len(terms),
            "terms": [{"id": local(t), "kind": title,
                       "fields": term_fields(g, t, origin[t], title)} for t in terms],
        })
    return {"groups": groups}


# ---------------------------------------------------------------------------
# xeo-schemes.json


def build_schemes(onto):
    path = os.path.join(onto, "xeo-schemes.ttl")
    g = Graph()
    g.parse(path, format="turtle")
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    # Schemes in the order the file states them (the page reads top to bottom
    # the way the Turtle does); rdflib keeps no file positions, so find them.
    pos = {m.group(1): m.start() for m in re.finditer(
        r"^xeos:([A-Za-z0-9_-]+)\s+a\s+skos:ConceptScheme", src, re.M)}

    def text(s, p):
        v = g.value(s, p)
        return str(v) if v is not None else None

    out = []
    schemes = sorted(g.subjects(RDF.type, SKOS.ConceptScheme),
                     key=lambda s: (pos.get(local(s), 1 << 30), local(s)))
    for scheme in schemes:
        # Same member rule and order as tools/gen_schemes.py.
        members = [c for c in g.subjects(SKOS.inScheme, scheme)
                   if (c, RDF.type, SKOS.Concept) in g]
        ordered, order_id = False, None
        for coll in g.subjects(SKOS.inScheme, scheme):
            if (coll, RDF.type, SKOS.OrderedCollection) in g:
                head = g.value(coll, SKOS.memberList)
                listed = list(Collection(g, head)) if head is not None else []
                if listed:
                    rest = [c for c in members if c not in listed]
                    members = listed + sorted(rest, key=local)
                    ordered, order_id = True, local(coll)
                break
        if not ordered:
            members.sort(key=lambda c: str(g.value(c, SKOS.notation)))
        fills = g.value(scheme, FILLS_SLOT)
        entry = {
            "id": local(scheme),
            "concepts": [{
                "id": local(c),
                "code": text(c, SKOS.notation) or "",
                "label": text(c, SKOS.prefLabel) or "",
                "definition": text(c, SKOS.definition) or "",
                "note": text(c, SKOS.note) or "",
            } for c in members],
            "label": text(scheme, SKOS.prefLabel) or "",
            "fillsSlot": local(fills) if fills is not None else "",
            "ordered": ordered,
            "source": text(scheme, DCTERMS.source) or "",
            "description": text(scheme, DCTERMS.description) or "",
        }
        if order_id:
            entry["orderId"] = order_id
        out.append(entry)
    return {"schemes": out}


# ---------------------------------------------------------------------------
# xeo-release.json


def mapping_files(onto):
    mdir = os.path.join(onto, "mappings")
    if not os.path.isdir(mdir):
        return []
    return sorted(f for f in os.listdir(mdir)
                  if not f.startswith(("_", ".")) and os.path.isfile(os.path.join(mdir, f)))


def build_release(g, modules, terms, schemes, onto):
    version = g.value(URIRef(NS), OWL.versionInfo)
    counts = {grp["title"]: len(grp["terms"]) for grp in terms["groups"]}
    return {
        "$comment": "Written by the ontology repo's tools/gen_site.py. Do not edit by hand.",
        "version": str(version) if version is not None else "",
        "modules": [m + ".ttl" for m in modules],
        "moduleCount": len(modules),
        "mappings": ["mappings/" + f for f in mapping_files(onto) if f.endswith(".ttl")],
        "terms": sum(counts.values()),
        "termCounts": counts,
        "schemes": len(schemes["schemes"]),
        "concepts": sum(len(s["concepts"]) for s in schemes["schemes"]),
    }


# ---------------------------------------------------------------------------


def copy_public(onto, modules, site):
    pub = os.path.join(site, "public")
    copied = []
    for f in [m + ".ttl" for m in modules] + PUBLIC_FILES:
        src = os.path.join(onto, f)
        if not os.path.exists(src):
            print(f"  (not in this release: {f})")
            continue
        os.makedirs(os.path.dirname(os.path.join(pub, f)), exist_ok=True)
        shutil.copyfile(src, os.path.join(pub, f))
        copied.append(f)
    maps = mapping_files(onto)
    if maps:
        os.makedirs(os.path.join(pub, "mappings"), exist_ok=True)
    for f in maps:
        shutil.copyfile(os.path.join(onto, "mappings", f), os.path.join(pub, "mappings", f))
        copied.append(os.path.join("mappings", f))
    print(f"copied {len(copied)} files into public/")


# The files a frozen release copy holds: what a consumer pins to a version.
FROZEN_FILES = ["schemes.json", "context.jsonld", "neo4j-profile.json"]


def freeze(onto, modules, site, version, force):
    if not version:
        sys.exit("no owl:versionInfo on the ontology: cannot name the frozen copy")
    dest = os.path.join(site, "public", "releases", version)
    if os.path.exists(dest) and not force:
        sys.exit(f"{dest} exists: a frozen copy is never rewritten (pass --force to overwrite)")
    os.makedirs(dest, exist_ok=True)
    files = [m + ".ttl" for m in modules] + FROZEN_FILES
    for f in files:
        src = os.path.join(onto, f)
        if not os.path.exists(src):
            print(f"  (not in this release: {f})")
            continue
        shutil.copyfile(src, os.path.join(dest, f))
    print(f"froze {len(files)} files into public/releases/{version}/")


def write_json(path, data):
    # indent=1 and no trailing newline: the format the hand-made files had.
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("site", nargs="?", default=BUNDLE,
                    help="a site repo checkout to write into (default: site-bundle/ here)")
    ap.add_argument("--onto", default=ROOT,
                    help="the ontology checkout to read (default: this one)")
    ap.add_argument("--no-copy", action="store_true", help="do not copy files into public/")
    ap.add_argument("--freeze", action="store_true",
                    help="also write the frozen copy public/releases/<version>/")
    ap.add_argument("--force", action="store_true",
                    help="with --freeze, overwrite an existing frozen copy")
    a = ap.parse_args()
    onto = os.path.abspath(a.onto)
    site = os.path.abspath(a.site)
    modules = module_files(onto)
    if "xeo-core" not in modules:
        sys.exit(f"no xeo-core.ttl in {onto}")
    if site != BUNDLE and not os.path.isdir(os.path.join(site, "src", "lib")):
        sys.exit(f"{site} does not look like a site checkout (no src/lib)")

    g, origin = load(onto, modules)
    terms = build_terms(g, origin)
    schemes = build_schemes(onto)
    release = build_release(g, modules, terms, schemes, onto)

    out = os.path.join(site, "src", "lib")
    os.makedirs(out, exist_ok=True)
    write_json(os.path.join(out, "xeo-terms.json"), terms)
    write_json(os.path.join(out, "xeo-schemes.json"), schemes)
    write_json(os.path.join(out, "xeo-release.json"), release)
    if not a.no_copy:
        copy_public(onto, modules, site)
    if a.freeze:
        freeze(onto, modules, site, release["version"], a.force)
    print(f"wrote into {site}")
    print(f"v{release['version']}: {release['moduleCount']} modules, "
          f"{release['terms']} terms {release['termCounts']}, "
          f"{release['schemes']} schemes, {release['concepts']} concepts")


if __name__ == "__main__":
    main()
