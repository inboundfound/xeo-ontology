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
- **`layer` is the instance-level epistemic layer.** A graph that wants to filter by kind of
  claim stamps each node and relationship with `layer`, one of `entity`, `episode`,
  `observation`, `derivation`, `interpretation`, `norm`. The value for a node or relationship is
  the `layer` of its label or type in the profile, with one exception the ontology states: a
  `MENTIONS` edge written by a model is a `derivation`, by a string match an `observation`.
  `layer` is a profile convention, not an XEO term: XEO types terms with `xeo:epistemicLayer`
  and has not decided to own an instance-level property (see `xeos:epistemicLayer`).

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
- **Stamp `layer` from it.** `labels[label].layer` and `relationshipTypes[type].layer` are the
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

### Node labels (45)

| Label | XEO class | Layer | Module |
|---|---|---|---|
| `AlgorithmRun` | `xeo:AlgorithmRun` | episode | analysis |
| `AnswerEngine` | `xeo:AnswerEngine` | entity | visibility |
| `Brand` | `xeo:Brand` | entity | visibility |
| `CallToAction` | `xeo:CallToAction` | entity | engagement |
| `Campaign` | `xeo:Campaign` | entity | delivery |
| `Capability` | `xeo:Capability` | entity | decision |
| `ConversationalAgent` | `xeo:ConversationalAgent` | entity | visibility |
| `ConversionEvent` | `xeo:ConversionEvent` | episode | engagement |
| `ConversionPoint` | `xeo:ConversionPoint` | entity | engagement |
| `Crawl` | `xeo:Crawl` | episode | core |
| `Diagnostic` | `xeo:Diagnostic` | entity | decision |
| `DiagnosticRun` | `xeo:DiagnosticRun` | episode | decision |
| `Domain` | `xeo:Domain` | entity | core |
| `Engine` | `xeo:Engine` | entity | visibility |
| `Entity` | `xeo:Entity` | entity | core |
| `Experiment` | `xeo:Experiment` | episode | decision |
| `ExternalEvent` | `xeo:ExternalEvent` | episode | decision |
| `Feedback` | `xeo:Feedback` | interpretation | decision |
| `Framework` | `xeo:Framework` | norm | strategy |
| `Gap` | `xeo:Gap` | interpretation | decision |
| `GatedAsset` | `xeo:GatedAsset` | entity | engagement |
| `GenerativeEngine` | `xeo:GenerativeEngine` | entity | visibility |
| `Intervention` | `xeo:Intervention` | entity | decision |
| `LLMResponse` | `xeo:LLMResponse` | episode | visibility |
| `LeadCaptureForm` | `xeo:LeadCaptureForm` | entity | engagement |
| `MetricTarget` | `xeo:MetricTarget` | interpretation | delivery |
| `Objective` | `xeo:Objective` | interpretation | delivery |
| `Organization` | `xeo:Organization` | entity | delivery |
| `Outcome` | `xeo:Outcome` | observation | decision |
| `Playbook` | `xeo:Playbook` | entity | strategy |
| `Practice` | `xeo:Practice` | norm | strategy |
| `Project` | `xeo:Project` | entity | delivery |
| `Prompt` | `xeo:Prompt` | entity | visibility |
| `Recommendation` | `xeo:Recommendation` | interpretation | decision |
| `SearchEngine` | `xeo:SearchEngine` | entity | visibility |
| `SearchIntent` | `xeo:SearchIntent` | entity | engagement |
| `SearchPerformanceFact` | `xeo:SearchPerformanceFact` | observation | core |
| `SerpSnapshot` | `xeo:SerpSnapshot` | episode | core |
| `Stage` | `xeo:Stage` | norm | strategy |
| `Tactic` | `xeo:Tactic` | entity | decision |
| `TacticAssessment` | `xeo:TacticAssessment` | interpretation | decision |
| `Term` | `xeo:Term` | entity | core |
| `Topic` | `xeo:Topic` | derivation | core |
| `URL` | `xeo:URL` | entity | core |
| `Website` | `xeo:Website` | entity | core |

### Relationship types (91)

`open` means the ontology leaves that side unconstrained. A concept slot may also be stored as a property key holding the concept's code.

