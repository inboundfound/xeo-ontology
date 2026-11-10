#!/usr/bin/env python3
"""Validate the XEO repository against its own rules.

One command, run locally and in CI, that fails when the ontology and the files
projected from it disagree:

  1. PARSE        every xeo-*.ttl module and the SHACL shapes parse as Turtle.
  2. TERMS        every class and property has rdfs:label, dct:description and a
                  valid xeo:epistemicLayer; every annotation property has an
                  rdfs:comment; every xeo: term a declaration points at
                  (domain, range, subPropertyOf, ...) is itself declared; all
                  modules carry the same owl:versionInfo.
  3. SCHEMES      every concept has a notation, label and definition; codes are
                  unique within a scheme; every scheme fills a declared slot.
                  In a vendor scheme (xeo-vendor-schemes.ttl) every concept
                  instead names the slot it fills, one SKOS match, a scope
                  note, a dated source and a mapping confidence.
  3b. STATUS      xeo:termStatus is 'core' or 'extension'; a deprecated term
                  names its replacement in rdfs:seeAlso and is still declared;
                  every earlier objectiveMetric code has its Metric in
                  xeos:metric under the same code; every Metric in the
                  reference schemes conforms to the shapes.
  4. CONTEXT      context.jsonld maps every class, property and individual, and
                  maps nothing that is not declared.
  5. GENERATED    neo4j-profile.json, context.neo4j.jsonld, docs/neo4j-profile.md,
                  schemes.json and xeo/index.html are what the generators would
                  write now (regenerated in memory and compared).
  6. EXAMPLES     every examples/*.jsonld uses only declared terms and concepts
                  and conforms to shapes/xeo-shapes.ttl; every
                  examples/invalid/*.jsonld breaks exactly the shapes it says
                  it breaks, so a shape that stops firing is caught too.

Exits non-zero on any failure.

Usage:  uv run --no-project --with rdflib --with pyshacl python tools/validate.py
"""
from __future__ import annotations

import glob
import json
import logging
import os
import sys

from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.namespace import DCTERMS, SKOS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_docs  # noqa: E402
import gen_profile  # noqa: E402
import gen_schemes  # noqa: E402

# examples/invalid/ carries ill-typed literals on purpose; rdflib logs a traceback
# for each one it cannot convert, which reads like a crash in a passing run.
logging.getLogger("rdflib.term").setLevel(logging.CRITICAL)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XEO = Namespace("https://xeoontology.org/xeo#")
XEOS = Namespace("https://xeoontology.org/schemes#")
XEOSH = Namespace("https://xeoontology.org/shapes#")
SH = Namespace("http://www.w3.org/ns/shacl#")
LAYERS = set(gen_profile.LAYERS)
SHAPES = os.path.join("shapes", "xeo-shapes.ttl")
VENDOR_SCHEMES = "xeo-vendor-schemes.ttl"
MATCHES = (SKOS.exactMatch, SKOS.closeMatch, SKOS.narrowMatch, SKOS.broadMatch, SKOS.relatedMatch)
CONFIDENCES = {"documented", "inferred", "verified"}
STATUSES = {"core", "extension"}
TERM_KINDS = (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty)
POINTERS = (RDFS.domain, RDFS.range, RDFS.subClassOf, RDFS.subPropertyOf,
            XEO.domainIncludes, XEO.rangeIncludes, XEO.fillsSlot)


class Report:
    def __init__(self) -> None:
        self.failures = 0

    def section(self, title: str, problems: list[str], ok: str) -> None:
        if problems:
            self.failures += len(problems)
            print(f"FAIL  {title}")
            for p in problems:
                print(f"        {p}")
        else:
            print(f"ok    {title}: {ok}")


def local(iri) -> str:
    return str(iri).split("#", 1)[1]


def in_xeo(iri) -> bool:
    return isinstance(iri, URIRef) and str(iri).startswith(str(XEO))


def modules() -> list[str]:
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "xeo-*.ttl")))


# --- 1. parse ----------------------------------------------------------------

def parse_all(report: Report):
    g = Graph()
    per_module: dict[str, Graph] = {}
    problems = []
    for name in modules() + [SHAPES]:
        mg = Graph()
        try:
            mg.parse(os.path.join(HERE, name), format="turtle")
        except Exception as exc:  # a parse error is the finding
            problems.append(f"{name}: {exc}")
            continue
        per_module[name] = mg
        if name != SHAPES:
            g += mg
    report.section("parse", problems,
                   f"{len(modules())} modules + shapes, {len(g)} ontology triples")
    return g, per_module


