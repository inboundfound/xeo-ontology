# Changelog

What changed in XEO, newest first. **Until 1.0, deprecated terms may be removed in the next
release. From 1.0, nothing is removed.** A term is deprecated, with `rdfs:seeAlso` naming its
replacement, before it is removed. Otherwise a release adds terms, widens a domain or range,
and corrects prose; a domain or range is not narrowed.

Versions before 0.6.0 are reconstructed from the git history.

## Unreleased — draft: the experiments, company knowledge and design modules

Three new add-on modules for the next release, every term in both marked
`xeo:termStatus "draft"`: declared so they can be tried, and free to change or go without a
deprecation step. Nothing released is renamed, removed, retyped or narrowed. The version stays
0.7.2 until the release commit.

### `xeo-experiments.ttl`

From the 0.7 plan of record and the research report on agent harnesses (§2 to §4.5, §7).
42 terms: `Arm`, `Trial`, `Benchmark`, `BenchmarkTask`, `Claim`, `ClaimCheck`, `Lesson`; how an
experiment is designed (`hasArm`, `testsTactic`, `isBaseline`, `primaryMetric`,
`guardrailMetric`, `preRegistrationRef`) and run (`hasTrial`, `onTask`, `inBenchmark`,
`trialReplicate`, `trialBlock`, `trialScore`, `failureClass`, `benchmarkVersion`,
`graderKind`, `taskRef`); what an arm measured (`armMean`, `armStandardDeviation`,
`armSampleSize`) and the interval around a change (`forArm`, `ciLower`, `ciUpper`,
`ciMethod`, `effectiveN`); claims (`claimedBy`, `claimMetric`, `claimedValue`,
`counterfactual`, `claimSourceUri`, `claimedAt`, `checksClaim`, `checkedBy`,
`claimVerdict`); lessons (`drawnFrom`, `adoptedAs`).

- **`Experiment` and `Outcome` stay in `xeo-decision.ttl`.** The plan lists them in the new
  module; they are released and cited by line number, so the move waits for a release
  decision. The new module points at them, and those links are optional.
- **An arm's own figures sit on the `Arm`, not on an `Outcome`.** An Outcome is a comparison
  and must state a `result`; the baseline arm has nothing to be compared with.
- **A `Lesson` is not a subclass of `Practice`.** XEO tells lessons, SOPs and best practices
  apart by source, not by class. A Lesson is the finding; the rule adopted from it is a
  Practice whose source is `learned` (`adoptedAs`).
- **Renamed from the research under the naming rule:** `block` is `trialBlock`, `reward` is
  `trialScore`, `replicate` is `trialReplicate`.
- **Three draft schemes:** `graderKind`, `failureClass`, `claimVerdict`. `confirmed` is added
  to the research's verdicts, which had no code for a claim that held.

### `xeo-knowledge.ttl`

Stage 2 of the company-knowledge planning brief: what schema.org lacks, each thing with its
layer. 13 terms: `Meeting` (episode), `Recording` and `Transcript` (observations, kept as
pointers), `Summary` (derivation), `ActionItem` (interpretation); `attendee`, `recordingOf`,
`transcriptOf`, `summarizes`, `raisedIn`, `assignedTo`; and `memberOf` and `unitOf` (from the
W3C Organization Ontology) for people and departments. A message, a thread and a document are
schema.org's `Message`, `Conversation` and `DigitalDocument`, and no class is minted for them.

### `xeo-design.ttl`

Design and web development: what a site is designed and built with, and how a new design is
proposed, shown and decided. 38 terms. The design system: `DesignSystem`, `DesignToken`,
`DesignComponent`, `DesignPattern`, `PageTemplate`, `DesignAsset`; `inDesignSystem`,
`usesDesignSystem` (from a `Website`), `aliasOf`, `usesToken`, `composedOf`, `variantOf`,
`usesAsset`, `usesTemplate` (from a `URL`), `designSystemVersion`, `tokenType`, `tokenValue`,
`tokenTier`, `tokenMode`, `assetKind`. The review: `DesignDirection`, `DesignElement`,
`DesignConcept`, `DesignDecision`; `directionFor`, `proposedIn` (a `Deliverable`), `elementOf`,
`seenOn`, `realizedAs`, `depicts`, `underDirection`, `replacesElement`, `fromDirection`,
`decidesOn`, `chosenConcept`, `decidedBy`, `elementKind`, `designVerdict`.