| Relationship type | XEO property | From | To | Layer | Module |
|---|---|---|---|---|---|
| `ABOUT` | `xeo:about` | `Prompt` · `Term` · `URL` | `Entity` · `Topic` | derivation | core |
| `ABOUT_TOPIC` | `xeo:aboutTopic` | `Campaign` | `Topic` | entity | delivery |
| `ACTIVATES` | `xeo:activates` | `Campaign` · `Organization` · `Project` | `Framework` · `Playbook` | norm | strategy |
| `ADDRESSABLE_BY` | `xeo:addressableBy` | `Gap` | `Tactic` | interpretation | decision |
| `ALGORITHM` | `xeo:algorithm` | `AlgorithmRun` | `skos:Concept` (concept slot) | episode | analysis |
| `APPLIED_PRACTICE` | `xeo:appliedPractice` | `Recommendation` | `Practice` | derivation | strategy |
| `APPLIES_AT_SCOPE` | `xeo:appliesAtScope` | open | `skos:Concept` (concept slot) | norm | strategy |
| `APPLIES_TO` | `xeo:appliesTo` | `Practice` | `Intervention` · `Tactic` · `URL` · `skos:Concept` | norm | strategy |
| `APPLIES_TO_CONCEPT` | `xeo:appliesToConcept` | `Practice` | `skos:Concept` (concept slot) | norm | strategy |
| `ASSESSED_AS` | `xeo:assessedAs` | `Recommendation` · `Tactic` | `TacticAssessment` | interpretation | decision |
| `AT_PRIORITY` | `xeo:atPriority` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | decision |
| `AT_STAGE` | `xeo:atStage` | `Diagnostic` · `Gap` · `Tactic` | `Stage` | norm | strategy |
| `ATTRIBUTED_RESPONSE` | `xeo:attributedResponse` | `ConversionEvent` | `LLMResponse` | interpretation | engagement |
| `AUTHORED_BY` | `xeo:authoredBy` | `Practice` | open | norm | strategy |
| `BASIS` | `xeo:basis` | open | `skos:Concept` (concept slot) | derivation | analysis |
| `CAPTURED_BY` | `xeo:capturedBy` | `ConversionEvent` | `ConversionPoint` | observation | engagement |
| `CHILD_OF` | `xeo:childOf` | `Topic` | `Topic` | derivation | core |
| `CITES` | `xeo:cites` | `LLMResponse` | `URL` | observation | visibility |
| `CLIENT_OF` | `xeo:clientOf` | `Organization` | `Organization` | entity | delivery |
| `CLOSES_GAP` | `xeo:closesGap` | `Recommendation` | `Gap` | interpretation | decision |
| `COMPETES_WITH` | `xeo:competesWith` | `Brand` · `Domain` · `Website` | `Brand` · `Domain` · `Website` | interpretation | visibility |
| `COMPUTED_BY` | `xeo:computedBy` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `AlgorithmRun` | derivation | analysis |
| `CONFOUNDED_BY` | `xeo:confoundedBy` | `Experiment` · `Outcome` | `ExternalEvent` | interpretation | decision |
| `CONSTRAINS` | `xeo:constrains` | `Practice` | `Recommendation` | norm | strategy |
| `COVERS_TERM` | `xeo:coversTerm` | `Campaign` | `Term` | entity | delivery |
| `COVERS_URL` | `xeo:coversUrl` | `Campaign` | `URL` | entity | delivery |
| `EFFORT_ESTIMATE` | `xeo:effortEstimate` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | delivery |
| `EVALUATED_PRACTICE` | `xeo:evaluatedPractice` | `Recommendation` | `Practice` | derivation | strategy |
| `EVIDENCED_BY` | `xeo:evidencedBy` | `Gap` | `LLMResponse` · `Prompt` · `SerpSnapshot` · `Term` · `URL` | derivation | decision |
| `EXECUTION` | `xeo:execution` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | delivery |
| `FANS_OUT_TO` | `xeo:fansOutTo` | `Prompt` | `Term` | observation | visibility |
| `FEEDBACK_ON` | `xeo:feedbackOn` | `Feedback` | `Gap` · `Recommendation` | interpretation | decision |
| `FETCHED` | `xeo:fetched` | `Crawl` | `URL` | observation | core |
| `FRAMEWORK_KIND` | `xeo:frameworkKind` | `Framework` | `skos:Concept` (concept slot) | norm | strategy |
| `GAP_TYPE` | `xeo:gapType` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `HAS_CAMPAIGN` | `xeo:hasCampaign` | `Project` | `Campaign` | entity | delivery |
| `HAS_CANONICAL` | `xeo:hasCanonical` | `URL` | `URL` | observation | core |
| `HAS_CONTROL` | `xeo:hasControl` | `Experiment` | `Term` · `URL` | episode | decision |
| `HAS_CONVERSION_POINT` | `xeo:hasConversionPoint` | `URL` | `ConversionPoint` | observation | engagement |
| `HAS_CRAWL` | `xeo:hasCrawl` | `Website` | `Crawl` | episode | core |
| `HAS_OBJECTIVE` | `xeo:hasObjective` | `Campaign` | `Objective` | interpretation | delivery |
| `HAS_PROJECT` | `xeo:hasProject` | `Website` | `Project` | entity | delivery |
| `HAS_RESPONSE` | `xeo:hasResponse` | `Prompt` | `LLMResponse` | episode | visibility |
| `HAS_RESULT` | `xeo:hasResult` | `SerpSnapshot` | `URL` | observation | core |
| `HAS_ROLE` | `xeo:hasRole` | `URL` | `skos:Concept` (concept slot) | derivation | strategy |
| `HAS_SNAPSHOT` | `xeo:hasSnapshot` | `Term` | `SerpSnapshot` | episode | core |
| `HAS_STAGE` | `xeo:hasStage` | `Framework` | `Stage` | norm | strategy |
| `HAS_TARGET` | `xeo:hasTarget` | `Objective` | `MetricTarget` | interpretation | delivery |
| `HAS_WEBSITE` | `xeo:hasWebsite` | `Brand` | `Website` | entity | visibility |
| `HOLDS_CAPABILITY` | `xeo:holdsCapability` | `Organization` | `Capability` | entity | delivery |
| `IMPLEMENTED_AS` | `xeo:implementedAs` | `Recommendation` | `Experiment` | episode | decision |
| `IN_CONTEXT` | `xeo:inContext` | `Experiment` | `Gap` | observation | decision |
| `IN_INTERVENTION` | `xeo:inIntervention` | `Tactic` | `Intervention` | derivation | decision |
| `IN_SCOPE` | `xeo:inScope` | `Project` | `Intervention` · `Tactic` | entity | delivery |
| `IN_TOPIC` | `xeo:inTopic` | `Term` | `Topic` | derivation | core |
| `INCLUDES` | `xeo:includes` | `Framework` · `Playbook` | `Diagnostic` · `Practice` · `Tactic` | entity | strategy |
| `ISSUED_FOR` | `xeo:issuedFor` | `Recommendation` | `Campaign` | interpretation | delivery |
| `LEARNED_FROM` | `xeo:learnedFrom` | `Practice` | `Experiment` · `Outcome` | derivation | strategy |
| `LINKS_TO` | `xeo:linksTo` | `URL` | `URL` | observation | core |
| `MAGNITUDE_UNIT` | `xeo:magnitudeUnit` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `MEASURES` | `xeo:measures` | `Experiment` | `MetricTarget` | observation | delivery |
| `MENTIONS` | `xeo:mentions` | `LLMResponse` | `Brand` | observation | visibility |
| `NEXT_STAGE` | `xeo:nextStage` | `Stage` | `Stage` | norm | strategy |
| `ON_DIMENSION` | `xeo:onDimension` | `TacticAssessment` | `skos:Concept` (concept slot) | interpretation | decision |
| `ON_DOMAIN` | `xeo:onDomain` | `URL` | `Domain` | entity | core |
| `ON_ENGINE` | `xeo:onEngine` | open | `Engine` | episode | visibility |
| `ORGANIZATION_KIND` | `xeo:organizationKind` | `Organization` | `skos:Concept` (concept slot) | entity | delivery |
| `OWNS` | `xeo:owns` | `Organization` | `Brand` · `Website` | entity | delivery |
| `PART_OF` | `xeo:partOf` | `URL` | `Website` | entity | core |
| `PRECEDENT_FOR` | `xeo:precedentFor` | `Experiment` | `Experiment` | derivation | analysis |
| `PRODUCED_OUTCOME` | `xeo:producedOutcome` | `Experiment` | `Outcome` | observation | decision |
| `RANKS_FOR` | `xeo:ranksFor` | `URL` | `Term` | observation | core |
| `RECOMMENDS` | `xeo:recommends` | `Recommendation` | `Tactic` | interpretation | decision |
| `REDIRECTS_TO` | `xeo:redirectsTo` | `URL` | `URL` | observation | core |
| `RELATED_TERM` | `xeo:relatedTerm` | `SerpSnapshot` | `Term` | observation | core |
| `RELATIVE_TO` | `xeo:relativeTo` | `Gap` | `Brand` · `Domain` · `URL` | interpretation | decision |
| `REQUIRES_CAPABILITY` | `xeo:requiresCapability` | `Tactic` | `Capability` | entity | decision |
| `REVEALED_IN` | `xeo:revealedIn` | `Gap` | `DiagnosticRun` | episode | decision |
| `REVEALS` | `xeo:reveals` | `Diagnostic` | `Gap` | interpretation | decision |
| `RUN_OF` | `xeo:runOf` | `DiagnosticRun` | `Diagnostic` | episode | decision |
| `SCOPED_TO` | `xeo:scopedTo` | `Topic` | `Website` | entity | core |
| `SIMILAR_TO` | `xeo:similarTo` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | derivation | analysis |
| `SUGGESTS` | `xeo:suggests` | `Diagnostic` | `Intervention` · `Tactic` | norm | decision |
| `SUPERSEDES` | `xeo:supersedes` | `Practice` | `Practice` | norm | strategy |
| `SUPPORTED_BY` | `xeo:supportedBy` | `Recommendation` | `Experiment` | interpretation | decision |
| `TARGETS_INTENT` | `xeo:targetsIntent` | open | `SearchIntent` | interpretation | engagement |
| `TESTS` | `xeo:tests` | `Experiment` | `Tactic` | episode | decision |
| `TRACKS_PROMPT` | `xeo:tracksPrompt` | `Website` | `Prompt` | entity | visibility |
| `TREATS` | `xeo:treats` | `Experiment` | `Term` · `URL` | episode | decision |
| `VERDICT` | `xeo:verdict` | `Feedback` · `Gap` | `skos:Concept` (concept slot) | interpretation | decision |
| `VISIBILITY_FOR` | `xeo:visibilityFor` | `Prompt` | `Brand` | observation | visibility |