# --- 2. terms ----------------------------------------------------------------

def declared(g: Graph) -> dict[URIRef, URIRef]:
    """Every xeo: subject that is declared as something, with its kind."""
    out = {}
    for kind in TERM_KINDS + (OWL.AnnotationProperty, OWL.Ontology, OWL.NamedIndividual):
        for s in g.subjects(RDF.type, kind):
            if in_xeo(s):
                out.setdefault(s, kind)
    return out


def check_terms(report: Report, g: Graph, per_module: dict[str, Graph]) -> dict:
    terms = declared(g)
    problems = []
    counts = {}
    for kind in TERM_KINDS:
        members = sorted((s for s, k in terms.items() if k == kind), key=local)
        counts[local(kind)] = len(members)
        for s in members:
            name = "xeo:" + local(s)
            if g.value(s, RDFS.label) is None:
                problems.append(f"{name} has no rdfs:label")
            if g.value(s, DCTERMS.description) is None:
                problems.append(f"{name} has no dct:description")
            layers = {str(o) for o in g.objects(s, XEO.epistemicLayer)}
            if not layers:
                problems.append(f"{name} has no xeo:epistemicLayer")
            elif len(layers) > 1 or not layers <= LAYERS:
                problems.append(f"{name} has xeo:epistemicLayer {sorted(layers)}; expected one of {sorted(LAYERS)}")
            if len(set(g.objects(s, RDFS.label))) > 1:
                problems.append(f"{name} has more than one rdfs:label")
            if len(set(g.objects(s, DCTERMS.description))) > 1:
                problems.append(f"{name} has more than one dct:description")
            kinds = [k for k in TERM_KINDS if (s, RDF.type, k) in g]
            if len(kinds) > 1:
                problems.append(f"{name} is declared as more than one kind of term")
    for s, kind in terms.items():
        if kind == OWL.AnnotationProperty and g.value(s, RDFS.comment) is None:
            problems.append(f"xeo:{local(s)} (annotation property) has no rdfs:comment")
    # Nothing may point at an undeclared xeo: term, or describe one.
    for s, p, o in g:
        if p in POINTERS and in_xeo(o) and o not in terms:
            problems.append(f"{s} {local(p) if in_xeo(p) else p} points at undeclared xeo:{local(o)}")
    for s in set(g.subjects()):
        if in_xeo(s) and s not in terms:
            problems.append(f"xeo:{local(s)} is described but never declared")
    versions = {}
    for name, mg in per_module.items():
        for ont in mg.subjects(RDF.type, OWL.Ontology):
            versions[name] = str(mg.value(ont, OWL.versionInfo))
    for name in modules():
        if name not in versions:
            problems.append(f"{name} has no owl:Ontology header")
    if len(set(versions.values())) > 1:
        problems.append(f"modules disagree on owl:versionInfo: {versions}")
    report.section(
        "terms", problems,
        f"{counts['Class']} classes, {counts['ObjectProperty']} object properties, "
        f"{counts['DatatypeProperty']} datatype properties, all labelled, described and layered; "
        f"version {next(iter(versions.values()), '?')}")
    return terms


# --- 3. schemes --------------------------------------------------------------

def check_vendor_concept(g: Graph, terms: dict, concepts: set, scheme, c) -> list[str]:
    """A crosswalk concept: the vendor's exact field, the slot it fills, and how that is known."""
    problems = []
    if g.value(c, SKOS.notation) is None:
        problems.append(f"{c} has no skos:notation")
    if not local(c).startswith(local(scheme) + "-"):
        problems.append(f"{c} is not named <scheme>-<field>")
    slots = list(g.objects(c, XEO.fillsSlot))
    if not slots:
        problems.append(f"{c} has no xeo:fillsSlot")
    for slot in slots:
        if slot not in terms:
            problems.append(f"{c} fills undeclared slot {slot}")
    kinds = [p for p in MATCHES if g.value(c, p) is not None]
    if len(kinds) != 1:
        problems.append(f"{c} needs exactly one kind of SKOS match, has {len(kinds)}")
    for p in kinds:
        for target in g.objects(c, p):
            if target not in terms and target not in concepts:
                problems.append(f"{c} matches undeclared {target}")
    if g.value(c, SKOS.scopeNote) is None:
        problems.append(f"{c} has no skos:scopeNote")
    source = g.value(c, DCTERMS.source)
    if source is None or "(read " not in str(source):
        problems.append(f"{c} has no dct:source with a read date")
    confidence = {str(o) for o in g.objects(c, XEO.mappingConfidence)}
    if len(confidence) != 1 or not confidence <= CONFIDENCES:
        problems.append(f"{c} needs one xeo:mappingConfidence from {sorted(CONFIDENCES)}")
    return problems