- **Tokens follow the W3C Design Tokens Format (2025.10).** `tokenType`'s codes are its type
  names, spelled as it spells them (camelCase), plus `string` and `boolean` for Figma's
  variables of those types. An alias is `aliasOf`. A token with a value per mode is one token
  per mode, until the format's own answer to themes is checked.
- **Approval is a decision, not a flag.** A direction carries no status; a `DesignDecision`
  about it does, with who and when, so a changed mind is a new decision beside the old one.
- **A card concept is a `DesignConcept` that depicts a card component.** No class for one kind
  of concept.
- **Not `Feedback`.** Feedback (decision) judges a machine's claim; a design decision is a
  person's call on a proposal.
- **Five draft schemes:** `tokenType`, `tokenTier`, `elementKind`, `assetKind`, `designVerdict`.
- `docs/design/research-prompt.md`: the prompt for checking the module against Figma, Claude's
  design features, Canva, Adobe and the token format.

### Also

- **Shapes (design):** five, each with a failing case: a token has one type and at most one
  alias; a token has a value or an alias; an element belongs to one website; a concept names
  what it depicts, under at most one direction; a decision names one thing and one verdict.
- **Alignment (design):** `DesignAsset` closeMatch `schema:MediaObject`, `DesignConcept`
  closeMatch `schema:CreativeWork`, `DesignDecision` closeMatch `schema:Review`, `usesAsset`
  closeMatch `schema:associatedMedia`.
- **Example (design):** `examples/design-review.jsonld` loads all ten design classes.
- `artifactUri` (core) may also sit on six design classes, and `statement` (decision) on a
  `DesignDirection` or a `DesignDecision`.
- **Shapes:** six, for the rules the two modules state as required (a trial belongs to one
  arm; a claim check names one claim and one verdict; a recording and a transcript name what
  they record; a summary and an action item name their source), each with a failing case in
  `examples/invalid/broken-rules.jsonld`.
- **Alignment:** `xeo-align.ttl` gains bridges to schema.org, PROV-O, ML-Schema and the W3C
  Organization Ontology for the new terms, and `Experiment` closeMatch `mls:Experiment`.
- **Examples:** `examples/experiment-arms.jsonld` and `examples/company-knowledge.jsonld` load
  every new class.
- `statement` (decision) may also sit on a `Claim` or a `Lesson`, and `artifactUri` (core) on
  a `Recording`, `Transcript` or `Summary`: two open lists widened.
- Generated files regenerated; `tools/gen_docs.py`, `gen_profile.py` and `gen_site.py` list the
  two modules.

## 0.7.2 — five wider edges, and three descriptions that now say one thing (2026-11-17)

A patch from mapping XEO against the production code its decision and work modules were lifted
from. Where the two disagreed and the ontology was the one out of step, the ontology changed.
No term is added, renamed, removed or retyped. Nothing is narrowed, so data that was valid in
0.7.1 is valid in 0.7.2. No tombstone is added. Every module file carries 0.7.2.

**Nobody outside uses XEO before 1.0, and released terms may still change.** This release
changes the stated domain or range of five released properties and the descriptions of three
more.

### Five edges, widened

Each hard `rdfs:domain` or `rdfs:range` became an open list (`xeo:domainIncludes`,
`xeo:rangeIncludes`), which is a hint and never an inference rule. The edit is in place, so no
line in `xeo-decision.ttl` moved.

| Property | 0.7.1 | 0.7.2 | Why |
|---|---|---|---|
| `addressableBy` | range `Tactic` | may point at a `Tactic` or an `Intervention` | A catalogue can hold a category of work with no tactic under it. The category then stands in. |
| `recommends` | range `Tactic` | `Tactic` or `Intervention` | The same. |
| `tests` | range `Tactic` | `Tactic` or `Intervention` | An experiment tests what its recommendation put forward. |
| `supersedes` | domain and range `Practice` | `Practice`, `Recommendation`, `Spec` or `DiagnosticRun`, the same class at both ends | The description of `DiagnosticRun` already said a later run supersedes an earlier one. A recommendation and a plan are replaced the same way. |
| `appliesTo` | domain `Practice` | `Practice`, `Gap` or `Recommendation` | A gap and a recommendation name the pages they are about. With a hard domain, every one that did was inferred to be a Practice. |

