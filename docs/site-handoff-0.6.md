# Site handoff: XEO 0.6.0

For whoever deploys xeoontology.org. The files are already applied and built on the site
repo's branch **`jamesmthornton/xeo-0.6`**, commit **`db17ac0`** (on top of `dd8c8d3`, which
first moved the site to 0.6). That branch is committed locally and not pushed.

**Merge the ontology's 0.6 pull request before you deploy.** The site's copy of the README
links to `CHANGELOG.md`, `docs/neo4j-profile.md` and `mappings/` on GitHub `main`; until the
PR merges, those links show 0.5.

The site files come from `tools/gen_site.py` in this repo (decision W3). From the ontology root:

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology
```

Without a path it writes the same layout into `site-bundle/` here (git-ignored), to copy over
a site checkout by hand. Then `npm run build` in the site repo. The site's older
`tools/sync_from_ontology.py` produces the same output and is kept.

## 1. Generated files, and where each goes

All paths are in the site repo. Every file below is written by `gen_site.py`; none is edited
by hand.

**Copied as-is into `public/`** (served at the same path on the site):

| Site path | From the ontology | Changed since `dd8c8d3` |
|---|---|---|
| `public/xeo-core.ttl` | `xeo-core.ttl` | yes: `Person`, `Organization`, `refersTo`, `mappingConfidence` |
| `public/xeo-visibility.ttl` | `xeo-visibility.ttl` | yes |
| `public/xeo-engagement.ttl` | `xeo-engagement.ttl` | yes: `CrmRecord` removed |
| `public/xeo-delivery.ttl` | `xeo-delivery.ttl` | yes: `Organization` moved to core |
| `public/xeo-metrics.ttl` | `xeo-metrics.ttl` | yes |
| `public/xeo-schemes.ttl` | `xeo-schemes.ttl` | yes: AI rate codes, D1 |
| `public/xeo-align.ttl` | `xeo-align.ttl` | yes |
| `public/xeo-decision.ttl`, `xeo-strategy.ttl`, `xeo-analysis.ttl` | same names | no |
| `public/schemes.json` | `schemes.json` | yes |
| `public/context.jsonld` | `context.jsonld` | yes |
| `public/context.neo4j.jsonld` | `context.neo4j.jsonld` | yes |
| `public/neo4j-profile.json` | `neo4j-profile.json` | yes |
| `public/schema.cypher` | `schema.cypher` | yes |
| `public/shapes/xeo-shapes.ttl` | `shapes/xeo-shapes.ttl` | no |
| `public/mappings/README.md`, `peec.ttl`, `profound.ttl` | `mappings/` | yes |
| `public/mappings/ga4.ttl`, `gsc.ttl`, `hubspot-crm.ttl` | `mappings/` | no |
| `public/LICENSE` | `LICENSE` | no |

**Generated into `src/lib/`** (read at build time, not served):

| Site path | Drives | Changed since `dd8c8d3` |
|---|---|---|
| `src/lib/xeo-terms.json` | `/xeo` | yes: 333 terms (`refersTo` added, `CrmRecord` gone) |
| `src/lib/xeo-schemes.json` | `/schemes` | yes: 50 schemes, 282 concepts |
| `src/lib/xeo-release.json` | every count and the version on every page | yes: 333 terms, 114 object properties |

**Edited by hand, once:** `src/content/readme.md` took the README changes since `cce79c1`
(already in `db17ac0`). See part 4.

## 2. Tombstones

**None for 0.6.** 0.6 deletes no published term. (`CrmRecord` and the unprefixed AI rate
codes existed only on the 0.6 branch and were never published, so nobody holds their
addresses.)

What 0.7 will need, each as "removed in 0.7, use X" at its old address:

| Address | Kind | Use instead (per the 0.7 plan) |
|---|---|---|
| `/xeo#lift` | property | `absoluteChange`, `relativeChange` |
| `/xeo#direction` | property | `betterDirection`, on the Metric |
| `/xeo#Informational`, `#Navigational`, `#CommercialInvestigation`, `#Transactional` | individuals | the `xeos:searchIntent` concepts (`/schemes#searchIntent`) |
| `/xeo#CallToAction`, `#LeadCaptureForm`, `#GatedAsset` | classes | `conversionPointType`: `cta`, `lead_form`, `gated_asset` |
| `/xeo#campaignInfluenceShare` | property | the attribution module's credit share; confirm the name in the 0.7 CHANGELOG |
| `/xeo#valuePeriod` and `/schemes#valuePeriod` (with its concepts) | property, scheme | `billingInterval` with `billingIntervalCount` (D3) |
| `/xeo#Term` | class | `SearchQuery`, once it lands |
| `/xeo#GenerativeEngine`, `#ConversationalAgent` | classes | `GenerativeOverview` or `AnswerEngine` (C3) |
| `/xeo#websiteId` | property | moves to the kit's profile; no XEO replacement |