def check_schemes(report: Report, g: Graph, terms: dict, per_module: dict) -> set[URIRef]:
    problems = []
    concepts = set(g.subjects(RDF.type, SKOS.Concept))
    schemes = set(g.subjects(RDF.type, SKOS.ConceptScheme))
    vendor_graph = per_module.get(VENDOR_SCHEMES, Graph())
    vendor = set(vendor_graph.subjects(RDF.type, SKOS.ConceptScheme))
    for scheme in sorted(schemes, key=str):
        for p in (SKOS.prefLabel, DCTERMS.description, DCTERMS.source):
            if g.value(scheme, p) is None:
                problems.append(f"{scheme} has no {p}")
        if scheme in vendor:
            # A crosswalk: the concept fills a slot, not the scheme, and a vendor
            # may reuse one field name in two reports, so codes may repeat.
            for c in sorted(g.subjects(SKOS.inScheme, scheme), key=str):
                if c in concepts:
                    problems += check_vendor_concept(g, terms, concepts, scheme, c)
            continue
        slot = g.value(scheme, XEO.fillsSlot)
        if slot is None:
            problems.append(f"{scheme} has no xeo:fillsSlot")
        elif slot not in terms:
            problems.append(f"{scheme} fills undeclared slot {slot}")
        seen = {}
        for c in g.subjects(SKOS.inScheme, scheme):
            if c not in concepts:
                continue
            code = g.value(c, SKOS.notation)
            if code is None:
                problems.append(f"{c} has no skos:notation")
            elif str(code) in seen:
                problems.append(f"{scheme} has code '{code}' twice")
            else:
                seen[str(code)] = c
            if code is not None and local(c) != f"{local(scheme)}-{code}":
                problems.append(f"{c} is not named <scheme>-<notation>")
            if g.value(c, XEO.mappingConfidence) is not None:
                problems.append(f"{c} carries a mapping confidence outside {VENDOR_SCHEMES}")
    for c in sorted(concepts, key=str):
        if g.value(c, SKOS.inScheme) is None:
            problems.append(f"{c} is in no scheme")
        for p in (SKOS.prefLabel, SKOS.definition):
            if g.value(c, p) is None:
                problems.append(f"{c} has no {p}")
    n_vendor = sum(1 for c in concepts if g.value(c, SKOS.inScheme) in vendor)
    report.section(
        "schemes", problems,
        f"{len(schemes) - len(vendor)} reference schemes, {len(concepts) - n_vendor} concepts; "
        f"{len(vendor)} vendor schemes, {n_vendor} mapped fields")
    return concepts


# --- 3b. status, deprecation, metrics ----------------------------------------

def check_status(report: Report, g: Graph, per_module: dict, terms: dict, concepts: set) -> None:
    from pyshacl import validate as shacl_validate

    problems = []
    extension = 0
    for s, o in g.subject_objects(XEO.termStatus):
        if str(o) not in STATUSES:
            problems.append(f"{s} has xeo:termStatus '{o}'; expected one of {sorted(STATUSES)}")
        extension += str(o) == "extension" and s in terms
    deprecated = sorted(s for s in g.subjects(OWL.deprecated, None)
                        if str(g.value(s, OWL.deprecated)).lower() == "true")
    for s in deprecated:
        if s not in terms:
            problems.append(f"{s} is deprecated but no longer declared; deprecation never removes a term")
        targets = list(g.objects(s, RDFS.seeAlso))
        if not targets:
            problems.append(f"{s} is deprecated and names no replacement in rdfs:seeAlso")
        for t in targets:
            if (in_xeo(t) and t not in terms) or (str(t).startswith(str(XEOS)) and t not in concepts):
                problems.append(f"{s} is replaced by undeclared {t}")
            if (t, OWL.deprecated, None) in g:
                problems.append(f"{s} is replaced by {t}, which is itself deprecated")
    # The codes consumers already store must resolve to a Metric under the same code.
    metrics = {str(g.value(c, SKOS.notation)): c for c in g.subjects(SKOS.inScheme, XEOS.metric)
               if (c, RDF.type, XEO.Metric) in g}
    for c in sorted(g.subjects(SKOS.inScheme, XEOS.objectiveMetric), key=str):
        code = str(g.value(c, SKOS.notation))
        twin = metrics.get(code)
        if twin is None:
            problems.append(f"{c}: code '{code}' has no xeo:Metric in xeos:metric")
        elif (c, SKOS.exactMatch, twin) not in g:
            problems.append(f"{c} is not skos:exactMatch {twin}")
    for c in sorted(g.subjects(SKOS.inScheme, XEOS.metric), key=str):
        if (c, RDF.type, SKOS.Concept) in g and (c, RDF.type, XEO.Metric) not in g:
            problems.append(f"{c} is in xeos:metric and is not an xeo:Metric")
    # Every published Metric obeys the rules the shapes state.
    shapes = per_module.get(SHAPES)
    published = Graph()
    for name in ("xeo-schemes.ttl", VENDOR_SCHEMES):
        published += per_module.get(name, Graph())
    if shapes is not None:
        conforms, results, _ = shacl_validate(published, shacl_graph=shapes, ont_graph=g,
                                              inference="none", advanced=False)
        if not conforms:
            for r in results.subjects(RDF.type, SH.ValidationResult):
                problems.append(f"{results.value(r, SH.focusNode)} — {results.value(r, SH.resultMessage)}")
    report.section(
        "status", problems,
        f"{extension} extension terms, {len(deprecated)} advisory deprecations each with a replacement; "
        f"{len(metrics)} Metrics conform, and all {len(list(g.subjects(SKOS.inScheme, XEOS.objectiveMetric)))} "
        f"earlier metric codes resolve")


