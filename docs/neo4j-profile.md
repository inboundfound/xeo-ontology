# XEO in Neo4j — the property-graph profile

XEO is written in Turtle and identified by IRIs. A property graph has neither, so this page
states the one rule that turns an XEO term into a Neo4j name, and lists every name the rule
produces. The list is generated from the Turtle by `tools/gen_profile.py`; the same run writes
`neo4j-profile.json` (for software) and `context.neo4j.jsonld` (to lift an export back to RDF).

## The naming rule

| XEO | Neo4j | Rule | Example |
|---|---|---|---|
| class | node label | the class local name, PascalCase, unchanged | `xeo:SerpSnapshot` → `:SerpSnapshot` |
| object property | relationship type | the local name in UPPER_SNAKE: an underscore before each capital, then upper-cased | `xeo:linksTo` → `:LINKS_TO`, `xeo:hasCanonical` → `:HAS_CANONICAL` |
| datatype property | property key | the local name, camelCase, unchanged | `xeo:avgPosition` → `avgPosition` |

Four conventions sit beside the rule.

- **Direction follows the ontology.** A relationship runs from the property's domain to its
  range: `(:URL)-[:PART_OF]->(:Website)`, never the reverse under another name.
- **Tenancy is the `websiteId` property**, on every tenant-scoped node and relationship. It is
  never a label. `Domain`, `Entity`, `Term` and `Engine` are shared and carry none.
- **Edge-carried properties stay on the relationship.** `avgPosition` belongs on `RANKS_FOR`,
  `anchorText` on `LINKS_TO`, `similarity` on `SIMILAR_TO`. Each property's description in the
  ontology says which relationship carries it.
- **`xeoLayer` is the instance-level epistemic layer.** A graph that wants to filter by kind of
  claim stamps each node and relationship with `xeoLayer`, one of `entity`, `episode`,
  `observation`, `derivation`, `interpretation`, `norm`. The value for a node or relationship is
  the `layer` of its label or type in the profile, with one exception the ontology states: a
  `MENTIONS` edge written by a model is a `derivation`, by a string match an `observation`.
  `xeoLayer` is a profile convention (`conventions.layerKey`), not an XEO term: XEO types terms
  with `xeo:epistemicLayer` and has not decided to own an instance-level property (see
  `xeos:epistemicLayer`). The key carries the prefix so that it cannot be mistaken for a layer of
  anything else in the graph (a map layer, a network layer, a model layer).

### Concept slots: a relationship or a code

Where the ontology has a slot whose value is a `skos:Concept` (`gapType`, `atPriority`,
`algorithm`, `basis`, `frameworkKind`, ...), a property graph may store it either way:

- as a relationship to a concept node: `(:Gap)-[:GAP_TYPE]->(:Concept {notation: 'thin_content'})`
- as a property holding the concept's code: `(:Gap {gapType: 'thin_content'})`

Both conform. The code is the concept's `skos:notation`, and a slot that rides on a
relationship (`basis` on `SIMILAR_TO`) can only be stored the second way. The profile lists
each concept slot under both `relationshipTypes` and `properties`, marked `"conceptSlot": true`,
with the reference schemes that fill it.

## Using `neo4j-profile.json`

```json
{
  "version": "0.6.0",
  "namespace": "https://xeoontology.org/xeo#",
  "labels":            { "URL": { "iri": "…#URL", "layer": "entity", "module": "core", "definition": "…" } },
  "relationshipTypes": { "LINKS_TO": { "iri": "…#linksTo", "term": "linksTo", "layer": "observation",
                                       "module": "core", "domain": ["URL"], "range": ["URL"] } },
  "properties":        { "avgPosition": { "iri": "…#avgPosition", "layer": "observation",
                                          "module": "core", "datatype": "xsd:decimal" } },
  "schemes":           { "device": ["desktop", "mobile", "tablet"] }
}
```

- **Vendor it.** Copy the file into your repository with the XEO version and commit it came
  from. It is deterministic (sorted keys, no timestamps), so a diff shows exactly what changed
  between two XEO versions.
- **Check your graph against it.** Every label, relationship type and property key your loaders
  write should be a key in the profile or on a short, named list of your own local terms.
  `CALL db.labels()`, `CALL db.relationshipTypes()` and `CALL db.propertyKeys()` give you the
  three sets to compare.
- **Read `domain` and `range` as expectations.** They merge the ontology's `rdfs:domain` /
  `rdfs:range` with its `xeo:domainIncludes` / `xeo:rangeIncludes` hints. An empty list means
  the ontology leaves that side open on purpose. A relationship between labels not listed is
  unlisted, not wrong.
- **Build enums from `schemes`.** Each scheme is the list of codes in stated order.
  `schemes.json` has the labels and definitions as well.
- **A controlled string names its schemes.** A property key such as `metric`, `sentiment` or
  `dealOutcome` lists the schemes its code comes from in `"schemes"`. `metric` holds the code of
  an `xeo:Metric`: `"metric": "ctr"` names `xeos:metric-ctr`, whose type, unit and better
  direction are in `schemes.json`. A graph that keeps Metrics as nodes links to them with
  `READING_OF`, `NUMERATOR` and the other relationship types instead.