`modelVersion` is **redefined, not deleted** (it becomes the dated build of a `Model`), so it
needs no tombstone; its entry on `/xeo` changes in place.

## 3. Frozen release copy

Proposed: `/releases/0.6.0/`, i.e. `public/releases/0.6.0/` in the site repo, holding the ten
module files (`xeo-*.ttl`), `schemes.json`, `context.jsonld` and `neo4j-profile.json`, exactly
as released. A frozen copy is never rewritten; the live root files move on with each release.

Create it after the 0.6 PR merges, from `main`:

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

`--freeze` writes `public/releases/<owl:versionInfo>/` and refuses to overwrite an existing
one (`--force` overrides). It is not in `db17ac0`, because the copy should be cut from the
merged release, not the branch. Nothing links to `/releases/` yet; a line on `/about` or the
home page ("Earlier releases: 0.6.0") is optional.

## 4. Copy changes

None to type by hand: since `dd8c8d3` the version, module count, term counts, scheme and
concept counts are read from `src/lib/xeo-release.json`. What the pages now say:

- Version **0.6.0** (was 0.5.0 on the live site).
- **333 terms**: 51 classes, 114 object properties, 147 datatype properties, 8 annotation
  properties, 4 individuals, 9 module records. **50 schemes, 282 concepts.** 10 modules.
- `/xeo` lists the new data files (`neo4j-profile.json`, `context.neo4j.jsonld`,
  `shapes/xeo-shapes.ttl`) beside `context.jsonld`, `schemes.json`, `schema.cypher`, and shows
  an extension or deprecated badge beside the layer badge.
- The rendered README (`src/content/readme.md`): `Person` and `Organization` are in core
  (the module table and the strata diagram); delivery no longer lists `Organization`; the
  0.6 slot row reads "the method, party and feedback slots"; deprecation now reads "Until 1.0,
  deprecated terms may be removed in the next release. From 1.0, nothing is removed."

For 0.7: the `/xeo` search placeholder suggests `websiteId`, which 0.7 deletes. Change it then.

## 5. After deploy, check

1. These resolve and scroll to the term: `https://xeoontology.org/xeo#Person`,
   `https://xeoontology.org/xeo#mappingConfidence`, `https://xeoontology.org/xeo#refersTo`.
   `https://xeoontology.org/schemes#metric-ai_mention_rate` shows the AI mention rate.
2. Tombstone: none in 0.6, so nothing to check. (`/xeo#CrmRecord` was never published and
   correctly lands at the top of `/xeo`.)
3. On `/xeo`, type `refersTo` in the search box: the `refersTo` card shows. `Person` works too.
4. The header reads v0.6.0 and "Ontology — 333 terms"; `https://xeoontology.org/schemes.json`
   and `https://xeoontology.org/neo4j-profile.json` download.

Already true before this release, and not fixed here: at 400px wide the header row is 82px
wider than the screen (the GitHub link and theme toggle), and the sticky filter bar on `/xeo`
covers the name of a term reached by its address (the card itself is in view).