`suggests` and `appliesTo` already accepted an `Intervention`. `Spec` is a draft term in the
work module; the link from `supersedes` is an open list, so decision still needs only core.

What did not change: on a `Practice`, an edit still mints a new Practice that `supersedes` the
old one. The layer of each property is as it was.

### Three descriptions, each now saying one thing

- **`measures` and `treats`.** The description of `measures` covered two edges: the target an
  experiment is read against, and a basis saying which pages were measured. It is the first
  only. `treats` is the pages or terms an experiment was run on, and its description now
  carries the role (primary or secondary) and the basis (how a page came to be in the measured
  set). Domain, range and layer of both are unchanged.
- **`Feedback`, `source` and `xeos:practiceSource`.** `source` said a learned Practice is
  earned from the experiment ledger. `Feedback` said learned rules are drawn from feedback.
  The first stands: a Practice an operator promotes from a Feedback is `authored`, because it
  rests on that person's authority and no experiment earned it. The definitions of the
  `authored` and `learned` concepts say so too. The three codes are unchanged.

### Docs

The 0.7.0 entry below, `docs/site-handoff-0.7.md` and `docs/v0.6-kit-sync.md` named an
individual. They now name the role or give the date.

### For a consumer

- A graph that checks relationship endpoints against `neo4j-profile.json` will see more
  allowed endpoints on `ADDRESSABLE_BY`, `RECOMMENDS`, `TESTS`, `SUPERSEDES` and `APPLIES_TO`.
  Nothing that passed before fails now.
- Do not read `rdfs:domain` or `rdfs:range` off those five properties any more: read the open
  lists.
- A consumer that shows the `learned` hint for a rule promoted from feedback should show
  `authored`.

Site: `docs/site-handoff-0.7.2.md`.

## 0.7.1 — agentic engineering module (draft), a looser Project, the name (2026-11-17)

A new add-on module for the agents that do the work; specs, work items and deliverables in
the work module; and a `Project` that no longer has to be a client contract. Everything added
is marked draft. No released term is renamed, removed or retyped, and every module still needs
only core. The new terms are from the XEO research report on agent harnesses and AI-assisted
development (10 November) and its handoff.

**Why a patch number.** No term published in 0.7.0 goes away or changes type, and everything
added is draft. What does change in released terms is prose: the descriptions of `Project`,
`Campaign`, `Objective` and their properties are loosened, and those of `Practice` and
`Recommendation` are widened. Data that was valid in 0.7.0 is valid in 0.7.1. Every module
file carries 0.7.1, as one release carries one version, including the modules this release
does not touch.

### A third term status, `draft`

`xeo:termStatus` now takes `core`, `extension` or `draft`. A draft term belongs to a module
still being written: it is declared so it can be tried against data, and it may change or be
removed without a deprecation step. A class stays draft until an example file loads it and its
maintainer lifts the mark; `tools/validate.py` lists each draft class with the example that
loads it. The profile, the term docs and `schemes.json` carry the mark. All 81 terms and 11
schemes below are draft.

### New module `xeo-agentic.ttl`

What exists because an agent ran or a model was called. 11 classes, 15 object properties, 46
datatype properties and one annotation property.

- **The harness:** `Harness` (two identities: `name` with `harnessVersion`, and a
  `harnessDigest` of the files actually loaded), `HarnessComponent` (`componentKind`,
  `loadMode`, `componentDigest`), `AgentRuntime` (`runtimeVersion`); `hasComponent`, `runsOn`.
- **What happened:** `AgentSession` (`sessionRef`, `startType`, `underHarness`, `onRuntime`,
  `continuesSession`), `AgentTurn` (`turnRef`), `ModelCall` (`modelCallRef`), `ToolCall`
  (`toolCallRef`, `toolName`, `toolSource`, `succeeded`, `errorClass`, `failureSignature`);
  `hasTurn`, `hasModelCall`, `hasToolCall`, and `inSession` for a record with no turn.
