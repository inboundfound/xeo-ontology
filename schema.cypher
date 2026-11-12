// XEO Ontology — Neo4j 5.x schema (core + visibility + engagement + decision + strategy + delivery + analysis)
// Entities are durable, episodes are immutable, tenancy lives in properties.

// ========== CORE ==========

// ---------- Entities ----------
CREATE CONSTRAINT website_id IF NOT EXISTS
FOR (w:Website) REQUIRE w.id IS UNIQUE;

CREATE CONSTRAINT website_origin IF NOT EXISTS
FOR (w:Website) REQUIRE w.origin IS UNIQUE;

// URL identity is (address, websiteId) — same address can exist under two tenants.
CREATE CONSTRAINT url_identity IF NOT EXISTS
FOR (u:URL) REQUIRE (u.address, u.websiteId) IS UNIQUE;

CREATE CONSTRAINT term_name IF NOT EXISTS
FOR (t:Term) REQUIRE t.name IS UNIQUE;

// Topics are derivations, scoped per site.
CREATE CONSTRAINT topic_identity IF NOT EXISTS
FOR (t:Topic) REQUIRE (t.name, t.websiteId) IS UNIQUE;

// ---------- Episodes ----------
CREATE CONSTRAINT crawl_id IF NOT EXISTS
FOR (c:Crawl) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT serp_snapshot_id IF NOT EXISTS
FOR (s:SerpSnapshot) REQUIRE s.id IS UNIQUE;

// ---------- Secondary indexes ----------
CREATE INDEX serp_snapshot_captured IF NOT EXISTS
FOR (s:SerpSnapshot) ON (s.capturedAt);

CREATE INDEX crawl_started IF NOT EXISTS
FOR (c:Crawl) ON (c.startedAt);

// RANKS_FOR is period-scoped; range scans by window are the hot path.
CREATE INDEX ranks_for_period IF NOT EXISTS
FOR ()-[r:RANKS_FOR]-() ON (r.periodStart);

// Link liveness checks resolve against the crawl that last saw the edge.
CREATE INDEX links_to_last_seen IF NOT EXISTS
FOR ()-[l:LINKS_TO]-() ON (l.lastSeenCrawlId);

CREATE INDEX fetched_status IF NOT EXISTS
FOR ()-[f:FETCHED]-() ON (f.statusCode);

// ========== VISIBILITY (the xEO layer) ==========

// ---------- Entities ----------
CREATE CONSTRAINT engine_id IF NOT EXISTS
FOR (e:Engine) REQUIRE e.id IS UNIQUE;

// Brands are tenant-scoped: the same market name can be tracked by two tenants.
CREATE CONSTRAINT brand_identity IF NOT EXISTS
FOR (b:Brand) REQUIRE (b.name, b.websiteId) IS UNIQUE;

CREATE CONSTRAINT prompt_identity IF NOT EXISTS
FOR (p:Prompt) REQUIRE (p.text, p.websiteId) IS UNIQUE;

// ---------- Episodes ----------
CREATE CONSTRAINT llm_response_id IF NOT EXISTS
FOR (r:LLMResponse) REQUIRE r.id IS UNIQUE;

CREATE INDEX llm_response_captured IF NOT EXISTS
FOR (r:LLMResponse) ON (r.capturedAt);

// ---------- Rollups ----------
// VISIBILITY_FOR mirrors RANKS_FOR: period-scoped projection over responses.
CREATE INDEX visibility_for_period IF NOT EXISTS
FOR ()-[v:VISIBILITY_FOR]-() ON (v.periodStart);

// MENTIONS rank is the list-position analysis hot path.
CREATE INDEX mentions_rank IF NOT EXISTS
FOR ()-[m:MENTIONS]-() ON (m.mentionRank);

// ========== ENGAGEMENT (draft) ==========

CREATE CONSTRAINT conversion_point_id IF NOT EXISTS
FOR (c:ConversionPoint) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT conversion_event_id IF NOT EXISTS
FOR (e:ConversionEvent) REQUIRE e.id IS UNIQUE;

CREATE INDEX conversion_event_time IF NOT EXISTS
FOR (e:ConversionEvent) ON (e.occurredAt);

// The CRM join contract: look up graph objects from a CRM record id.
CREATE INDEX conversion_point_crm_ref IF NOT EXISTS
FOR (c:ConversionPoint) ON (c.crmRecordRef);

// ========== DECISION (the interpretation tier) ==========

// ---------- Entities ----------
// Tactics are a shared library (global); intervention category is a slotted-in concept.
CREATE CONSTRAINT tactic_id IF NOT EXISTS
FOR (t:Tactic) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT diagnostic_id IF NOT EXISTS
FOR (d:Diagnostic) REQUIRE d.id IS UNIQUE;

