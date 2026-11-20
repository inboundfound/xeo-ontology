# Research prompt: check the XEO design module against the design tools

A prompt for a research agent (or a person) to collect the vocabulary the main design tools and
the design-token standard use, and to check `xeo-design.ttl` (draft, 0.8) against it. Paste
everything below the line. The module, its schemes and its example are the input; the output is
one report that says, term by term, whether XEO's names and shapes hold up.

---

## The task

XEO is an open ontology (`https://xeoontology.org/xeo#`) for the work growth and web teams do.
Its draft design module, `xeo-design.ttl`, describes what a website is designed and built with
(a `DesignSystem` of `DesignToken`s, `DesignComponent`s, `DesignPattern`s, `PageTemplate`s and
`DesignAsset`s) and how a new design is proposed and decided (`DesignDirection`s, the existing
site's `DesignElement`s, `DesignConcept`s drawn under a direction, and the reviewer's
`DesignDecision`s). Read the module, its five draft schemes at the foot of `xeo-schemes.ttl`
(`tokenType`, `tokenTier`, `elementKind`, `assetKind`, `designVerdict`), its shapes at the foot
of `shapes/xeo-shapes.ttl`, and `examples/design-review.jsonld` before you start.

Collect, from each source below, the nouns and fields it uses for the same ideas, and say for
each whether XEO already has it, has something close, or lacks it. The aim is a module whose
terms a designer, a developer and an agent would recognise from the tools they already use,
without copying any one vendor's vocabulary into the ontology.

## Sources, in this order

Read primary documentation only: the standard itself, the vendor's developer and help docs, the
API reference. Note the URL and the date you read it for every claim. Where a page is behind a
login or you could not read it, say so; do not fill the gap from memory.

1. **W3C Design Tokens Community Group.** The Design Tokens Format Module (the latest published
   version, 2025.10 at the time of writing, and the editor's draft if it differs), and any
   companion modules it names (colour, and the resolver or theming module for sets, modes and
   themes). Collect: the token and group structure, every `$type` (simple and composite) and its
   value shape, `$description`, `$extensions`, `$deprecated`, aliases (`{group.token}` and
   `$ref`), group inheritance (`$extends`), `$root`, and how themes or modes are expressed.
2. **Figma.** Variables (variable collections, modes, variable types, scopes, aliasing,
   extended collections), styles (colour, text, effect, layout grid), components, component sets
   and variants, component properties (boolean, instance swap, text, variant, slot if present),
   instances and overrides, libraries, Dev Mode, Code Connect, and the names the REST API and the
   Plugin API use for each. Also what Figma calls a page, a frame, a section and a prototype.
3. **Claude's design features.** What Claude offers for design work as documented by Anthropic:
   artifacts and any design, design-system or slide artifact types, design-related skills in
   Claude Code, and connectors to Figma or Canva where they exist. Collect the nouns these use
   (design system, direction, variant, concept, review) and what each holds.
4. **Canva.** Brand Kit (brand colours, fonts, logos, brand voice), designs and their pages,
   elements, templates and brand templates, folders and assets; the Canva Connect API's
   resources (designs, assets, brand templates, autofill, exports) and the Apps SDK's terms.
5. **Adobe.** Spectrum (Adobe's design system: its token tiers, the `spectrum-tokens` naming,
   components and their variants and states), Adobe Express (brand kits, templates, the add-on
   SDK), Creative Cloud Libraries (colours, character styles, graphics), and Adobe XD's
   components, states and assets panel, noting XD's current support status.
6. **Also worth a pass, briefly:** WordPress `theme.json` (presets for colour, font size and
   spacing; block styles, patterns, templates and template parts), Material Design 3's token
   tiers (reference, system, component), Style Dictionary, Tokens Studio, Storybook (stories,
   args, controls), and Penpot. These show where design tokens and components meet code and a
   CMS, which is where XEO's `URL`, `PageTemplate` and `DesignComponent` meet.

## What to check, for each source

1. **Each XEO class and property.** Is there a term in the source for the same idea? Give the
   source's exact name and field, its meaning in one line, and the match: `exact`, `close` (say
   the difference), `broader`, `narrower`, or `none`.
2. **Each scheme's codes.** Does `tokenType` cover every token type the source has? Are
   `tokenTier`'s three tiers how the source tiers tokens? Are `elementKind`, `assetKind` and
   `designVerdict` complete and named as people in the field would name them?
3. **Modes and themes.** XEO stores a token with a value per mode as one `DesignToken` per mode
   with a `tokenMode`. Does that fit how Figma modes, the token format's theming module and
   `theme.json` style variations work, or should a token carry one value per mode on itself?
4. **Variants.** XEO makes a variant a component of its own that is a `variantOf` another.
   Does that fit Figma's component sets and variant properties, Spectrum's variants and states,
   and code libraries' props? Should a variant's properties (size, state, emphasis) be terms?
5. **Where the vendor's identifiers go.** List the stable identifiers each tool gives a token,
   component, style, design or asset (a Figma node id or component key, a Canva design id). XEO
   keeps these out of the ontology, in a mapping file per tool (`mappings/`, see
   `mappings/_template.ttl`). Draft the rows a `mappings/figma.ttl` and a `mappings/canva.ttl`
   would hold.
6. **The review half.** Do any of the tools model a design direction, a concept or mockup
   under one, or a reviewer's keep, replace or approve call (comments, approvals, branch
   reviews, Dev Mode statuses such as "ready for dev")? Name the terms and say whether
   `DesignDirection`, `DesignConcept` and `DesignDecision` fit them.
7. **The open questions the module lists.** For each, say what the sources suggest: rights to an
   asset (licence, credit, expiry); accessibility results (contrast, component checks);
   breakpoints and responsive rules; a CMS block as a kind of component; atomic-design levels as
   a scheme; a design file's pages and frames; a direction's rank within a proposal.

## What to return

One Markdown report, in this order:

1. **Summary**: up to ten lines. What holds, what should change, what is missing.
2. **Crosswalk table**: one row per XEO term (all 38), with a column per source giving the
   source's term and the match. Empty cell means the source has no such idea.
3. **Scheme check**: for each of the five schemes, codes to add, rename or drop, each with the
   source that supports it.
4. **Proposed changes to the module**: each as one line, with its kind (add a term, rename,
   widen, a new code, a new shape), the XEO layer a new term would carry (entity, episode,
   observation, derivation, interpretation or norm), the sources behind it, and how sure you
   are (`documented`, `inferred`, or `verified` against live output).
5. **Mapping-file drafts**: the rows for Figma and Canva, as in point 5 above.
6. **Questions for the maintainer**: only those the sources cannot settle.
7. **Sources**: every URL with the date read.

## Rules

- Primary sources only, cited inline. Mark anything you could not confirm as unconfirmed.
- Quote field and type names exactly as the source writes them, including case.
- Do not propose copying a vendor's whole vocabulary. XEO names an idea once and maps each tool
  onto it; a term earns its place when two or more sources share the idea.
- XEO's naming rule: a property named for what it says (`tokenValue`, not `value`), camelCase,
  no vendor names in term names.
- This report goes into a public repository. Use no client, person or project names; use
  `example.org` and invented names in any example.