- **The settings a model was called with:** `InvocationConfig` (`modelProvider`,
  `requestedModel`, `reasoningLevel`, `temperature`, `maxOutputTokens`, `toolSetDigest`), and
  `usedConfig`, which links a `ModelCall` to it. A captured `LLMResponse` (visibility) can
  carry `usedConfig` too: an optional link that works when both modules are loaded. These are
  here and not in core because they are detail about one model call. What every graph needs
  in order to say which build answered, `Model` and `producedByModel`, stays in core.
- **Usage:** `uncachedInputTokens`, `cacheReadTokens`, `cacheWriteTokens` and `outputTokens`
  never overlap, and `reasoningTokens` is a part of output. A field named `input_tokens`
  excludes cached tokens at one provider and includes them at another, so it is mapped by
  vendor and that vendor's `tokenAccounting`, never by its name. Also `latencyMs`,
  `timeToFirstTokenMs`, `attemptCount`, `stopReason`.
- **Cache writes by lifetime:** `cacheWriteDefaultLifetimeTokens` and
  `cacheWriteExtendedLifetimeTokens`, the two parts of `cacheWriteTokens`, for a provider that
  charges more to write a cache entry it keeps longer. They sum to the total and are never
  added to it. A cost figure for such a provider is computed from the parts.
- **Cost:** `costAmount` with `costBasis` and core's `currencyCode`. A derivation, unless the
  basis is an invoice.
- **Rules firing:** `EnforcementEvent` (`enforcementDecision`, `decisionSource`, `reasonText`,
  `onToolCall`). A component is a file, and the rule it states is a `Practice`
  (`expressesPractice`); the moment the rule fired is the event (`firedPractice`), an episode
  beside `appliedPractice`, which stays a derivation. A `Practice` gains `enforcementPoint`
  and `failureMode`.
- **`Compaction`** (`compactionTrigger`, `tokensBefore`, `tokensAfter`) and **`Delegation`**
  (`parentAgentId`, `childAgentId`, `returnsControl`, `childSession`).
- `producedInSession`: the session a `Deliverable` came out of.

Its links to decision (four), to work (one) and to visibility (`usedConfig` on an
`LLMResponse`) are optional and work when both are loaded.

### Core

- **`artifactUri`** (draft): where the file behind a node is kept. The sibling of
  `datasetUri`. The one new term in core.

### Work

- **`Spec`** (`specKind`, `withinProject`), **`WorkItem`** (`tracesTo` a Spec or a
  Recommendation) and **`Deliverable`** (`fulfils` a WorkItem), all draft. They are in work,
  not in the agentic module, because a person writes a spec and hands back a deliverable as
  often as an agent does.
- How they sit beside what was there: an `Objective` says what should move and a `Spec` what
  is to be built; a `Recommendation` is the call to do something and a `WorkItem` one step of
  doing it; a `Deliverable` is what was handed back and an `Outcome` what was measured after.

### `Project`, `Campaign` and `Objective` are loosened

Until now their descriptions carried one agency's operating rules as if they were what the
terms mean. They were prose, never shapes, and they are now optional in the prose too.

- **A `Project` is a bounded body of work**, client or internal. It need not be a contract,
  sit on one `Website`, have a `Campaign`, an `interventionQuota` or an end date. An internal
  `Spec` can sit `withinProject`. `engagementType`, `interventionQuota`, `cadence`,
  `durationDays` and `inScope` are all still declared and all optional.
- **A `Campaign`** need not have a `Topic` or an `Objective`. **An `Objective`** need not have
  targets or a results window.
- **Absence means "not stated".** No `interventionQuota` is no stated ceiling, not a ceiling of
  zero. No `inScope` is no stated contract scope, not an empty one. A consumer that computes
  room left in a quota must read it that way.
- **Kept**, because other terms lean on them: at most one `Objective` per `Campaign`, at most
  one primary target per `Objective`, exactly one `targetMetric` per `MetricTarget`.
- Descriptions edited in place, one line for one line: `Project`, `Campaign`, `Objective`,
  `hasProject`, `inScope`, `aboutTopic`, `hasObjective`, `hasTarget`, `execution`,
  `engagementType`, `interventionQuota`, `cadence`, `durationDays`, `isPrimary`, `clientOf`;
  the scheme `xeos:engagementType`; the `schema:Project` note in `xeo-align.ttl`.

