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

Before release, the same version took in two research reports (2026-11-10): what a metric is,
and the CRM pipeline. They are the **Metrics** and **CRM pipeline** sections below. Both were
landed without a breaking change: where a report asked for an existing term to be renamed,
retyped or removed, the new form was added beside it and the old one deprecated as advice.

Counts: 36 → 50 classes, 61 → 113 object properties, 65 → 147 datatype properties,
20 → 50 reference schemes, 93 → 281 concepts; 5 vendor schemes mapping 57 fields.
(After the kit sync alone: 45, 91, 95, 29, 146.)

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
  `docs/neo4j-profile.md`. The profile's convention for the instance-level layer stamp is the
  property key `xeoLayer` (`conventions.layerKey`). Drafts of this branch called it `layer`; it
  was renamed before release so the key cannot be read as a layer of anything else.
- `shapes/xeo-shapes.ttl`: fifteen SHACL shapes for rules that were prose only.
- `examples/`: a worked instance graph, a Neo4j-form sample, and one failing case per shape.
- `tools/validate.py` and `.github/workflows/validate.yml`.
- Labels, descriptions and layers for every existing class and property that lacked one
  (126 labels, 23 descriptions, 9 layers), appended as extra triples.

### Metrics

From the metrics and KPIs research report. Until now a target named its metric with a string
whose meaning lived in one scheme's notes, and an Outcome recorded a bare "lift". A target
could be set on search clicks and on nothing else XEO measures.

**A new module, `xeo-metrics.ttl`.**

- `Metric`: a named rule, not a number. `metricType`, `unit`, `betterDirection`, `additivity`
  (exactly one each); `aggregation` and `readsSlot` for a simple metric; `numerator` and
  `denominator` for a ratio; `inputMetric` and `expression` for a derived one; `metricFilter`,
  `timeAnchor`, `minDenominator`. *Why:* every semantic layer surveyed (dbt MetricFlow, Cube,
  LookML, Malloy, OSI) defines a metric this way, and without it two reports on one experiment
  could disagree and both be right.
- `MetricReading`: the value a Metric took over one window, for one scope, from one source.
  `readingOf`, `scope`, `value`, `numeratorValue`, `denominatorValue`. *Why:* a bare decimal
  cannot be recomputed or rolled up. A ratio is rolled up from its parts, never averaged.
- No KPI class. *Why:* no system surveyed models one as a type. The role is `isPrimary`, which
  gained the alt label "KPI".
- Extension set (marked `xeo:termStatus "extension"`): `offsetWindow`, `cumulativeWindow`,
  `grainToDate`, `conversionEntity`, `conversionWindow`, `baseMetric`, `conversionMetric`,
  `percentileValue`, `agentContext`, `aggregationBasis`, `dataState`.

**Decision.** `resultReading`, `absoluteChange`, `relativeChange` on an Outcome, and
`magnitudeMetric` on a Gap. *Why:* "lift" could be points or a percentage; both changes are now
stated, signed and raw, and read through the Metric's better direction.

**Delivery.** `baselineReading` (the reading behind the cached `baseline`),
`resultsWindowStart` (*why:* a window length with no start cannot be computed),
`targetCurrency`, and `objectiveReading` (extension): an Objective is judged on one reading
over its deduplicated scope, never on the sum of its Outcomes.

**`metric` stays a string.** Its code is now defined as the `skos:notation` of a Metric in
`xeos:metric`. Nothing a consumer stores changes.

**Reference schemes.** `metric` (35 Metrics across search, AI visibility, website analytics and
CRM pipeline, each with its type, unit, direction and additivity), `metricType`, `aggregation`,
`metricUnit`, `betterDirection`, `additivity`; `relative` and `absolute_change` in `targetKind`;
and, as extensions, `timeGrain`, `aggregationBasis`, `dataState`. `objectiveMetric` is kept as
the compatibility list: each of its eight concepts is an `exactMatch` of its Metric under the
same code. Every `minDenominator` is an inferred default, and says so.

**`ctr` unit, flagged and not changed.** The published `objectiveMetric` concept notes its unit
as percent. Search Console returns a 0 to 1 quotient. The Metric `ctr` states ratio; the old
note is left as published, with an editorial note, until stored values are checked.

### CRM pipeline

From the CRM pipeline research report. The graph still never mirrors the CRM, and
`crmRecordRef` is still the join. These are the few neutral slots without which "pipeline
created" and "revenue won" cannot be computed.

**Engagement** (appended to `xeo-engagement.ttl`).

