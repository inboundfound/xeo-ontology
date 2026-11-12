# xeoontology.org update: deploy 0.6, then build the term map

For whoever updates xeoontology.org: a person, or an agent handed this file. It is
self-contained. Written 12 November 2026.

There are three parts, in order:

- **Part A. Deploy 0.6 now.** It's ready, already built on a site branch.
- **Part B. Build the term map.** Build it now on its own branch, and launch it with 0.7 (decision W2).
- **Part C. When 0.7 is released.** Tombstones, a frozen copy, and the launch.

## Where things stand

| Repo | State |
|---|---|
| `inboundfound/xeo-ontology` (public) | `main` has 0.6 (#3) and the first 0.7 pull request (#5: the modules). 0.7 is **not released**. The rest of it (deletions, core and sales, attribution) is still to come. |
| `inboundfound/site-weo-the-web-engine-optimization-ontology` (private, Astro 5) | The live site is 0.5. Branch `jamesmthornton/xeo-0.6` (commit `db17ac0`, local, not pushed) is 0.6, generated and built. |

**Two traps:**

1. **Don't generate the site from today's `main`.** `main` already has 0.7's new module files, but still says version 0.6.0. Generating from it now would publish 0.7's layout labelled 0.6.0. Generate from commit `2587695` (the last 0.6 commit on `main`) until 0.7 is released.
2. **The frozen 0.6.0 copy must also come from `2587695`, not `main`.** `docs/site-handoff-0.6.md` says "from `main`"; that was written before 0.7 started landing. This file corrects it.

All ontology commands below run from the ontology repo root and need `uv`. The site generator is `tools/gen_site.py` in the ontology repo (decision W3).

---

## Part A. Deploy 0.6

**A1. Tag the release.** Optional, but it gives `2587695` a name everything else can point at.

```
git tag -a v0.6.0 2587695 -m "XEO 0.6.0"
git push origin v0.6.0
```

**A2. Get a 0.6 checkout of the ontology** without disturbing your working copy:

```
git worktree add ../xeo-0.6.0 2587695      # or v0.6.0 after A1
```

**A3. The site.** The 0.6 files are already applied and built on the site repo's branch `jamesmthornton/xeo-0.6`. To rebuild them yourself, run this against the A2 checkout:

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --onto ../xeo-0.6.0
```

**A4. The frozen copy** (decision W5), from the same checkout:

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --onto ../xeo-0.6.0 --freeze
```

This writes `public/releases/0.6.0/`, and refuses to overwrite an existing copy. Commit it on the site branch.

**A5. Copy changes for the home page**, made by hand in the site repo. The repo's description no longer says "xEO family", and the site should follow:

| Where | Now | Change to |
|---|---|---|
| `src/pages/index.astro`, the `lede` | "A small, standards-grounded vocabulary for how engines … One graph model for the whole **xEO** family: SEO, GEO, AEO, and whatever letter comes next." | "XEO is a standards-grounded ontology for AI agents that support growth engineering teams. Core covers sites, pages, queries, crawls, observations and metrics. Add-on modules cover AI visibility, graph analysis, sales, client work, decisions and strategy. Every term states the kind of claim it makes and what it is grounded in." |
| `src/pages/index.astro`, `seo.title` | "XEO — the ontology for the xEO family" | "XEO — an ontology for growth engineering agents" |
| `src/pages/index.astro`, `seo.description` | "…vocabulary for how search, generative, answer and conversational engines see, cite and serve web content…" | "XEO is an open, standards-grounded ontology for AI agents that support growth engineering teams: sites, search, AI answers, metrics, sales and client work. v${VERSION}, CC BY 4.0." |
| `src/content/readme.md`, line 1 | "# XEO — the ontology for the xEO family" | Leave as is. It's a copy of the ontology README, whose title changes in a small ontology pull request (still to open). Copy the new title over when that merges. |

**A6. Build and deploy:** `npm ci && npm run build` in the site repo, then deploy as usual. The live site's commits are "Publish …" from SiteGen.

**A7. Check after deploy** (from `docs/site-handoff-0.6.md` §5):

1. `https://xeoontology.org/xeo#Person`, `#refersTo` and `#mappingConfidence` each scroll to their term.
2. `https://xeoontology.org/schemes#metric-ai_mention_rate` shows the AI mention rate.
3. On `/xeo`, typing `refersTo` in the search box shows that term.
4. The header reads v0.6.0, and `/schemes.json`, `/neo4j-profile.json` and `/releases/0.6.0/xeo-core.ttl` download.

**A8. Clean up:** `git worktree remove ../xeo-0.6.0` in the ontology repo.

0.6 deletes no published term, so it needs no tombstones.

---

## Part B. The term map

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
  {"id": "seo-agency",     "label": "SEO agency with a method",        "modules": ["core", "visibility", "analysis", "work", "decision", "strategy"]},
  {"id": "full-agency",    "label": "SEO, AEO and sales agency",       "modules": ["core", "visibility", "analysis", "work", "decision", "strategy", "sales", "attribution"]},
  {"id": "ai-agency",      "label": "AI-native agency",                "modules": ["core", "visibility", "analysis", "work", "decision", "strategy", "sales", "attribution", "experiments", "agentic-engineering"]},
  {"id": "online-seller",  "label": "Online seller (ecommerce, courses)", "modules": ["core", "attribution"]}
]
```

Some of these modules don't exist yet (`attribution`, `experiments`, `agentic-engineering`). A persona filter ignores module names the release doesn't have, so this file never needs to change when they arrive.

**Module names.** Strip the `xeo-` prefix for display. Order them as `xeo-release.json` lists them: core first, then the add-ons. Leave out `xeo-schemes` and `xeo-align`: one holds reference values and the other alignments, and neither declares terms a graph would carry.
- **For 0.6** that's core, visibility, engagement, decision, strategy, delivery, analysis, metrics.
- **For 0.7** it's core, visibility, analysis, sales, work, decision, strategy (attribution comes later).

The map must work for both releases with no code change.

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

1. With the 0.6 data, the grid shows 8 module rows. With the 0.7 data (generated from `main` into a scratch folder, not deployed) it shows 7. No code differs between the two.
2. `/xeo?module=sales&layer=observation` loads with both filters set, and the counts agree with the cards shown.
3. `/xeo#refersTo` opens and shows that card with its name visible below the sticky bar, even when the URL also has filter parameters.
4. With the persona "Online seller" selected, only core terms (and attribution terms, once they exist) are listed, and the other rows of the grid are dimmed.
5. At 400px wide, nothing scrolls the page sideways: the grid scrolls inside its own box, and the header fits. That header is the known 82px overflow; fix it here.
6. With JavaScript off, every term is still in the page.
7. `npm run build` passes, and every term count on the page matches `xeo-release.json`.

---

## Part C. When 0.7 is released

Not yet: 0.7 is released when its last pull request (attribution) merges and the modules say `0.7.0`. The ontology repo will then have `docs/site-handoff-0.7.md` with the exact lists. In outline:

- **Generate** from `main` (no `--onto`), then `--freeze` for `public/releases/0.7.0/`.
- **Remove three files from `public/`:** `xeo-engagement.ttl`, `xeo-delivery.ttl` and `xeo-metrics.ttl` no longer exist. Leave a short tombstone at each old address saying where its terms went: core, `xeo-sales.ttl`, or `xeo-work.ttl`.
- **Term tombstones,** "removed in 0.7, use X", for every term 0.7 deletes. The list is in `docs/site-handoff-0.6.md` §2, and the 0.7 handoff will confirm it.
- **`/xeo` search placeholder:** it suggests `websiteId`, which 0.7 deletes. Change it to `refersTo`.
- **Launch the map** (Part B), merged into the same deploy.
- **Copy the README** into `src/content/readme.md` again: the 0.7 README has the new module table.
