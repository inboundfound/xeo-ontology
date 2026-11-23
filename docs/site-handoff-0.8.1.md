# Site handoff: XEO 0.8.1

For whoever updates xeoontology.org. With the 0.8.0 handoff done first (`site-handoff-0.8.md`),
doing everything below leaves the site matching the released ontology. 0.8.1 adds no term and
no file: it adds each label's key to the generated profile.

## What changed for the site

- **`neo4j-profile.json` has a `key` or a `keyFrom` on 56 of 102 labels**, and
  `conventions.surrogateKey`. The Neo4j profile page (`docs/neo4j-profile.md`) has a Key column
  in its label table and one new convention bullet.
- **No term is added, removed or changed**, no scheme, no module file. No new tombstone.
  `tombstones.json` still lists 15 terms.
- **Counts are as in 0.8.0:** 102 classes, 192 object properties, 270 datatype properties, 85
  schemes, 485 concepts, 176 draft terms.

## Steps

**1. Generate from `main` at the release commit, and freeze 0.8.1:**

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

Or run it with no path: everything is written to `site-bundle/` in the ontology checkout. The
frozen copy goes to `public/releases/0.8.1/`; earlier frozen copies are left as they are.

**2. Copy, by hand.**

| Where | Change to |
|---|---|
| `src/content/readme.md` | Replace it with the ontology's `README.md` as of 0.8.1. Its text did not change, so this is a no-op if 0.8.0 was done. |
| The Neo4j profile page, if the site shows it | Replace it with `docs/neo4j-profile.md` |
| The changelog page, if the site keeps one | Add the 0.8.1 entry from `CHANGELOG.md` |

**3. Build and deploy** as for 0.7.0.

## Check after deploy

1. The header reads v0.8.1. `/releases/0.8.1/neo4j-profile.json` downloads, and
   `/releases/0.8.0/neo4j-profile.json` still does.
2. `/neo4j-profile.json` has `"surrogateKey": "id"` under `conventions`, `labels.Website.key`
   is `[["id"], ["origin"]]` and `labels.SearchEngine.keyFrom` is `"Engine"`.
3. The term count on `/xeo` is the same as for 0.8.0.