### Property keys (109)

| Property key | Datatype | Values from | Layer | Module |
|---|---|---|---|---|
| `algorithm` | concept code | `algorithm` | episode | analysis |
| `appliesAtScope` | concept code |  | norm | strategy |
| `appliesToConcept` | concept code |  | norm | strategy |
| `atPriority` | concept code | `priority` | interpretation | decision |
| `basis` | concept code | `similarityBasis` | derivation | analysis |
| `effortEstimate` | concept code | `effort` | interpretation | delivery |
| `execution` | concept code | `execution` | interpretation | delivery |
| `frameworkKind` | concept code | `frameworkKind` | norm | strategy |
| `gapType` | concept code | `gapType` | derivation | decision |
| `hasRole` | concept code |  | derivation | strategy |
| `magnitudeUnit` | concept code | `magnitudeUnit` | derivation | decision |
| `onDimension` | concept code |  | interpretation | decision |
| `organizationKind` | concept code | `organizationKind` | entity | delivery |
| `verdict` | concept code | `feedbackVerdict` · `gapVerdict` | interpretation | decision |
| `address` | `xsd:string` |  | entity | core |
| `anchorText` | `xsd:string` |  | observation | core |
| `approved` | `xsd:boolean` |  | interpretation | decision |
| `assignedAt` | `xsd:dateTime` |  | derivation | core |
| `avgPosition` | `xsd:decimal` |  | observation | core |
| `baseline` | `xsd:decimal` |  | observation | delivery |
| `baselineCapturedAt` | `xsd:dateTime` |  | observation | delivery |
| `betweenness` | `xsd:decimal` |  | derivation | analysis |
| `cadence` | `xsd:string` | `cadence` | entity | delivery |
| `capturedAt` | `xsd:dateTime` |  | episode | visibility |
| `citationRank` | `xsd:integer` |  | observation | visibility |
| `citationRate` | `xsd:decimal` |  | observation | visibility |
| `clicks` | `xsd:integer` |  | observation | core |
| `communityId` | `xsd:integer` |  | derivation | analysis |
| `concludedAt` | `xsd:dateTime` |  | episode | decision |
| `confidence` | `xsd:decimal` |  | derivation | core |
| `contentHash` | `xsd:string` |  | derivation | core |
| `contentType` | `xsd:string` |  | observation | core |
| `crawlDepth` | `xsd:integer` |  | derivation | core |
| `crawler` | `xsd:string` |  | episode | core |
| `crmRecordRef` | `xsd:string` |  | entity | engagement |
| `ctr` | `xsd:decimal` |  | observation | core |
| `datasetUri` | `xsd:string` |  | derivation | core |
| `degree` | `xsd:integer` |  | derivation | analysis |
| `deletedAt` | `xsd:dateTime` |  | entity | delivery |
| `device` | `xsd:string` | `device` | episode | core |
| `direction` | `xsd:string` |  | interpretation | delivery |
| `durationDays` | `xsd:integer` |  | entity | delivery |
| `embeddedAt` | `xsd:dateTime` |  | derivation | core |
| `embeddingDim` | `xsd:integer` |  | derivation | core |
| `embeddingModel` | `xsd:string` |  | derivation | core |
| `embeddingRef` | `xsd:string` |  | derivation | core |
| `endedAt` | `xsd:dateTime` |  | episode | core |
| `engagementType` | `xsd:string` | `engagementType` | entity | delivery |
| `entityRef` | `xsd:string` |  | entity | core |
| `fetchedAt` | `xsd:dateTime` |  | observation | core |
| `fired` | `xsd:boolean` |  | derivation | strategy |
| `firstSeenAt` | `xsd:dateTime` |  | observation | core |
| `h1` | `xsd:string` |  | observation | core |
| `halfLife` | `xsd:duration` |  | norm | strategy |
| `impressions` | `xsd:integer` |  | observation | core |
| `indexable` | `xsd:boolean` |  | derivation | core |
| `interventionQuota` | `xsd:integer` |  | entity | delivery |
| `isPrimary` | `xsd:boolean` |  | interpretation | delivery |
| `lastSeenAt` | `xsd:dateTime` |  | observation | core |
| `lastSeenCrawlId` | `xsd:string` |  | episode | core |
| `lift` | `xsd:decimal` |  | observation | decision |
| `linkPosition` | `xsd:string` | `linkPosition` | derivation | core |
| `locale` | `xsd:string` |  | episode | core |
| `magnitude` | `xsd:decimal` |  | derivation | decision |
| `mentionRank` | `xsd:integer` |  | observation | visibility |
| `mentionRate` | `xsd:decimal` |  | observation | visibility |
| `metaDescription` | `xsd:string` |  | observation | core |
| `method` | `xsd:string` |  | interpretation | decision |
| `metric` | `xsd:string` | `objectiveMetric` | interpretation | delivery |
| `model` | `xsd:string` |  | episode | visibility |
| `modelVersion` | `xsd:string` |  | episode | visibility |
| `name` | `xsd:string` |  | entity | core |
| `occurredAt` | `xsd:dateTime` |  | episode | engagement |
| `origin` | `xsd:string` |  | entity | core |
| `pageRank` | `xsd:decimal` |  | derivation | analysis |
| `parameters` | `xsd:string` |  | episode | analysis |
| `periodEnd` | `xsd:date` |  | derivation | core |
| `periodStart` | `xsd:date` |  | derivation | core |
| `position` | `xsd:integer` |  | observation | core |
| `practiceKind` | `xsd:string` | `practiceKind` | norm | strategy |
| `practiceOutcome` | `xsd:string` | `practiceOutcome` | derivation | strategy |
| `projection` | `xsd:string` |  | episode | analysis |
| `ranAt` | `xsd:dateTime` |  | episode | analysis |
| `rationale` | `xsd:string` |  | norm | strategy |
| `rel` | `xsd:string` |  | observation | core |
| `responses` | `xsd:integer` |  | observation | visibility |
| `result` | `xsd:string` | `outcomeResult` | observation | decision |
| `resultReason` | `xsd:string` | `outcomeResultReason` | observation | decision |
| `resultType` | `xsd:string` | `serpResultType` | observation | core |
| `resultsWindowDays` | `xsd:integer` |  | interpretation | delivery |
| `robotsMeta` | `xsd:string` |  | observation | core |
| `score` | `xsd:decimal` |  | interpretation | decision |
| `sentiment` | `xsd:string` | `sentiment` | derivation | visibility |
| `similarity` | `xsd:decimal` |  | derivation | analysis |
| `source` | `xsd:string` | `practiceSource` | norm | strategy |
| `stageOrder` | `xsd:integer` |  | norm | strategy |
| `startedAt` | `xsd:dateTime` |  | episode | core |
| `statement` | `xsd:string` |  | norm | strategy |
| `status` | `xsd:string` | `experimentStatus` · `practiceStatus` · `recommendationStatus` | norm | strategy |
| `statusCode` | `xsd:integer` |  | observation | core |
| `syncedAt` | `xsd:dateTime` |  | derivation | core |
| `targetKind` | `xsd:string` | `targetKind` | interpretation | delivery |
| `targetValue` | `xsd:decimal` |  | interpretation | delivery |
| `test` | `xsd:string` |  | norm | strategy |
| `text` | `xsd:string` |  | entity | visibility |
| `title` | `xsd:string` |  | observation | core |
| `webSearchEnabled` | `xsd:boolean` |  | episode | visibility |
| `websiteId` | `xsd:string` |  | entity | core |
| `wordCount` | `xsd:integer` |  | derivation | core |