- **Read `status` and `deprecated` where present.** `"status": "extension"` marks a term that is
  declared and usable but that not every implementation is expected to support.
  `"deprecated": true` marks a term that still works and that XEO will not remove;
  `"replacedBy"` names what to write instead. An entry with neither is a current core term.
- **Vendor crosswalks are not in the profile.** Which vendor field fills which slot is in
  `mappings/` (one file per tool, not part of the ontology) and under `vendorSchemes` in `schemes.json`.
- **Stamp `xeoLayer` from it.** `labels[label].layer` and `relationshipTypes[type].layer` are the
  values to write.

## Lifting an export to RDF

`context.neo4j.jsonld` is a JSON-LD context keyed the way Neo4j names things. Shape each node
as `{ "id": …, "type": <label>, …properties }`, put an edge without properties on its start
node as `"<RELATIONSHIP_TYPE>": <end id>`, and the document parses as RDF with XEO IRIs. A
concept slot stored as a code resolves into the one scheme that fills it
(`"gapType": "thin_content"` becomes `xeos:gapType-thin_content`).

An edge that carries properties has no direct RDF form. Write it as an `Edge` record beside the
plain triple, which the context maps to an `rdf:Statement`:

```json
{ "type": "Edge", "start": "ex:url-1", "edge": "RANKS_FOR", "end": "ex:term-1",
  "avgPosition": "4.2", "clicks": 310 }
```

Write decimals as strings (`"4.2"`). A bare JSON number coerced to `xsd:decimal` is serialized
by JSON-LD processors in double notation, which is not a valid decimal.

`examples/neo4j-export.jsonld` is a small worked export; `examples/learn-graph.jsonld` is the
same kind of graph written against the camelCase `context.jsonld`.

## The mapping

<!-- BEGIN GENERATED: tools/gen_profile.py -->

Generated from XEO 0.6.0. Do not edit between the markers; run `tools/gen_profile.py`.

### Node labels (51)

| Label | XEO class | Layer | Module |
|---|---|---|---|
| `AlgorithmRun` | `xeo:AlgorithmRun` | episode | analysis |
| `AnswerEngine` | `xeo:AnswerEngine` | entity | visibility |
| `Brand` | `xeo:Brand` | entity | visibility |
| `CallToAction` (deprecated) | `xeo:CallToAction` | entity | core |
| `Campaign` | `xeo:Campaign` | entity | work |
| `Capability` | `xeo:Capability` | entity | decision |
| `ConversationalAgent` | `xeo:ConversationalAgent` | entity | visibility |
| `ConversionEvent` | `xeo:ConversionEvent` | episode | core |
| `ConversionPoint` | `xeo:ConversionPoint` | entity | core |
| `Crawl` | `xeo:Crawl` | episode | core |
| `Diagnostic` | `xeo:Diagnostic` | entity | decision |
| `DiagnosticRun` | `xeo:DiagnosticRun` | episode | decision |
| `Domain` | `xeo:Domain` | entity | core |
| `Engine` | `xeo:Engine` | entity | core |
| `Entity` | `xeo:Entity` | entity | core |
| `Experiment` | `xeo:Experiment` | episode | decision |
| `ExternalEvent` | `xeo:ExternalEvent` | episode | decision |
| `Feedback` | `xeo:Feedback` | interpretation | decision |
| `Framework` | `xeo:Framework` | norm | strategy |
| `Gap` | `xeo:Gap` | interpretation | decision |
| `GatedAsset` (deprecated) | `xeo:GatedAsset` | entity | core |
| `GenerativeEngine` | `xeo:GenerativeEngine` | entity | visibility |
| `Intervention` | `xeo:Intervention` | entity | decision |
| `LLMResponse` | `xeo:LLMResponse` | episode | visibility |
| `LeadCaptureForm` (deprecated) | `xeo:LeadCaptureForm` | entity | core |
| `Metric` | `xeo:Metric` | norm | core |
| `MetricReading` | `xeo:MetricReading` | observation | core |
| `MetricTarget` | `xeo:MetricTarget` | interpretation | work |
| `Objective` | `xeo:Objective` | interpretation | work |
| `Organization` | `xeo:Organization` | entity | core |
| `Outcome` | `xeo:Outcome` | observation | decision |
| `OwnerChange` (extension) | `xeo:OwnerChange` | episode | sales |
| `Person` | `xeo:Person` | entity | core |
| `PipelineRollup` | `xeo:PipelineRollup` | derivation | sales |
| `Playbook` | `xeo:Playbook` | entity | strategy |
| `Practice` | `xeo:Practice` | norm | strategy |
| `Project` | `xeo:Project` | entity | work |
| `Prompt` | `xeo:Prompt` | entity | visibility |
| `Recommendation` | `xeo:Recommendation` | interpretation | decision |
| `SearchEngine` | `xeo:SearchEngine` | entity | core |
| `SearchIntent` | `xeo:SearchIntent` | entity | core |
| `SearchPerformanceFact` | `xeo:SearchPerformanceFact` | observation | core |
| `SerpSnapshot` | `xeo:SerpSnapshot` | episode | core |
| `Stage` | `xeo:Stage` | norm | strategy |
| `StageTransition` | `xeo:StageTransition` | episode | sales |
| `Tactic` | `xeo:Tactic` | entity | decision |
| `TacticAssessment` | `xeo:TacticAssessment` | interpretation | decision |
| `Term` | `xeo:Term` | entity | core |
| `Topic` | `xeo:Topic` | derivation | core |
| `URL` | `xeo:URL` | entity | core |
| `Website` | `xeo:Website` | entity | core |

