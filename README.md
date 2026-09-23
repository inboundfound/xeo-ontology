# XEO — the ontology for the xEO family

A small, standards-grounded vocabulary for how engines — search engines, generative
overviews, answer engines, conversational agents — see, cite, and serve web content.
One graph model for the whole **xEO** family: SEO, GEO, AEO, and whatever letter
comes next.

The `x` is the variable. That is the whole point of the name: the letter in front
keeps changing, and the discipline behind it doesn't.

**Prefix:** `xeo:` · **Namespace:** `https://xeoontology.org/xeo#`
· **Status:** v0.5 — open draft, built to be riffed on. Issues and PRs welcome.

> **Namespace note.** Term IRIs resolve at `xeoontology.org`, not at this repo.
> Whoever serves that domain must publish `/xeo` (the term docs), `/schemes`,
> `/context.jsonld` and `/schemes.json` from this repo's contents, or every IRI
> here 404s. The namespace deliberately does not point at a GitHub org, so the
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
2. **Epistemic layering.** Every term is typed by the kind of claim it makes:
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

| File | Layer | Contents |
|---|---|---|
| `xeo-core.ttl` | the SEO substrate | `Website`, `URL`, `Term`, `Crawl`, `SerpSnapshot`, `Topic`, `SearchPerformanceFact`; `FETCHED`, `LINKS_TO`, `REDIRECTS_TO`, `HAS_CANONICAL`, `RANKS_FOR` (windowed rollups with `datasetUri` provenance), `HAS_RESULT`, `IN_TOPIC` |
| `xeo-visibility.ttl` | the xEO layer | `Engine` (+ `SearchEngine` / `GenerativeEngine` / `AnswerEngine` / `ConversationalAgent`), `Brand`, `Prompt`, `LLMResponse`; `CITES`, `MENTIONS {mentionRank}`, `FANS_OUT_TO` (fan-out queries **are** Terms — the join back to rank data), `VISIBILITY_FOR` rollups (`mentionRate`, `citationRate`) |
| `xeo-engagement.ttl` | draft v0 | `SearchIntent` individuals (Broder 2002, extended), `ConversionPoint` (+ `CallToAction` / `LeadCaptureForm` / `GatedAsset`), `ConversionEvent`, `crmRecordRef` (the CRM join key), `attributedResponse` (pre-click attribution — a labeled interpretation) |
| `xeo-decision.ttl` | the interpretation tier | `Diagnostic`, `Gap`, `Tactic`, `Capability`, `Experiment`, `Outcome`, `Recommendation`; the chain `reveals`→`addressableBy`→`requiresCapability` (scope gate)→`tests`/`inContext`→`recommends`/`supportedBy`. Classes, never values — `gapType`/`inIntervention`/`onDimension`/`atPriority` are `skos:Concept` slots you fill. |
| `xeo-strategy.ttl` | the norms tier | `Practice` (a standing rule: `guardrail` vetoes a candidate, `preference` reorders it, `guidance` caveats it), `Playbook` (a reusable discipline bundle); `constrains`, `appliesToConcept`, `appliedPractice` (the audit edge — why a candidate was blocked), `supersedes` (revisable, never deleted), `hasRole` (page roles as a derivation, not regexes), `appliesAtScope` (the tenancy specificity ladder). Governs **how** a `Recommendation` is allowed to be made. |
| `xeo-delivery.ttl` | the delivery layer | `Project` (the contract — `engagementType`, `interventionQuota`, `cadence`/`durationDays`, what's `inScope`), `Campaign` (a body of work `aboutTopic`, covering URLs and Terms), `Objective` → `MetricTarget` (the intent, as targets a later `Outcome` is read against). `Recommendation` `issuedFor` a campaign; `Experiment` `measures` a target. The layer the decision and norms tiers left open. |
| `xeo-schemes.ttl` · `schemes.json` | reference values | **The slots, filled.** SKOS concept schemes for every `skos:Concept` slot and controlled string in the ontology — 20 schemes, ~100 concepts: gap types, verdicts, priority, the intervention catalogue, lifecycles, metrics, epistemic layers. Every value lifted from a production implementation and sourced. `schemes.json` is the generated projection for anything that builds an enum at boot. |
| `xeo-align.ttl` | interoperability | Optional bridges — schema.org (`WebSite`, `WebPage`, `Brand`, `Observation`), PROV-O (`Crawl`→`Activity`, `Engine`→`SoftwareAgent`, `LLMResponse`→`Entity`), SKOS (`Topic`→`Concept`, `childOf`→`broader`). **Alignments, not dependencies.** |
| `context.jsonld` | interoperability | A JSON-LD `@context` mapping graph labels/relationships/properties to IRIs — turns a Neo4j export into valid RDF/JSON-LD in one pass. |
| `schema.cypher` | property graph | Neo4j 5.x constraints + indexes for every module |

The core module is the stable substrate. Visibility is field-tested against a
working tracker/response-capture/Neo4j implementation. Decision and strategy are
implemented in production (see `xeo-graph-kit` for a runnable slice). Engagement
is an early draft published for discussion — the "pre-click funnel" seam that
engine-side data has been missing.

## The mental model

```
                        entities (durable)          episodes (immutable)
  core        Website · URL · Term · Topic     Crawl · SerpSnapshot
  visibility  Engine · Brand · Prompt          LLMResponse
  engagement  ConversionPoint · SearchIntent   ConversionEvent
  decision    Gap · Tactic · Capability        Experiment (→ Outcome)
  strategy    Practice · Playbook               (norms — rules, not events)
  delivery    Project · Campaign                (Objective → MetricTarget: the intent)

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

// Pre-click to pipeline (engagement draft): visibility windows around a conversion
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
WHERE all(c IN [(t)-[:REQUIRES_CAPABILITY]->(cap) | cap]
          WHERE (cap)-[:APPROVED]->() OR cap.approved = true)   // scope gate
OPTIONAL MATCH (e:Experiment)-[:TESTS]->(t),
              (e)-[:IN_CONTEXT]->(:Gap)-[:GAP_TYPE]->(gt)<-[:GAP_TYPE]-(g),
              (e)-[:PRODUCED_OUTCOME]->(o:Outcome)
RETURN t.label, count(e) AS precedents, avg(o.lift) AS avg_lift
ORDER BY precedents DESC, avg_lift DESC;
```

**Classes, never values.** `Gap` and `Tactic` are terms; a *Citation-Waterfall
stage* and *"publish a comparison page"* are not — they are `skos:Concept`s and
instances you slot into `gapType`, `inIntervention`, `onDimension`, `atPriority`.
That split is the point: **open scaffolding, your proprietary blend.** The frame
grows adoption; the fill is yours. (This is the one module that leans on SKOS as
a load-bearing primitive rather than an optional bridge — the taxonomy standard
is the right base for the "bring your own scheme" layer.)

## Interoperability — stands alone, bridges out

XEO has **no hard dependency**: core, visibility, and engagement load and reason
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
- **PROV-O** (the provenance spine): XEO's epistemic layering *is* provenance.
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

- **Filled-in norms** — `xeo-strategy` ships the *mechanism* for standing rules
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
| `practiceKind` · `practiceSource` · `practiceOutcome` | the norms tier | how a rule acts, where it came from, what it did |
| `outcomeResult` · `outcomeResultReason` | `xeo:result` · `xeo:resultReason` | did it move, and why it couldn't be judged |
| `objectiveMetric` · `targetKind` · `engagementType` · `cadence` · `effort` · `execution` | the delivery layer | |
| `magnitudeUnit` | `xeo:magnitudeUnit` | 8 — a size is never rendered bare |
| `epistemicLayer` | `xeo:epistemicLayer` | the six kinds of claim, one IRI each |

Two conventions make them consumable by software: `skos:notation` on every
concept is **the code** — the exact string a system stores or sends — and
`schemes.json` is a generated projection of the whole file, so a catalog can
build a JSON Schema `enum` at boot without parsing Turtle:

```python
import json, urllib.request
schemes = json.load(urllib.request.urlopen(
    "https://raw.githubusercontent.com/inboundfound/xeo-ontology/main/schemes.json"))["schemes"]
GAP_TYPES = [c["code"] for c in schemes["gapType"]["concepts"]]   # 14 codes, in stated order
```

Regenerate with `python tools/gen_schemes.py` after editing the TTL; never edit
the JSON by hand.

## Using it

```bash
# property graph
cat schema.cypher | cypher-shell -u neo4j -p <password>
```

The TTL files are plain OWL — load `xeo-core`, `xeo-visibility`,
`xeo-engagement`, `xeo-decision`, `xeo-strategy`, `xeo-delivery`, and (if you
want the crosswalk) `xeo-align` into any triple store or ontology editor.
Decision builds on core; strategy and delivery build on decision; the rest stand
alone. `xeo-schemes` is SKOS data, not ontology — load it where you want the
reference values. To publish graph data as linked data, serve your
Neo4j export under `context.jsonld` and it validates as RDF/JSON-LD.

**Namespace.** Terms currently resolve under GitHub Pages
(`https://xeoontology.org/xeo#`). The intended permanent home
is **xeoontology.org** — served with content negotiation so each term IRI
resolves to human docs (HTML) or the ontology (Turtle). Local term names never
change, so a w3id.org-style redirect can front either host without breaking any
published IRI.

## Maintained by

[Inbound Found](https://github.com/inboundfound). Built by working backwards
from a production marketing knowledge graph, then generalized. Contributions,
counter-proposals, and rude questions about our modeling choices are all welcome.

## License

[CC BY 4.0](LICENSE) — use it, extend it, ship it; just attribute.
