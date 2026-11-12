# Mappings: where a tool's field meets an XEO slot

These files are **not part of the ontology.** XEO holds slots. A vendor's field names, enums and
value sets never become XEO terms. They go here, one file per tool, and nothing in the ontology
points at them. `tools/validate.py` enforces both halves: a mapping may not declare an XEO term,
and no module may reference a mapping.

`xeo-schemes.ttl` holds the reference *fillings* of slots, the values a slot may take. This folder
holds *crosswalks*: which field of whose API carries a slot. They are kept apart because they are
used differently. A filling is something a graph stores. A crosswalk is something a loader or a
classifier reads.

| File | Tool | Scheme |
|---|---|---|
| `hubspot-crm.ttl` | HubSpot CRM deal and contact properties | `xeos:hubspotCrm` |
| `gsc.ttl` | Google Search Console Search Analytics API | `xeos:gsc` |
| `ga4.ttl` | Google Analytics 4 Data API | `xeos:ga4` |
| `peec.ttl` | Peec AI Customer API (brands report) | `xeos:peec` |
| `profound.ttl` | Profound External API (visibility and citations reports) | `xeos:profound` |

`schemes.json` carries all of them under `vendorSchemes`, for loaders that do not read Turtle.

## What every mapped field carries

| Property | What it holds |
|---|---|
| `skos:notation` | the exact string the vendor stores or sends |
| `skos:definition` | what the vendor says the field is, paraphrased |
| `xeo:fillsSlot` | the XEO property the field's value goes into |
| one SKOS match | `exactMatch`, `closeMatch`, `narrowMatch`, `broadMatch` or `relatedMatch`, to the slot or, for a metric field, to the Metric in `xeos:metric` it is a reading of |
| `skos:scopeNote` | the vendor's firing condition, formula or trap |
| `dct:source` | the page the mapping was read from, and the date |
| `xeo:mappingConfidence` | how the mapping is known |

## Nothing here is verified

Both research reports behind these files read documentation and ran no API call. So
`xeo:mappingConfidence` is `documented` or `inferred`, and never `verified`.

- **documented**: the vendor's own documentation states the field and its meaning, and the report
  read it there.
- **inferred**: the meaning is documented, but the field's internal name was confirmed only from a
  secondary source (a community thread, a third-party connector), or the role given to the field
  is the report's reading and not the vendor's statement.
- **verified**: checked against live API output. No mapping is yet.

Check a mapping against live output before a classifier is trained on it.

## What was left out

Only rows the reports mark documented were transcribed. The rest are named here so that their
absence is a statement and not an oversight.

- **HubSpot**: `hs_analytics_source_data_1` (to `referringPlatform`; inferred), `hs_lead_status`,
  `deal_currency_code`, `hs_is_closed`, and the deal probability, forecast category, ARR and
  closed-lost-reason properties (internal names unverified); the pipelines API stage metadata
  (probability, isClosed), which the report inventories and does not map; every traffic-source
  value except `AI_REFERRALS`, whose neutral channel the report does not state; the Analytics v2
  and Campaigns reporting fields (visits, contacts, sessionToContactRate, influencedContacts and
  others).
- **Google Search Console**: `dataState` (secondary source).
- **Peec**: `win_rate` ("win" is not defined in the documentation read); the Data Studio
  connector's field of the same name as the API's visibility, which is a count (noted on the API
  concept).
- **Profound**: `average_position` (the population it averages over is undocumented; inferred);
  `count` in the citations report; `dimensions`, `date_interval` and `category_id`, which fill no
  one slot.

Whole tools not yet transcribed. The reports carry draft mappings for:

- **CRM**: Salesforce, Pipedrive, Dynamics 365, Zoho CRM, Close, Attio. Freshsales, Copper and
  monday CRM were not read at all.
- **Metrics**: dbt MetricFlow, Cube, LookML, Malloy, OSI / Apache Ossie (the definition side: these
  map to the Metric's own properties), Matomo, HubSpot analytics.

## Sources and names

The reports give an exact page for some fields and a page group for the rest. Where only the group
is known, `dct:source` says so in words and invents no URL.

A concept is named `xeos:<scheme>-<field>`. Where the field name is not a legal local name
(`metrics[].expression`), the IRI uses a readable slug and `skos:notation` still holds the exact
string. A vendor may use one field name for two things in two reports (Profound's
`share_of_voice`); those are two concepts with the same notation, told apart by their IRIs and
scope notes.

## Vendor records in a graph: the label convention

A crosswalk says which field fills which slot. In a property graph the record those fields came
from is a node too, and it gets a **vendor label**: the vendor's name in capitals, an
underscore, and the record type as the vendor names it.

| Record | Label | Refers to |
|---|---|---|
| a HubSpot contact | `HUBSPOT_Contact` | `Person` |
| a HubSpot company | `HUBSPOT_Company` | `Organization` |
| a HubSpot deal | `HUBSPOT_Deal` | nothing: not a party |
| a Hyros lead | `HYROS_Lead` | `Person` |
| a SegMetrics visitor | `SEGMETRICS_Visitor` | `Person` |

- A record of a person or an organization has one `REFERS_TO` (`xeo:refersTo`) to the canonical
  `Person` or `Organization`, the core node that exists once per real party. Every system's copy
  of the same person points at the same node, the same way.
- A deal, a task or any other record that is not a party is a vendor-labelled node with no
  canonical counterpart. It links to the parties through the vendor's own associations.
- The neutral pipeline properties (`crmRecordRef`, `dealAmount`, `stageRef`, `firstTouchChannel`,
  ...) sit on the vendor-labelled node. The canonical node copies no vendor's fields.
- `REFERS_TO` is a derivation and carries `method`: `system-key:<key>` where the systems share a
  key, `email-match` or `name-match` where values were compared, `manual` where a person linked
  them; and `confidence` where the method gives one.
- Vendor labels are never XEO terms. They are the implementation's convention, like the files in
  this folder, and the validator does not check them.

```cypher
MERGE (p:Person {id: $personId})
MERGE (c:HUBSPOT_Contact {crmRecordRef: $ref})
MERGE (c)-[r:REFERS_TO]->(p)
SET r.method = 'email-match', r.confidence = 0.9
```

## Adding a tool

1. Copy `_template.ttl` to `<tool>.ttl`. A file whose name starts with an underscore is skipped by
   the tools, so the template itself is never loaded.
2. Declare one `skos:ConceptScheme` for the tool, with a label, a description and a dated source.
3. Add one concept per field. Use the vendor's exact field name as `skos:notation`. Point
   `xeo:fillsSlot` at an XEO property that already exists. If no slot fits, the field does not get
   mapped; open an issue about the slot instead of inventing one here.
4. Choose the match honestly. `exactMatch` only when the vendor's definition and XEO's are the
   same thing. A ratio with a different denominator is a `closeMatch`.
5. Set `xeo:mappingConfidence`. Use `verified` only after comparing against a real response.
6. Run `python tools/gen_schemes.py`, then `python tools/validate.py`. The validator checks every
   field above and fails on a missing one.
