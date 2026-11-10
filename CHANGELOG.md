# Changelog

What changed in XEO, newest first. The rule since 0.3: **no breaking changes**. A term IRI,
once published, is never renamed or removed, and a domain or range is never narrowed. A
release may add terms, widen a domain or range, and correct prose.

Versions before 0.6.0 are reconstructed from the git history.

## 0.6.0 — kit sync (2026-11-09)

The partner repository `xeo-graph-kit` is gaining three courses that teach graphs to SEOs, and
it now uses XEO's names for everything it teaches. This release adds the terms those courses
need, fixes the places where the kit's use showed an existing term was wrong, and adds the
machinery (a Neo4j profile, SHACL shapes, a validator) that lets the two repositories stay in
step. The review guide is [`docs/v0.6-kit-sync.md`](docs/v0.6-kit-sync.md).

Counts: 36 → 45 classes, 61 → 91 object properties, 65 → 95 datatype properties,
20 → 29 reference schemes, 93 → 146 concepts.

### Added

**A new module, `xeo-analysis.ttl`** (derived structure). Once the data is a graph, people run
algorithms over it and write the results back, where they sit beside the observations looking
exactly like them. The module names what was written and how it came to be there.

- `AlgorithmRun` with `algorithm`, `parameters`, `projection`, `ranAt`; `computedBy` from any
  output back to its run. *Why:* a score cannot be compared with anything, including an earlier
  value of itself, unless it says what it was computed on.
- `similarTo` with `similarity` and `basis`; `precedentFor` as its sub-property between
  Experiments. *Why:* similarity edges were being written under local names with no stated
  basis.
- `pageRank`, `betweenness`, `degree`, `communityId`. *Why:* the kit writes them; each
  description says the value is meaningless without its projection.

**Core.**

- `Domain` and `onDomain`. *Why:* a competitor's result on a results page is a URL that belongs
  to no tracked Website. It needs somewhere to attach that is not tenant-scoped.
- `Entity`, `entityRef`, `about`. *Why:* `inTopic` covers a Term in a keyword cluster. Nothing
  said what a page or a prompt is about, or linked that to a knowledge-base identity.
- `relatedTerm`, `locale`, `device`. *Why:* `SerpSnapshot` was defined as "for a stated engine,
  locale, and device" and had no property for any of the three.
- `contentType`, `robotsMeta`, `contentHash`, `crawlDepth`, `indexable`, `wordCount`, `h1`,
  `linkPosition`, `crawler`, `startedAt`, `endedAt`, `lastSeenCrawlId`, `syncedAt`,
  `embeddedAt`, `embeddingDim`. *Why:* every one was already named in a description, in
  `schema.cypher` or in a crawl export, and none was a declared term. Five of them
  (`contentHash`, `crawlDepth`, `indexable`, `wordCount`, `linkPosition`) are marked
  `derivation`, not `observation`, because a crawler computes them by its own rule.
- `xeo:domainIncludes` and `xeo:rangeIncludes` (annotation properties). *Why:* XEO leaves many
  domains open on purpose, because `rdfs:domain` is an entailment rule. These say where a
  property is expected without that entailment, so the docs, the Neo4j profile and a consumer's
  checks have something to read.

**Visibility.** `hasWebsite` (*why:* `citationRate` is defined over "the brand's owned URLs"
and nothing said which those were), `competesWith`, `sentiment`.

**Decision.**

- `DiagnosticRun`, `runOf`, `revealedIn`; `Feedback`, `feedbackOn`. *Why:* the production
  implementers named both as missing (`LG_DiagnosticRun`, `LG_Feedback`).
- `ExternalEvent`, `confoundedBy`. *Why:* an Outcome could say `confounded_external` and could
  not say by what.
- `treats`, `hasControl`, `implementedAs`. *Why:* an Experiment recorded which tactic it tested
  and not which pages, against what control, or which Recommendation it carried out.
- `relativeTo`, `suggests`.

**Strategy.**

- `Framework`, `Stage`, `hasStage`, `nextStage`, `atStage`, `frameworkKind`, `stageOrder`,
  `test`. *Why:* a method with ordered stages could only be flattened into a Playbook, which
  has no order.
- `learnedFrom`. *Why:* a Practice could claim `source: learned` with nothing to check it
  against.
- `appliesTo`, with `appliesToConcept` declared its sub-property.
- `evaluatedPractice` and `fired`, with `appliedPractice` declared its sub-property. *Why:* the
  audit record had only its positive half.

**Delivery.** `Organization`, `organizationKind`, `owns`, `clientOf`, `holdsCapability`. *Why:*
the only tenancy node was the Website. Explicitly not a CRM mirror.

