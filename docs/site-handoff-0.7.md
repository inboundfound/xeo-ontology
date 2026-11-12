# Site handoff: XEO 0.7.0

For whoever updates xeoontology.org: a person, or an agent handed this file. It is
self-contained. Written 12 November 2026, for the 0.7.0 release.

The live site is still 0.5. 0.6 and 0.7 go out together. There are three parts, in order:

- **Part A. Freeze 0.6.0.** A frozen copy of the 0.6 release, cut from its commit (decision W5).
- **Part B. Deploy 0.7.0.** Generate from `main`; the tombstones; the home-page copy; checks.
- **Part C. The term map.** It launches with 0.7 (decision W2), so it ships in the same deploy if it's ready, or in the next one.

## Where things stand

| Repo | State |
|---|---|
| `inboundfound/xeo-ontology` (public) | `main` holds 0.7.0 once its pull request merges. 0.6.0's last commit is `2587695`. |
| `inboundfound/site-weo-the-web-engine-optimization-ontology` (private, Astro 5) | Live: 0.5. Branch `jamesmthornton/xeo-0.6` (commit `db17ac0`, local, not pushed) has 0.6 applied, plus the generator-driven version and counts. Start from that branch. |

All ontology commands run from the ontology repo root and need `uv`. The site generator is
`tools/gen_site.py` in the ontology repo (decision W3).

---

## Part A. Freeze 0.6.0

**A1. Tag 0.6.0** (optional, but gives the commit a name):

```
git tag -a v0.6.0 2587695 -m "XEO 0.6.0"
git push origin v0.6.0
```

**A2. Check out 0.6** beside your working copy, without disturbing it:

```
git worktree add ../xeo-0.6.0 2587695
```

