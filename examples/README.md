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
| `agent-session.jsonld` | The draft terms of 0.7.1: one harness, one agent session under it, the spec it worked from, and a deliverable from the agent beside one made by hand. Loads all fourteen draft classes. |
| `experiment-arms.jsonld` | The draft experiments module: a benchmark of audit tasks, an experiment with a baseline arm and a treated arm and some of their trials, the outcome of one against the other with its interval, a vendor's claim and our check of it, and the lesson drawn and the practice it became. Loads all seven of its classes. |
| `company-knowledge.jsonld` | The draft company knowledge module: a team that is a unit of an agency, its members, a meeting with its recording, transcript and summary, and two action items, one raised in an email kept as `schema:EmailMessage`. Loads all five of its classes. |
| `design-review.jsonld` | The draft design module: an existing site's elements up for review, two directions proposed in one deliverable, card concepts under each, a reviewer's keep, replace, approve and shortlist decisions, and the design system built from the approved direction, with tokens (an alias, a light and a dark mode), components, a variant, a pattern, a page template and assets. Loads all ten of its classes. |
| `invalid/broken-rules.jsonld` | One deliberately wrong node or edge per SHACL shape, each tagged with the shape it must break. The validator fails if a shape stops firing. |
| `profiles/agency-delivery/` | Test data for the optional profile `shapes/profiles/agency-delivery.ttl`, and for nothing else: a retainer and a one-off that meet one agency's contract rules, and in `invalid/` the graphs that break them (an internal project among them, which is valid XEO). The files above are never held to a profile. |

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
   `ai_citation_rate`; one `Practice` fired on it and one was evaluated and did not
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

## What `agent-session.jsonld` walks through

Every new term in it is draft. The runtime, provider and model are invented.

1. **The harness** (`xeo-agentic.ttl`). An `AgentRuntime` at a version, and a `Harness` with
   a name, a `harnessVersion` and a `harnessDigest`. Three `HarnessComponent`s: an instruction
   file that is always loaded, a skill loaded on demand, and a hook. The hook
   `expressesPractice`: the rule itself is a `Practice`, enforced at `hook`, failing open.
2. **The work** (`xeo-work.ttl`). A `Spec` of kind `plan` within a `Project`, and two
   `WorkItem`s that `tracesTo` it. That Project is a client retainer on the site. A second
   `Project` is internal work: it has a name and nothing else (no Website, contract type or
   quota), and a `Spec` sits `withinProject` it the same way.
3. **A session.** An `AgentSession` with the runtime's own `sessionRef`, the harness it ran
   under and the runtime it ran on. One `AgentTurn`, and one `ModelCall` under a shared
   `InvocationConfig`: `requestedModel` is an alias, and `producedByModel` names the
   build that answered. Its four token counts do not overlap, and `reasoningTokens` is part of
   `outputTokens`. Its cache writes are also given by lifetime: 1,500 at the default
   lifetime and 600 at an extended one, which sum to the `cacheWriteTokens` total of 2,100. Its cost is an estimate (`costBasis`), with the price table in `method`.
4. **A rule firing.** Three `ToolCall`s. The first was denied: an `EnforcementEvent` with its
   `enforcementDecision`, the reason given, the call it was about and the `Practice` that
   fired. The second succeeded. The third failed, which is `succeeded` false with an
   `errorClass` and a `failureSignature`.
5. **Delegation and compaction.** A `Delegation` whose subagent ran in a `childSession`; a
   `Compaction` with the context size before and after, pointing at the summary it wrote.
6. **Two deliverables.** One `fulfils` the first work item and was `producedInSession`. The
   other fulfils the second and was made by a person, so it names no session.
7. **The next day.** A second session, `startType` `continue`, which `continuesSession` the
   first.

## What `experiment-arms.jsonld` walks through

Every new term in it is draft. The tool, its maker and the numbers are invented.

1. **Two Metrics of the team's own.** `task_pass_rate`, the mean of the trial scores, is the
   experiment's `primaryMetric`; `cost_per_task` is its `guardrailMetric`.
2. **A benchmark.** `Example SEO audit tasks`, version 1.0, graded by a `verifier`, with two
   `BenchmarkTask`s.
3. **The experiment and its arms.** It `tests` a `Tactic` (give the agent a content-audit
   skill), names where its plan was written beforehand (`preRegistrationRef`) and `hasArm` two
   arms: the baseline without the skill (`isBaseline`) and the treated arm that `testsTactic`.
   Each arm carries its mean, standard deviation and sample size on the primary metric.
4. **Trials.** Five of the arms' 79 counted trials are shown, each `onTask` with a
   `trialReplicate` and a `trialScore`. One failed for an infrastructure reason
   (`failureClass`), has no score, and is left out of its arm's figures.
5. **The outcome.** One `Outcome` `forArm` the treated arm: 0.15 more than the baseline, a
   quarter more, `significant`, with a 95% interval from 0.04 to 0.26 and an `effectiveN` of 18.5.
6. **A claim and its check.** A vendor's `Claim` that the skill adds 40 points, against the
   same agent without it, and a `ClaimCheck` `checkedBy` the experiment: `real_but_small`.
7. **What was learned.** A `Lesson` `drawnFrom` the outcome and the check, `adoptedAs` a
   `Practice` whose source is `learned`.

## What `company-knowledge.jsonld` walks through

Every new term in it is draft. The people have no names on purpose; the agency is invented.

1. **People and units.** A content team that is a `unitOf` an agency, and two people who are
   each a `memberOf` it.
2. **A meeting and its records.** A `Meeting` with its two `attendee`s; a `Recording` of it, a
   `Transcript` of the recording, and a `Summary` of the transcript written by a model. Each
   record is a pointer (`artifactUri`); no audio or words are in the graph.
3. **What was agreed.** One `ActionItem` `raisedIn` the meeting and its summary, `assignedTo` a
   person; another raised in an email, kept as a `schema:EmailMessage`, and assigned to the team.

## What `design-review.jsonld` walks through

Every new term in it is draft. The site, the reviewer and the colours are invented.

1. **The existing site.** Three `DesignElement`s of `example.org`, each with its `elementKind`
   and the pages it is `seenOn`: the logo lockup, a wave divider, and a news card.
2. **Two directions.** `Calm editorial` and `Bold and bright`, each `directionFor` the site and
   the redesign `Project`, both `proposedIn` one `Deliverable`, each with its idea as a `statement`.
3. **Concepts.** A news-card concept under each direction (`depicts` the card component and the
   old news card, `replacesElement` the old one), and a section-break concept that replaces the
   divider under the calm direction. Each is a pointer to its image.
4. **The review.** Four `DesignDecision`s by one reviewer: keep the logo; replace the divider
   under the calm direction with its concept (`chosenConcept`); approve the calm direction; and
   shortlist the bold card for later.
5. **The system built from the pick.** A `DesignSystem` `fromDirection` the calm direction, which
   the site `usesDesignSystem`. A primitive colour, a semantic colour that is an `aliasOf` it in
   light mode and has its own value in dark mode, a spacing step; a headline font and the logo
   file as `DesignAsset`s (the old logo element is `realizedAs` the file); a button, its quiet
   `variantOf`, the card `composedOf` the button, a news-listing `DesignPattern`, and an article
   `PageTemplate` that a news page `usesTemplate`.