**Reference schemes.** `serpResultType`, `linkPosition`, `similarityBasis`, `algorithm`,
`frameworkKind`, `organizationKind`, `sentiment`, `device`, `feedbackVerdict`; and
`mention_rate` and `citation_rate` in `objectiveMetric`, so a campaign can target AI
visibility.

**Tooling and interop.**

- `tools/gen_profile.py` → `neo4j-profile.json`, `context.neo4j.jsonld`,
  `docs/neo4j-profile.md`.
- `shapes/xeo-shapes.ttl`: fifteen SHACL shapes for rules that were prose only.
- `examples/`: a worked instance graph, a Neo4j-form sample, and one failing case per shape.
- `tools/validate.py` and `.github/workflows/validate.yml`.
- Labels, descriptions and layers for every existing class and property that lacked one
  (126 labels, 23 descriptions, 9 layers), appended as extra triples.

### Widened

A domain or range removed because it was too narrow. Removing one only ever removes an
entailment, so no existing data changes meaning.

| Property | Was | Now | Why |
|---|---|---|---|
| `embeddingRef`, `embeddingModel` | domain `Term` | open | URLs, Prompts and Topics are embedded too |
| `onEngine` | domain `LLMResponse` | open | a SerpSnapshot is on an engine |
| `assessedAs` | domain `Tactic` | open | production scores the Recommendation |
| `verdict` | domain `Gap` | open | a Feedback carries a verdict of its own |
| `occurredAt` | domain `ConversionEvent` | open | an ExternalEvent occurs at a time |
| `includes` | domain `Playbook` | open | a Framework includes the same things |
| `activates` | range `Playbook` | open | a Framework is activated the same way |

`Topic`'s description now covers grouping URLs as well as Terms.

### Fixed

- **`capturedAt` and `model` typed every SerpSnapshot and topic assignment as an
  LLMResponse.** Both had `rdfs:domain xeo:LLMResponse`, while core defines a SerpSnapshot as
  captured at a moment and `inTopic` as carrying a model. Domain removed.
- **`statement` typed every Gap, Recommendation and Objective as a Practice.** Same cause, same
  fix.
- **Stale hosting prose.** `xeo-core.ttl` and the README said the namespace was served from
  GitHub Pages. It is served at xeoontology.org.
- **The README's payoff query** matched `(cap)-[:APPROVED]->()` and `(:Gap)-[:GAP_TYPE]->()`.
  `approved` is a boolean property, and the query returned `t.label`, which is not a term.
- **`schema.cypher` indexed two undeclared keys** (`startedAt`, `lastSeenCrawlId`). Both are
  now declared.
- **The term docs said v0.2** and omitted the delivery module. The version is now read from the
  ontology.

### Line stability

`launch-guardian` and `if-control-center` cite these files by line number. Every in-place
change replaced one line with one line; every new term is appended below the existing text. No
existing declaration moved. The 33 line citations and 110 term references in those two
repositories resolve exactly as they did before this release.

## 0.5.0 — WEO becomes XEO (2026-09-23)

- The vocabulary is renamed from WEO to XEO: prefix `xeo:`, files `xeo-*.ttl`.
- The namespace moves off GitHub Pages to `https://xeoontology.org/xeo#`, with reference
  schemes at `https://xeoontology.org/schemes#`, so the vocabulary's identity survives a
  repository move.
- Local term names are unchanged.

## 0.4.0 — reference schemes and delivery (2026-09-19)

- `xeo-delivery.ttl`: `Project`, `Campaign`, `Objective`, `MetricTarget` and the properties
  that hang work on them.
- `xeo-schemes.ttl` and the generated `schemes.json`: twenty SKOS schemes filling the
  ontology's slots with the values one agency runs in production.
- Decision gains `verdict`, `magnitude`, `magnitudeUnit`, `result`, `resultReason`; strategy
  gains `practiceOutcome`. All appended at the foot.

## 0.3.0 — the norms tier reaches every surface (2026-09-09 to 2026-09-18)

- `source` and `status` freed of their `xeo:Practice` domain.
- The README, `schema.cypher` and `context.jsonld` catch up with the strategy module; nineteen
  relationship-carried properties the context already published are declared.
- Module headers for decision and strategy, placed at the foot so cited lines hold.
- `tools/verify_citations.py`: checks consumers' line citations and term references.
- `REFERENCES.md`: SEOntology as prior art.

## 0.2.0 — first publication (2026-07-15 to 2026-07-20)

- `core`, `visibility` and `engagement` (draft) modules.
- `align`: bridges to schema.org, PROV-O and SKOS; `context.jsonld`.
- `decision` (the interpretation tier) and generated term docs.
- `strategy` (the norms tier); the `judgment` layer renamed `interpretation`.