### Relationship types (114)

`open` means the ontology leaves that side unconstrained. A concept slot may also be stored as a property key holding the concept's code.

| Relationship type | XEO property | From | To | Layer | Module |
|---|---|---|---|---|---|
| `ABOUT` | `xeo:about` | `Prompt` · `Term` · `URL` | `Entity` · `Topic` | derivation | core |
| `ABOUT_TOPIC` | `xeo:aboutTopic` | `Campaign` | `Topic` | entity | work |
| `ACTIVATES` | `xeo:activates` | `Campaign` · `Organization` · `Project` | `Framework` · `Playbook` | norm | strategy |
| `ADDITIVITY` | `xeo:additivity` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `ADDRESSABLE_BY` | `xeo:addressableBy` | `Gap` | `Tactic` | interpretation | decision |
| `AGGREGATION` | `xeo:aggregation` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `AGGREGATION_BASIS` (extension) | `xeo:aggregationBasis` | `MetricReading` | `skos:Concept` (concept slot) | observation | core |
| `ALGORITHM` | `xeo:algorithm` | `AlgorithmRun` | `skos:Concept` (concept slot) | episode | analysis |
| `APPLIED_PRACTICE` | `xeo:appliedPractice` | `Recommendation` | `Practice` | derivation | strategy |
| `APPLIES_AT_SCOPE` | `xeo:appliesAtScope` | open | `skos:Concept` (concept slot) | norm | strategy |
| `APPLIES_TO` | `xeo:appliesTo` | `Practice` | `Intervention` · `Tactic` · `URL` · `skos:Concept` | norm | strategy |
| `APPLIES_TO_CONCEPT` | `xeo:appliesToConcept` | `Practice` | `skos:Concept` (concept slot) | norm | strategy |
| `ASSESSED_AS` | `xeo:assessedAs` | `Recommendation` · `Tactic` | `TacticAssessment` | interpretation | decision |
| `AT_PRIORITY` | `xeo:atPriority` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | decision |
| `AT_STAGE` | `xeo:atStage` | `Diagnostic` · `Gap` · `Tactic` | `Stage` | norm | strategy |
| `ATTRIBUTED_RESPONSE` | `xeo:attributedResponse` | `ConversionEvent` | `LLMResponse` | interpretation | visibility |
| `AUTHORED_BY` | `xeo:authoredBy` | `Practice` | open | norm | strategy |
| `BASE_METRIC` (extension) | `xeo:baseMetric` | `Metric` | `Metric` | norm | core |
| `BASELINE_READING` | `xeo:baselineReading` | `MetricTarget` · `Outcome` | `MetricReading` | observation | work |
| `BASIS` | `xeo:basis` | open | `skos:Concept` (concept slot) | derivation | analysis |
| `BETTER_DIRECTION` | `xeo:betterDirection` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `CAPTURED_BY` | `xeo:capturedBy` | `ConversionEvent` | `ConversionPoint` | observation | core |
| `CHILD_OF` | `xeo:childOf` | `Topic` | `Topic` | derivation | core |
| `CITES` | `xeo:cites` | `LLMResponse` | `URL` | observation | visibility |
| `CLIENT_OF` | `xeo:clientOf` | `Organization` | `Organization` | entity | work |
| `CLOSES_GAP` | `xeo:closesGap` | `Recommendation` | `Gap` | interpretation | decision |
| `COMPETES_WITH` | `xeo:competesWith` | `Brand` · `Domain` · `Website` | `Brand` · `Domain` · `Website` | interpretation | visibility |
| `COMPUTED_BY` | `xeo:computedBy` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `AlgorithmRun` | derivation | analysis |
| `CONFOUNDED_BY` | `xeo:confoundedBy` | `Experiment` · `Outcome` | `ExternalEvent` | interpretation | decision |
| `CONSTRAINS` | `xeo:constrains` | `Practice` | `Recommendation` | norm | strategy |
| `CONVERSION_ENTITY` (extension) | `xeo:conversionEntity` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `CONVERSION_METRIC` (extension) | `xeo:conversionMetric` | `Metric` | `Metric` | norm | core |
| `COVERS_TERM` | `xeo:coversTerm` | `Campaign` | `Term` | entity | work |
| `COVERS_URL` | `xeo:coversUrl` | `Campaign` | `URL` | entity | work |
| `DATA_STATE` (extension) | `xeo:dataState` | `MetricReading` | `skos:Concept` (concept slot) | observation | core |
| `DENOMINATOR` | `xeo:denominator` | `Metric` | `Metric` | norm | core |
| `EFFORT_ESTIMATE` | `xeo:effortEstimate` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | work |
| `EVALUATED_PRACTICE` | `xeo:evaluatedPractice` | `Recommendation` | `Practice` | derivation | strategy |
| `EVIDENCED_BY` | `xeo:evidencedBy` | `Gap` | `LLMResponse` · `Prompt` · `SerpSnapshot` · `Term` · `URL` | derivation | decision |
| `EXECUTION` | `xeo:execution` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | work |
| `FANS_OUT_TO` | `xeo:fansOutTo` | `Prompt` | `Term` | observation | visibility |
| `FEEDBACK_ON` | `xeo:feedbackOn` | `Feedback` | `Gap` · `Recommendation` | interpretation | decision |
| `FETCHED` | `xeo:fetched` | `Crawl` | `URL` | observation | core |
| `FRAMEWORK_KIND` | `xeo:frameworkKind` | `Framework` | `skos:Concept` (concept slot) | norm | strategy |
| `GAP_TYPE` | `xeo:gapType` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `GRAIN_TO_DATE` (extension) | `xeo:grainToDate` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `HAS_CAMPAIGN` | `xeo:hasCampaign` | `Project` | `Campaign` | entity | work |
| `HAS_CANONICAL` | `xeo:hasCanonical` | `URL` | `URL` | observation | core |
| `HAS_CONTROL` | `xeo:hasControl` | `Experiment` | `Term` · `URL` | episode | decision |
| `HAS_CONVERSION_POINT` | `xeo:hasConversionPoint` | `URL` | `ConversionPoint` | observation | core |
| `HAS_CRAWL` | `xeo:hasCrawl` | `Website` | `Crawl` | episode | core |
| `HAS_OBJECTIVE` | `xeo:hasObjective` | `Campaign` | `Objective` | interpretation | work |
| `HAS_PROJECT` | `xeo:hasProject` | `Website` | `Project` | entity | work |
| `HAS_RESPONSE` | `xeo:hasResponse` | `Prompt` | `LLMResponse` | episode | visibility |
| `HAS_RESULT` | `xeo:hasResult` | `SerpSnapshot` | `URL` | observation | core |
| `HAS_ROLE` | `xeo:hasRole` | `URL` | `skos:Concept` (concept slot) | derivation | strategy |
| `HAS_SNAPSHOT` | `xeo:hasSnapshot` | `Term` | `SerpSnapshot` | episode | core |
| `HAS_STAGE` | `xeo:hasStage` | `Framework` | `Stage` | norm | strategy |
| `HAS_TARGET` | `xeo:hasTarget` | `Objective` | `MetricTarget` | interpretation | work |
| `HAS_WEBSITE` | `xeo:hasWebsite` | `Brand` | `Website` | entity | visibility |
| `HOLDS_CAPABILITY` | `xeo:holdsCapability` | `Organization` | `Capability` | entity | work |
| `IMPLEMENTED_AS` | `xeo:implementedAs` | `Recommendation` | `Experiment` | episode | decision |
| `IN_CONTEXT` | `xeo:inContext` | `Experiment` | `Gap` | observation | decision |
| `IN_INTERVENTION` | `xeo:inIntervention` | `Tactic` | `Intervention` | derivation | decision |
| `IN_SCOPE` | `xeo:inScope` | `Project` | `Intervention` · `Tactic` | entity | work |
| `IN_TOPIC` | `xeo:inTopic` | `Term` | `Topic` | derivation | core |
| `INCLUDES` | `xeo:includes` | `Framework` · `Playbook` | `Diagnostic` · `Practice` · `Tactic` | entity | strategy |
| `INPUT_METRIC` | `xeo:inputMetric` | `Metric` | `Metric` | norm | core |
| `ISSUED_FOR` | `xeo:issuedFor` | `Recommendation` | `Campaign` | interpretation | work |
| `LEARNED_FROM` | `xeo:learnedFrom` | `Practice` | `Experiment` · `Outcome` | derivation | strategy |
| `LINKS_TO` | `xeo:linksTo` | `URL` | `URL` | observation | core |
| `MAGNITUDE_METRIC` | `xeo:magnitudeMetric` | `Gap` | `Metric` | derivation | decision |
| `MAGNITUDE_UNIT` | `xeo:magnitudeUnit` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `MEASURES` | `xeo:measures` | `Experiment` | `MetricTarget` | episode | work |
| `MENTIONS` | `xeo:mentions` | `LLMResponse` | `Brand` | observation | visibility |
| `METRIC_TYPE` | `xeo:metricType` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `NEXT_STAGE` | `xeo:nextStage` | `Stage` | `Stage` | norm | strategy |
| `NUMERATOR` | `xeo:numerator` | `Metric` | `Metric` | norm | core |
| `OBJECTIVE_READING` (extension) | `xeo:objectiveReading` | `Objective` | `MetricReading` | derivation | work |
| `ON_DIMENSION` | `xeo:onDimension` | `TacticAssessment` | `skos:Concept` (concept slot) | interpretation | decision |
| `ON_DOMAIN` | `xeo:onDomain` | `URL` | `Domain` | entity | core |
| `ON_ENGINE` | `xeo:onEngine` | open | `Engine` | episode | core |
| `ORGANIZATION_KIND` | `xeo:organizationKind` | `Organization` | `skos:Concept` (concept slot) | entity | core |
| `OWNS` | `xeo:owns` | `Organization` | `Brand` · `Website` | entity | core |
| `PART_OF` | `xeo:partOf` | `URL` | `Website` | entity | core |
| `PRECEDENT_FOR` | `xeo:precedentFor` | `Experiment` | `Experiment` | derivation | analysis |
| `PRODUCED_OUTCOME` | `xeo:producedOutcome` | `Experiment` | `Outcome` | observation | decision |
| `RANKS_FOR` | `xeo:ranksFor` | `URL` | `Term` | observation | core |
| `READING_OF` | `xeo:readingOf` | `MetricReading` | `Metric` | observation | core |
| `READS_SLOT` | `xeo:readsSlot` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `RECOMMENDS` | `xeo:recommends` | `Recommendation` | `Tactic` | interpretation | decision |
| `REDIRECTS_TO` | `xeo:redirectsTo` | `URL` | `URL` | observation | core |
| `REFERS_TO` | `xeo:refersTo` | open | `Organization` · `Person` | derivation | core |
| `RELATED_TERM` | `xeo:relatedTerm` | `SerpSnapshot` | `Term` | observation | core |
| `RELATIVE_TO` | `xeo:relativeTo` | `Gap` | `Brand` · `Domain` · `URL` | interpretation | decision |
| `REQUIRES_CAPABILITY` | `xeo:requiresCapability` | `Tactic` | `Capability` | entity | decision |
| `RESULT_READING` | `xeo:resultReading` | `Outcome` | `MetricReading` | observation | decision |
| `REVEALED_IN` | `xeo:revealedIn` | `Gap` | `DiagnosticRun` | episode | decision |
| `REVEALS` | `xeo:reveals` | `Diagnostic` | `Gap` | interpretation | decision |
| `RUN_OF` | `xeo:runOf` | `DiagnosticRun` | `Diagnostic` | episode | decision |
| `SCOPE` | `xeo:scope` | `MetricReading` | `Brand` · `Campaign` · `Prompt` · `Term` · `Topic` · `URL` · `Website` | observation | core |
| `SCOPED_TO` | `xeo:scopedTo` | `Topic` | `Website` | entity | core |
| `SIMILAR_TO` | `xeo:similarTo` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | derivation | analysis |
| `SUGGESTS` | `xeo:suggests` | `Diagnostic` | `Intervention` · `Tactic` | norm | decision |
| `SUPERSEDES` | `xeo:supersedes` | `Practice` | `Practice` | norm | strategy |
| `SUPPORTED_BY` | `xeo:supportedBy` | `Recommendation` | `Experiment` | interpretation | decision |
| `TARGETS_INTENT` | `xeo:targetsIntent` | open | `SearchIntent` | interpretation | core |
| `TESTS` | `xeo:tests` | `Experiment` | `Tactic` | episode | decision |
| `TIME_ANCHOR` | `xeo:timeAnchor` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `TRACKS_PROMPT` | `xeo:tracksPrompt` | `Website` | `Prompt` | entity | visibility |
| `TREATS` | `xeo:treats` | `Experiment` | `Term` · `URL` | episode | decision |
| `UNIT` | `xeo:unit` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `VERDICT` | `xeo:verdict` | `Feedback` · `Gap` | `skos:Concept` (concept slot) | interpretation | decision |
| `VISIBILITY_FOR` | `xeo:visibilityFor` | `Prompt` | `Brand` | observation | visibility |

