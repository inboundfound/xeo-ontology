# References — prior art

Ontologies and vocabularies XEO relates to. Distilled so the source repos don't need to be
checked out locally.

---

## SEOntology (`seovoc`) — WordLift et al.

<https://github.com/seontology/seontology> · namespace `https://w3id.org/seovoc/` · 96 commits, none ours

The closest prior art to XEO: an open-source SEO domain ontology, initially developed by
WordLift and enriched by SEO practitioners and knowledge engineers. Described by its authors as
"a semantic operating system for modern SEO" — a shared vocabulary letting agents, apps and
researchers reason about, audit and optimise content. Self-described as an early draft.

Accepted at **SEMANTiCS 2026** (Research & Innovation Track).

Ships `seovoc.ttl` / `seovoc.owl` (~134 KB). Imports/relates to `schema.org`, `skos`, `voaf`,
`dc`/`dcterms`, and WordLift's earlier `SEO_Ontology`.

```bibtex
@software{gjorgjevska2026seontology,
  title        = {SEOntology: A Domain Ontology for Semantic Modeling of Search Engine Optimization Workflows},
  author       = {Gjorgjevska, Emilija and Riccitelli, David and Jovanovik, Milos and Volpini, Andrea},
  year         = {2026},
  url          = {https://github.com/seontology/seontology},
  note         = {Accepted at SEMANTiCS 2026 Research & Innovation Track}
}
```

### Relationship to XEO

We reference SEOntology as prior art and expect to align to it where the vocabularies genuinely
meet. They are not the same ontology, and the difference is one of subject rather than quality:

**SEOntology models traditional SEO.** Its subject is the SEO workflow — content, crawling,
keywords, on-page structure — expressed as linked data so agents and apps can reason over it.
That is real and useful ground, and where XEO touches it we should relate terms rather than
restate them.

**XEO is AI-native and xEO-scoped.** The subject is web *engine* optimization across the whole
xEO family — SEO, GEO and AEO together — where the consuming system is as often an answer engine
or an assistant as a search engine. That changes what has to be modelled.

Two areas extend past SEOntology's scope, and they are the reason XEO exists rather than being a
profile of `seovoc`:

1. **Decision intelligence.** XEO carries the reasoning, not only the artefacts — diagnostics and
   their stages (`xeo-decision`), norms that fire or veto (`xeo-strategy`: Practices, guardrails,
   provenance, an experiment ledger that promotes a `claimed` practice to `learned`), and
   provenance all the way down. Modelling *why* a recommendation was made, and how much to trust
   it, is a first-class requirement here.
2. **Chat assistant / agent surface.** Engagement with assistants — citations, mentions, sentiment
   and the visibility layer they feed (`xeo-visibility`, `xeo-engagement`) — is native to XEO's
   subject and largely outside a workflow-centred SEO vocabulary.

**Practical stance:** cite SEOntology, align the overlapping terms in `xeo-align.ttl` when we do
the alignment pass, and do not force the decision-intelligence or assistant layers into it. The
overlap is worth an explicit mapping; the extension is the point of the ontology.

**Status:** `xeo-align.ttl` currently relates XEO to `schema.org`, `prov` and `skos` (`dcterms` is
used for module metadata, not aligned to),
and does not yet mention `seovoc`. The alignment pass is open work.

---

## Also related

The runnable consumer of this ontology is
[`xeo-graph-kit`](https://github.com/inboundfound/xeo-graph-kit), which carries its own
`REFERENCES.md` for the implementation-side prior art (Neo4j context graphs, GEO tactics
planning).