**The old rules are kept as an optional profile**, `shapes/profiles/agency-delivery.ttl`: eight
SHACL shapes a team loads beside the base shapes if its every project is a contract (a type
and a quota on every project, on exactly one website; a cadence for a retainer and a run
length for a one-off; one topic and one objective per campaign; a results window, at least one
target and exactly one primary target per objective). `tools/validate.py` checks each profile
against its own test data in `examples/profiles/`; the examples in `examples/` are never held
to one. A graph that fails a profile is still valid XEO.

### Decision

- **`Practice`**: its description said it governs how recommendations are made, while four
  new terms treat a rule a harness states or enforces as a `Practice`. It now says a Practice
  governs a class of choices: a `Recommendation` in the decision chain, an agent's action
  under a harness. `constrains` is unchanged.
- **`Recommendation`**: its description now says `closesGap` and `supportedBy` are optional. A
  call a person or an agent makes from tacit or general knowledge, with no diagnosed `Gap` and
  no `Experiment` behind it, is a `Recommendation`, and its `method` says so. No shape ever
  required either link.

### The name

`XEO` in prose, `xeo` in prefixes, file names and code. The spelling with a lowercase x and
capital EO is gone from the modules and the docs. Where it stood for SEO, GEO and AEO taken
together, the text now says that; the title of the visibility module is "XEO Visibility (AI
answers: GEO and AEO)".

### Reference schemes

Eleven, 51 concepts: `harnessComponentKind`, `loadMode`, `startType`, `toolSource`,
`hookDecision` (fills `enforcementDecision`), `decisionSource`, `enforcementPoint`,
`failureMode`, `compactionTrigger`, `costBasis`, `specKind`.

### Example

`examples/agent-session.jsonld`: one harness, one session under it, the spec it worked from,
and one deliverable from the agent beside one made by hand. It loads all 14 new classes, shows
a model call's cache writes split by lifetime, and has an internal `Project`, with a name and
nothing else, holding a `Spec`.

### Tombstones

`tombstones.json` gains `epistemicLayer`, renamed `xeoLayer` in 0.7.0 and missing from the
list until now. Nothing is removed in 0.7.1.

### Not in this release

`Requirement`, `AcceptanceCriterion` and `ReviewVerdict`; `Handoff`, `McpServer` and
`AgentFramework`; the experiment design terms (arms, trials, benchmarks, claims), which belong
to an experiments module; widening the range of `constrains` to cover an agent's actions;
moving `webSearchEnabled` onto the configuration; any vendor mapping; SHACL shapes in the base
file and Neo4j constraints for the new classes, including a shape that checks the two
cache-write parts sum to the total.

## 0.7.0 — modules, deletions, core and sales, attribution (2026-11-12)

Every module now needs only core; deprecated terms are deleted; core gains `Model`,
`Consent` and inbound references; a target links to its Metric; and a new attribution
module covers touches, journeys, revenue, spend and attribution models. Decided in the 0.7
plan of record (11 November) and the decisions taken on it on 12 November.

**Breaking, on purpose.** Until 1.0, deprecated terms may be removed in the next release.
Every removal below was deprecated in 0.6 with its replacement named, or is replaced in this
release. `tools/term_list.py --against <ref> --removed ... --added ...` states each change
exactly.

### Modules

Every module now needs only core. A link between two add-ons (a practice constraining a
recommendation, a recommendation issued for a campaign) is optional and works when both are
loaded. `tools/validate.py` checks that core loads alone and lists those links. "Layer" now
means only the kind of claim a term makes; the files are modules.