### Property keys (169)

| Property key | Datatype | Values from | Layer | Module |
|---|---|---|---|---|
| `additivity` | concept code | `additivity` | norm | core |
| `aggregation` | concept code | `aggregation` | norm | core |
| `aggregationBasis` (extension) | concept code | `aggregationBasis` | observation | core |
| `algorithm` | concept code | `algorithm` | episode | analysis |
| `appliesAtScope` | concept code |  | norm | strategy |
| `appliesToConcept` | concept code |  | norm | strategy |
| `atPriority` | concept code | `priority` | interpretation | decision |
| `basis` | concept code | `similarityBasis` | derivation | analysis |
| `betterDirection` | concept code | `betterDirection` | norm | core |
| `dataState` (extension) | concept code | `dataState` | observation | core |
| `effortEstimate` | concept code | `effort` | interpretation | work |
| `execution` | concept code | `execution` | interpretation | work |
| `frameworkKind` | concept code | `frameworkKind` | norm | strategy |
| `gapType` | concept code | `gapType` | derivation | decision |
| `grainToDate` (extension) | concept code | `timeGrain` | norm | core |
| `hasRole` | concept code |  | derivation | strategy |
| `magnitudeUnit` | concept code | `magnitudeUnit` | derivation | decision |
| `metricType` | concept code | `metricType` | norm | core |
| `onDimension` | concept code |  | interpretation | decision |
| `organizationKind` | concept code | `organizationKind` | entity | core |
| `unit` | concept code | `metricUnit` | norm | core |
| `verdict` | concept code | `feedbackVerdict` · `gapVerdict` | interpretation | decision |
| `absoluteChange` | `xsd:decimal` |  | derivation | decision |
| `address` | `xsd:string` |  | entity | core |
| `agentContext` (extension) | `xsd:string` |  | norm | core |
| `amountAtTransition` | `xsd:decimal` |  | episode | sales |
| `amountInReportingCurrency` (extension) | `xsd:decimal` |  | derivation | core |
| `anchorText` | `xsd:string` |  | observation | core |
| `approved` | `xsd:boolean` |  | interpretation | decision |
| `assignedAt` | `xsd:dateTime` |  | derivation | core |
| `avgPosition` | `xsd:decimal` |  | observation | core |
| `baseline` | `xsd:decimal` |  | observation | work |
| `baselineCapturedAt` | `xsd:dateTime` |  | observation | work |
| `betweenness` | `xsd:decimal` |  | derivation | analysis |
| `cadence` | `xsd:string` | `cadence` | entity | work |
| `campaignInfluenceShare` (extension) | `xsd:decimal` |  | derivation | sales |
| `capturedAt` | `xsd:dateTime` |  | episode | core |
| `citationRank` | `xsd:integer` |  | observation | visibility |
| `citationRate` | `xsd:decimal` |  | derivation | visibility |
| `clicks` | `xsd:integer` |  | observation | core |
| `communityId` | `xsd:integer` |  | derivation | analysis |
| `concludedAt` | `xsd:dateTime` |  | episode | decision |
| `confidence` | `xsd:decimal` |  | derivation | core |
| `contentHash` | `xsd:string` |  | derivation | core |
| `contentType` | `xsd:string` |  | observation | core |
| `conversionPointType` | `xsd:string` | `conversionPointType` | entity | core |
| `conversionWindow` (extension) | `xsd:duration` |  | norm | core |
| `convertedAt` (extension) | `xsd:dateTime` |  | episode | sales |
| `convertedTo` (extension) | `xsd:string` |  | episode | sales |
| `crawlDepth` | `xsd:integer` |  | derivation | core |
| `crawler` | `xsd:string` |  | episode | core |
| `crmObjectType` | `xsd:string` | `crmObjectType` | entity | sales |
| `crmRecordRef` | `xsd:string` |  | entity | sales |
| `crmSystem` | `xsd:string` | `crmSystem` | entity | sales |
| `ctr` | `xsd:decimal` |  | observation | core |
| `cumulativeWindow` (extension) | `xsd:duration` |  | norm | core |
| `currencyCode` | `xsd:string` |  | observation | core |
| `datasetUri` | `xsd:string` |  | derivation | core |
| `dealAmount` | `xsd:decimal` |  | observation | sales |
| `dealClosedAt` | `xsd:dateTime` |  | observation | sales |
| `dealOutcome` | `xsd:string` | `dealOutcome` | observation | sales |
| `dealProbability` (extension) | `xsd:decimal` |  | interpretation | sales |
| `degree` | `xsd:integer` |  | derivation | analysis |
| `deletedAt` | `xsd:dateTime` |  | entity | work |
| `denominatorValue` | `xsd:decimal` |  | observation | core |
| `device` | `xsd:string` | `device` | episode | core |
| `direction` (deprecated) | `xsd:string` |  | interpretation | work |
| `durationDays` | `xsd:integer` |  | entity | work |
| `embeddedAt` | `xsd:dateTime` |  | derivation | core |
| `embeddingDim` | `xsd:integer` |  | derivation | core |
| `embeddingModel` | `xsd:string` |  | derivation | core |
| `embeddingRef` | `xsd:string` |  | derivation | core |
| `endedAt` | `xsd:dateTime` |  | episode | core |
| `engagementType` | `xsd:string` | `engagementType` | entity | work |
| `enteredAt` | `xsd:dateTime` |  | episode | sales |
| `entityRef` | `xsd:string` |  | entity | core |
| `exitedAt` | `xsd:dateTime` |  | episode | sales |
| `expectedCloseDate` | `xsd:date` |  | interpretation | sales |
| `expression` | `xsd:string` |  | norm | core |
| `fetchedAt` | `xsd:dateTime` |  | observation | core |
| `fired` | `xsd:boolean` |  | derivation | strategy |
| `firstSeenAt` | `xsd:dateTime` |  | observation | core |
| `firstTouchChannel` | `xsd:string` | `acquisitionChannel` | derivation | sales |
| `forecastCategory` (extension) | `xsd:string` | `forecastCategory` | interpretation | sales |
| `fromStageRef` | `xsd:string` |  | episode | sales |
| `h1` | `xsd:string` |  | observation | core |
| `halfLife` | `xsd:duration` |  | norm | strategy |
| `impressions` | `xsd:integer` |  | observation | core |
| `indexable` | `xsd:boolean` |  | derivation | core |
| `interventionQuota` | `xsd:integer` |  | entity | work |
| `isPrimary` | `xsd:boolean` |  | interpretation | work |
| `lastSeenAt` | `xsd:dateTime` |  | observation | core |
| `lastSeenCrawlId` | `xsd:string` |  | episode | core |
| `latestTouchChannel` (extension) | `xsd:string` |  | derivation | sales |
| `leadStatus` (extension) | `xsd:string` |  | interpretation | sales |
| `lifecycleStage` (extension) | `xsd:string` | `lifecycleStageClass` | interpretation | sales |
| `lift` (deprecated) | `xsd:decimal` |  | observation | decision |
| `linkPosition` | `xsd:string` | `linkPosition` | derivation | core |
| `locale` | `xsd:string` |  | episode | core |
| `lostReason` (extension) | `xsd:string` |  | interpretation | sales |
| `magnitude` | `xsd:decimal` |  | derivation | decision |
| `marketingCampaignRef` (extension) | `xsd:string` |  | entity | sales |
| `mentionRank` | `xsd:integer` |  | observation | visibility |
| `mentionRate` | `xsd:decimal` |  | derivation | visibility |
| `metaDescription` | `xsd:string` |  | observation | core |
| `method` | `xsd:string` |  | interpretation | decision |
| `metric` | `xsd:string` | `metric` · `objectiveMetric` | interpretation | work |
| `metricFilter` | `xsd:string` |  | norm | core |
| `minDenominator` | `xsd:integer` |  | norm | core |
| `model` | `xsd:string` |  | episode | core |
| `modelVersion` | `xsd:string` |  | episode | visibility |
| `name` | `xsd:string` |  | entity | core |
| `numeratorValue` | `xsd:decimal` |  | observation | core |
| `occurredAt` | `xsd:dateTime` |  | episode | core |
| `offsetWindow` (extension) | `xsd:duration` |  | norm | core |
| `origin` | `xsd:string` |  | entity | core |
| `ownerRef` | `xsd:string` |  | entity | sales |
| `pageRank` | `xsd:decimal` |  | derivation | analysis |
| `parameters` | `xsd:string` |  | episode | analysis |
| `percentileValue` (extension) | `xsd:decimal` |  | norm | core |
| `periodEnd` | `xsd:date` |  | derivation | core |
| `periodStart` | `xsd:date` |  | derivation | core |
| `pipelineRef` | `xsd:string` |  | entity | sales |
| `position` | `xsd:integer` |  | observation | core |
| `practiceKind` | `xsd:string` | `practiceKind` | norm | strategy |
| `practiceOutcome` | `xsd:string` | `practiceOutcome` | derivation | strategy |
| `projection` | `xsd:string` |  | episode | analysis |
| `ranAt` | `xsd:dateTime` |  | episode | analysis |
| `rationale` | `xsd:string` |  | norm | strategy |
| `recordCreatedAt` | `xsd:dateTime` |  | observation | sales |
| `recordOrigin` (extension) | `xsd:string` | `recordOrigin` | observation | sales |
| `recurringValue` (extension) | `xsd:decimal` |  | observation | core |
| `referringPlatform` | `xsd:string` |  | derivation | sales |
| `rel` | `xsd:string` |  | observation | core |
| `relativeChange` | `xsd:decimal` |  | derivation | decision |
| `responses` | `xsd:integer` |  | observation | visibility |
| `result` | `xsd:string` | `outcomeResult` | observation | decision |
| `resultReason` | `xsd:string` | `outcomeResultReason` | observation | decision |
| `resultType` | `xsd:string` | `serpResultType` | observation | core |
| `resultsWindowDays` | `xsd:integer` |  | interpretation | work |
| `resultsWindowStart` | `xsd:date` |  | interpretation | work |
| `robotsMeta` | `xsd:string` |  | observation | core |
| `score` | `xsd:decimal` |  | interpretation | decision |
| `sentiment` | `xsd:string` | `sentiment` | derivation | visibility |
| `similarity` | `xsd:decimal` |  | derivation | analysis |
| `source` | `xsd:string` | `practiceSource` | norm | strategy |
| `stageClass` | `xsd:string` | `dealStageClass` | norm | sales |
| `stageDefaultProbability` (extension) | `xsd:decimal` |  | norm | sales |
| `stageOrder` | `xsd:integer` |  | norm | strategy |
| `stageRef` | `xsd:string` |  | entity | sales |
| `stageSlot` | `xsd:string` | `stageSlot` | episode | sales |
| `startedAt` | `xsd:dateTime` |  | episode | core |
| `statement` | `xsd:string` |  | norm | strategy |
| `status` | `xsd:string` | `experimentStatus` · `practiceStatus` · `recommendationStatus` | norm | strategy |
| `statusCode` | `xsd:integer` |  | observation | core |
| `syncedAt` | `xsd:dateTime` |  | derivation | core |
| `targetCurrency` | `xsd:string` |  | interpretation | work |
| `targetKind` | `xsd:string` | `targetKind` | interpretation | work |
| `targetValue` | `xsd:decimal` |  | interpretation | work |
| `test` | `xsd:string` |  | norm | strategy |
| `text` | `xsd:string` |  | entity | visibility |
| `title` | `xsd:string` |  | observation | core |
| `toStageRef` | `xsd:string` |  | episode | sales |
| `value` | `xsd:decimal` |  | observation | core |
| `valuePeriod` (extension) | `xsd:string` | `valuePeriod` | observation | core |
| `webSearchEnabled` | `xsd:boolean` |  | episode | visibility |
| `websiteId` | `xsd:string` |  | entity | core |
| `weightedAmount` (extension) | `xsd:decimal` |  | derivation | sales |
| `wordCount` | `xsd:integer` |  | derivation | core |

