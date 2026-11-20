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
- **`xeoLayer` is the layer, on terms and on instances alike.** A graph that wants to filter by kind of
  claim stamps each node and relationship with `xeoLayer`, one of `entity`, `episode`,
  `observation`, `derivation`, `interpretation`, `norm`. The value for a node or relationship is
  the `layer` of its label or type in the profile, with one exception the ontology states: a
  `MENTIONS` edge written by a model is a `derivation`, by a string match an `observation`.
  XEO types its terms with the same name, `xeo:xeoLayer` (`epistemicLayer` until 0.7), and the
  six values are the scheme `xeos:xeoLayer`; the profile records the key as
  `conventions.layerKey`. The key carries the prefix so that it cannot be mistaken for a layer of
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
  `"status": "draft"` marks a term of a module still being written, which may change or be
  removed without a deprecation step.
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

Generated from XEO 0.7.2. Do not edit between the markers; run `tools/gen_profile.py`.

### Node labels (102)

| Label | XEO class | Layer | Module |
|---|---|---|---|
| `ActionItem` (draft) | `xeo:ActionItem` | interpretation | knowledge |
| `AgentRuntime` (draft) | `xeo:AgentRuntime` | entity | agentic |
| `AgentSession` (draft) | `xeo:AgentSession` | episode | agentic |
| `AgentTurn` (draft) | `xeo:AgentTurn` | episode | agentic |
| `AlgorithmRun` | `xeo:AlgorithmRun` | episode | analysis |
| `AnswerEngine` | `xeo:AnswerEngine` | entity | visibility |
| `Arm` (draft) | `xeo:Arm` | entity | experiments |
| `AttributedCredit` | `xeo:AttributedCredit` | derivation | attribution |
| `AttributionModel` | `xeo:AttributionModel` | norm | attribution |
| `AttributionRollup` | `xeo:AttributionRollup` | derivation | attribution |
| `Benchmark` (draft) | `xeo:Benchmark` | entity | experiments |
| `BenchmarkTask` (draft) | `xeo:BenchmarkTask` | entity | experiments |
| `BookedMeeting` | `xeo:BookedMeeting` | episode | attribution |
| `Brand` | `xeo:Brand` | entity | visibility |
| `Call` | `xeo:Call` | episode | attribution |
| `Campaign` | `xeo:Campaign` | entity | work |
| `Capability` | `xeo:Capability` | entity | decision |
| `Chargeback` | `xeo:Chargeback` | episode | attribution |
| `Claim` (draft) | `xeo:Claim` | interpretation | experiments |
| `ClaimCheck` (draft) | `xeo:ClaimCheck` | interpretation | experiments |
| `Compaction` (draft) | `xeo:Compaction` | episode | agentic |
| `Consent` | `xeo:Consent` | observation | core |
| `ConversionEvent` | `xeo:ConversionEvent` | episode | core |
| `ConversionPoint` | `xeo:ConversionPoint` | entity | core |
| `Crawl` | `xeo:Crawl` | episode | core |
| `CreditAnchor` | `xeo:CreditAnchor` | norm | attribution |
| `Delegation` (draft) | `xeo:Delegation` | episode | agentic |
| `Deliverable` (draft) | `xeo:Deliverable` | episode | work |
| `DesignAsset` (draft) | `xeo:DesignAsset` | entity | design |
| `DesignComponent` (draft) | `xeo:DesignComponent` | entity | design |
| `DesignConcept` (draft) | `xeo:DesignConcept` | entity | design |
| `DesignDecision` (draft) | `xeo:DesignDecision` | interpretation | design |
| `DesignDirection` (draft) | `xeo:DesignDirection` | entity | design |
| `DesignElement` (draft) | `xeo:DesignElement` | entity | design |
| `DesignPattern` (draft) | `xeo:DesignPattern` | entity | design |
| `DesignSystem` (draft) | `xeo:DesignSystem` | entity | design |
| `DesignToken` (draft) | `xeo:DesignToken` | entity | design |
| `Diagnostic` | `xeo:Diagnostic` | entity | decision |
| `DiagnosticRun` | `xeo:DiagnosticRun` | episode | decision |
| `Domain` | `xeo:Domain` | entity | core |
| `EnforcementEvent` (draft) | `xeo:EnforcementEvent` | episode | agentic |
| `Engine` | `xeo:Engine` | entity | core |
| `Entity` | `xeo:Entity` | entity | core |
| `Experiment` | `xeo:Experiment` | episode | decision |
| `ExternalEvent` | `xeo:ExternalEvent` | episode | decision |
| `Feedback` | `xeo:Feedback` | interpretation | decision |
| `Framework` | `xeo:Framework` | norm | decision |
| `Gap` | `xeo:Gap` | interpretation | decision |
| `GenerativeOverview` | `xeo:GenerativeOverview` | entity | visibility |
| `Harness` (draft) | `xeo:Harness` | entity | agentic |
| `HarnessComponent` (draft) | `xeo:HarnessComponent` | entity | agentic |
| `IdentityLink` | `xeo:IdentityLink` | derivation | attribution |
| `InboundReference` | `xeo:InboundReference` | observation | core |
| `Intervention` | `xeo:Intervention` | entity | decision |
| `InvocationConfig` (draft) | `xeo:InvocationConfig` | entity | agentic |
| `Journey` | `xeo:Journey` | derivation | attribution |
| `LLMResponse` | `xeo:LLMResponse` | episode | visibility |
| `Lesson` (draft) | `xeo:Lesson` | interpretation | experiments |
| `Meeting` (draft) | `xeo:Meeting` | episode | knowledge |
| `Metric` | `xeo:Metric` | norm | core |
| `MetricReading` | `xeo:MetricReading` | observation | core |
| `MetricTarget` | `xeo:MetricTarget` | interpretation | work |
| `Model` | `xeo:Model` | entity | core |
| `ModelCall` (draft) | `xeo:ModelCall` | episode | agentic |
| `Objective` | `xeo:Objective` | interpretation | work |
| `Order` | `xeo:Order` | episode | attribution |
| `Organization` | `xeo:Organization` | entity | core |
| `Outcome` | `xeo:Outcome` | observation | decision |
| `OwnerChange` (extension) | `xeo:OwnerChange` | episode | sales |
| `PageTemplate` (draft) | `xeo:PageTemplate` | entity | design |
| `Payment` | `xeo:Payment` | episode | attribution |
| `Person` | `xeo:Person` | entity | core |
| `PipelineRollup` | `xeo:PipelineRollup` | derivation | sales |
| `Playbook` | `xeo:Playbook` | entity | decision |
| `Practice` | `xeo:Practice` | norm | decision |
| `Project` | `xeo:Project` | entity | work |
| `Prompt` | `xeo:Prompt` | entity | visibility |
| `Recommendation` | `xeo:Recommendation` | interpretation | decision |
| `Recording` (draft) | `xeo:Recording` | observation | knowledge |
| `Refund` | `xeo:Refund` | episode | attribution |
| `RevenueEvent` | `xeo:RevenueEvent` | episode | attribution |
| `SearchEngine` | `xeo:SearchEngine` | entity | core |
| `SearchIntent` | `xeo:SearchIntent` | entity | core |
| `SearchPerformanceFact` | `xeo:SearchPerformanceFact` | observation | core |
| `SerpSnapshot` | `xeo:SerpSnapshot` | episode | core |
| `Spec` (draft) | `xeo:Spec` | entity | work |
| `SpendRollup` | `xeo:SpendRollup` | observation | attribution |
| `Stage` | `xeo:Stage` | norm | decision |
| `StageTransition` | `xeo:StageTransition` | episode | sales |
| `Subscription` | `xeo:Subscription` | entity | attribution |
| `Summary` (draft) | `xeo:Summary` | derivation | knowledge |
| `Tactic` | `xeo:Tactic` | entity | decision |
| `TacticAssessment` | `xeo:TacticAssessment` | interpretation | decision |
| `Term` | `xeo:Term` | entity | core |
| `ToolCall` (draft) | `xeo:ToolCall` | episode | agentic |
| `Topic` | `xeo:Topic` | derivation | core |
| `Touchpoint` | `xeo:Touchpoint` | episode | attribution |
| `Transcript` (draft) | `xeo:Transcript` | observation | knowledge |
| `Trial` (draft) | `xeo:Trial` | episode | experiments |
| `URL` | `xeo:URL` | entity | core |
| `Website` | `xeo:Website` | entity | core |
| `WorkItem` (draft) | `xeo:WorkItem` | entity | work |

