# Examples

Small instance graphs that use XEO terms. Everything in them is fictional
(`example.com`, `example.org`, invented brands and tools). They are checked on every
push by `tools/validate.py`: each file may use only declared terms and concepts, and
must conform to `shapes/xeo-shapes.ttl`.

| File | What it is |
|---|---|
| `learn-graph.jsonld` | One site, end to end, written against the camelCase `context.jsonld`. Covers the whole chain the `xeo-graph-kit` courses teach. |
| `metrics-and-pipeline.jsonld` | What 0.6.0 adds for measurement: a tenant's own `Metric`, two `MetricReading`s, an `Outcome` computed from them, and a CRM deal pointer with its stage history. |
| `neo4j-export.jsonld` | A few of the same nodes written the way Neo4j names things (UPPER_SNAKE relationship types, concept slots stored as codes), lifted by `context.neo4j.jsonld`. Includes a `Metric`, a `MetricReading` and a `MetricTarget`. |
| `invalid/broken-rules.jsonld` | One deliberately wrong node or edge per SHACL shape, each tagged with the shape it must break. The validator fails if a shape stops firing. |

## What `learn-graph.jsonld` walks through

1. **The web graph.** An agency and its client (`Organization`), the client's `Website`,
   three of its `URL`s and one competitor URL. The competitor URL has no `partOf`; it
   has `onDomain`. One `Crawl`, with what it saw on the `fetched` and `linksTo` edges.
2. **The SERP.** A `Term`, its windowed `ranksFor` rollup, and one `SerpSnapshot` with
   a `locale` and `device`, two results (the competitor's featured snippet at 1, our
   guide at 6) and a `relatedTerm`.
3. **AI answers.** A `Prompt`, one captured `LLMResponse` that cites both pages and
   mentions only the competitor `Brand` (with `sentiment` and the extraction `method`),
   and the `visibilityFor` rollup. `hasWebsite` is what lets `citationRate` be computed.
4. **Meaning.** A `Topic`, an `Entity`, `inTopic` and `about` edges with method and
   confidence, and one `similarTo` edge with its `similarity` and `basis`.
5. **Algorithm outputs.** Two `AlgorithmRun`s. Each scored URL points at the run that
   scored it (`computedBy`), and the run states its `projection`.
6. **The method.** A `Framework` of three ordered `Stage`s, with a `Diagnostic` and a
   `Tactic` placed `atStage`, the `Capability` the tactic requires, and what the
   diagnostic `suggests`.
7. **The decision and the loop.** A `DiagnosticRun` reveals a `Gap` (with a magnitude
   and its unit, `relativeTo` the competitor's page). An operator's `Feedback` accepts
   it. A `Recommendation` is issued into a `Campaign` whose `MetricTarget` is
   `citation_rate`; one `Practice` fired on it and one was evaluated and did not
   (`evaluatedPractice` with `fired`). It is `implementedAs` an `Experiment` with a
   treated page and a control. An earlier experiment is its `precedentFor`, and that
   one's `Outcome` was `confoundedBy` an `ExternalEvent`. The new outcome is what a
   `Practice` is `learnedFrom`.

## What `metrics-and-pipeline.jsonld` walks through

1. **A Metric of the tenant's own.** `ai_referred_pipeline` is not in `xeos:metric`. It is
   defined the same way the published ones are: a `metricType`, an `aggregation`, the slot it
   reads (`dealAmount`), a `timeAnchor`, a `metricFilter`, a `unit`, a `betterDirection` and an
   `additivity`.
2. **Targets that name a Metric by its code.** `"metric": "ctr"` is the notation of
   `xeos:metric-ctr`. The target carries no `direction`: the Metric states it. The currency
   target states `targetCurrency`.
3. **Two readings and the Outcome between them.** Both are readings of the same Metric over the
   same `scope`, on the same `aggregationBasis`, across 28-day windows, and each carries the
   clicks and impressions behind the rate. The `Outcome` points at both and records
   `absoluteChange` (0.011, which is 1.1 points) and `relativeChange` (0.3235).
4. **A deal, by pointer.** One node identified by `crmRecordRef`, carrying only the neutral
   slots: amount and currency, outcome, the tenant's own stage and pipeline ids, owner, created
   and closed times, and a first touch of `ai_assistant` from `chatgpt.com` with the
   classifier named in `method`. It has no XEO class, on purpose. A second node is one row of
   the tenant's stage map (`closedwon` means `won`).
5. **Stage history and a rollup.** A `StageTransition` for the deal entering its closing stage,
   and a `PipelineRollup`: a reading of `revenue_won` for the window, with its currency.

## Two conventions the files rely on

**An edge that carries properties is written twice.** RDF has no edge properties. The
plain triple is stated on the start node (`"ranksFor": "ex:term-calibration"`), and
the properties go on an `Edge` record beside it, which the local context maps to an
`rdf:Statement`:

```json
{ "type": "Edge", "start": "ex:url-guide", "edge": "ranksFor", "end": "ex:term-calibration",
  "avgPosition": "6.4", "clicks": 310 }
```

In Neo4j the same thing is one relationship with properties. The `Edge`, `start`,
`edge` and `end` keys are defined in each example's own context (and in
`context.neo4j.jsonld`); they are not XEO terms.

**Decimals are strings.** `"avgPosition": "6.4"`, not `6.4`. JSON-LD serializes a bare
JSON number coerced to `xsd:decimal` in double notation (`6.4E0`), which is not a valid
decimal. Integers and booleans are written bare.

## Running the checks

```bash
uv run --no-project --with rdflib --with pyshacl python tools/validate.py
```

To validate your own data against the shapes:

```bash
uv run --no-project --with pyshacl pyshacl -s shapes/xeo-shapes.ttl your-graph.ttl
```
