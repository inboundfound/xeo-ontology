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
   `WorkItem`s that `tracesTo` it.
3. **A session.** An `AgentSession` with the runtime's own `sessionRef`, the harness it ran
   under and the runtime it ran on. One `AgentTurn`, and one `ModelCall` under a shared
   `InvocationConfig`: `requestedModel` is an alias, and `producedByModel` names the
   build that answered. Its four token counts do not overlap, and `reasoningTokens` is part of
   `outputTokens`. Its cost is an estimate (`costBasis`), with the price table in `method`.
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