### Relationship types (192)

`open` means the ontology leaves that side unconstrained. A concept slot may also be stored as a property key holding the concept's code.

| Relationship type | XEO property | From | To | Layer | Module |
|---|---|---|---|---|---|
| `ABOUT` | `xeo:about` | `Prompt` · `Term` · `URL` | `Entity` · `Topic` | derivation | core |
| `ABOUT_TOPIC` | `xeo:aboutTopic` | `Campaign` | `Topic` | entity | work |
| `ACQUIRED_BY_TACTIC` | `xeo:acquiredByTactic` | `InboundReference` | `Tactic` | interpretation | decision |
| `ACTIVATES` | `xeo:activates` | `Campaign` · `Organization` · `Project` | `Framework` · `Playbook` | norm | decision |
| `ADDITIVITY` | `xeo:additivity` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `ADDRESSABLE_BY` | `xeo:addressableBy` | `Gap` | `Intervention` · `Tactic` | interpretation | decision |
| `ADOPTED_AS` (draft) | `xeo:adoptedAs` | `Lesson` | `Practice` | norm | experiments |
| `AGGREGATION` | `xeo:aggregation` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `AGGREGATION_BASIS` (extension) | `xeo:aggregationBasis` | `MetricReading` | `skos:Concept` (concept slot) | observation | core |
| `ALGORITHM` | `xeo:algorithm` | `AlgorithmRun` | `skos:Concept` (concept slot) | episode | analysis |
| `ALIAS_OF` (draft) | `xeo:aliasOf` | `DesignToken` | `DesignToken` | entity | design |
| `APPLIED_PRACTICE` | `xeo:appliedPractice` | `Recommendation` | `Practice` | derivation | decision |
| `APPLIES_AT_SCOPE` | `xeo:appliesAtScope` | open | `skos:Concept` (concept slot) | norm | decision |
| `APPLIES_TO` | `xeo:appliesTo` | `Gap` · `Practice` · `Recommendation` | `Intervention` · `Tactic` · `URL` · `skos:Concept` | norm | decision |
| `APPLIES_TO_CONCEPT` | `xeo:appliesToConcept` | `Practice` | `skos:Concept` (concept slot) | norm | decision |
| `ASSESSED_AS` | `xeo:assessedAs` | `Recommendation` · `Tactic` | `TacticAssessment` | interpretation | decision |
| `ASSIGNED_TO` (draft) | `xeo:assignedTo` | `ActionItem` | `Organization` · `Person` | interpretation | knowledge |
| `AT_PRIORITY` | `xeo:atPriority` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | decision |
| `AT_STAGE` | `xeo:atStage` | `Diagnostic` · `Gap` · `Tactic` | `Stage` | norm | decision |
| `ATTENDEE` (draft) | `xeo:attendee` | `Meeting` | `Person` | episode | knowledge |
| `ATTRIBUTED_RESPONSE` | `xeo:attributedResponse` | `ConversionEvent` | `LLMResponse` | interpretation | visibility |
| `AUTHORED_BY` | `xeo:authoredBy` | `Practice` | open | norm | decision |
| `BASE_METRIC` (extension) | `xeo:baseMetric` | `Metric` | `Metric` | norm | core |
| `BASELINE_READING` | `xeo:baselineReading` | `MetricTarget` · `Outcome` | `MetricReading` | observation | work |
| `BASIS` | `xeo:basis` | open | `skos:Concept` (concept slot) | derivation | analysis |
| `BETTER_DIRECTION` | `xeo:betterDirection` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `CAPTURED_BY` | `xeo:capturedBy` | `ConversionEvent` | `ConversionPoint` | observation | core |
| `CHECKED_BY` (draft) | `xeo:checkedBy` | `ClaimCheck` | `Experiment` | interpretation | experiments |
| `CHECKS_CLAIM` (draft) | `xeo:checksClaim` | `ClaimCheck` | `Claim` | interpretation | experiments |
| `CHILD_OF` | `xeo:childOf` | `Topic` | `Topic` | derivation | core |
| `CHILD_SESSION` (draft) | `xeo:childSession` | `Delegation` | `AgentSession` | episode | agentic |
| `CHOSEN_CONCEPT` (draft) | `xeo:chosenConcept` | `DesignDecision` | `DesignConcept` | interpretation | design |
| `CITES` | `xeo:cites` | `LLMResponse` | `URL` | observation | visibility |
| `CLAIM_METRIC` (draft) | `xeo:claimMetric` | `Claim` | `Metric` | interpretation | experiments |
| `CLAIMED_BY` (draft) | `xeo:claimedBy` | `Claim` | `Organization` · `Person` | interpretation | experiments |
| `CLIENT_OF` | `xeo:clientOf` | `Organization` | `Organization` | entity | work |
| `CLOSES_GAP` | `xeo:closesGap` | `Recommendation` | `Gap` | interpretation | decision |
| `COMPETES_WITH` | `xeo:competesWith` | `Brand` · `Domain` · `Website` | `Brand` · `Domain` · `Website` | interpretation | visibility |
| `COMPOSED_OF` (draft) | `xeo:composedOf` | `DesignComponent` · `DesignPattern` · `PageTemplate` | `DesignComponent` · `DesignPattern` | entity | design |
| `COMPUTED_BY` | `xeo:computedBy` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `AlgorithmRun` | derivation | analysis |
| `CONFOUNDED_BY` | `xeo:confoundedBy` | `Experiment` · `Outcome` | `ExternalEvent` | interpretation | decision |
| `CONSENT_SUBJECT` | `xeo:consentSubject` | `Consent` | `Organization` · `Person` | observation | core |
| `CONSTRAINS` | `xeo:constrains` | `Practice` | `Recommendation` | norm | decision |
| `CONTINUES_SESSION` (draft) | `xeo:continuesSession` | `AgentSession` | `AgentSession` | episode | agentic |
| `CONVERSION_ENTITY` (extension) | `xeo:conversionEntity` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `CONVERSION_METRIC` (extension) | `xeo:conversionMetric` | `Metric` | `Metric` | norm | core |
| `COVERS_TERM` | `xeo:coversTerm` | `Campaign` | `Term` | entity | work |
| `COVERS_URL` | `xeo:coversUrl` | `Campaign` | `URL` | entity | work |
| `CREDIT_FOR` | `xeo:creditFor` | `AttributedCredit` | `ConversionEvent` · `RevenueEvent` | derivation | attribution |
| `CREDITED_TOUCHPOINT` | `xeo:creditedTouchpoint` | `AttributedCredit` | `Touchpoint` | derivation | attribution |
| `DATA_STATE` (extension) | `xeo:dataState` | `MetricReading` | `skos:Concept` (concept slot) | observation | core |
| `DECIDED_BY` (draft) | `xeo:decidedBy` | `DesignDecision` | `Person` | interpretation | design |
| `DECIDES_ON` (draft) | `xeo:decidesOn` | `DesignDecision` | `DesignConcept` · `DesignDirection` · `DesignElement` | interpretation | design |
| `DENOMINATOR` | `xeo:denominator` | `Metric` | `Metric` | norm | core |
| `DEPICTS` (draft) | `xeo:depicts` | `DesignConcept` | `DesignComponent` · `DesignElement` · `DesignPattern` · `PageTemplate` · `URL` | entity | design |
| `DIRECTION_FOR` (draft) | `xeo:directionFor` | `DesignDirection` | `Brand` · `Project` · `Website` | entity | design |
| `DRAWN_FROM` (draft) | `xeo:drawnFrom` | `Lesson` | `ClaimCheck` · `Experiment` · `Outcome` | derivation | experiments |
| `EFFORT_ESTIMATE` | `xeo:effortEstimate` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | work |
| `ELEMENT_OF` (draft) | `xeo:elementOf` | `DesignElement` | `Website` | entity | design |
| `EVALUATED_PRACTICE` | `xeo:evaluatedPractice` | `Recommendation` | `Practice` | derivation | decision |
| `EVIDENCED_BY` | `xeo:evidencedBy` | `Gap` | `LLMResponse` · `Prompt` · `SerpSnapshot` · `Term` · `URL` | derivation | decision |
| `EXECUTION` | `xeo:execution` | `Recommendation` | `skos:Concept` (concept slot) | interpretation | work |
| `EXPRESSES_PRACTICE` (draft) | `xeo:expressesPractice` | `HarnessComponent` | `Practice` | norm | agentic |
| `FANS_OUT_TO` | `xeo:fansOutTo` | `Prompt` | `Term` | observation | visibility |
| `FEEDBACK_ON` | `xeo:feedbackOn` | `Feedback` | `Gap` · `Recommendation` | interpretation | decision |
| `FETCHED` | `xeo:fetched` | `Crawl` | `URL` | observation | core |
| `FIRED_PRACTICE` (draft) | `xeo:firedPractice` | `EnforcementEvent` | `Practice` | episode | agentic |
| `FOR_ARM` (draft) | `xeo:forArm` | `Outcome` | `Arm` | episode | experiments |
| `FRAMEWORK_KIND` | `xeo:frameworkKind` | `Framework` | `skos:Concept` (concept slot) | norm | decision |
| `FROM_DIRECTION` (draft) | `xeo:fromDirection` | `DesignSystem` | `DesignDirection` | entity | design |
| `FULFILS` (draft) | `xeo:fulfils` | `Deliverable` | `WorkItem` | episode | work |
| `GAP_TYPE` | `xeo:gapType` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `GRAIN_TO_DATE` (extension) | `xeo:grainToDate` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `GUARDRAIL_METRIC` (draft) | `xeo:guardrailMetric` | `Experiment` | `Metric` | episode | experiments |
| `HAS_ARM` (draft) | `xeo:hasArm` | `Experiment` | `Arm` | episode | experiments |
| `HAS_CAMPAIGN` | `xeo:hasCampaign` | `Project` | `Campaign` | entity | work |
| `HAS_CANONICAL` | `xeo:hasCanonical` | `URL` | `URL` | observation | core |
| `HAS_COMPONENT` (draft) | `xeo:hasComponent` | `Harness` | `HarnessComponent` | entity | agentic |
| `HAS_CONTROL` | `xeo:hasControl` | `Experiment` | `Term` · `URL` | episode | decision |
| `HAS_CONVERSION_POINT` | `xeo:hasConversionPoint` | `URL` | `ConversionPoint` | observation | core |
| `HAS_CRAWL` | `xeo:hasCrawl` | `Website` | `Crawl` | episode | core |
| `HAS_CREDIT_ANCHOR` | `xeo:hasCreditAnchor` | `AttributionModel` | `CreditAnchor` | norm | attribution |
| `HAS_MODEL_CALL` (draft) | `xeo:hasModelCall` | `AgentTurn` | `ModelCall` | episode | agentic |
| `HAS_OBJECTIVE` | `xeo:hasObjective` | `Campaign` | `Objective` | interpretation | work |
| `HAS_PROJECT` | `xeo:hasProject` | `Website` | `Project` | entity | work |
| `HAS_RESPONSE` | `xeo:hasResponse` | `Prompt` | `LLMResponse` | episode | visibility |
| `HAS_RESULT` | `xeo:hasResult` | `SerpSnapshot` | `URL` | observation | core |
| `HAS_ROLE` | `xeo:hasRole` | `URL` | `skos:Concept` (concept slot) | derivation | decision |
| `HAS_SNAPSHOT` | `xeo:hasSnapshot` | `Term` | `SerpSnapshot` | episode | core |
| `HAS_STAGE` | `xeo:hasStage` | `Framework` | `Stage` | norm | decision |
| `HAS_TARGET` | `xeo:hasTarget` | `Objective` | `MetricTarget` | interpretation | work |
| `HAS_TOOL_CALL` (draft) | `xeo:hasToolCall` | `AgentTurn` | `ToolCall` | episode | agentic |
| `HAS_TOUCHPOINT` | `xeo:hasTouchpoint` | `Journey` | `Touchpoint` | derivation | attribution |
| `HAS_TRIAL` (draft) | `xeo:hasTrial` | `Arm` | `Trial` | episode | experiments |
| `HAS_TURN` (draft) | `xeo:hasTurn` | `AgentSession` | `AgentTurn` | episode | agentic |
| `HAS_WEBSITE` | `xeo:hasWebsite` | `Brand` | `Website` | entity | visibility |
| `HOLDS_CAPABILITY` | `xeo:holdsCapability` | `Organization` | `Capability` | entity | work |
| `IDENTITY_RESOLVES_TO` | `xeo:identityResolvesTo` | `IdentityLink` | `Organization` · `Person` | derivation | attribution |
| `IMPLEMENTED_AS` | `xeo:implementedAs` | `Recommendation` | `Experiment` | episode | decision |
| `IN_BENCHMARK` (draft) | `xeo:inBenchmark` | `BenchmarkTask` | `Benchmark` | entity | experiments |
| `IN_CONTEXT` | `xeo:inContext` | `Experiment` | `Gap` | observation | decision |
| `IN_DESIGN_SYSTEM` (draft) | `xeo:inDesignSystem` | `DesignAsset` · `DesignComponent` · `DesignPattern` · `DesignToken` · `PageTemplate` | `DesignSystem` | entity | design |
| `IN_INTERVENTION` | `xeo:inIntervention` | `Tactic` | `Intervention` | derivation | decision |
| `IN_SCOPE` | `xeo:inScope` | `Project` | `Intervention` · `Tactic` | entity | work |
| `IN_SESSION` (draft) | `xeo:inSession` | `Compaction` · `Delegation` · `EnforcementEvent` · `ModelCall` · `ToolCall` | `AgentSession` | episode | agentic |
| `IN_TOPIC` | `xeo:inTopic` | `Term` | `Topic` | derivation | core |
| `INCLUDES` | `xeo:includes` | `Framework` · `Playbook` | `Diagnostic` · `Practice` · `Tactic` | entity | decision |
| `INPUT_METRIC` | `xeo:inputMetric` | `Metric` | `Metric` | norm | core |
| `ISSUED_FOR` | `xeo:issuedFor` | `Recommendation` | `Campaign` | interpretation | work |
| `JOURNEY_OF` | `xeo:journeyOf` | `Journey` | `Organization` · `Person` | derivation | attribution |
| `LEARNED_FROM` | `xeo:learnedFrom` | `Practice` | `Experiment` · `Outcome` | derivation | decision |
| `LINKS_TO` | `xeo:linksTo` | `URL` | `URL` | observation | core |
| `MAGNITUDE_METRIC` | `xeo:magnitudeMetric` | `Gap` | `Metric` | derivation | decision |
| `MAGNITUDE_UNIT` | `xeo:magnitudeUnit` | `Gap` | `skos:Concept` (concept slot) | derivation | decision |
| `MEASURES` | `xeo:measures` | `Experiment` | `MetricTarget` | episode | work |
| `MEMBER_OF` (draft) | `xeo:memberOf` | `Person` | `Organization` | entity | knowledge |
| `MENTIONS` | `xeo:mentions` | `LLMResponse` | `Brand` | observation | visibility |
| `METRIC_TYPE` | `xeo:metricType` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `NEXT_STAGE` | `xeo:nextStage` | `Stage` | `Stage` | norm | decision |
| `NUMERATOR` | `xeo:numerator` | `Metric` | `Metric` | norm | core |
| `OBJECTIVE_READING` (extension) | `xeo:objectiveReading` | `Objective` | `MetricReading` | derivation | work |
| `ON_DIMENSION` | `xeo:onDimension` | `TacticAssessment` | `skos:Concept` (concept slot) | interpretation | decision |
| `ON_DOMAIN` | `xeo:onDomain` | `URL` | `Domain` | entity | core |
| `ON_ENGINE` | `xeo:onEngine` | open | `Engine` | episode | core |
| `ON_RUNTIME` (draft) | `xeo:onRuntime` | `AgentSession` | `AgentRuntime` | episode | agentic |
| `ON_TASK` (draft) | `xeo:onTask` | `Trial` | `BenchmarkTask` | episode | experiments |
| `ON_TOOL_CALL` (draft) | `xeo:onToolCall` | `EnforcementEvent` | `ToolCall` | episode | agentic |
| `ORGANIZATION_KIND` | `xeo:organizationKind` | `Organization` | `skos:Concept` (concept slot) | entity | core |
| `OWNS` | `xeo:owns` | `Organization` | `Brand` · `Website` | entity | core |
| `PART_OF` | `xeo:partOf` | `URL` | `Website` | entity | core |
| `PRECEDENT_FOR` | `xeo:precedentFor` | `Experiment` | `Experiment` | derivation | analysis |
| `PRIMARY_METRIC` (draft) | `xeo:primaryMetric` | `Experiment` | `Metric` | episode | experiments |
| `PRODUCED_BY_MODEL` | `xeo:producedByModel` | open | `Model` | observation | core |
| `PRODUCED_IN_SESSION` (draft) | `xeo:producedInSession` | `Deliverable` | `AgentSession` | episode | agentic |
| `PRODUCED_OUTCOME` | `xeo:producedOutcome` | `Experiment` | `Outcome` | observation | decision |
| `PROPOSED_IN` (draft) | `xeo:proposedIn` | `DesignConcept` · `DesignDirection` | `Deliverable` | entity | design |
| `RAISED_IN` (draft) | `xeo:raisedIn` | `ActionItem` | `Meeting` · `Summary` · `Transcript` | interpretation | knowledge |
| `RANKS_FOR` | `xeo:ranksFor` | `URL` | `Term` | observation | core |
| `READING_OF` | `xeo:readingOf` | `MetricReading` | `Metric` | observation | core |
| `READS_SLOT` | `xeo:readsSlot` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `REALIZED_AS` (draft) | `xeo:realizedAs` | `DesignElement` | `DesignAsset` · `DesignComponent` · `DesignPattern` · `DesignToken` · `PageTemplate` | entity | design |
| `RECOMMENDS` | `xeo:recommends` | `Recommendation` | `Intervention` · `Tactic` | interpretation | decision |
| `RECORDING_OF` (draft) | `xeo:recordingOf` | `Recording` | `Meeting` | episode | knowledge |
| `REDIRECTS_TO` | `xeo:redirectsTo` | `URL` | `URL` | observation | core |
| `REFERENCE_TARGET` | `xeo:referenceTarget` | `InboundReference` | `Brand` · `Organization` · `URL` · `Website` | observation | core |
| `REFERENCING_URL` | `xeo:referencingUrl` | `InboundReference` | `URL` | observation | core |
| `REFERS_TO` | `xeo:refersTo` | open | `Organization` · `Person` | derivation | core |
| `REFUNDS_ORDER` | `xeo:refundsOrder` | `Chargeback` · `Refund` | `Order` | observation | attribution |
| `RELATED_TERM` | `xeo:relatedTerm` | `SerpSnapshot` | `Term` | observation | core |
| `RELATIVE_TO` | `xeo:relativeTo` | `Gap` | `Brand` · `Domain` · `URL` | interpretation | decision |
| `REPLACES_ELEMENT` (draft) | `xeo:replacesElement` | `DesignConcept` | `DesignElement` | entity | design |
| `REQUIRES_CAPABILITY` | `xeo:requiresCapability` | `Tactic` | `Capability` | entity | decision |
| `RESULT_READING` | `xeo:resultReading` | `Outcome` | `MetricReading` | observation | decision |
| `REVEALED_IN` | `xeo:revealedIn` | `Gap` | `DiagnosticRun` | episode | decision |
| `REVEALS` | `xeo:reveals` | `Diagnostic` | `Gap` | interpretation | decision |
| `REVENUE_SUBJECT` | `xeo:revenueSubject` | `RevenueEvent` · `Subscription` | `Organization` · `Person` | observation | attribution |
| `RUN_OF` | `xeo:runOf` | `DiagnosticRun` | `Diagnostic` | episode | decision |
| `RUNS_ON` (draft) | `xeo:runsOn` | `Harness` | `AgentRuntime` | entity | agentic |
| `SCOPE` | `xeo:scope` | `MetricReading` | `Brand` · `Campaign` · `Prompt` · `Term` · `Topic` · `URL` · `Website` | observation | core |
| `SCOPED_TO` | `xeo:scopedTo` | `Topic` | `Website` | entity | core |
| `SEEN_ON` (draft) | `xeo:seenOn` | `DesignElement` | `URL` | entity | design |
| `SHOWN_ON_SEARCH_ENGINE` | `xeo:shownOnSearchEngine` | `GenerativeOverview` | `SearchEngine` | entity | visibility |
| `SIMILAR_TO` | `xeo:similarTo` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | `Experiment` · `Prompt` · `Term` · `Topic` · `URL` | derivation | analysis |
| `SUGGESTS` | `xeo:suggests` | `Diagnostic` | `Intervention` · `Tactic` | norm | decision |
| `SUMMARIZES` (draft) | `xeo:summarizes` | `Summary` | `Meeting` · `Transcript` | derivation | knowledge |
| `SUPERSEDES` | `xeo:supersedes` | `DiagnosticRun` · `Practice` · `Recommendation` · `Spec` | `DiagnosticRun` · `Practice` · `Recommendation` · `Spec` | norm | decision |
| `SUPPORTED_BY` | `xeo:supportedBy` | `Recommendation` | `Experiment` | interpretation | decision |
| `TARGET_METRIC` | `xeo:targetMetric` | `MetricTarget` | `Metric` | interpretation | work |
| `TARGETS_INTENT` | `xeo:targetsIntent` | open | `SearchIntent` | interpretation | core |
| `TESTS` | `xeo:tests` | `Experiment` | `Intervention` · `Tactic` | episode | decision |
| `TESTS_TACTIC` (draft) | `xeo:testsTactic` | `Arm` | `Tactic` | episode | experiments |
| `TIME_ANCHOR` | `xeo:timeAnchor` | `Metric` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#Property` | norm | core |
| `TOUCH_LANDING_URL` | `xeo:touchLandingUrl` | `Touchpoint` | `URL` | observation | attribution |
| `TRACES_TO` (draft) | `xeo:tracesTo` | `WorkItem` | `Recommendation` · `Spec` | entity | work |
| `TRACKS_PROMPT` | `xeo:tracksPrompt` | `Website` | `Prompt` | entity | visibility |
| `TRANSCRIPT_OF` (draft) | `xeo:transcriptOf` | `Transcript` | `Recording` | episode | knowledge |
| `TREATS` | `xeo:treats` | `Experiment` | `Term` · `URL` | episode | decision |
| `UNDER_DIRECTION` (draft) | `xeo:underDirection` | `DesignConcept` · `DesignDecision` | `DesignDirection` | entity | design |
| `UNDER_HARNESS` (draft) | `xeo:underHarness` | `AgentSession` | `Harness` | episode | agentic |
| `UNIT` | `xeo:unit` | `Metric` | `skos:Concept` (concept slot) | norm | core |
| `UNIT_OF` (draft) | `xeo:unitOf` | `Organization` | `Organization` | entity | knowledge |
| `USED_CONFIG` (draft) | `xeo:usedConfig` | `LLMResponse` · `ModelCall` | `InvocationConfig` | episode | agentic |
| `USES_ASSET` (draft) | `xeo:usesAsset` | `DesignComponent` · `DesignConcept` · `DesignPattern` · `PageTemplate` · `URL` | `DesignAsset` | entity | design |
| `USES_ATTRIBUTION_MODEL` | `xeo:usesAttributionModel` | `AttributedCredit` · `AttributionRollup` | `AttributionModel` | derivation | attribution |
| `USES_DESIGN_SYSTEM` (draft) | `xeo:usesDesignSystem` | `Website` | `DesignSystem` | entity | design |
| `USES_TEMPLATE` (draft) | `xeo:usesTemplate` | `URL` | `PageTemplate` | entity | design |
| `USES_TOKEN` (draft) | `xeo:usesToken` | `DesignComponent` · `DesignConcept` · `DesignPattern` · `PageTemplate` | `DesignToken` | entity | design |
| `VARIANT_OF` (draft) | `xeo:variantOf` | `DesignComponent` | `DesignComponent` | entity | design |
| `VERDICT` | `xeo:verdict` | `Feedback` · `Gap` | `skos:Concept` (concept slot) | interpretation | decision |
| `VIA_TOUCHPOINT` | `xeo:viaTouchpoint` | `ConversionEvent` | `Touchpoint` | derivation | attribution |
| `VISIBILITY_FOR` | `xeo:visibilityFor` | `Prompt` | `Brand` | observation | visibility |
| `WITHIN_PROJECT` (draft) | `xeo:withinProject` | `Spec` | `Project` | entity | work |