### Reference schemes (29)

| Scheme | Codes |
|---|---|
| `algorithm` | `betweenness` · `cosine` · `degree` · `fastrp` · `knn` · `label_propagation` · `leiden` · `louvain` · `node_similarity` · `pagerank` · `shortest_path` |
| `cadence` | `monthly` · `quarterly` |
| `device` | `desktop` · `mobile` · `tablet` |
| `effort` | `hours` · `days` · `weeks` · `quarter` |
| `engagementType` | `oneoff` · `retainer` |
| `epistemicLayer` | `entity` · `episode` · `observation` · `derivation` · `interpretation` · `norm` |
| `execution` | `advised` · `ours` |
| `experimentStatus` | `measuring` · `concluded` · `cancelled` · `unmeasurable` |
| `feedbackVerdict` | `accepted` · `needs_work` · `rejected` |
| `frameworkKind` | `checklist` · `diagnostic` · `playbook` · `tactic_matrix` |
| `gapType` | `missing_page` · `orphaned` · `buried` · `thin_content` · `split` · `content_subtopic` · `content_format_asset` · `content_proof` · `content_intent_fit` · `visibility_deficit` · `position_climb` · `zero_click` · `project_footprint` · `domain_authority_deficit` |
| `gapVerdict` | `attack` · `defend` · `fix_first` · `hold` · `ignore` |
| `intervention` | `brand-entity-ops` · `community-mobilization` · `content-optimization` · `editorial-placement` · `local-placement` · `onsite-content-advisory` · `owned-content-creation` · `technical-onsite` |
| `linkPosition` | `content` · `footer` · `header` · `navigation` · `other` · `sidebar` |
| `magnitudeUnit` | `clicks` · `impressions` · `inlinks` · `keywords` · `positions` · `referring_domains` · `sessions_estimated` · `words` |
| `objectiveMetric` | `citation_rate` · `clicks` · `ctr` · `etv` · `impressions` · `mention_rate` · `position` · `rank_absolute` |
| `organizationKind` | `agency` · `brand` · `in_house` |
| `outcomeResult` | `inconclusive` · `no_change` · `significant` |
| `outcomeResultReason` | `baseline_unavailable` · `below_volume_floor` · `co_intervention` · `confounded_external` · `no_page_data` · `no_qualifying_snapshot` · `window_incomplete` |
| `practiceKind` | `guardrail` · `guidance` · `preference` |
| `practiceOutcome` | `caveated` · `reranked` · `vetoed` |
| `practiceSource` | `authored` · `claimed` · `learned` |
| `practiceStatus` | `proposed` · `active` · `deprecated` |
| `priority` | `P0` · `P1` · `P2` |
| `recommendationStatus` | `pending` · `in_progress` · `blocked` · `cancelled` · `completed` |
| `sentiment` | `mixed` · `negative` · `neutral` · `positive` |
| `serpResultType` | `ai_overview` · `featured_snippet` · `image` · `knowledge_panel` · `local_pack` · `organic` · `paid` · `people_also_ask` · `related_search` · `shopping` · `top_stories` · `video` |
| `similarityBasis` | `lexical` · `links` · `shared_terms` · `structural_embedding` · `text_embedding` |
| `targetKind` | `absolute` · `percent` |

<!-- END GENERATED -->