// Capabilities are the scope-gate levers, approved per tenant.
CREATE CONSTRAINT capability_identity IF NOT EXISTS
FOR (c:Capability) REQUIRE (c.name, c.websiteId) IS UNIQUE;

// Gaps are diagnosed per tenant.
CREATE CONSTRAINT gap_id IF NOT EXISTS
FOR (g:Gap) REQUIRE g.id IS UNIQUE;

CREATE CONSTRAINT recommendation_id IF NOT EXISTS
FOR (r:Recommendation) REQUIRE r.id IS UNIQUE;

// ---------- Episodes ----------
CREATE CONSTRAINT experiment_id IF NOT EXISTS
FOR (e:Experiment) REQUIRE e.id IS UNIQUE;

CREATE INDEX experiment_concluded IF NOT EXISTS
FOR (e:Experiment) ON (e.concludedAt);

// Precedent lookup: "tactics tried against a gap of this kind" scans by gapType.
CREATE INDEX gap_website IF NOT EXISTS
FOR (g:Gap) ON (g.websiteId);

// ========== PRACTICES (in decision since 0.7) ==========
// Practices and Playbooks are authored once and reused; what varies per tenant is
// which Playbooks are activated and which Practices are overridden. Both are
// global by id — tenancy rides on the activation and override edges, not on the
// rule itself. Matches xeo-graph-kit/seed/practices.cypher.

CREATE CONSTRAINT practice_id IF NOT EXISTS
FOR (p:Practice) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT playbook_id IF NOT EXISTS
FOR (pb:Playbook) REQUIRE pb.id IS UNIQUE;

// Only 'active' Practices fire; 'proposed' is visible but inert, 'deprecated' is
// retired-not-deleted (superseding one deprecates it). Every evaluation filters
// on this, so it is the hot path.
CREATE INDEX practice_status IF NOT EXISTS
FOR (p:Practice) ON (p.status);

// A claimed Practice decays unless experiments promote it; the sweep scans by source.
CREATE INDEX practice_source IF NOT EXISTS
FOR (p:Practice) ON (p.source);

// The audit trail: "which rules fired on this recommendation, and why".
CREATE INDEX applied_practice_method IF NOT EXISTS
FOR ()-[a:APPLIED_PRACTICE]-() ON (a.method);

// ========== DELIVERY (projects, campaigns, objectives) ==========
// The container work is delivered in. Projects and campaigns are tenant-scoped
// entities; objectives and metric targets are interpretations that experiments
// are read against — so none of them are ever deleted, only stamped deletedAt.

CREATE CONSTRAINT project_id IF NOT EXISTS
FOR (p:Project) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT campaign_id IF NOT EXISTS
FOR (c:Campaign) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT objective_id IF NOT EXISTS
FOR (o:Objective) REQUIRE o.id IS UNIQUE;

// A target's id is what measured history anchors to; soft-deleted, never dropped.
CREATE CONSTRAINT metric_target_id IF NOT EXISTS
FOR (t:MetricTarget) REQUIRE t.id IS UNIQUE;

// "Everything live for this website" is the list view; deletedAt filters it.
CREATE INDEX project_website IF NOT EXISTS
FOR (p:Project) ON (p.websiteId);

CREATE INDEX campaign_website IF NOT EXISTS
FOR (c:Campaign) ON (c.websiteId);

// The quota gate counts open recommendations per campaign, by status.
CREATE INDEX recommendation_status IF NOT EXISTS
FOR (r:Recommendation) ON (r.status);

// ========== v0.6.0 (kit sync) ==========
// Constraints and indexes for the identity-bearing classes added in 0.6.0.
// Label = class name, relationship type = UPPER_SNAKE of the object property,
// property key = datatype property (docs/neo4j-profile.md, neo4j-profile.json).

// ---------- Core ----------
// A registrable domain is shared, not tenant-scoped: one node per name, no
// websiteId. A competitor's URL attaches here by ON_DOMAIN.
CREATE CONSTRAINT domain_name IF NOT EXISTS
FOR (d:Domain) REQUIRE d.name IS UNIQUE;

// Entities are shared too. entityRef is the identity where one exists; an
// entity with no knowledge-base reference is matched by name.
CREATE CONSTRAINT entity_ref IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entityRef IS UNIQUE;

CREATE INDEX entity_name IF NOT EXISTS
FOR (e:Entity) ON (e.name);

// "Editorial links only" is the usual projection filter for link analysis.
CREATE INDEX links_to_position IF NOT EXISTS
FOR ()-[l:LINKS_TO]-() ON (l.linkPosition);