**A3. Freeze it** into the site checkout:

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --onto ../xeo-0.6.0 --no-copy --freeze
```

This writes `public/releases/0.6.0/`. It also rewrites `src/lib/*.json` with the 0.6 data, which Part B overwrites. Then remove the checkout with `git worktree remove ../xeo-0.6.0`.

## Part B. Deploy 0.7.0

**B1. Generate from `main`, and freeze 0.7.0:**

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

What this writes:

- **`public/`:** the ten module files, the data files and `mappings/`.
- **Four removed files:** `xeo-engagement.ttl`, `xeo-delivery.ttl`, `xeo-metrics.ttl` and `xeo-strategy.ttl` are each overwritten with a three-line comment saying where their terms went, so the old URLs still answer.
- **`src/lib/`:** `xeo-terms.json`, `xeo-schemes.json`, `xeo-release.json`, and the new `xeo-tombstones.json`.
- **`public/releases/0.7.0/`:** the frozen copy.

**B2. Show the term tombstones on `/xeo`.** `src/lib/xeo-tombstones.json` lists every removed term:

```json
{"terms": [{"term": "lift", "removedIn": "0.7.0", "useInstead": ["absoluteChange", "relativeChange"]}, ...],
 "files": [{"file": "xeo-engagement.ttl", "removedIn": "0.7.0", "note": "..."}, ...]}
```

On `/xeo`, render each removed term after the live terms, as a short card:
- `id` equal to the term, so `/xeo#lift` lands on it;
- the text "Removed in 0.7.0. Use …";
- each `useInstead` name linked to its card, and the `note` if there is one.

These cards are not counted in the term totals, and the filters hide them unless a "show removed" toggle is on. A `#term` address that matches a tombstone opens it, as for a live term. There are 14 for 0.7.

`websiteId` is **not** removed: it stays, optional. The 0.6 handoff listed it as a tombstone; ignore that line. `Term` also stays.

**B3. Home-page copy, by hand.** The repo's description no longer says "xEO family", and the site follows:

| Where | Change to |
|---|---|
| `src/pages/index.astro`, `lede` | "XEO is a standards-grounded ontology for AI agents that support growth engineering teams. Core covers sites, pages, queries, crawls, observations and metrics. Add-on modules cover AI visibility, graph analysis, sales, attribution, client work and decisions. Every term states the kind of claim it makes and what it is grounded in." |
| `src/pages/index.astro`, `seo.title` | "XEO — an ontology for growth engineering agents" |
| `src/pages/index.astro`, `seo.description` | "XEO is an open, standards-grounded ontology for AI agents that support growth engineering teams: sites, search, AI answers, metrics, sales, attribution and client work. v${VERSION}, CC BY 4.0." |
| `src/content/readme.md` | Replace it with the ontology's `README.md` as of 0.7.0. It has the new title, module table and stack figure. |
| `src/pages/xeo.astro`, the search placeholder | Change "gap, citation, websiteId…" to "gap, citation, refersTo…". |

**B4. Build and deploy:** `npm ci && npm run build`, then deploy as usual (the live site's commits are "Publish …" from SiteGen).

**B5. Check after deploy:**

1. `https://xeoontology.org/xeo#Consent`, `#AttributionModel` and `#targetMetric` each scroll to their term.
2. `https://xeoontology.org/xeo#lift` shows its tombstone, naming `absoluteChange` and `relativeChange`.
3. `https://xeoontology.org/xeo-strategy.ttl` returns the three-line note.
4. On `/xeo`, a search for `Touchpoint` finds it.
5. The header reads v0.7.0. `/releases/0.6.0/xeo-core.ttl` and `/releases/0.7.0/xeo-core.ttl` both download.
6. `/schemes#metric-roas` shows ROAS.

---

## Part C. The term map

### What it is

The old `WEO Ontology Map.html` (v0.4, built by hand) showed every term placed on two axes: **which kind of claim it makes** (its layer) and **which module holds it**. Clicking a layer, a module or a cell filtered everything below it. Its idea was right. Its data, its module list and its WEO wording are out of date.

The map rebuilds that idea on the live site, from the generated data, so it can't drift. It is decisions W1 and W4:

- **W1:** search and filters replace the plain term list at `/xeo`, and the module picture goes on the home page.
- **W4:** filters for layer, module, kind, status and persona. A filter by source tool waits until the mappings are verified.

### Where

- **`/xeo` becomes the map,** with three sections stacked on one page (detail below):
  1. the layer stack;
  2. the module × layer grid;
  3. the filtered term list.

  The current `/xeo` already has search plus module and layer filters (`src/pages/xeo.astro`). Extend that page; don't replace it. Every term's address (`/xeo#Person`) must keep working, because the ontology's IRIs resolve there.
- **The home page gets the module picture:** core in the middle, the add-ons around it. Each module links to `/xeo?module=<name>`.

### Data: all of it is generated

Hand-keep nothing about terms. The site already gets these from `tools/gen_site.py`:

| File | What the map reads from it |
|---|---|
| `src/lib/xeo-terms.json` | `groups[]`: Classes, Object properties, Datatype properties, Annotation properties, Individuals, Modules. Each term has `id`, `kind`, and `fields` as `[name, value]` pairs: `label`, `module` (e.g. `xeo-sales`), `layer`, `status` (`extension`, `deprecated` or both, joined by " · "), `domain`, `expected on`, `range`, `expected to point at`, `subclass of`, `subproperty of`, `closeMatch`, `seeAlso`, `grounded in`, `canonical store`, `description`. A Modules entry also has `version` and `creator`. |
| `src/lib/xeo-release.json` | `version`, `modules` (the file list, core first), `mappings` (the vendor mapping files), the term and scheme counts |
| `src/lib/xeo-schemes.json` | The `xeoLayer` scheme: the six layers, each with a label and a definition. Use these for the layer glosses rather than writing new ones. |

One file is the site's own, because it's a product choice and not part of the ontology:

**`src/lib/personas.json`** (proposed: Jim to confirm the module lists). This is the T1 decision's six personas, each mapped to the modules it loads:

```json
[
  {"id": "site-seo",       "label": "Site owner doing SEO",            "modules": ["core", "analysis"]},
  {"id": "site-seo-aeo",   "label": "Site owner doing SEO and AEO",    "modules": ["core", "visibility", "analysis"]},
  {"id": "seo-agency",     "label": "SEO agency with a method",        "modules": ["core", "visibility", "analysis", "work", "decision"]},
  {"id": "full-agency",    "label": "SEO, AEO and sales agency",       "modules": ["core", "visibility", "analysis", "work", "decision", "sales", "attribution"]},
  {"id": "ai-agency",      "label": "AI-native agency",                "modules": ["core", "visibility", "analysis", "work", "decision", "sales", "attribution", "experiments", "agentic-engineering"]},
  {"id": "online-seller",  "label": "Online seller (ecommerce, courses)", "modules": ["core", "attribution"]}
]
```

Some of these modules don't exist yet (`experiments`, `agentic-engineering`). A persona filter ignores module names the release doesn't have, so this file never needs to change when they arrive.

**Module names.** Strip the `xeo-` prefix for display. Order them as `xeo-release.json` lists them: core first, then the add-ons. Leave out `xeo-schemes` and `xeo-align`: one holds reference values and the other alignments, and neither declares terms a graph would carry.
- **For 0.7** that's core, visibility, analysis, sales, attribution, attribution-sales, work, decision. Show `attribution-sales` as a small note under attribution ("bridge to sales"), not as a row of its own.

Read the list from the data, so a later release's modules (experiments, agentic engineering) appear with no code change.

### Section 1: the layer stack

Six bands, bottom to top: entity, episode, observation, derivation, interpretation, norm. Each band shows:
- its name;
- its one-line definition from the `xeoLayer` scheme;
- how many terms it holds under the current filters.

Clicking a band sets the layer filter; clicking it again clears it. This is the site's existing Stratum Column, drawn large. Keep the site's six layer colours (`--tier-entity` … `--tier-norm` in `src/styles/global.css`).

### Section 2: the module × layer grid

- **Shape:** rows are modules, in release order; columns are the six layers; each cell shows its term count.
- **Clicking:** a cell sets both the module and the layer filter. A row header sets the module, a column header sets the layer.
- **Empty cells** show `·` and can't be clicked.
- **Current selection:** the cell that matches the filters is outlined.
- **Persona filter:** when one is set, the rows outside that persona's modules are dimmed, not hidden, so the reader sees what they'd be leaving out.

### Section 3: the term list

- **Filters,** all combined (AND), each a single choice with an "all" option:
  - search (label, id, description);
  - layer;
  - module;
  - kind (class, object property, datatype property, annotation property, individual);
  - status (core, extension, deprecated);
  - persona.

  Each option shows its count under the other filters, e.g. `sales (31)`. A **Clear all** link resets everything.
- **Each term card shows:**
  - its label;
  - its `xeo:` id, in mono;
  - badges for layer, module, kind and any status;
  - the first sentence of its description.

  Opening a card shows every other field: domain, range, the "expected" lists, subclass or subproperty, grounded in, canonical store, seeAlso, and the full description. Names of other terms inside those fields link to their cards.
- **Filter state lives in the URL query** (`/xeo?module=sales&layer=observation&persona=online-seller&q=deal`), so a filtered view can be shared. The page reads the query on load, and updates it with `history.replaceState` when a filter changes. Browser storage is optional and only for convenience.
- **A `#term` address always wins.** Clear the filters, open that card, scroll to it and flash it, as `/xeo` does today. Also fix the known bug while you're there: the sticky filter bar covers the term's name. Give cards `scroll-margin-top` equal to the bar's height.
- **No JavaScript:** the full list still renders in the HTML, as it does today.

### Home page: the module picture

- **Layout:** core as one wide band, with the add-ons as smaller blocks around or above it, each showing its name, a one-line description and its term count.
- **Descriptions:** take each one from the module's own `dct:description`, which is the "Modules" group in `xeo-terms.json`. Trim it to its first sentence.
- **Links:** each block goes to `/xeo?module=<name>`.
- **One line under it:** "Every module needs only core. Load core and the add-ons you use."

Don't draw it as a dependency ladder or a stack of floors: since 0.7 the add-ons don't depend on each other (decision C1). The plan of record keeps the "stack" drawing only as a picture of how an agency typically grows into XEO.

### Optional section: vendor mappings

A short panel listing `xeo-release.json`'s `mappings` (one file per tool: HubSpot CRM, Search Console, GA4, Peec, Profound), each linking to its file under `/mappings/`, with a note that none is verified against live output yet. This replaces the old map's "The seam" section. A filter by source tool waits until the mappings are verified (W4).

### What not to carry over from the old map

- WEO, `weo:`, and "xEO family" wording anywhere.
- The "Gaps" list, which was v0.4 plans, now done or superseded.
- The phrase "epistemic". The layer is called `xeoLayer` since 0.7, and the plan of record calls "epistemic" jargon.
- The sentence about modules being "a separation of epistemic powers", and any figure that implies a dependency ladder.
- The five-tier "judgment" wording in the site's `DESIGN.md`. It predates the six layers: interpretation and norm are separate. Keep `DESIGN.md`'s visual system (paper and ink, hairlines, mono identifiers, the Stratum Column), but with six layers.

### Done when

1. With the 0.7 data, the grid shows 7 module rows (attribution-sales as a note under attribution). Generating the 0.6 data into a scratch folder gives 8 rows from the same code.
2. `/xeo?module=sales&layer=observation` loads with both filters set, and the counts agree with the cards shown.
3. `/xeo#refersTo` opens and shows that card with its name visible below the sticky bar, even when the URL also has filter parameters.
4. With the persona "Online seller" selected, only core and attribution terms are listed, and the other rows of the grid are dimmed.
5. At 400px wide, nothing scrolls the page sideways: the grid scrolls inside its own box, and the header fits. That header is the known 82px overflow; fix it here.
6. With JavaScript off, every term is still in the page.
7. `npm run build` passes, and every term count on the page matches `xeo-release.json`.

---