### Reference schemes (50)

| Scheme | Codes |
|---|---|
| `acquisitionChannel` | `ai_assistant` · `ai_overview` · `direct` · `email` · `offline` · `organic_search` · `organic_social` · `other` · `paid_search` · `paid_social` · `referral` |
| `additivity` | `additive` · `non_additive` · `semi_additive` |
| `aggregation` | `count` · `count_distinct` · `last` · `max` · `mean` · `median` · `min` · `percentile` · `sum` · `weighted_mean` |
| `aggregationBasis` | `auto` · `by_page` · `by_property` |
| `algorithm` | `betweenness` · `cosine` · `degree` · `fastrp` · `knn` · `label_propagation` · `leiden` · `louvain` · `node_similarity` · `pagerank` · `shortest_path` |
| `betterDirection` | `down` · `none` · `up` |
| `cadence` | `monthly` · `quarterly` |
| `conversionPointType` | `chat` · `cta` · `gated_asset` · `lead_form` · `meeting_booker` |
| `crmObjectType` | `deal` · `lead` · `organization` · `person` |
| `crmSystem` | `attio` · `close` · `dynamics365` · `hubspot` · `pipedrive` · `salesforce` · `zoho` |
| `dataState` | `final` · `partial` |
| `dealOutcome` | `lost` · `open` · `won` |
| `dealStageClass` | `lost` · `open` · `won` |
| `device` | `desktop` · `mobile` · `tablet` |
| `effort` | `hours` · `days` · `weeks` · `quarter` |
| `engagementType` | `oneoff` · `retainer` |
| `execution` | `advised` · `ours` |
| `experimentStatus` | `measuring` · `concluded` · `cancelled` · `unmeasurable` |
| `feedbackVerdict` | `accepted` · `needs_work` · `rejected` |
| `forecastCategory` | `best_case` · `closed` · `commit` · `omitted` · `pipeline` |
| `frameworkKind` | `checklist` · `diagnostic` · `playbook` · `tactic_matrix` |
| `gapType` | `missing_page` · `orphaned` · `buried` · `thin_content` · `split` · `content_subtopic` · `content_format_asset` · `content_proof` · `content_intent_fit` · `visibility_deficit` · `position_climb` · `zero_click` · `project_footprint` · `domain_authority_deficit` |
| `gapVerdict` | `attack` · `defend` · `fix_first` · `hold` · `ignore` |
| `intervention` | `brand-entity-ops` · `community-mobilization` · `content-optimization` · `editorial-placement` · `local-placement` · `onsite-content-advisory` · `owned-content-creation` · `technical-onsite` |
| `lifecycleStageClass` | `customer` · `evangelist` · `lead` · `mql` · `opportunity` · `other` · `sql` · `subscriber` |
| `linkPosition` | `content` · `footer` · `header` · `navigation` · `other` · `sidebar` |
| `magnitudeUnit` | `clicks` · `impressions` · `inlinks` · `keywords` · `positions` · `referring_domains` · `sessions_estimated` · `words` |
| `metric` | `ai_answers_citing_owned` · `ai_answers_mentioning` · `ai_answers_sampled` · `ai_assistant_sessions` · `ai_average_position` · `ai_brand_mentions` · `ai_citation_rate` · `ai_citation_share` · `ai_citations` · `ai_mention_rate` · `ai_owned_citations` · `ai_referred_leads` · `ai_sentiment` · `ai_share_of_voice` · `ai_tracked_brand_mentions` · `clicks` · `converting_sessions` · `ctr` · `deals_closed` · `deals_created` · `deals_won` · `engaged_sessions` · `engagement_rate` · `etv` · `impressions` · `key_events` · `leads_created` · `pipeline_created` · `position` · `rank_absolute` · `revenue_won` · `sales_cycle_days` · `session_conversion_rate` · `sessions` · `win_rate` |
| `metricType` | `conversion` · `cumulative` · `derived` · `ratio` · `simple` |
| `metricUnit` | `count` · `currency` · `days` · `rank` · `ratio` · `score_0_100` · `seconds` |
| `objectiveMetric` | `ai_citation_rate` · `ai_mention_rate` · `clicks` · `ctr` · `etv` · `impressions` · `position` · `rank_absolute` |
| `organizationKind` | `agency` · `brand` · `in_house` |
| `outcomeResult` | `inconclusive` · `no_change` · `significant` |
| `outcomeResultReason` | `baseline_unavailable` · `below_volume_floor` · `co_intervention` · `confounded_external` · `no_page_data` · `no_qualifying_snapshot` · `window_incomplete` |
| `practiceKind` | `guardrail` · `guidance` · `preference` |
| `practiceOutcome` | `caveated` · `reranked` · `vetoed` |
| `practiceSource` | `authored` · `claimed` · `learned` |
| `practiceStatus` | `proposed` · `active` · `deprecated` |
| `priority` | `P0` · `P1` · `P2` |
| `recommendationStatus` | `pending` · `in_progress` · `blocked` · `cancelled` · `completed` |
| `recordOrigin` | `api` · `form` · `import` · `integration` · `manual` |
| `searchIntent` | `commercial_investigation` · `informational` · `navigational` · `transactional` |
| `sentiment` | `mixed` · `negative` · `neutral` · `positive` |
| `serpResultType` | `ai_overview` · `featured_snippet` · `image` · `knowledge_panel` · `local_pack` · `organic` · `paid` · `people_also_ask` · `related_search` · `shopping` · `top_stories` · `video` |
| `similarityBasis` | `lexical` · `links` · `shared_terms` · `structural_embedding` · `text_embedding` |
| `stageSlot` | `deal_stage` · `lead_status` · `lifecycle` |
| `targetKind` | `absolute` · `absolute_change` · `percent` · `relative` |
| `timeGrain` | `day` · `month` · `quarter` · `week` · `year` |
| `valuePeriod` | `annual` · `monthly` · `one_time` |
| `xeoLayer` | `entity` · `episode` · `observation` · `derivation` · `interpretation` · `norm` |

<!-- END GENERATED -->