// Snapshots are compared within one locale and device, never pooled across.
CREATE INDEX serp_snapshot_locale_device IF NOT EXISTS
FOR (s:SerpSnapshot) ON (s.locale, s.device);

CREATE INDEX has_result_type IF NOT EXISTS
FOR ()-[r:HAS_RESULT]-() ON (r.resultType);

// ---------- Decision ----------
CREATE CONSTRAINT diagnostic_run_id IF NOT EXISTS
FOR (r:DiagnosticRun) REQUIRE r.id IS UNIQUE;

CREATE INDEX diagnostic_run_ran IF NOT EXISTS
FOR (r:DiagnosticRun) ON (r.ranAt);

CREATE CONSTRAINT feedback_id IF NOT EXISTS
FOR (f:Feedback) REQUIRE f.id IS UNIQUE;

CREATE CONSTRAINT external_event_id IF NOT EXISTS
FOR (e:ExternalEvent) REQUIRE e.id IS UNIQUE;

// "What happened inside this measurement window" scans by time.
CREATE INDEX external_event_time IF NOT EXISTS
FOR (e:ExternalEvent) ON (e.occurredAt);

CREATE INDEX experiment_started IF NOT EXISTS
FOR (e:Experiment) ON (e.startedAt);

// ---------- Strategy ----------
// A Framework is authored once and reused, like a Playbook: global by id, with
// tenancy on the ACTIVATES edge. Its name is what a person looks it up by.
CREATE CONSTRAINT framework_id IF NOT EXISTS
FOR (f:Framework) REQUIRE f.id IS UNIQUE;

CREATE INDEX framework_name IF NOT EXISTS
FOR (f:Framework) ON (f.name);

// A Stage is identified by name within its Framework. Neo4j cannot constrain
// across a relationship, so the Stage carries a surrogate id (by convention
// "<framework id>/<stage name>") and the pair is enforced by the loader.
CREATE CONSTRAINT stage_id IF NOT EXISTS
FOR (s:Stage) REQUIRE s.id IS UNIQUE;

CREATE INDEX stage_order IF NOT EXISTS
FOR (s:Stage) ON (s.stageOrder);

// The negative half of the audit trail: "which rules were checked and did not fire".
CREATE INDEX evaluated_practice_fired IF NOT EXISTS
FOR ()-[e:EVALUATED_PRACTICE]-() ON (e.fired);

// ---------- Canonical parties (core) ----------
// One node per real person or organization. Each system's record of one is its
// own vendor-labelled node (HUBSPOT_Contact, HYROS_Lead) with a REFERS_TO here;
// vendor labels are the implementation's, so they get no constraint in this file.
CREATE CONSTRAINT organization_id IF NOT EXISTS
FOR (o:Organization) REQUIRE o.id IS UNIQUE;

CREATE INDEX organization_name IF NOT EXISTS
FOR (o:Organization) ON (o.name);

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

// ---------- Analysis ----------
CREATE CONSTRAINT algorithm_run_id IF NOT EXISTS
FOR (r:AlgorithmRun) REQUIRE r.id IS UNIQUE;

CREATE INDEX algorithm_run_ran IF NOT EXISTS
FOR (r:AlgorithmRun) ON (r.ranAt);

// "Nearest neighbours above a cutoff, on one basis" is the similarity hot path.
CREATE INDEX similar_to_basis IF NOT EXISTS
FOR ()-[s:SIMILAR_TO]-() ON (s.basis, s.similarity);

// ========== NOTES ==========
// Every property key and relationship type used above is now a declared XEO
// term. Until 0.6.0 this file indexed two the ontology named only in prose
// (startedAt on :Crawl, lastSeenCrawlId on LINKS_TO) and mentioned a third
// (embeddedAt). The one key that is not an XEO term is `id`: a surrogate key
// for nodes whose identity is not a natural property, a property-graph
// convention the ontology does not define.
// Embeddings live in an external vector store; the graph keeps only the
// derivation claim (embeddingRef, embeddingModel, embeddedAt, embeddingDim) on
// the embedded node — a :Term, a :URL, a :Prompt or a :Topic.
// Daily search-performance grain lives in a column store (e.g. BigQuery) as
// SearchPerformanceFact rows; the graph keeps windowed RANKS_FOR rollups.
// Raw LLM responses may be archived outside the graph at scale; keep the
// episode node + observation edges here and point datasetUri at the archive.

// Optional — only if you later choose to colocate vectors in Neo4j:
// CREATE VECTOR INDEX term_embedding IF NOT EXISTS
// FOR (t:Term) ON (t.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,   // must match embeddingModel
//   `vector.similarity_function`: 'cosine'
// }};
