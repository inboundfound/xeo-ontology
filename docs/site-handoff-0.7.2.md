# Site handoff: XEO 0.7.2

For whoever updates xeoontology.org. This list is meant to be complete for 0.7.2: with the
0.7.0 and 0.7.1 handoffs done first (`site-handoff-0.7.md`, `site-handoff-0.7.1.md`), doing
everything below leaves the site matching the released ontology. 0.7.2 adds no term, removes
none and renames none.

## What changed for the site

- **The version.** Every module file, `schemes.json`, `neo4j-profile.json` and the shapes
  carry 0.7.2.
- **Five properties have wider endpoints.** Their term pages change by themselves from the
  generated JSON: the `domain` or `range` row goes, and an `expected on` or
  `expected to point at` row lists the classes.

  | Term | Row that goes | Row that appears |
  |---|---|---|
  | `addressableBy` | range: Tactic | expected to point at: Tactic, Intervention |
  | `recommends` | range: Tactic | expected to point at: Tactic, Intervention |
  | `tests` | range: Tactic | expected to point at: Tactic, Intervention |
  | `supersedes` | domain: Practice; range: Practice | expected on, and expected to point at: Practice, Recommendation, Spec, DiagnosticRun |
  | `appliesTo` | domain: Practice | expected on: Practice, Gap, Recommendation |

- **Nine descriptions are reworded**, also picked up from the generated JSON with no work:
  the five properties above, plus `measures`, `treats`, `Feedback` and `source`.
- **Two scheme definitions are reworded:** `authored` and `learned` in `practiceSource`. The
  schemes page picks them up from the generated `xeo-schemes.json`.
- **No new file, no new module, no new tombstone.** There are still eleven module files and
  `tombstones.json` still lists 15 terms.
- **Counts are unchanged:** 80 classes, 150 object properties, 239 datatype properties, 77
  schemes, 427 concepts, 81 draft terms.

## Steps

**1. Generate from `main`, and freeze 0.7.2:**

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

It writes the eleven module files and the data files to `public/`, the JSON to `src/lib/`,
and the frozen copy to `public/releases/0.7.2/`. The frozen copies of earlier releases are
left as they are.

**2. Copy, by hand.**

| Where | Change to |
|---|---|
| `src/content/readme.md` | Replace it with the ontology's `README.md` as of 0.7.2. The README's text did not change in 0.7.2, so this is a no-op if 0.7.1 was done. |
| Anywhere the site says a recommendation, a gap or an experiment points only at a tactic | "a tactic, or a category of work where no tactic under it is named" |
| Anywhere the site says a learned rule comes from feedback | "A rule promoted from an operator's feedback is authored. Learned means earned from experiments." |
| The changelog page, if the site keeps one | Add the 0.7.2 entry from `CHANGELOG.md` |

A search of the site's source for "drawn from", "learned" and "supersedes" finds the places
to read. There may be none: the term pages are generated.

**3. Build and deploy** as for 0.7.0.

## Check after deploy

1. The header reads v0.7.2. `/releases/0.7.2/xeo-decision.ttl` downloads, and
   `/releases/0.7.1/xeo-decision.ttl` still does.
2. `https://xeoontology.org/xeo#supersedes` shows no `domain` row, and lists Practice,
   Recommendation, Spec and DiagnosticRun as expected on and expected to point at.
3. `#recommends`, `#addressableBy` and `#tests` each list Tactic and Intervention.
4. `#appliesTo` lists Practice, Gap and Recommendation as expected on.
5. `#measures` reads "This edge says which target and nothing about pages", and `#treats`
   mentions a role and a basis.
6. `#Feedback` reads "A Practice promoted from a Feedback is authored".
7. `/schemes#practiceSource-authored` reads "or a rule an operator promoted from feedback".
8. The term count on `/xeo` is the same as for 0.7.1.