No term was added or removed and no term's meaning changed. `tools/term_list.py --against
<0.6 ref> --rename epistemicLayer=xeoLayer` finds the same 324 terms, and the only
statements that differ are wording that named the old files or the old property name.

| Module | 0.6 | 0.7 |
|---|---|---|
| core | `xeo-core.ttl` | also holds `Engine` and `SearchEngine` (with `onEngine`, `capturedAt` and `model`, which a core `SerpSnapshot` carries), `SearchIntent`, website conversions (`ConversionPoint`, `ConversionEvent` and their properties), the money terms (`currencyCode`, `recurringValue`, `valuePeriod`, `amountInReportingCurrency`), and everything that was `xeo-metrics.ttl` |
| visibility | `xeo-visibility.ttl` | gains `attributedResponse` from engagement; loses the five engine terms to core |
| sales | the CRM half of `xeo-engagement.ttl` | `xeo-sales.ttl` |
| work | `xeo-delivery.ttl` | `xeo-work.ttl`, renamed: it already held the agency terms |
| analysis, decision, strategy | unchanged | unchanged |

`xeo-engagement.ttl`, `xeo-delivery.ttl` and `xeo-metrics.ttl` no longer exist. Terms moved
into core were appended at its foot, so line citations into core still resolve.

**Renamed.** `xeo:epistemicLayer` is now `xeo:xeoLayer`, the name the kit already stamps on
every node. The scheme of its six values is `xeos:xeoLayer`, its concepts
`xeos:xeoLayer-entity` and so on. A consumer that reads the old name reads nothing: rename it.

**Strategy merges into decision** (decided 12 November). Practices govern Recommendations, and on
its own the module had little to say. `xeo-strategy.ttl` is appended at the foot of
`xeo-decision.ttl`, unchanged. Line citations into `xeo-strategy.ttl` must name terms instead.

**Every observation names its grounding.** The 19 that did not now do, and `validate.py` fails
an observation with no `groundedIn`.

### Removed

| Term | Use instead |
|---|---|
| `lift` | `absoluteChange` and `relativeChange` on the Outcome |
| `direction` | `betterDirection`, stated once on the Metric |
| `Informational`, `Navigational`, `CommercialInvestigation`, `Transactional` | the `xeos:searchIntent` concepts |
| `CallToAction`, `LeadCaptureForm`, `GatedAsset` | `conversionPointType`: `cta`, `lead_form`, `gated_asset` |
| `campaignInfluenceShare` | `creditShare` on an `AttributedCredit` (attribution) |
| `GenerativeEngine` | `GenerativeOverview` (a rename) |
| `ConversationalAgent` | `AnswerEngine` |
| `metric` (the text code on a MetricTarget) | `targetMetric`, a link to the Metric node |
| `valuePeriod` and `xeos:valuePeriod` | `billingInterval` with `billingIntervalCount` |

`websiteId` stays, and is optional: nothing requires it. `Term` stays until `SearchQuery` lands.

### Redefined

- `modelVersion` is now the dated build of a `Model`, in core. It was a text field on an
  `LLMResponse`.
- `Engine` is a parent class only: every engine node is a `SearchEngine` (core), a
  `GenerativeOverview` or an `AnswerEngine` (visibility).

### Core and sales

- **`Model`**, with `modelFamily`, `modelVersion` and `modelKind`. `producedByModel` links an
  answer to it. The plain `model` text field stays, for imports that only give a name.
- **`Consent`**: one recorded choice for one purpose by one Person or Organization, as one
  system captured it. Its properties are `consentSubject`, `consentPurpose`, `consentStatus`,
  `consentRecordedAt`, `consentCapturedBy` and `consentSource`. History is kept, and
  validity under law is left to an interpretation. It has close matches to W3C DPV in
  `xeo-align.ttl`, and a shape.
- **`InboundReference`**: a page on another site that links to or mentions you. Its
  properties are `referencingUrl`, `referenceTarget` and `referenceKind`. How it came about
  is `acquiredByTactic` (decision); an organic reference has none.
- **`targetMetric`** links a MetricTarget to its Metric (C5). Neo4j constraints are added for
  Metric and MetricReading (K3), and for Model, Consent and InboundReference.
- **Acquisition channels:** 14, adding `affiliate`, `display` and `programmatic` (D2).
- **`billingInterval`** (day, week, month, year) and **`billingIntervalCount`** replace
  `valuePeriod` (D3). Quarterly is month and 3.

### Attribution (new module)

`xeo-attribution.ttl` needs only core, so an online seller with no CRM loads core and
attribution and nothing else.

- **Touches and identity:**
  - `Touchpoint`, carrying `touchType`, `touchChannel`, the UTM fields, `clickIdentifier`,
    ad pointers and `touchLandingUrl`.
  - `Journey`, of a Person or an Organization.
  - `IdentityLink`, whose methods include `ip_to_company`.
- **Calls and meetings:** `Call` and `BookedMeeting` are kinds of `ConversionEvent`.
  `callOutcome` records the outcome and `outcomeJudgedBy` says who judged it.
- **Revenue without a pipeline:** `Order`, `Payment`, `Refund`, `Chargeback` and
  `Subscription`, with their amounts, `quoteValue` and `customerStatus`.
- **Spend:** `SpendRollup`, per campaign, ad set or ad.
- **Attribution models:** an `AttributionModel` is described by its structure, never by a
  vendor's name for it: `creditRule`, `CreditAnchor`s (positions include `qualified`),
  `lookbackWindow`, eligible touch types (email opens are not eligible by default),
  deduplication, `dateBasis` and `revenueBasis`.
- **Results:** `AttributedCredit` and `AttributionRollup`. A shape requires both to name
  their model with `usesAttributionModel`.
- **Moved here from sales:** `firstTouchChannel`, `latestTouchChannel` and
  `referringPlatform`.
- **Eight metrics:** ad spend, attributed revenue, ROAS, blended ROAS, cost per lead, cost
  per acquisition, lifetime value and payback period.
- **Bridge:** `xeo-attribution-sales.ttl` lets B2B models read deal stages
  (`anchorStageRef`, `creditForDeal`).

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

Counts: 36 → 51 classes, 61 → 114 object properties, 65 → 147 datatype properties,
20 → 50 reference schemes, 93 → 282 concepts; 5 vendor schemes mapping 57 fields.
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
- `Person` and `Organization`, the canonical parties: one node per real person or organization.
  `Organization` keeps `owns` and `organizationKind`. `refersTo` (derivation) runs from any
  system's record of a party (a HubSpot contact or company, a Hyros lead, a SegMetrics visitor)
  to the canonical node, and carries the method of the match. Both classes are `exactMatch`
  schema.org's (`xeo-align.ttl`). *Why:* every system holds its own copy of a person, and the
  copies need one node to join on, mapped the same way whatever the vendor. The canonical node
  copies no vendor's fields; the vendor's record keeps them, under a vendor label that is the
  implementation's convention, never an XEO term (`mappings/README.md`). Decided 2026-11-12;
  `Organization`, `owns` and `organizationKind` were in delivery earlier in 0.6.

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

**Delivery.** `clientOf` and `holdsCapability`, between Organizations (core). *Why:* the only
tenancy node was the Website, so "this agency's client" and "what this team can do" had
nowhere to hang.

**Reference schemes.** `serpResultType`, `linkPosition`, `similarityBasis`, `algorithm`,
`frameworkKind`, `organizationKind`, `sentiment`, `device`, `feedbackVerdict`; and
`ai_mention_rate` and `ai_citation_rate` in `objectiveMetric`, so a campaign can target AI
visibility. The AI rate codes are `ai_mention_rate` and `ai_citation_rate` (decided 2026-11-12,
so every AI visibility code carries the `ai_` prefix); the properties `mentionRate` and
`citationRate` keep their names.

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
- The window is core's `periodStart` and `periodEnd`, reworded (decided 2026-11-12): calendar
  dates, both days included, in the source's own time zone. No new window pair.
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
same code. No numbers in the ontology (decided 2026-11-12): `minDenominator` is a slot, and no
published Metric carries a value for it. Each implementation sets its own.

**`ctr` unit, corrected to ratio.** The published `objectiveMetric` concept noted its unit as
percent. Search Console returns a 0 to 1 quotient, and the Metric `ctr` states ratio, so the old
note now says ratio too. Stored values were not checked first: a consumer that built on the old
note may hold 5 where this means 0.05, and should check its `ctr` targets and baselines before
reading them as ratios. An editorial note on the concept says the same.

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
  scheme includes `ai_assistant`, and `ai_overview` (extension) for a visit sent by an AI
  overview on a search engine's results page. *Why:* that visit is neither an assistant's nor an
  ordinary result. No source reports it separately yet, so nothing fills it.
- No CRM record class. The record-level properties sit on the system's own record, a
  vendor-labelled node (`HUBSPOT_Contact`, `HUBSPOT_Deal`) that `refersTo` the canonical
  `Person` or `Organization` where it stands for one. *Why:* one class standing for a person, a
  company, a deal or a task says too little. (A `CrmRecord` class was minted on 2026-11-11 and
  removed before release, 2026-11-12.)
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

`owl:deprecated true` with an `rdfs:seeAlso` to the replacement. In 0.6 every one of these
stays declared, typed and valid. Until 1.0, deprecated terms may be removed in the next
release, so these may go in 0.7. The flag says which form a new implementation should write.

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
