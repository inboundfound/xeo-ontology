# XEO — the ontology for the xEO family

A small, standards-grounded vocabulary for how engines — search engines, generative
overviews, answer engines, conversational agents — see, cite, and serve web content.
One graph model for the whole **xEO** family: SEO, GEO, AEO, and whatever letter
comes next.

The `x` is the variable. That is the whole point of the name: the letter in front
keeps changing, and the discipline behind it doesn't.

**Prefix:** `xeo:` · **Namespace:** `https://xeoontology.org/xeo#`
· **Status:** v0.6 — open draft, built to be riffed on. Issues and PRs welcome.
What changed and why: [`CHANGELOG.md`](CHANGELOG.md).

> **Namespace note.** Term IRIs resolve at `xeoontology.org`, not at this repo.
> Whoever serves that domain must publish `/xeo` (the term docs), `/schemes`,
> `/context.jsonld`, `/schemes.json`, `/neo4j-profile.json`,
> `/context.neo4j.jsonld` and `/shapes` from this repo's contents, or every IRI
> here 404s. Publishing is a manual step after each release. The namespace deliberately does not point at a GitHub org, so the
> vocabulary's identity survives a repo move, an org rename, or a change of host.

## Why "XEO"

Marketers already think in `-EO`: SEO, then GEO, then AEO. The engines keep
changing; the discipline — *make your content legible and creditable to the machine
between you and your audience* — doesn't. XEO names that discipline once, and the
ontology's `Engine` taxonomy absorbs new surfaces as subclasses instead of new
acronyms.

## What makes this one different

1. **Observations are grounded in primary standards.** Every observational term
   cites the spec or API contract that defines it — HTTP (RFC 9110), WHATWG
   HTML/URL, RFC 6596, the GSC Search Analytics API, per-provider response
   annotations. No dependency on any third-party SEO vocabulary.
