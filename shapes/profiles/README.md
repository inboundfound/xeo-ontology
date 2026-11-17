# Optional profiles

`shapes/xeo-shapes.ttl` checks only what XEO says is true of every graph. A profile is a second
SHACL file that checks one team's operating rules on top of that. **Nothing in the ontology
depends on a profile, and a graph that fails one is still valid XEO.** Load a profile only if
its rules are your rules.

| File | Whose rules | What it requires |
|---|---|---|
| `agency-delivery.ttl` | An agency whose every project is a client contract (lifted from Inbound Found's implementations) | A `Project` has one `engagementType` and one `interventionQuota`, and is the `hasProject` of exactly one `Website`. A retainer has a `cadence` and no `durationDays`; a one-off the reverse. A `Campaign` has exactly one `aboutTopic` and one `hasObjective`. An `Objective` has a `resultsWindowDays`, at least one target, and exactly one target with `isPrimary` true. |

Until 0.7.1 the rules in `agency-delivery.ttl` were written into the descriptions of `Project`,
`Campaign` and `Objective`, as if they were what those terms mean. They are now optional there
and enforceable here. See the note at the foot of `xeo-work.ttl`.

## Use one

```
pyshacl -s shapes/xeo-shapes.ttl -s shapes/profiles/agency-delivery.ttl your-data.ttl
```

## Add one

A profile is `shapes/profiles/<name>.ttl`, with an `owl:Ontology` header carrying the release's
`owl:versionInfo`, and two folders of test data:

- `examples/profiles/<name>/*.jsonld`: data that conforms to the profile.
- `examples/profiles/<name>/invalid/*.jsonld`: data that breaks it, each node naming the shape
  it breaks (`expect`), as in `examples/invalid/`.

`tools/validate.py` fails if a profile does not parse, names a term XEO does not declare, has a
shape with no failing case, or disagrees with its test data. A profile may only constrain terms
the ontology declares; it may not declare terms of its own.