### Property keys (290)

| Property key | Datatype | Values from | Layer | Module |
|---|---|---|---|---|
| `additivity` | concept code | `additivity` | norm | core |
| `aggregation` | concept code | `aggregation` | norm | core |
| `aggregationBasis` (extension) | concept code | `aggregationBasis` | observation | core |
| `algorithm` | concept code | `algorithm` | episode | analysis |
| `appliesAtScope` | concept code |  | norm | decision |
| `appliesToConcept` | concept code |  | norm | decision |
| `atPriority` | concept code | `priority` | interpretation | decision |
| `basis` | concept code | `similarityBasis` | derivation | analysis |
| `betterDirection` | concept code | `betterDirection` | norm | core |
| `dataState` (extension) | concept code | `dataState` | observation | core |
| `effortEstimate` | concept code | `effort` | interpretation | work |
| `execution` | concept code | `execution` | interpretation | work |
| `frameworkKind` | concept code | `frameworkKind` | norm | decision |
| `gapType` | concept code | `gapType` | derivation | decision |
| `grainToDate` (extension) | concept code | `timeGrain` | norm | core |
| `hasRole` | concept code |  | derivation | decision |
| `magnitudeUnit` | concept code | `magnitudeUnit` | derivation | decision |
| `metricType` | concept code | `metricType` | norm | core |
| `onDimension` | concept code |  | interpretation | decision |
| `organizationKind` | concept code | `organizationKind` | entity | core |
| `unit` | concept code | `metricUnit` | norm | core |
| `verdict` | concept code | `feedbackVerdict` · `gapVerdict` | interpretation | decision |
| `absoluteChange` | `xsd:decimal` |  | derivation | decision |
| `adCampaignRef` | `xsd:string` |  | entity | attribution |
| `adRef` | `xsd:string` |  | entity | attribution |
| `adSetRef` | `xsd:string` |  | entity | attribution |
| `address` | `xsd:string` |  | entity | core |
| `agentContext` (extension) | `xsd:string` |  | norm | core |
| `amountAtTransition` | `xsd:decimal` |  | episode | sales |
| `amountInReportingCurrency` (extension) | `xsd:decimal` |  | derivation | core |
| `anchorPosition` | `xsd:string` | `anchorPosition` | norm | attribution |
| `anchorStageRef` | `xsd:string` |  | norm | attribution-sales |
| `anchorText` | `xsd:string` |  | observation | core |
| `anchorWeight` | `xsd:decimal` |  | norm | attribution |
| `approved` | `xsd:boolean` |  | interpretation | decision |
| `armMean` (draft) | `xsd:decimal` |  | derivation | experiments |
| `armSampleSize` (draft) | `xsd:integer` |  | derivation | experiments |
| `armStandardDeviation` (draft) | `xsd:decimal` |  | derivation | experiments |
| `artifactUri` (draft) | `xsd:string` |  | entity | core |
| `assetKind` (draft) | `xsd:string` | `assetKind` | entity | design |
| `assignedAt` | `xsd:dateTime` |  | derivation | core |
| `attemptCount` (draft) | `xsd:integer` |  | observation | agentic |
| `attributedConversions` | `xsd:decimal` |  | derivation | attribution |
| `attributedRevenue` | `xsd:decimal` |  | derivation | attribution |
| `avgPosition` | `xsd:decimal` |  | observation | core |
| `baseline` | `xsd:decimal` |  | observation | work |
| `baselineCapturedAt` | `xsd:dateTime` |  | observation | work |
| `benchmarkVersion` (draft) | `xsd:string` |  | entity | experiments |
| `betweenness` | `xsd:decimal` |  | derivation | analysis |
| `billingInterval` | `xsd:string` | `billingInterval` | observation | core |
| `billingIntervalCount` | `xsd:positiveInteger` |  | observation | core |
| `cacheReadTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `cacheWriteDefaultLifetimeTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `cacheWriteExtendedLifetimeTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `cacheWriteTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `cadence` | `xsd:string` | `cadence` | entity | work |
| `callOutcome` | `xsd:string` | `callOutcome` | interpretation | attribution |
| `capturedAt` | `xsd:dateTime` |  | episode | core |
| `childAgentId` (draft) | `xsd:string` |  | episode | agentic |
| `ciLower` (draft) | `xsd:decimal` |  | derivation | experiments |
| `ciMethod` (draft) | `xsd:string` |  | derivation | experiments |
| `ciUpper` (draft) | `xsd:decimal` |  | derivation | experiments |
| `citationRank` | `xsd:integer` |  | observation | visibility |
| `citationRate` | `xsd:decimal` |  | derivation | visibility |
| `claimSourceUri` (draft) | `xsd:string` |  | entity | experiments |
| `claimVerdict` (draft) | `xsd:string` | `claimVerdict` | interpretation | experiments |
| `claimedAt` (draft) | `xsd:date` |  | episode | experiments |
| `claimedValue` (draft) | `xsd:decimal` |  | interpretation | experiments |
| `clickIdentifier` | `xsd:string` |  | observation | attribution |
| `clicks` | `xsd:integer` |  | observation | core |
| `communityId` | `xsd:integer` |  | derivation | analysis |
| `compactionTrigger` (draft) | `xsd:string` | `compactionTrigger` | episode | agentic |
| `componentDigest` (draft) | `xsd:string` |  | entity | agentic |
| `componentKind` (draft) | `xsd:string` | `harnessComponentKind` | entity | agentic |
| `concludedAt` | `xsd:dateTime` |  | episode | decision |
| `confidence` | `xsd:decimal` |  | derivation | core |
| `consentCapturedBy` | `xsd:string` |  | observation | core |
| `consentPurpose` | `xsd:string` | `consentPurpose` | observation | core |
| `consentRecordedAt` | `xsd:dateTime` |  | observation | core |
| `consentSource` | `xsd:string` | `consentSource` | observation | core |
| `consentStatus` | `xsd:string` | `consentStatus` | observation | core |
| `contentHash` | `xsd:string` |  | derivation | core |
| `contentType` | `xsd:string` |  | observation | core |
| `conversionPointType` | `xsd:string` | `conversionPointType` | entity | core |
| `conversionRole` | `xsd:string` | `conversionRole` | interpretation | attribution |
| `conversionWindow` (extension) | `xsd:duration` |  | norm | core |
| `convertedAt` (extension) | `xsd:dateTime` |  | episode | sales |
| `convertedTo` (extension) | `xsd:string` |  | episode | sales |
| `costAmount` (draft) | `xsd:decimal` |  | derivation | agentic |
| `costBasis` (draft) | `xsd:string` | `costBasis` | derivation | agentic |
| `counterfactual` (draft) | `xsd:string` |  | interpretation | experiments |
| `crawlDepth` | `xsd:integer` |  | derivation | core |
| `crawler` | `xsd:string` |  | episode | core |
| `creditForDeal` | `xsd:string` |  | derivation | attribution-sales |
| `creditRule` | `xsd:string` | `creditRule` | norm | attribution |
| `creditShare` | `xsd:decimal` |  | derivation | attribution |
| `crmObjectType` | `xsd:string` | `crmObjectType` | entity | sales |
| `crmRecordRef` | `xsd:string` |  | entity | sales |
| `crmSystem` | `xsd:string` | `crmSystem` | entity | sales |
| `ctr` | `xsd:decimal` |  | observation | core |
| `cumulativeWindow` (extension) | `xsd:duration` |  | norm | core |
| `currencyCode` | `xsd:string` |  | observation | core |
| `customerStatus` | `xsd:string` | `customerStatus` | derivation | attribution |
| `datasetUri` | `xsd:string` |  | derivation | core |
| `dateBasis` | `xsd:string` | `dateBasis` | norm | attribution |
| `dealAmount` | `xsd:decimal` |  | observation | sales |
| `dealClosedAt` | `xsd:dateTime` |  | observation | sales |
| `dealOutcome` | `xsd:string` | `dealOutcome` | observation | sales |
| `dealProbability` (extension) | `xsd:decimal` |  | interpretation | sales |
| `decisionSource` (draft) | `xsd:string` | `decisionSource` | episode | agentic |
| `deduplicationRule` | `xsd:string` |  | norm | attribution |
| `degree` | `xsd:integer` |  | derivation | analysis |
| `deletedAt` | `xsd:dateTime` |  | entity | work |
| `denominatorValue` | `xsd:decimal` |  | observation | core |
| `designSystemVersion` (draft) | `xsd:string` |  | entity | design |
| `designVerdict` (draft) | `xsd:string` | `designVerdict` | interpretation | design |
| `device` | `xsd:string` | `device` | episode | core |
| `discountAmount` | `xsd:decimal` |  | observation | attribution |
| `durationDays` | `xsd:integer` |  | entity | work |
| `effectiveN` (draft) | `xsd:decimal` |  | derivation | experiments |
| `elementKind` (draft) | `xsd:string` | `elementKind` | entity | design |
| `eligibleTouchType` | `xsd:string` |  | norm | attribution |
| `embeddedAt` | `xsd:dateTime` |  | derivation | core |
| `embeddingDim` | `xsd:integer` |  | derivation | core |
| `embeddingModel` | `xsd:string` |  | derivation | core |
| `embeddingRef` | `xsd:string` |  | derivation | core |
| `endedAt` | `xsd:dateTime` |  | episode | core |
| `enforcementDecision` (draft) | `xsd:string` | `hookDecision` | episode | agentic |
| `enforcementPoint` (draft) | `xsd:string` | `enforcementPoint` | norm | agentic |
| `engagementType` | `xsd:string` | `engagementType` | entity | work |
| `enteredAt` | `xsd:dateTime` |  | episode | sales |
| `entityRef` | `xsd:string` |  | entity | core |
| `errorClass` (draft) | `xsd:string` |  | observation | agentic |
| `exitedAt` | `xsd:dateTime` |  | episode | sales |
| `expectedCloseDate` | `xsd:date` |  | interpretation | sales |
| `expression` | `xsd:string` |  | norm | core |
| `failureClass` (draft) | `xsd:string` | `failureClass` | episode | experiments |
| `failureMode` (draft) | `xsd:string` | `failureMode` | norm | agentic |
| `failureSignature` (draft) | `xsd:string` |  | derivation | agentic |
| `fetchedAt` | `xsd:dateTime` |  | observation | core |
| `fired` | `xsd:boolean` |  | derivation | decision |
| `firstSeenAt` | `xsd:dateTime` |  | observation | core |
| `firstTouchChannel` | `xsd:string` | `acquisitionChannel` | derivation | attribution |
| `forecastCategory` (extension) | `xsd:string` | `forecastCategory` | interpretation | sales |
| `fromStageRef` | `xsd:string` |  | episode | sales |
| `graderKind` (draft) | `xsd:string` | `graderKind` | entity | experiments |
| `grossAmount` | `xsd:decimal` |  | observation | attribution |
| `h1` | `xsd:string` |  | observation | core |
| `halfLife` | `xsd:duration` |  | norm | decision |
| `harnessDigest` (draft) | `xsd:string` |  | entity | agentic |
| `harnessVersion` (draft) | `xsd:string` |  | entity | agentic |
| `identityMethod` | `xsd:string` | `identityMethod` | derivation | attribution |
| `impressions` | `xsd:integer` |  | observation | core |
| `indexable` | `xsd:boolean` |  | derivation | core |
| `interventionQuota` | `xsd:integer` |  | entity | work |
| `isBaseline` (draft) | `xsd:boolean` |  | entity | experiments |
| `isPrimary` | `xsd:boolean` |  | interpretation | work |
| `lastSeenAt` | `xsd:dateTime` |  | observation | core |
| `lastSeenCrawlId` | `xsd:string` |  | episode | core |
| `latencyMs` (draft) | `xsd:decimal` |  | observation | agentic |
| `latestTouchChannel` (extension) | `xsd:string` |  | derivation | attribution |
| `leadStatus` (extension) | `xsd:string` |  | interpretation | sales |
| `lifecycleStage` (extension) | `xsd:string` | `lifecycleStageClass` | interpretation | sales |
| `linkPosition` | `xsd:string` | `linkPosition` | derivation | core |
| `linkedIdentifier` | `xsd:string` |  | observation | attribution |
| `loadMode` (draft) | `xsd:string` | `loadMode` | entity | agentic |
| `locale` | `xsd:string` |  | episode | core |
| `lookbackWindow` | `xsd:duration` |  | norm | attribution |
| `lostReason` (extension) | `xsd:string` |  | interpretation | sales |
| `magnitude` | `xsd:decimal` |  | derivation | decision |
| `marketingCampaignRef` (extension) | `xsd:string` |  | entity | sales |
| `maxOutputTokens` (draft) | `xsd:integer` |  | entity | agentic |
| `mentionRank` | `xsd:integer` |  | observation | visibility |
| `mentionRate` | `xsd:decimal` |  | derivation | visibility |
| `metaDescription` | `xsd:string` |  | observation | core |
| `method` | `xsd:string` |  | interpretation | decision |
| `metricFilter` | `xsd:string` |  | norm | core |
| `minDenominator` | `xsd:integer` |  | norm | core |
| `model` | `xsd:string` |  | episode | core |
| `modelCallRef` (draft) | `xsd:string` |  | episode | agentic |
| `modelFamily` | `xsd:string` |  | entity | core |
| `modelKind` | `xsd:string` | `modelKind` | entity | core |
| `modelProvider` (draft) | `xsd:string` |  | entity | agentic |
| `modelVersion` | `xsd:string` |  | entity | core |
| `name` | `xsd:string` |  | entity | core |
| `numeratorValue` | `xsd:decimal` |  | observation | core |
| `occurredAt` | `xsd:dateTime` |  | episode | core |
| `offsetWindow` (extension) | `xsd:duration` |  | norm | core |
| `origin` | `xsd:string` |  | entity | core |
| `outcomeJudgedBy` | `xsd:string` | `outcomeJudgedBy` | interpretation | attribution |
| `outputTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `ownerRef` | `xsd:string` |  | entity | sales |
| `pageRank` | `xsd:decimal` |  | derivation | analysis |
| `paidAmount` | `xsd:decimal` |  | observation | attribution |
| `parameters` | `xsd:string` |  | episode | analysis |
| `parentAgentId` (draft) | `xsd:string` |  | episode | agentic |
| `percentileValue` (extension) | `xsd:decimal` |  | norm | core |
| `periodEnd` | `xsd:date` |  | derivation | core |
| `periodStart` | `xsd:date` |  | derivation | core |
| `pipelineRef` | `xsd:string` |  | entity | sales |
| `position` | `xsd:integer` |  | observation | core |
| `practiceKind` | `xsd:string` | `practiceKind` | norm | decision |
| `practiceOutcome` | `xsd:string` | `practiceOutcome` | derivation | decision |
| `preRegistrationRef` (draft) | `xsd:string` |  | episode | experiments |
| `projection` | `xsd:string` |  | episode | analysis |
| `quoteValue` | `xsd:decimal` |  | interpretation | attribution |
| `ranAt` | `xsd:dateTime` |  | episode | analysis |
| `rationale` | `xsd:string` |  | norm | decision |
| `reasonText` (draft) | `xsd:string` |  | episode | agentic |
| `reasoningLevel` (draft) | `xsd:string` |  | entity | agentic |
| `reasoningTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `recordCreatedAt` | `xsd:dateTime` |  | observation | sales |
| `recordOrigin` (extension) | `xsd:string` | `recordOrigin` | observation | sales |
| `recurringValue` (extension) | `xsd:decimal` |  | observation | core |
| `referenceKind` | `xsd:string` | `referenceKind` | observation | core |
| `referringPlatform` | `xsd:string` |  | derivation | attribution |
| `refundedAmount` | `xsd:decimal` |  | observation | attribution |
| `rel` | `xsd:string` |  | observation | core |
| `relativeChange` | `xsd:decimal` |  | derivation | decision |
| `requestedModel` (draft) | `xsd:string` |  | entity | agentic |
| `responses` | `xsd:integer` |  | observation | visibility |
| `result` | `xsd:string` | `outcomeResult` | observation | decision |
| `resultReason` | `xsd:string` | `outcomeResultReason` | observation | decision |
| `resultType` | `xsd:string` | `serpResultType` | observation | core |
| `resultsWindowDays` | `xsd:integer` |  | interpretation | work |
| `resultsWindowStart` | `xsd:date` |  | interpretation | work |
| `returnsControl` (draft) | `xsd:boolean` |  | episode | agentic |
| `revenueBasis` | `xsd:string` | `revenueBasis` | norm | attribution |
| `robotsMeta` | `xsd:string` |  | observation | core |
| `runtimeVersion` (draft) | `xsd:string` |  | entity | agentic |
| `score` | `xsd:decimal` |  | interpretation | decision |
| `sentiment` | `xsd:string` | `sentiment` | derivation | visibility |
| `sessionRef` (draft) | `xsd:string` |  | episode | agentic |
| `shippingAmount` | `xsd:decimal` |  | observation | attribution |
| `similarity` | `xsd:decimal` |  | derivation | analysis |
| `source` | `xsd:string` | `practiceSource` | norm | decision |
| `specKind` (draft) | `xsd:string` | `specKind` | entity | work |
| `spendAmount` | `xsd:decimal` |  | observation | attribution |
| `spendLevel` | `xsd:string` | `spendLevel` | observation | attribution |
| `stageClass` | `xsd:string` | `dealStageClass` | norm | sales |
| `stageDefaultProbability` (extension) | `xsd:decimal` |  | norm | sales |
| `stageOrder` | `xsd:integer` |  | norm | decision |
| `stageRef` | `xsd:string` |  | entity | sales |
| `stageSlot` | `xsd:string` | `stageSlot` | episode | sales |
| `startType` (draft) | `xsd:string` | `startType` | episode | agentic |
| `startedAt` | `xsd:dateTime` |  | episode | core |
| `statement` | `xsd:string` |  | norm | decision |
| `status` | `xsd:string` | `experimentStatus` · `practiceStatus` · `recommendationStatus` | norm | decision |
| `statusCode` | `xsd:integer` |  | observation | core |
| `stopReason` (draft) | `xsd:string` |  | observation | agentic |
| `succeeded` (draft) | `xsd:boolean` |  | observation | agentic |
| `syncedAt` | `xsd:dateTime` |  | derivation | core |
| `targetCurrency` | `xsd:string` |  | interpretation | work |
| `targetKind` | `xsd:string` | `targetKind` | interpretation | work |
| `targetValue` | `xsd:decimal` |  | interpretation | work |
| `taskRef` (draft) | `xsd:string` |  | entity | experiments |
| `taxAmount` | `xsd:decimal` |  | observation | attribution |
| `temperature` (draft) | `xsd:decimal` |  | entity | agentic |
| `test` | `xsd:string` |  | norm | decision |
| `text` | `xsd:string` |  | entity | visibility |
| `timeToFirstTokenMs` (draft) | `xsd:decimal` |  | observation | agentic |
| `title` | `xsd:string` |  | observation | core |
| `toStageRef` | `xsd:string` |  | episode | sales |
| `tokenMode` (draft) | `xsd:string` |  | entity | design |
| `tokenTier` (draft) | `xsd:string` | `tokenTier` | entity | design |
| `tokenType` (draft) | `xsd:string` | `tokenType` | entity | design |
| `tokenValue` (draft) | `xsd:string` |  | entity | design |
| `tokensAfter` (draft) | `xsd:integer` |  | observation | agentic |
| `tokensBefore` (draft) | `xsd:integer` |  | observation | agentic |
| `toolCallRef` (draft) | `xsd:string` |  | episode | agentic |
| `toolName` (draft) | `xsd:string` |  | episode | agentic |
| `toolSetDigest` (draft) | `xsd:string` |  | entity | agentic |
| `toolSource` (draft) | `xsd:string` | `toolSource` | episode | agentic |
| `touchChannel` | `xsd:string` |  | derivation | attribution |
| `touchType` | `xsd:string` | `touchType` | observation | attribution |
| `trialBlock` (draft) | `xsd:string` |  | episode | experiments |
| `trialReplicate` (draft) | `xsd:integer` |  | episode | experiments |
| `trialScore` (draft) | `xsd:decimal` |  | observation | experiments |
| `turnRef` (draft) | `xsd:string` |  | episode | agentic |
| `uncachedInputTokens` (draft) | `xsd:integer` |  | observation | agentic |
| `utmCampaign` | `xsd:string` |  | observation | attribution |
| `utmContent` | `xsd:string` |  | observation | attribution |
| `utmMedium` | `xsd:string` |  | observation | attribution |
| `utmSource` | `xsd:string` |  | observation | attribution |
| `utmTerm` | `xsd:string` |  | observation | attribution |
| `value` | `xsd:decimal` |  | observation | core |
| `webSearchEnabled` | `xsd:boolean` |  | episode | visibility |
| `websiteId` | `xsd:string` |  | entity | core |
| `weightedAmount` (extension) | `xsd:decimal` |  | derivation | sales |
| `wordCount` | `xsd:integer` |  | derivation | core |