- `crmRecordRef` tightened: the value is written `crmSystem:crmTenantId:crmObjectType:recordId`
  and never holds a form id. `crmSystem` and `crmObjectType` state two of its parts on their
  own. *Why:* bare ids collide across accounts, and a form is an on-page mechanism, not a CRM
  record. Still an `xsd:string`; an id stored earlier is still valid.
- `dealAmount` with `currencyCode`; `dealOutcome` (open, won, lost); `ownerRef`; `pipelineRef`
  and `stageRef` (the tenant's own ids) with a neutral `stageClass`; `recordCreatedAt`;
  `dealClosedAt`, kept apart from `expectedCloseDate`. *Why:* all seven CRMs read expose them,
  and several keep the forecast and the actual close date in one field.
- `StageTransition` with `stageSlot`, `fromStageRef`, `toStageRef`, `enteredAt`, `exitedAt`,
  `amountAtTransition`.
- `firstTouchChannel` and `referringPlatform`, both derivations. *Why:* "original source" is a
  classifier's output or a salesperson's picklist, not a measurement. The `acquisitionChannel`
  scheme includes `ai_assistant`.
- `PipelineRollup`, a `MetricReading` of a pipeline Metric.
- `conversionPointType`.
- Extension set: `latestTouchChannel`, `lifecycleStage`, `leadStatus`,
  `stageDefaultProbability`, `dealProbability`, `weightedAmount`, `amountInReportingCurrency`,
  `forecastCategory`, `recurringValue`, `valuePeriod`, `lostReason`, `recordOrigin`,
  `convertedTo`, `convertedAt`, `marketingCampaignRef`, `campaignInfluenceShare`,
  `OwnerChange`. Lifecycle stage is here and not in the core because one CRM of the seven read
  carries it natively.
- A CRM marketing campaign is never an `xeo:Campaign`. It is reached by `marketingCampaignRef`.

**Reference schemes.** `crmSystem`, `crmObjectType`, `dealOutcome`, `dealStageClass`,
`stageSlot`, `acquisitionChannel`, `conversionPointType`, `searchIntent`; and, as extensions,
`lifecycleStageClass`, `forecastCategory`, `recordOrigin`, `valuePeriod`.

**A new folder, `mappings/`, one file per tool.** It is not part of the ontology: a mapping
declares no XEO term, no module points at one, and the validator checks both. (Before release
these were one module, `xeo-vendor-schemes.ttl`; the split changed no triple in any scheme.
`xeo:mappingConfidence` is now declared in core.) Vendor field names never become XEO terms. Each is a
concept in its vendor's scheme, with the exact field name, the slot it fills, a SKOS match, a
scope note, a dated source and `xeo:mappingConfidence`. Transcribed: HubSpot CRM, Google Search
Console, GA4, Peec and Profound (57 fields; 53 documented, 4 inferred, none verified against
live output). Not yet transcribed: Salesforce, Pipedrive, Dynamics 365, Zoho, Close, Attio,
dbt, Cube, LookML, Malloy, OSI, Matomo, HubSpot analytics.

**Tooling.** `xeo:termStatus` (core) marks the extension set. Ten more SHACL shapes (25 in
all) and a third example file. The profile, `schemes.json` and the term docs carry `status`,
`deprecated` and `replacedBy`; `schemes.json` gains `vendorSchemes`. The validator checks the
vendor schemes, the status and deprecation markers, that every earlier metric code resolves
to a Metric, and that every published Metric conforms to the shapes.

### Deprecated (advisory)

`owl:deprecated true` with an `rdfs:seeAlso` to the replacement. Every one of these stays
declared, typed and valid, and none will be removed. The flag says which form a new
implementation should write.

| Term | Write instead |
|---|---|
| `lift` | `absoluteChange`, `relativeChange` |
| `direction` | `betterDirection`, on the Metric |
| `CallToAction`, `LeadCaptureForm`, `GatedAsset` | `conversionPointType` |
| `Informational`, `Navigational`, `CommercialInvestigation`, `Transactional` | the `xeos:searchIntent` concepts |

`MetricTargetShape` no longer requires `direction`; a stored one is still checked.

### Fixed (layer)

A term's `xeo:epistemicLayer` corrected. Nothing about its type, range or meaning changed, but
a consumer that selects terms by layer will find these one layer over.

| Term | Was | Now | Why |
|---|---|---|---|
| `measures` | observation | episode | it records an experiment's design, fixed at setup |
| `mentionRate`, `citationRate` | observation | derivation | a computed share is a derivation, by XEO's own rule |
| `etv` (the metric) | no layer stated | readings are derivations | a vendor's model output, not a measurement |

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
repositories resolve exactly as they did before this release. The metrics and CRM pipeline
pass kept to the same rule: 25 one-for-one line edits across six files, everything else
appended.

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