# --- 4. context --------------------------------------------------------------

def check_context(report: Report, g: Graph, terms: dict) -> None:
    problems = []
    with open(os.path.join(HERE, "context.jsonld"), encoding="utf-8") as fh:
        pairs = json.load(fh, object_pairs_hook=list)
    ctx_pairs = dict(pairs)["@context"]
    keys = [k for k, _ in ctx_pairs]
    for k in sorted({k for k in keys if keys.count(k) > 1}):
        problems.append(f"context.jsonld defines '{k}' more than once")
    ctx = dict(ctx_pairs)
    mapped = {}
    for key, value in ctx.items():
        target = dict(value).get("@id") if isinstance(value, list) else value
        if isinstance(target, str) and target.startswith("xeo:"):
            mapped[key] = target[4:]
    expect = {local(s): kind for s, kind in terms.items()
              if kind in TERM_KINDS or kind == OWL.NamedIndividual}
    for name in sorted(expect):
        if mapped.get(name) != name:
            problems.append(f"context.jsonld does not map '{name}' to xeo:{name}")
    for key, target in sorted(mapped.items()):
        if URIRef(XEO[target]) not in terms:
            problems.append(f"context.jsonld maps '{key}' to undeclared xeo:{target}")
    for name, kind in expect.items():
        value = ctx.get(name)
        spec = dict(value) if isinstance(value, list) else {}
        if kind == OWL.ObjectProperty and spec.get("@type") != "@id":
            problems.append(f"context.jsonld: object property '{name}' must be typed @id")
        if kind == OWL.DatatypeProperty:
            rng = g.value(URIRef(XEO[name]), RDFS.range)
            want = gen_profile.short(rng) if rng is not None else "xsd:string"
            got = spec.get("@type", "xsd:string")
            if got != want:
                problems.append(f"context.jsonld: '{name}' is {got}, the ontology says {want}")
    report.section("context", problems, f"context.jsonld covers all {len(expect)} terms")


# --- 5. generated files ------------------------------------------------------

def check_generated(report: Report) -> None:
    problems = []
    expected = dict(gen_profile.outputs())
    expected["schemes.json"] = gen_schemes.render()
    expected[os.path.join("xeo", "index.html")] = gen_docs.render()
    for rel, want in sorted(expected.items()):
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            problems.append(f"{rel} is missing — run its generator")
            continue
        with open(path, encoding="utf-8") as fh:
            if fh.read() != want:
                problems.append(f"{rel} is stale — regenerate it (tools/gen_*.py) and commit")
    report.section("generated", problems, f"{len(expected)} generated files are up to date")


# --- 6. examples -------------------------------------------------------------