### Reference schemes (85)

| Scheme | Codes |
|---|---|
| `acquisitionChannel` | `affiliate` · `ai_assistant` · `ai_overview` · `direct` · `display` · `email` · `offline` · `organic_search` · `organic_social` · `other` · `paid_search` · `paid_social` · `programmatic` · `referral` |
| `additivity` | `additive` · `non_additive` · `semi_additive` |
| `aggregation` | `count` · `count_distinct` · `last` · `max` · `mean` · `median` · `min` · `percentile` · `sum` · `weighted_mean` |
| `aggregationBasis` | `auto` · `by_page` · `by_property` |
| `algorithm` | `betweenness` · `cosine` · `degree` · `fastrp` · `knn` · `label_propagation` · `leiden` · `louvain` · `node_similarity` · `pagerank` · `shortest_path` |
| `anchorPosition` | `customer_close` · `first_touch` · `last_touch` · `lead_created` · `opportunity_created` · `qualified` |
| `assetKind` | `animation` · `font` · `graphic` · `icon` · `illustration` · `logo` · `photograph` · `video` |
| `betterDirection` | `down` · `none` · `up` |
| `billingInterval` | `day` · `month` · `week` · `year` |
| `cadence` | `monthly` · `quarterly` |
| `callOutcome` | `cancelled` · `good_lead` · `no_show` · `not_a_lead` · `previously_marked_good_lead` · `qualified` · `unqualified` |
| `claimVerdict` | `confirmed` · `debunked` · `real_but_small` · `real_with_conditions` · `unsubstantiated` · `unverified` |
| `compactionTrigger` | `auto` · `manual` |
| `consentPurpose` | `ad_personalization` · `ad_storage` · `ad_user_data` · `ai_data_use` · `analytics_cookies` · `email_marketing` · `model_training` · `other` |
| `consentSource` | `api` · `banner` · `contract` · `form` · `inferred_default` |
| `consentStatus` | `denied` · `granted` · `unspecified` |
| `conversionPointType` | `chat` · `cta` · `gated_asset` · `lead_form` · `meeting_booker` |
| `conversionRole` | `lead` · `opportunity` · `other` · `qualified_lead` · `sale` |
| `costBasis` | `configured_rate` · `estimated_list_price` · `invoice` |
| `creditRule` | `algorithmic` · `custom` · `first_touch` · `full_credit_each` · `last_touch` · `linear` · `position_based` · `time_decay` |
| `crmObjectType` | `deal` · `lead` · `organization` · `person` |
| `crmSystem` | `attio` · `close` · `dynamics365` · `hubspot` · `pipedrive` · `salesforce` · `zoho` |
| `customerStatus` | `new` · `repeat` |
| `dataState` | `final` · `partial` |
| `dateBasis` | `conversion_date` · `touch_date` |
| `dealOutcome` | `lost` · `open` · `won` |
| `dealStageClass` | `lost` · `open` · `won` |
| `decisionSource` | `classifier` · `config` · `hook` · `user` |
| `designVerdict` | `approve` · `defer` · `keep` · `reject` · `remove` · `replace` · `shortlist` |
| `device` | `desktop` · `mobile` · `tablet` |
| `effort` | `hours` · `days` · `weeks` · `quarter` |
| `elementKind` | `color` · `component` · `iconography` · `illustration` · `imagery` · `layout` · `logo` · `motion` · `navigation` · `pattern` · `typography` |
| `enforcementPoint` | `config` · `hook` · `permission_rule` · `prompt` · `proxy` · `tool` |
| `engagementType` | `oneoff` · `retainer` |
| `execution` | `advised` · `ours` |
| `experimentStatus` | `measuring` · `concluded` · `cancelled` · `unmeasurable` |
| `failureClass` | `agent` · `excluded` · `infrastructure` |
| `failureMode` | `fail_closed` · `fail_open` |
| `feedbackVerdict` | `accepted` · `needs_work` · `rejected` |
| `forecastCategory` | `best_case` · `closed` · `commit` · `omitted` · `pipeline` |
| `frameworkKind` | `checklist` · `diagnostic` · `playbook` · `tactic_matrix` |
| `gapType` | `missing_page` · `orphaned` · `buried` · `thin_content` · `split` · `content_subtopic` · `content_format_asset` · `content_proof` · `content_intent_fit` · `visibility_deficit` · `position_climb` · `zero_click` · `project_footprint` · `domain_authority_deficit` |
| `gapVerdict` | `attack` · `defend` · `fix_first` · `hold` · `ignore` |
| `graderKind` | `human` · `llm_judge` · `none` · `verifier` |
| `harnessComponentKind` | `hook` · `instruction_file` · `mcp_server` · `memory` · `middleware` · `permission_rule` · `plugin` · `script` · `settings` · `skill` · `subagent_definition` · `tool_guidance` |
| `hookDecision` | `allow` · `ask` · `block_after` · `defer` · `deny` · `override` · `rewrite_input` · `rewrite_output` · `trim` |
| `identityMethod` | `click_id` · `email_match` · `fingerprint` · `form_fill` · `ip_to_company` · `login` · `vendor_graph` |
| `intervention` | `brand-entity-ops` · `community-mobilization` · `content-optimization` · `editorial-placement` · `local-placement` · `onsite-content-advisory` · `owned-content-creation` · `technical-onsite` |
| `lifecycleStageClass` | `customer` · `evangelist` · `lead` · `mql` · `opportunity` · `other` · `sql` · `subscriber` |
| `linkPosition` | `content` · `footer` · `header` · `navigation` · `other` · `sidebar` |
| `loadMode` | `always_loaded` · `event_triggered` · `on_demand` |
| `magnitudeUnit` | `clicks` · `impressions` · `inlinks` · `keywords` · `positions` · `referring_domains` · `sessions_estimated` · `words` |
| `metric` | `ad_spend` · `ai_answers_citing_owned` · `ai_answers_mentioning` · `ai_answers_sampled` · `ai_assistant_sessions` · `ai_average_position` · `ai_brand_mentions` · `ai_citation_rate` · `ai_citation_share` · `ai_citations` · `ai_mention_rate` · `ai_owned_citations` · `ai_referred_leads` · `ai_sentiment` · `ai_share_of_voice` · `ai_tracked_brand_mentions` · `attributed_revenue` · `blended_roas` · `clicks` · `converting_sessions` · `cost_per_acquisition` · `cost_per_lead` · `ctr` · `deals_closed` · `deals_created` · `deals_won` · `engaged_sessions` · `engagement_rate` · `etv` · `impressions` · `key_events` · `leads_created` · `lifetime_value` · `payback_period` · `pipeline_created` · `position` · `rank_absolute` · `revenue_won` · `roas` · `sales_cycle_days` · `session_conversion_rate` · `sessions` · `win_rate` |
| `metricType` | `conversion` · `cumulative` · `derived` · `ratio` · `simple` |
| `metricUnit` | `count` · `currency` · `days` · `rank` · `ratio` · `score_0_100` · `seconds` |
| `modelKind` | `classifier` · `decision` · `embedding` · `image` · `language` · `reranker` |
| `objectiveMetric` | `ai_citation_rate` · `ai_mention_rate` · `clicks` · `ctr` · `etv` · `impressions` · `position` · `rank_absolute` |
| `organizationKind` | `agency` · `brand` · `in_house` |
| `outcomeJudgedBy` | `ai` · `person` · `rule` |
| `outcomeResult` | `inconclusive` · `no_change` · `significant` |
| `outcomeResultReason` | `baseline_unavailable` · `below_volume_floor` · `co_intervention` · `confounded_external` · `no_page_data` · `no_qualifying_snapshot` · `window_incomplete` |
| `practiceKind` | `guardrail` · `guidance` · `preference` |
| `practiceOutcome` | `caveated` · `reranked` · `vetoed` |
| `practiceSource` | `authored` · `claimed` · `learned` |
| `practiceStatus` | `proposed` · `active` · `deprecated` |
| `priority` | `P0` · `P1` · `P2` |
| `recommendationStatus` | `pending` · `in_progress` · `blocked` · `cancelled` · `completed` |
| `recordOrigin` | `api` · `form` · `import` · `integration` · `manual` |
| `referenceKind` | `link` · `mention` |
| `revenueBasis` | `gross` · `net_of_refunds` · `paid` |
| `searchIntent` | `commercial_investigation` · `informational` · `navigational` · `transactional` |
| `sentiment` | `mixed` · `negative` · `neutral` · `positive` |
| `serpResultType` | `ai_overview` · `featured_snippet` · `image` · `knowledge_panel` · `local_pack` · `organic` · `paid` · `people_also_ask` · `related_search` · `shopping` · `top_stories` · `video` |
| `similarityBasis` | `lexical` · `links` · `shared_terms` · `structural_embedding` · `text_embedding` |
| `specKind` | `design` · `functional_requirements` · `plan` · `prd` |
| `spendLevel` | `ad` · `ad_set` · `campaign` |
| `stageSlot` | `deal_stage` · `lead_status` · `lifecycle` |
| `startType` | `continue` · `fresh` · `resume` |
| `targetKind` | `absolute` · `absolute_change` · `percent` · `relative` |
| `timeGrain` | `day` · `month` · `quarter` · `week` · `year` |
| `tokenTier` | `component` · `primitive` · `semantic` |
| `tokenType` | `boolean` · `border` · `color` · `cubicBezier` · `dimension` · `duration` · `fontFamily` · `fontWeight` · `gradient` · `number` · `shadow` · `string` · `strokeStyle` · `transition` · `typography` |
| `toolSource` | `builtin` · `mcp` · `plugin` |
| `touchType` | `ad_click` · `ad_view` · `call` · `chat` · `email` · `email_open` · `form` · `meeting` · `offline` · `other` · `text_message` · `visit` |
| `xeoLayer` | `entity` · `episode` · `observation` · `derivation` · `interpretation` · `norm` |

<!-- END GENERATED -->
