# Site handoff: XEO 0.8.0

For whoever updates xeoontology.org. This list is meant to be complete for 0.8.0: with the
0.7.0, 0.7.1 and 0.7.2 handoffs done first (`site-handoff-0.7.md`, `site-handoff-0.7.1.md`,
`site-handoff-0.7.2.md`), doing everything below leaves the site matching the released
ontology. 0.8.0 adds three draft modules, widens one released property and removes nothing.

## What changed for the site

- **Three more module files:** `xeo-experiments.ttl` (experiments), `xeo-knowledge.ttl`
  (company knowledge) and `xeo-design.ttl` (design and web development). There are now
  fourteen.
- **93 new terms, all marked draft:** 42 in experiments, 13 in knowledge, 38 in design. They
  show the draft badge that 0.7.1 added, from `"status": "draft"` in `xeo-terms.json`.
- **Eight new schemes, all draft:** `graderKind`, `failureClass`, `claimVerdict`
  (experiments) and `tokenType`, `tokenTier`, `elementKind`, `assetKind`, `designVerdict`
  (design). `tokenType`'s codes are camelCase (`fontFamily`, `cubicBezier`) because they are
  the W3C Design Tokens Format's own type names; show them as they are.
- **One widened property:** `owns` (core) is expected to point at a Website, a Brand or a
  Project. Its term page picks this up from the generated JSON.
- **Reworded descriptions:** `owns` and `hasProject`, and every description that lists where a
  shared property may sit (`artifactUri`, `statement`). Picked up from the generated JSON.
- **New example files:** `examples/experiment-arms.jsonld`, `examples/company-knowledge.jsonld`
  and `examples/design-review.jsonld`, if the site links the examples.
- **No new tombstone.** `tombstones.json` still lists 15 terms.
- **Counts:** 102 classes, 192 object properties, 268 datatype properties, 85 schemes, 484
  concepts, 174 draft terms. The pages read these from `xeo-release.json`; nothing is typed.

## Steps

**1. Generate from `main` at the release commit, and freeze 0.8.0:**

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

Or, without a site checkout, run it with no path: everything is written to `site-bundle/` in
the ontology checkout, laid out as the site lays it out. It writes the fourteen module files
and the data files to `public/`, the JSON to `src/lib/`, and the frozen copy to
`public/releases/0.8.0/`. The frozen copies of earlier releases are left as they are.

**2. List the three modules wherever the site lists modules.** One line each:

| Module | Line |
|---|---|
| experiments | "How a test is designed and read: arms, trials, benchmarks, claims and their checks, lessons. Draft." |
| knowledge | "A company's own meetings and what was agreed in them, as pointers: recordings, transcripts, summaries, action items, membership. Draft." |
| design | "What a site is designed and built with (design systems, tokens, components, patterns, templates, assets) and how a new design is proposed and decided (directions, concepts, review decisions). Draft." |

**3. Copy, by hand.**

| Where | Change to |
|---|---|
| Home page, the sentence listing add-on modules | add "and, as drafts, experiments, company knowledge and design" |
| `src/content/readme.md` | Replace it with the ontology's `README.md` as of 0.8.0 |
| The changelog page, if the site keeps one | Add the 0.8.0 entry from `CHANGELOG.md` |

**4. Build and deploy** as for 0.7.0.

## Check after deploy

1. The header reads v0.8.0. `/releases/0.8.0/xeo-design.ttl` downloads, and
   `/releases/0.7.2/xeo-decision.ttl` still does.
2. `https://xeoontology.org/xeo-experiments.ttl`, `/xeo-knowledge.ttl` and `/xeo-design.ttl`
   download.
3. `https://xeoontology.org/xeo#DesignToken`, `#DesignDecision`, `#Meeting` and `#Trial` each
   scroll to their term, each with the draft badge, each under its own module.
4. On `/xeo`, the status filter set to `draft` lists 174 terms.
5. `/schemes#tokenType-fontFamily` and `/schemes#designVerdict-replace` show their codes.
6. `#owns` lists Website, Brand and Project as expected to point at.
7. The term count on `/xeo` is 93 more than for 0.7.2.