def load_jsonld(path: str) -> Graph:
    """Parse a JSON-LD file with its relative contexts read from disk, not the network."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    ctx = doc.get("@context")
    items = ctx if isinstance(ctx, list) else [ctx]
    resolved = []
    for item in items:
        if isinstance(item, str) and "://" not in item:
            with open(os.path.normpath(os.path.join(os.path.dirname(path), item)), encoding="utf-8") as fh:
                resolved.append(json.load(fh)["@context"])
        else:
            resolved.append(item)
    doc["@context"] = resolved
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def undeclared_in(data: Graph, terms: dict, concepts: set) -> list[str]:
    out = set()
    for s, p, o in data:
        for node, role in ((p, "property"), (o, "value")):
            if in_xeo(node) and node not in terms:
                out.add(f"uses undeclared xeo:{local(node)} as a {role}")
            if isinstance(node, URIRef) and str(node).startswith(str(XEOS)) and node not in concepts:
                out.add(f"uses undeclared concept xeos:{local(node)}")
    return sorted(out)


def check_examples(report: Report, g: Graph, per_module: dict, terms: dict, concepts: set) -> None:
    from pyshacl import validate as shacl_validate

    shapes = per_module.get(SHAPES)
    if shapes is None:
        report.section("examples", ["shapes did not parse; examples not checked"], "")
        return
    problems = []
    # An example points at published concepts (xeos:metric-ctr) without restating
    # them. A rule that reads through such a pointer, like "a reading of a
    # currency metric names its currency", needs the concept's own triples in the
    # graph being validated, so the reference schemes are validated with it.
    reference = per_module.get("xeo-schemes.ttl", Graph())
    valid = sorted(glob.glob(os.path.join(HERE, "examples", "*.jsonld")))
    invalid = sorted(glob.glob(os.path.join(HERE, "examples", "invalid", "*.jsonld")))
    if not valid:
        problems.append("no examples/*.jsonld found")
    triples = 0
    for path in valid:
        rel = os.path.relpath(path, HERE)
        try:
            data = load_jsonld(path)
        except Exception as exc:
            problems.append(f"{rel}: {exc}")
            continue
        triples += len(data)
        if not len(data):
            problems.append(f"{rel}: parsed to no triples")
        problems += [f"{rel} {m}" for m in undeclared_in(data, terms, concepts)]
        conforms, results, _ = shacl_validate(data + reference, shacl_graph=shapes, ont_graph=g,
                                              inference="none", advanced=False)
        if not conforms:
            for r in results.subjects(RDF.type, SH.ValidationResult):
                problems.append(f"{rel}: {results.value(r, SH.focusNode)} — "
                                f"{results.value(r, SH.resultMessage)}")
    fired_total = 0
    for path in invalid:
        rel = os.path.relpath(path, HERE)
        data = load_jsonld(path)
        expected = {(s, str(o)) for s, o in data.subject_objects(XEOSH.expectedViolation)}
        data.remove((None, XEOSH.expectedViolation, None))
        _, results, _ = shacl_validate(data + reference, shacl_graph=shapes, ont_graph=g,
                                       inference="none", advanced=False)
        fired = set()
        for r in results.subjects(RDF.type, SH.ValidationResult):
            shape = results.value(r, SH.sourceShape)
            # A property shape is a blank node; report the node shape that owns it.
            owner = next(shapes.subjects(SH.property, shape), shape)
            fired.add((results.value(r, SH.focusNode), local(owner)))
        fired_total += len(fired)
        for focus, shape in sorted(expected - fired, key=str):
            problems.append(f"{rel}: {focus} should break {shape} and does not")
        for focus, shape in sorted(fired - expected, key=str):
            problems.append(f"{rel}: {focus} breaks {shape}, which the file does not expect")
    all_shapes = {local(s) for s in shapes.subjects(RDF.type, SH.NodeShape)}
    exercised = set()
    for path in invalid:
        exercised |= {str(o) for o in load_jsonld(path).objects(None, XEOSH.expectedViolation)}
    for shape in sorted(all_shapes - exercised):
        problems.append(f"shape {shape} has no failing case in examples/invalid/")
    report.section(
        "examples", problems,
        f"{len(valid)} valid ({triples} triples) conform to {len(all_shapes)} shapes; "
        f"{len(invalid)} invalid break the {fired_total} rules they should")


def main() -> int:
    report = Report()
    g, per_module = parse_all(report)
    terms = check_terms(report, g, per_module)
    concepts = check_schemes(report, g, terms, per_module)
    check_status(report, g, per_module, terms, concepts)
    check_context(report, g, terms)
    check_generated(report)
    check_examples(report, g, per_module, terms, concepts)
    # Not a failure: observation terms the ontology has not yet grounded.
    ungrounded = sorted(local(s) for s, k in terms.items() if k in TERM_KINDS
                        and str(g.value(s, XEO.epistemicLayer)) == "observation"
                        and g.value(s, XEO.groundedIn) is None)
    if ungrounded:
        print(f"note  {len(ungrounded)} observation terms name no xeo:groundedIn: {', '.join(ungrounded)}")
    print()
    if report.failures:
        print(f"FAILED: {report.failures} problem(s)")
        return 1
    print("PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
