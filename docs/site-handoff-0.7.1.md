# Site handoff: XEO 0.7.1

For whoever updates xeoontology.org. Short, because 0.7.1 only adds: do the 0.7.0 handoff
(`site-handoff-0.7.md`) first if the site is not on 0.7.0 yet, then this.

## What changed for the site

- **One more module file:** `xeo-agentic.ttl` (agentic engineering). There are now eleven.
- **79 new terms, all marked draft:** 63 in `xeo-agentic.ttl`, 9 in `xeo-core.ttl`
  (`InvocationConfig`, `usedConfig`, its six settings, `artifactUri`) and 7 in `xeo-work.ttl`
  (`Spec`, `WorkItem`, `Deliverable` and their properties).
- **A new status value, `draft`.** `xeo-terms.json` carries `"status": "draft"` on those terms,
  and `xeo-schemes.json` on eleven schemes.
- **No removals.** `tombstones.json` is unchanged.

## Steps

**1. Generate from `main`, and freeze 0.7.1:**

```
uv run --no-project --python 3.12 --with rdflib \
    python tools/gen_site.py /path/to/site-xeoontology --freeze
```

It writes the eleven module files and the data files to `public/`, the JSON to `src/lib/`,
and the frozen copy to `public/releases/0.7.1/`.

**2. Show the draft mark on `/xeo`.** Where a term's `status` is `draft`, show a "draft" badge
beside its layer, as for `extension`. Add `draft` to the status filter. One line of copy under
the filters: "A draft term belongs to a module still being written and may change or be
removed."

**3. Copy, by hand.**

| Where | Change to |
|---|---|
| Home page, the sentence listing add-on modules | add "and, as a draft, the agents that do the work" |
| `src/content/readme.md` | Replace it with the ontology's `README.md` as of 0.7.1 |

**4. Build and deploy** as for 0.7.0.

## Check after deploy

1. `https://xeoontology.org/xeo#AgentSession`, `#InvocationConfig` and `#Deliverable` each
   scroll to their term, and each shows the draft badge.
2. `https://xeoontology.org/xeo-agentic.ttl` downloads.
3. On `/xeo`, a search for `EnforcementEvent` finds it, and the status filter set to `draft`
   lists only the new terms.
4. The header reads v0.7.1. `/releases/0.7.1/xeo-core.ttl` downloads.
5. `/schemes#hookDecision-deny` shows the code.