2. **Layering.** Every term is typed by the kind of claim it makes (`xeoLayer`):
   `entity` (durable identity) · `episode` (happened at a time, immutable) ·
   `observation` (measured fact) · `derivation` (model output — carries method,
   model, confidence) · `interpretation` (a strategist's claim, labeled as one) ·
   `norm` (a standing rule about a class of cases, not a call about one).
   An agent assembling context can filter to observations only.
3. **Storage-agnostic.** The ontology defines meaning and identity keys; every
   term declares a *canonical store*. The graph holds what you traverse; the
   column store holds high-cardinality time-series facts; the vector store holds
   geometry; the CRM holds the pipeline. Identity keys join across stores.
4. **Tenancy is data, not schema.** Scope lives in properties (`websiteId`),
   never in dynamic labels.
5. **Integrate with data sources, not vocabularies.** Mapping modules for your
   CRM/analytics stack are operational pointers (identity keys), never baked-in
   vendor vocabularies.

## Modules

Every module needs only core; load core and the add-ons you use. A link between two add-ons (a practice constraining a recommendation, a recommendation issued for a campaign) works when both are loaded. `tools/validate.py` checks that core loads alone and lists those links.

| File | Role | Contents |
|---|---|---|
| `xeo-core.ttl` | the substrate every module needs | `Website`, `URL`, `Domain` (the registrable domain any URL sits on, tracked or not), `Term`, `Crawl`, `SerpSnapshot`, `Topic`, `Entity`, `SearchPerformanceFact`; `Person` and `Organization` (the canonical parties: one node per real person or organization, which every system's record of it points at with `REFERS_TO`; an Organization `owns` websites and brands); `FETCHED`, `LINKS_TO`, `REDIRECTS_TO`, `HAS_CANONICAL`, `ON_DOMAIN`, `RANKS_FOR` (windowed rollups with `datasetUri` provenance), `HAS_RESULT`, `RELATED_TERM`, `IN_TOPIC`, `ABOUT`; `Engine` and `SearchEngine`; `SearchIntent`; website conversions (`ConversionPoint` with a `conversionPointType`, `ConversionEvent`); the money terms (`currencyCode`, `recurringValue`, `amountInReportingCurrency`); and metrics: `Metric` (a named rule: `metricType`, `aggregation`, `readsSlot` or `numerator` / `denominator`, `unit`, `betterDirection`, `additivity`, `minDenominator`) and `MetricReading` (the value that rule took over one window, for one `scope`, from one source). No KPI class: that is `isPrimary`. |
| `xeo-visibility.ttl` | AI answers | `GenerativeEngine` / `AnswerEngine` / `ConversationalAgent` (kinds of core's `Engine`), `Brand`, `Prompt`, `LLMResponse`; `CITES`, `MENTIONS {mentionRank, sentiment}`, `FANS_OUT_TO` (fan-out queries **are** Terms — the join back to rank data), `VISIBILITY_FOR` rollups (`mentionRate`, `citationRate`), `HAS_WEBSITE`, `COMPETES_WITH`, `attributedResponse` (pre-click attribution — a labeled interpretation) |
| `xeo-analysis.ttl` | derived structure | What algorithms and models add to the graph: `AlgorithmRun` (algorithm, parameters, projection), `COMPUTED_BY`, `SIMILAR_TO {similarity, basis}`, `PRECEDENT_FOR`, and the node scores `pageRank`, `betweenness`, `degree`, `communityId`. All derivations. Similarity and centrality nominate candidates; they decide nothing, and a score is meaningless without the projection it was computed on. |
| `xeo-sales.ttl` | the CRM side | **The CRM seam:** `crmRecordRef` (the join key, typed by `crmSystem` and `crmObjectType`) and the few neutral slots that make pipeline numbers computable without mirroring any CRM — `dealAmount` (with core's `currencyCode`), `dealOutcome`, `stageRef` / `pipelineRef` with a neutral `stageClass`, `ownerRef`, `recordCreatedAt`, `dealClosedAt`, `firstTouchChannel` (with an `ai_assistant` channel), `StageTransition`, `PipelineRollup`. Lifecycle stage, probabilities and weighted amounts are an extension set. Was the CRM half of `xeo-engagement` until 0.7. |
| `xeo-work.ttl` | clients and delivery | `Project` (the contract — `engagementType`, `interventionQuota`, `cadence`/`durationDays`, what's `inScope`), `Campaign` (a body of work `aboutTopic`, covering URLs and Terms), `Objective` → `MetricTarget` (the intent, as targets a later `Outcome` is read against). `Recommendation` `issuedFor` a campaign; `Experiment` `measures` a target. An `Organization` (core) is `clientOf` another and `holdsCapability`. Was `xeo-delivery` until 0.7. |
| `xeo-decision.ttl` | gaps to recommendations | `Diagnostic` (and its episode, `DiagnosticRun`), `Gap`, `Tactic`, `Capability`, `Experiment`, `Outcome`, `ExternalEvent`, `Recommendation`, `Feedback`; the chain `reveals`→`addressableBy`→`requiresCapability` (scope gate)→`tests`/`inContext`→`recommends`/`supportedBy`. Classes, never values — `gapType`/`inIntervention`/`onDimension`/`atPriority` are `skos:Concept` slots you fill. **Practices** (strategy until 0.7): `Practice` (a standing rule: `guardrail` vetoes a candidate, `preference` reorders it, `guidance` caveats it), `Playbook` (a reusable discipline bundle); `constrains`, `appliesToConcept`, `appliedPractice` (the audit edge — why a candidate was blocked), `supersedes` (revisable, never deleted), `hasRole` (page roles as a derivation, not regexes), `appliesAtScope` (the tenancy specificity ladder); `Framework` and `Stage` (a named method as data: stages, ordered or not, with diagnostics and tactics placed `atStage`); `learnedFrom` and `evaluatedPractice {fired}`. Governs **how** a `Recommendation` is allowed to be made. |
| `xeo-schemes.ttl` · `schemes.json` | reference values | **The slots, filled.** SKOS concept schemes for every `skos:Concept` slot and controlled string in the ontology — 50 schemes, ~280 concepts: gap types, verdicts, priority, the intervention catalogue, lifecycles, **the Metrics themselves** (`xeos:metric`: search, AI visibility, analytics, CRM pipeline), metric types and units, deal outcomes, acquisition channels, SERP result types, link positions, algorithms, layers. Every scheme names its source. `schemes.json` is the generated projection for anything that builds an enum at boot. |
| [`mappings/`](mappings/README.md) | vendor mappings, **not part of the ontology** | **Where a vendor's field meets a slot.** One file and one SKOS scheme per tool; each concept holds the vendor's exact field name (`skos:notation`), the slot it fills, a SKOS match, a scope note, a dated source and an `xeo:mappingConfidence`. Transcribed so far: HubSpot CRM, Google Search Console, GA4, Peec, Profound. From documentation only: nothing is verified against live API output yet, and each file says which mappings are inferred. Nothing in the ontology points at a mapping, and the folder has a template for adding a tool. |
| `xeo-align.ttl` | interoperability | Optional bridges — schema.org (`WebSite`, `WebPage`, `Brand`, `Observation`), PROV-O (`Crawl`→`Activity`, `Engine`→`SoftwareAgent`, `LLMResponse`→`Entity`), SKOS (`Topic`→`Concept`, `childOf`→`broader`). **Alignments, not dependencies.** |
| `context.jsonld` | interoperability | A JSON-LD `@context` mapping graph labels/relationships/properties to IRIs — turns a Neo4j export into valid RDF/JSON-LD in one pass. |
| `schema.cypher` | property graph | Neo4j 5.x constraints + indexes for every module |
| `neo4j-profile.json` · `context.neo4j.jsonld` | property graph | **Generated.** Every class as a node label, every object property as an `UPPER_SNAKE` relationship type, every datatype property as a property key, each with its IRI, layer and module. See [Use it from Neo4j](#use-it-from-neo4j). |
| `shapes/xeo-shapes.ttl` | validation | SHACL shapes for the rules the ontology states in prose: a magnitude has a unit, a confidence is between 0 and 1, a captured response names its model, a ratio metric has a numerator and a denominator, a deal amount has a currency. Conservative; nothing is closed. |
| `examples/` | worked data | One fictional site, end to end, as JSON-LD that conforms to the shapes; and a second file for metrics, readings, an outcome and a CRM deal pointer. |

The core module is the stable substrate. Visibility is field-tested against a
working tracker/response-capture/Neo4j implementation. Decision and strategy are
implemented in production (see `xeo-graph-kit` for a runnable slice). Engagement
is an early draft published for discussion — the "pre-click funnel" seam that
engine-side data has been missing.

## The mental model

```
                        entities (durable)          episodes (immutable)
  core        Website · URL · Term · Topic     Crawl · SerpSnapshot
              Person · Organization · Engine   ConversionEvent
              ConversionPoint · SearchIntent   MetricReading (the number, over a window)
              Metric (a rule, not a number)
  visibility  Brand · Prompt                   LLMResponse
  analysis    (scores and similarity edges)    AlgorithmRun
  sales       (CRM records, by pointer)        StageTransition · OwnerChange
  work        Project · Campaign                (Objective → MetricTarget: the intent)
  decision    Gap · Tactic · Capability        Experiment (→ Outcome)
              Practice · Playbook               (norms — rules, not events)

  every add-on needs only core

  observations attach facts to entities/episodes (FETCHED, CITES, MENTIONS…)
  derivations carry method/model/confidence (IN_TOPIC, embeddingRef…)
  interpretations are labeled claims (targetsIntent, addressableBy, Recommendation)
  norms are standing rules over a class of cases (Practice constrains …)
  high-cardinality facts live in column stores; graphs keep windowed rollups
  with datasetUri pointing at the authoritative table

  the strata get more interpretive upward: core is bedrock (falsifiable,
  standards-grounded); decision is the surface (diagnosed, recommended); strategy
  governs it (what SHOULD hold, not what is). Load only the strata you need —
  filter to observation and the interpretation and norm tiers drop away.
```

Two rollup patterns rhyme on purpose:

- `(:URL)-[:RANKS_FOR {clicks, impressions, avgPosition, periodStart, periodEnd, datasetUri}]->(:Term)`
- `(:Prompt)-[:VISIBILITY_FOR {mentionRate, citationRate, responses, periodStart, periodEnd, datasetUri}]->(:Brand)`

The first summarizes the SEO world (facts in your column store); the second
summarizes the xEO world (facts in your response archive). Same discipline,
new engine.

## Example queries the model is shaped for

```cypher
// Cited but not named: pages that ground answers naming someone else
MATCH (r:LLMResponse)-[:CITES]->(u:URL {websiteId: $tenant})
WHERE NOT EXISTS { MATCH (r)-[:MENTIONS]->(:Brand {websiteId: $tenant}) }
RETURN u.address, count(r) AS ghost_citations ORDER BY ghost_citations DESC;

// List filler: mentioned often, ranked late
MATCH (r:LLMResponse)-[m:MENTIONS]->(b:Brand)
RETURN b.name, count(r) AS mentions, avg(m.mentionRank) AS avg_rank
ORDER BY mentions DESC;

// The fan-out join: engine retrieval queries you already rank for
MATCH (p:Prompt)-[:FANS_OUT_TO]->(t:Term)<-[rf:RANKS_FOR]-(u:URL)
WHERE rf.avgPosition <= 10
RETURN p.text, t.name, u.address, rf.avgPosition;

// Pre-click to pipeline: visibility windows around a conversion
MATCH (e:ConversionEvent)-[:CAPTURED_BY]->(cp:ConversionPoint)<-[:HAS_CONVERSION_POINT]-(u:URL)
MATCH (r:LLMResponse)-[:CITES]->(u)
WHERE r.capturedAt < e.occurredAt <= r.capturedAt + duration('P7D')
RETURN e.id, cp.crmRecordRef, collect(r.id) AS candidate_responses;
```

## The decision layer — from an observation to a labeled recommendation

`xeo-decision.ttl` is where facts become a plan, honestly labeled as
interpretation. It is the one chain the whole model builds toward —

```
observation  →  Diagnostic reveals Gap  →  Gap addressableBy Tactic
             →  Tactic requiresCapability          (the scope gate)
             →  Experiment tests Tactic, inContext Gap, producedOutcome
             →  Recommendation recommends Tactic, closesGap, supportedBy Experiment
```

The payoff query — *the metric that triggered a diagnosis, the gap it revealed,
the in-reach tactic to close it, and the precedent that earns the pick* — is one
traversal:

```cypher
// In-reach tactics for an open gap, ranked by precedent strength
MATCH (g:Gap {websiteId: $tenant})-[:ADDRESSABLE_BY]->(t:Tactic)
WHERE all(cap IN [(t)-[:REQUIRES_CAPABILITY]->(c:Capability) | c]
          WHERE cap.websiteId = $tenant AND cap.approved)        // scope gate
OPTIONAL MATCH (e:Experiment)-[:TESTS]->(t),
              (e)-[:IN_CONTEXT]->(prior:Gap),
              (e)-[:PRODUCED_OUTCOME]->(o:Outcome)
WHERE prior.gapType = g.gapType                                  // same kind of gap
RETURN t.name, count(e) AS precedents, avg(o.relativeChange) AS avg_change
ORDER BY precedents DESC, avg_change DESC;
```

`approved` is a boolean property on the `Capability`, and `gapType` is a concept
slot stored here as its code. A graph that keeps concepts as nodes matches
`(prior)-[:GAP_TYPE]->(c)<-[:GAP_TYPE]-(g)` instead; both forms conform (see
[`docs/neo4j-profile.md`](docs/neo4j-profile.md)).

**Classes, never values.** `Gap` and `Tactic` are terms; a *Citation-Waterfall
stage* and *"publish a comparison page"* are not — they are `skos:Concept`s and
instances you slot into `gapType`, `inIntervention`, `onDimension`, `atPriority`.
That split is the point: **open scaffolding, your proprietary blend.** The frame
grows adoption; the fill is yours. (This is the one module that leans on SKOS as
a load-bearing primitive rather than an optional bridge — the taxonomy standard
is the right base for the "bring your own scheme" layer.)

## Interoperability — stands alone, bridges out

XEO has **no hard dependency**: core and every add-on load and reason
with zero external vocabularies present. It grounds its own terms in primary
standards (HTTP, WHATWG, the GSC API) rather than borrowing another SEO ontology.

For anyone who already speaks the foundational web vocabularies, `xeo-align.ttl`
is an **optional crosswalk** — alignments, not imports:

- **schema.org** (the neutral base for web entities): `Website`→`schema:WebSite`,
  `URL`→`schema:WebPage`, `Brand`→`schema:Brand`, `SearchPerformanceFact`→`schema:Observation`.
  Two calibrated choices keep the bridges honest: `xeo:URL` is a `skos:closeMatch`
  (not an equivalence) to `schema:WebPage`, because XEO deliberately keeps the
  address (entity) separate from the page's rendered state (a Fetch observation);
  metrics map to `schema:Observation`, never a reified score class.
- **PROV-O** (the provenance spine): XEO's layering *is* provenance.
  `Crawl` is a `prov:Activity`, `Engine` a `prov:SoftwareAgent`, a captured
  `LLMResponse` a `prov:Entity` attributed (`onEngine`→`prov:wasAttributedTo`) to
  the engine that generated it. The decision layer extends the same spine — an
  `Experiment` is a `prov:Activity` that `produced` its `Outcome` (a
  `prov:Entity`), and a `Gap`/`Recommendation` `wasDerivedFrom` its evidence.
- **SKOS** (the taxonomy spine): `Topic` is a `skos:Concept`, `childOf` is
  `skos:broader`. This is the seam where users slot in their **own** concept
  scheme — of topics, gaps, or funnel stages — without editing the ontology.

Alignment uses `skos:closeMatch` where the correspondence is approximate (no
forced logical entailment) and `rdfs:subClassOf`/`subPropertyOf` only where an XEO
term is a genuine specialization. The bridges assert nothing false and can be
ignored entirely.

`context.jsonld` is the operational half: point it at a Neo4j export and the
graph's labels, relationship types, and properties become valid RDF/JSON-LD —
object properties resolve to node references, datatype properties carry their
`xsd` types. Legible names in the graph, real IRIs on export.

## What is deliberately NOT here

- **Filled-in norms** — `xeo-decision` ships the *mechanism* for standing rules
  (`Practice`, `practiceKind`, `appliesToConcept`, `appliedPractice`), never the
  rules themselves. "Never 301 a paginated archive" is an instance you author, and
  which Practices a given tenancy activates or overrides is data, not schema.
- **Filled-in taxonomies, as classes** — the actual interventions, priorities,
  gap types, and the dimensions a tactic is scored on are `skos:Concept` schemes
  you slot in, never classes baked into the vocabulary. Ship your blend; keep the
  frame. What *is* here, separately, is one blend published as a reference —
  see "The slots, filled" below.
- **Vendor vocabularies** — your CRM and analytics stack join via identity keys
  (`crmRecordRef`, `datasetUri`), never as imported schemas.
- **Quality scores and other unfalsifiable constructs** — if it isn't an
  observation, a provenance-carrying derivation, a labeled interpretation, or a
  norm that says so out loud, it doesn't get a term.

## The slots, filled — reference schemes

An ontology that ships classes and never values leaves slots: `xeo:gapType`,
`xeo:atPriority`, `xeo:inIntervention`, `xeo:status`. A slot nobody fills gets
filled locally, once per consumer, in prose — and the same status ends up
described five different ways across five systems.

`xeo-schemes.ttl` fills the slots with the vocabulary one agency actually runs in
production, lifted verbatim from the repos named in each scheme's `dct:source`.
It is published under its own namespace (`xeos:`) so it stays separable from
the ontology proper: **adopt a scheme as-is, extend it, or replace it** — the
slot is what XEO defines; a scheme is one answer.

| Scheme | Fills | Concepts |
|---|---|---|
| `gapType` | `xeo:gapType` | 14 — what kind of deficit a Diagnostic found |
| `gapVerdict` | `xeo:verdict` | 5 — attack · fix first · defend · hold · ignore |
| `intervention` | `xeo:inIntervention` | 8 — **the service catalogue**: what an agency can deploy, who controls it, lead time |
| `priority` | `xeo:atPriority` | 3 — now · next · later |
| `recommendationStatus` · `experimentStatus` · `practiceStatus` | `xeo:status` | the three lifecycles |
| `practiceKind` · `practiceSource` · `practiceOutcome` | practices (decision) | how a rule acts, where it came from, what it did |
| `outcomeResult` · `outcomeResultReason` | `xeo:result` · `xeo:resultReason` | did it move, and why it couldn't be judged |
| `objectiveMetric` · `targetKind` · `engagementType` · `cadence` · `effort` · `execution` | the work module | `objectiveMetric` is the earlier list of metric codes, kept for compatibility; each is an exactMatch of its Metric in `metric` |
| `metric` | `xeo:metric` | 35 — **the Metrics**: each an `xeo:Metric` with a type, unit, better direction and additivity. Search, AI visibility, analytics, CRM pipeline |
| `metricType` · `aggregation` · `metricUnit` · `betterDirection` · `additivity` | the Metric's own slots | how a metric is computed, in what unit, which way is better, whether it sums |
| `crmSystem` · `crmObjectType` · `dealOutcome` · `dealStageClass` · `stageSlot` · `acquisitionChannel` · `conversionPointType` · `searchIntent` | the CRM seam | the few closed lists the pipeline slots need; `acquisitionChannel` includes `ai_assistant` |
| `timeGrain` · `aggregationBasis` · `dataState` · `lifecycleStageClass` · `forecastCategory` · `recordOrigin` · `valuePeriod` | extension slots | marked `xeo:termStatus "extension"` |
| `magnitudeUnit` | `xeo:magnitudeUnit` | 8 — a size is never rendered bare |
| `serpResultType` · `device` · `linkPosition` | `xeo:resultType` · `xeo:device` · `xeo:linkPosition` | what kind of result, on which device, and where on the page a link sits |
| `sentiment` | `xeo:sentiment` | 4 — positive · neutral · negative · mixed |
| `algorithm` · `similarityBasis` | `xeo:algorithm` · `xeo:basis` | what ran, and what was compared |
| `frameworkKind` · `organizationKind` · `feedbackVerdict` | `xeo:frameworkKind` · `xeo:organizationKind` · `xeo:verdict` | the method, party and feedback slots added in 0.6 |
| `xeoLayer` | `xeo:xeoLayer` | the six kinds of claim, one IRI each |

**Core, extension, deprecated.** A term or scheme marked `xeo:termStatus "extension"` is
declared and usable, and is not something every implementation is expected to support;
a term with no status is core. A term marked `owl:deprecated true` is still declared and
still valid: its `rdfs:seeAlso` names what to write instead. Until 1.0, deprecated terms may be
removed in the next release. From 1.0, nothing is removed.
Both markers are carried into `neo4j-profile.json` and the term docs.

Two conventions make them consumable by software: `skos:notation` on every
concept is **the code** — the exact string a system stores or sends — and
`schemes.json` is a generated projection of the whole file, so a catalog can
build a JSON Schema `enum` at boot without parsing Turtle:

```python
import json, urllib.request
schemes = json.load(urllib.request.urlopen(
    "https://xeoontology.org/schemes.json"))["schemes"]
GAP_TYPES = [c["code"] for c in schemes["gapType"]["concepts"]]   # 14 codes, in stated order
```

Regenerate with `python tools/gen_schemes.py` after editing the TTL; never edit
the JSON by hand.

## Use it from Neo4j

A property graph has labels, relationship types and property keys, not IRIs. One
rule maps XEO onto them:

| XEO | Neo4j | Example |
|---|---|---|
| class | node label, unchanged | `xeo:SerpSnapshot` → `:SerpSnapshot` |
| object property | relationship type, `UPPER_SNAKE` | `xeo:linksTo` → `:LINKS_TO` |
| datatype property | property key, unchanged | `xeo:avgPosition` → `avgPosition` |

Tenancy is the `websiteId` property, never a label. `neo4j-profile.json` is that
mapping written out for software: every label, relationship type and property
key with its IRI, layer, module, and expected domain and range, plus
the reference schemes as plain code lists. Vendor it, and check the names your
loaders write against it. `context.neo4j.jsonld` is the same mapping as a
JSON-LD context, so a Neo4j export lifts back to RDF.

Both are generated from the Turtle (`tools/gen_profile.py`) and are never edited
by hand. The naming rule in full, how to consume the profile, and the complete
mapping table are in [`docs/neo4j-profile.md`](docs/neo4j-profile.md).

## Using it

```bash
# property graph
cat schema.cypher | cypher-shell -u neo4j -p <password>
```

The TTL files are plain OWL — load `xeo-core` and whichever add-ons you use
(`xeo-visibility`, `xeo-analysis`, `xeo-sales`, `xeo-work`, `xeo-decision`),
and (if you want the crosswalk) `xeo-align`, into any triple
store or ontology editor. Every add-on needs only core. `xeo-schemes` is SKOS data, not ontology — load it where you want the
reference values, and the file for your tool from `mappings/` where a loader needs to know which
vendor field fills which slot. To publish graph data as linked data, serve your
Neo4j export under `context.jsonld` and it validates as RDF/JSON-LD.

**Namespace.** Terms resolve at **xeoontology.org**
(`https://xeoontology.org/xeo#`), which serves the term docs as HTML. Content
negotiation, so the same IRI returns Turtle to a client that asks for it, is
intended and not yet in place. The namespace does not name the host, so a
w3id.org-style redirect can front it later without changing any term IRI.

**Checking a change.** One command validates the repository: every term is
labelled, described and layered; `context.jsonld` covers every term; the
generated files are current; the examples conform to the SHACL shapes.

```bash
uv run --no-project --with rdflib --with pyshacl python tools/validate.py
```

It runs on every push and pull request. After editing a `.ttl`, regenerate with
`tools/gen_schemes.py`, `tools/gen_docs.py` and `tools/gen_profile.py`.

## Maintained by

[Inbound Found](https://github.com/inboundfound). Built by working backwards
from a production marketing knowledge graph, then generalized. Contributions,
counter-proposals, and rude questions about our modeling choices are all welcome.

## License

[CC BY 4.0](LICENSE) — use it, extend it, ship it; just attribute.
