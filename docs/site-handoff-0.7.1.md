# Site handoff: XEO 0.7.1

For whoever updates xeoontology.org. Do the 0.7.0 handoff (`site-handoff-0.7.md`) first if the
site is not on 0.7.0 yet, then this. 0.7.1 adds terms, rewords some released ones, and removes
nothing.

## What changed for the site

- **One more module file:** `xeo-agentic.ttl` (agentic engineering). There are now eleven.
- **81 new terms, all marked draft:** 73 in `xeo-agentic.ttl`, 7 in `xeo-work.ttl` (`Spec`,
  `WorkItem`, `Deliverable` and their properties) and 1 in `xeo-core.ttl` (`artifactUri`).
  `InvocationConfig`, `usedConfig` and the six settings are in `xeo-agentic.ttl`, not in core.
- **A new status value, `draft`.** `xeo-terms.json` carries `"status": "draft"` on those terms,
  and `xeo-schemes.json` on eleven schemes.
- **Reworded descriptions of released terms**, which the term pages pick up from the generated
  JSON with no work: `Project`, `Campaign`, `Objective` and their properties (loosened: a
  project no longer has to be a client contract), `Practice`, `Recommendation`.
- **The visibility module's title** is now "XEO Visibility (AI answers: GEO and AEO)".
- **One more tombstone:** `epistemicLayer`, renamed `xeoLayer` in 0.7.0. `tombstones.json` now
  lists 15 terms. No term is removed in 0.7.1.
- **One more public file:** `shapes/profiles/agency-delivery.ttl`, an optional SHACL profile.
  `tools/gen_site.py` copies it to `public/shapes/profiles/`.

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
| Anywhere the site describes a Project as "the contract" or says a quota is required | "a bounded body of work, client or internal"; contract terms are optional |
| Wherever shapes are linked | add a line for the optional profile: "`/shapes/profiles/agency-delivery.ttl`: one agency's contract rules. Optional; a graph that fails it is still valid XEO." |

**4. The name.** It is written `XEO` in prose and `xeo` in prefixes, file names and code.
Search the site's source for the spelling with a lowercase x and capital EO ("xEO") and
replace each one: with `XEO` where it is the name, and with "SEO, GEO and AEO" or "AI answers"
where it stood for the family of disciplines. The repo itself now has none outside the site
handoffs, which quote it as the string to look for.

**5. Build and deploy** as for 0.7.0.

## Check after deploy

1. `https://xeoontology.org/xeo#AgentSession`, `#InvocationConfig` and `#Deliverable` each
   scroll to their term, and each shows the draft badge. `InvocationConfig` is listed under
   the agentic module.
2. `https://xeoontology.org/xeo-agentic.ttl` downloads.
3. On `/xeo`, a search for `EnforcementEvent` finds it, and the status filter set to `draft`
   lists only the 81 new terms.
4. The header reads v0.7.1. `/releases/0.7.1/xeo-core.ttl` downloads.
5. `/schemes#hookDecision-deny` shows the code.
6. `#Project` reads "A bounded body of work", and `#epistemicLayer` opens its tombstone.
7. `https://xeoontology.org/shapes/profiles/agency-delivery.ttl` downloads.
8. A search of the built site for "xEO" (case-sensitive) finds nothing.
