# Research results: the XEO design module against the design tools

The answer to `docs/design/research-prompt.md` for `xeo-design.ttl` at 0.8.0 (draft). Every
source was read on **2026-11-20**. The work was done by an AI agent reading primary
documentation, and no API was called, so nothing here is `verified`. Each claim carries a source
key such as [D1] or [F4], and §7 lists every key with its URL. A claim marked *(summary)* was
seen only in a search engine's summary of the page, because the page itself could not be
fetched. Read it as unconfirmed.

## 1. Summary

1. **Most of the module holds up.** `DesignSystem`, `DesignToken`, `DesignComponent`, `aliasOf`,
   `tokenType` and `tokenMode` each have an exact or close counterpart in at least three sources.
   `tokenType`'s 13 format codes match the published 2025.10 type list exactly [D5].
2. **One token node per mode is correct.** The format's Resolver Module 2025.10 keeps each
   context (light, dark) as its own set of files, merged by path [D3]. Adobe Spectrum's new design
   data keeps one row per mode, tied together by a shared `conceptId` [A3]. Figma keeps all modes
   on one variable, `valuesByMode` [F4], and a loader can split that.
3. **Fixed in place:** `tokenValue`'s examples were wrong for 2025.10. A colour, a dimension and
   a duration are JSON objects there [D1, D2]. Also fixed: `tokenTier`'s list of what other
   systems call their tiers, plus alternative labels on its codes; `aliasOf` now covers `$ref`;
   `tokenType` now states how a type is inherited; `variantOf` now says how Figma's component
   sets map. One code was added: `designVerdict` `revise` (Figma's "Request changes" [F14],
   Canva's "Needs changes" [V17]).
4. **Missing, and shared by two or more sources (proposed, not made):**
   - variant properties: Figma, Penpot, Spectrum, Storybook
   - a token mode on more than one axis: the Resolver, Spectrum, Tokens Studio, Penpot
   - a join key for a tool's own identifiers: every tool
   - a token's name in code: Figma `codeSyntax`, WordPress CSS variables
   - accessibility check results: Figma, Canva, Claude
   - breakpoints: Figma Sites, WordPress 7.1, Material 3
5. **No tool models the review half.** None has an object for a design direction, a concept or a
   decision about one element. Approvals exist for a whole design or a whole branch (Figma,
   Canva, Adobe). Claude's design features use the word "direction" in prose only [C4]. XEO's
   review half is its own, and nothing in the sources contradicts it.
6. **Name clash to watch.** In Canva and Adobe Express a "template" is a starting design you copy,
   not the layout a kind of page is built from. In Spectrum a "variant" is one option of a
   component, not a component of its own. XEO's names are right for the web; the mappings must
   say which is which.

## 2. Crosswalk

**How to read the table**
- **Match values:** `exact`, `close` (the difference is given), `broader` (the source's idea is
  wider than XEO's), `narrower`, `related`.
- **Empty cell:** the source has no such idea.
- **Column "WP":** WordPress `theme.json` and block themes.
- **Column "Other":** Material 3 (M3), Style Dictionary (SD), Tokens Studio (TS), Storybook (SB),
  Penpot (PP), atomic design (AD), and Adobe's Design System Package format (DSP).

| # | XEO term | W3C Design Tokens (D) | Figma (F) | Claude (C) | Canva (V) | Adobe (A) | WP (W) | Other (O) |
|---|---|---|---|---|---|---|---|---|
| 1 | `DesignSystem` | a token file plus a resolver document: narrower, tokens only [D1, D3] | a library of components, styles and variables: close. There is no "design system" object; plan rows say "Organization-wide design systems" [F19] | "Design system" (the Design systems template: colours, typography, components, layout patterns; a guide, tokens and components): exact [C2, C5] | Brand Kit (colours, fonts, logos, brand voice, brand templates): close, with no components [V13, V7] | Spectrum design data (tokens, components, mode sets, guidelines): exact [A2]. A CC Library, or an Express brand: close [A11, A10 (summary)] | a block theme (`theme.json`, `/patterns`, `/templates`): close [W1, W7] | DSP "Design System Package": exact [A14]. PP shared library: close [O7] |
| 2 | `DesignToken` | a token, an object with `$value`: exact [D1] | a variable (`Variable`, holding `valuesByMode`): close, one node per mode in XEO [F4]. A style (`FILL`, `TEXT`, `EFFECT`, `GRID`): close for composites [F7] | "Design tokens are the named color, typography, and spacing values": exact [C6] | a Brand Kit colour (`palettes[].colors[]`): narrower [V12] | a Spectrum token: exact [A1, A3]. A CC Libraries Color or Character Style element: close [A11] | a preset (`settings.color.palette[]`, `typography.fontSizes[]`, `spacing.spacingSizes[]`, `shadow.presets[]`) or `settings.custom`: close [W1, W3] | an M3 token [O1], an SD token [O4], a TS token [O5], a PP token [O7]: all exact |
| 3 | `DesignComponent` | | `COMPONENT`, or `COMPONENT_SET` with its instances: exact [F9, F7] | "Components: Buttons, cards, navigation elements": exact [C5] | none: an element is a rect, a shape, text, an embed or a group [V10] | a Spectrum component (`button.json`: options, states, anatomy, implementations): exact [A6]. An XD "Main component": exact [A13 (summary)] | a block (`block.json`): close. `styles.elements` (`button`, `heading`): narrower [W10, W2] | SB `component` in a story's meta: exact [O6]. PP "Main component": exact [O7]. AD atoms, molecules and organisms: broader [O8] |
| 4 | `DesignPattern` | | | "Layout patterns: Spacing, grid systems, and page structures": close, layout rather than composite UI [C5] | | | a block pattern (`/patterns`, synced patterns): exact. A template part: close [W9, W8] | AD organisms: close [O8] |
| 5 | `PageTemplate` | | | | template, brand template (`brand_template_id`): different, a starting design to copy [V7, V3] | Express template: different [A10 (summary)]. CC Libraries `Template` element: different [A11] | template (`/templates`, `customTemplates` with `postTypes`): exact [W7, W1] | AD templates: exact [O8] |
| 6 | `DesignAsset` | "File: for assets" is listed as a likely future type, non-normative [D1 §8.8] | "assets" in a Figma library means components, styles and variables: different [F19]. The MCP tool `upload_assets` [F23] | brand guideline assets (logos, palettes, type specs) as inputs: close [C5] | asset (`type`: `image` or `video`): exact [V5]. Brand Kit logos, fonts, photos, icons, illustrations, graphics: exact [V13] | a CC Libraries element (Graphic, Video, Animation, Model and others): exact [A11, A12] | `fontFace[].src`: narrower, fonts only [W1] | TS `asset` type: close [O5]. PP assets (components, colours, typographies): broader [O7]. DSP `/assets` [A14] |
| 7 | `DesignDirection` | | a branch: related, an alternative line of work [F14] | "explore a different direction", "explore more directions": prose, no object [C4, C3]. The `frontend-design` skill's "aesthetic direction" [C8] | | | | |
| 8 | `DesignElement` | | | | the brand-check dimensions (colour palette, typography, logo treatment, copy tone): related [C11] | | | |
| 9 | `DesignConcept` | | `FRAME`, `SECTION`, or a prototype flow, as the place a concept is kept: related [F9, F21] | an artboard in a Design artifact, and "2–3 options": related [C4] | a design and its pages: related [V1, V2] | Express `PageNode` and `ArtboardNode`: related [A9 (summary)] | | SB story ("captures the rendered state of a UI component"): close [O6]. PP board: related [O7] |
| 10 | `DesignDecision` | | branch review (Approve, Request changes): close, but it judges a branch [F14]. Dev Mode `devStatus`: different, a handoff state [F8, F12] | inline comments, "Send to Claude": related [C12] | design approval (`approval_response{approved, ready_to_publish, message}`): close, but it judges a whole design [V9, V17] | Express Simple review (Approve, Needs work): close [A15 (summary)] | | |
| 11 | `inDesignSystem` | membership of a file or set: implicit [D3] | `variableCollectionId`; a library file: close [F4] | implicit [C5] | | `library_id` on a CC element: exact [A12] | implicit in the theme | |
| 12 | `usesDesignSystem` | | a library enabled for a file: close (not confirmed in REST) | a project "automatically inherits your organization's design system": close, a project not a site [C4] | Brand Kits assigned to folders: close [V15] | | the active theme of a site: close | |
| 13 | `aliasOf` | `{group.token}`, or a `$ref` to the whole token: exact [D1 §7] | `VARIABLE_ALIAS` (`id`): exact [F4] | | | an alias, "A token that references another token": exact [A1]. `$ref` (to a uuid or a conceptId): exact [A3] | | SD `{a.b.c}` [O4], TS and PP `{name}` [O5, O7]: exact. M3 tokens "point to" other tokens [O1] |
| 14 | `usesToken` | | `boundVariables`: close [F8] | | | component tokens and relationship records: close [A2] | a style that uses a preset: close [W2] | M3 component tokens: close [O1] |
| 15 | `composedOf` | | nested instances, `exposedInstances`, slots (`SLOT`): close [F9, F11] | | | `anatomy` and `slots` in component data: close [A6] | a pattern's block markup; `allowedBlocks`: close [W10] | AD molecules made of atoms: close [O8] |
| 16 | `variantOf` | | a variant: a `COMPONENT` inside a `COMPONENT_SET`, with `VARIANT` and `variantOptions`: close [F7, F8] | | | `variant`, one option value (`accent`, `primary`): different [A6, A8]. XD states: narrower [A13 (summary)] | a block style variation (`is-style-{name}`), or block `variations`: close [W4, W10] | PP variants (`Color=Primary + Size=Small`): close [O7]. SB one story per set of args: close [O6] |
| 17 | `usesAsset` | | | | an image or video element (`addElementAtPoint` types `image`, `video`): close [V11] | | `fontFace` loaded by a theme: narrower [W1] | |
| 18 | `usesTemplate` | | | | create a design from `brand_template_id`: different [V3] | | a page's template (`customTemplates`, `postTypes`): exact [W1] | |
| 19 | `designSystemVersion` | the resolver's `version` is the format's version (`2025.10`), not the system's: none [D3] | a file version (`label`): close [F16] | the "Published" toggle: related [C5] | | DSP `dsp_spec_version` and `build_status_label`: related [A14] | | |
| 20 | `tokenType` | `$type`: exact [D1, D5] | `resolvedType` (`BOOLEAN`, `FLOAT`, `STRING`, `COLOR`; the Plugin API adds `EASING` and `TIMING`): close [F4, F2, F3] | | | `$schema` token types (`color-set.json`, `alias.json`): close [A5] | the preset category (`color`, `font-size`): close [W2] | the TS type list (24): broader [O5]. PP types: close [O7] |
| 21 | `tokenValue` | `$value`: exact [D1] | `valuesByMode[modeId]`: exact, per mode [F4] | | `color` (`{type:"solid", color:"#hex"}`): exact [V12] | `value`, or `sets.{mode}.value`: exact [A5] | `color`, `size`, `shadow`, `gradient`: exact [W1] | SD `value` [O4] |
| 22 | `tokenTier` | none in the Format. The Color Module names base, alias and component in a non-normative note [D2 §7] | | | | `tokenTier` `primitive`, `semantic` or `component`: exact, the same codes [A2]. The site says "Primitive (aka Global)", "Semantic", "Component-specific" [A1] | | M3 `ref`, `sys`, `comp`: exact [O1] |
| 23 | `tokenMode` | a context of a modifier (`modifiers.{name}.contexts`): close, one axis per modifier [D3] | a mode (`modes`, `modeId`; one set per collection): exact [F4, F1] | | | mode sets `colorScheme` (`light`, `dark`, `wireframe`), `scale` (`desktop`, `mobile`), `contrast`: close [A4] | a theme style variation (`/styles/*.json`): close [W6] | TS theme in a theme group [O5], PP theme in a theme group [O7]: close. M3 "contexts" [O1] |
| 24 | `assetKind` | | | | asset `type` (`image`, `video`); brand categories Logos, Photos, Icons, Illustrations, Graphics: close [V5, V13] | CC element types (Graphic, Video, Animation, Model, Pattern and others): broader [A11] | | |
| 25 | `directionFor` | | | a project: related [C4] | | | | |
| 26 | `proposedIn` | | a file or a branch: related | a Design artifact, which can hold several options: close [C1, C4] | a design: related [V1] | | | |
| 27 | `elementOf` | | | | | | | |
| 28 | `seenOn` | | `generate_figma_design` ("Turns live web UI into design layers"): related [F23] | | | | | |
| 29 | `realizedAs` | | Code Connect (a Figma component to a code component): related [F13] | `/design-sync` (a repo's React design system to Claude Design): related [C7] | | `implementations` (`@react-spectrum/s2`, `swc-button`): related [A6] | | |
| 30 | `depicts` | | an instance in a frame: related [F9] | an artboard: related [C4] | | | | SB story of a component: close [O6] |
| 31 | `underDirection` | | | | | | | |
| 32 | `replacesElement` | | | | | | | |
| 33 | `fromDirection` | | | | | | | |
| 34 | `elementKind` | | | the contents of a design system (colour palette, typography, components, layout patterns): close [C5] | the brand check's five dimensions (colour palette, typography, logo treatment, copy tone, overall consistency): close [C11] | Express brand (logos, colours, fonts, brand voice): close [A10 (summary)] | | |
| 35 | `decidesOn` | | the branch under review: close [F14]. A comment's `client_meta` (a node or region): related [F20] | a comment's target (an artboard, a slide, an object): related [C12] | the design under approval: close [V9] | | | |
| 36 | `chosenConcept` | | | | a suggestion thread's `status` `accepted`: narrower [V8] | | | |
| 37 | `decidedBy` | the reviewer; a comment's `user`: exact [F14, F20] | | a comment's author: related [C12] | `triggering_user`, `responding_groups`: close, can be a group [V9] | | | |
| 38 | `designVerdict` | | Approve, Request changes; badges "In review", "Changes suggested", "Approved": close [F14] | | "Approved", "Awaiting review", "Needs changes"; `approved` true or false: close [V17, V9] | Approve, Needs work [A15 (summary)]. Frame.io Approved, Needs Review, In Progress [A16 (summary)] | | |

## 3. Scheme check

**`tokenType` (15 codes).**
- **Keep all 13 format codes.** They are the 2025.10 schema's enum exactly: `color`,
  `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`, `strokeStyle`,
  `border`, `transition`, `shadow`, `gradient`, `typography` [D5].
- **Keep `string` and `boolean`.** The format has neither: "every design token MUST use one of
  these types" [D1 §8]. They are needed for Figma's `STRING` and `BOOLEAN` [F4] and Tokens
  Studio's `text` and `boolean` [O5].
  - One inconsistency in the format: its Example 12 writes `"$type": "string"` although
    `string` is not a type [D1 §6.3].
- **Add none.** The other candidates are all purposes of `dimension` or `number`, not new kinds
  of value:
  - Tokens Studio's `opacity`, `borderRadius`, `spacing`, `sizing`, `textCase` and
    `textDecoration` [O5].
  - Penpot's `rotation` and `stroke width` [O7].
  - Figma's `EASING` maps to `cubicBezier`, except for a spring, which has no format type.
    `TIMING` maps to `duration` [F3]. That is a matter for the mapping, not the scheme.
  - The format names "Font style", "Percentage/ratio" and "File" as likely future types
    [D1 §8.8]. Add them if they are published.
- **Value shapes changed in 2025.10.** A colour is `{colorSpace, components, alpha?, hex?}`
  [D2 §4.1]. A dimension is `{value, unit: px|rem}` and a duration `{value, unit: ms|s}`
  [D1 §8.2, §8.5]. `tokenValue`'s description now says so (fixed).

**`tokenTier` (3 codes).**
- **Keep the codes.** Adobe Spectrum's design-data spec uses the same three codes, `primitive`,
  `semantic` and `component`, as its own `tokenTier` [A2]. Material 3 maps one to one: `ref`,
  `sys`, `comp` [O1]. The format defines no tiers [D1]. Its Color Module, in a non-normative
  note, says base, alias and component [D2 §7].
- **Fixed in the description:** the old line cited "global, alias and component", which no
  source uses as written.
- **Added as `skos:altLabel`:**
  - Reference, Base and Global on `primitive`
  - System and Alias on `semantic`
  - Component-specific on `component`
- **Spectrum derives a tier when none is given:** an alias is semantic, and a component field
  makes a token component [A2]. Worth copying into a loader, not the ontology.

**`elementKind` (11 codes).**
- **No source has a list of parts to catalogue in an existing site.** The nearest are:
  - Canva's brand check: colour palette, typography, logo treatment, copy tone, overall
    consistency [C11]
  - Claude's design system: colour palette, typography, components, layout patterns [C5]
  - Canva's and Express's brand voice [V14, A10 (summary)]
- **Candidate to add: `voice`** (copy tone). Two vendors carry it, so it passes the two-source
  rule, but whether a design review covers copy is a call for the maintainer. It is a question
  (Q4), not an edit.
- **Not proposed:** shape or elevation (radius, shadow). Only Material treats them as separate
  styles.

**`assetKind` (8 codes).**
- **The codes match Canva's brand-asset categories:** Logos, Fonts, Photos (as `photograph`),
  Icons, Illustrations, Graphics [V13]. Canva's asset API has `image` and `video` only [V5].
- **CC Libraries also has Video and Animation** (and its Graphic) [A11].
- **One source each, so not proposed:**
  - 3D `Model`, `Material` and `Light`, and `Pattern`, all CC Libraries only [A11]
  - audio (XD libraries) [A13 (summary)]
- **Colours and character styles are not assets.** Both CC Libraries and Canva put them in
  libraries and Brand Kits, but in XEO they are tokens.

**`designVerdict` (7 codes, now 8).**
- **Added `revise`** (altLabels Request changes, Needs changes). The changes-requested call
  appears in:
  - Figma branch review: Approve, Request changes; badge "Changes suggested" [F14]
  - Canva design approval: Approved, Awaiting review, Needs changes [V17]
  - Adobe Express: Approve, Needs work [A15 (summary)]
  - Frame.io via Workfront: Approved, Needs Work [A16 (summary)]
  - Before this, XEO could not say "not yet, rework it".
- **Not added:**
  - "Awaiting review" and "In review" are states of a request, not calls.
  - `READY_FOR_DEV` and `COMPLETED` are handoff states (Q7).
- **No source has** `keep`, `replace`, `remove` or `shortlist`. They are the element-by-element
  review's own codes and stand on that practice.

## 4. Proposed changes to the module

None of these is made. Each gives its kind, the layer, the sources and the confidence.

| # | Change | Kind | Layer | Sources | Confidence |
|---|---|---|---|---|---|
| P1 | `variantValue` on `DesignComponent`: one "property=value" pair per axis that makes a variant (`size=small`, `state=hover`, `emphasis=quiet`). Multi-valued. Covers states as well, the way Figma and Penpot model states as variant values | add a term | entity | Figma `VARIANT` and `variantOptions` [F8]; Penpot `Color=Primary + Size=Small` [O7]; Spectrum `options` and `states` [A6, A7]; Code Connect `figma.enum` and `variant` [F13]; Storybook args [O6] | documented |
| P2 | `tokenMode` may be repeated, one value per modifier, written `modifier:context` (`theme:dark`, `scale:mobile`), where a value depends on more than one axis | widen (convention, plus a shape for the pattern) | entity | Resolver modifiers and contexts, whose resolutions multiply [D3 §4.1.5]; Spectrum `colorScheme`, `scale`, `contrast` [A4]; Tokens Studio "multi-dimensional theming" [O5]; Penpot theme groups [O7]; Figma one mode per collection, across several collections [F1] | documented |
| P3 | A join key for a tool's record, written `tool:file:objectType:id` (`figma:<fileKey>:variable:<key>`), on the model of `crmRecordRef` (sales) | add a term (`designRecordRef`) | entity | Figma `key` and `id`, stable over a variable's life [F5]; component and style `key` [F7]; Canva `id` on designs, pages and assets [V1, V2, V5]; CC Libraries `id` and `library_urn` [A12]; Spectrum `uuid` [A3] | documented |
| P4 | A token's name in code, per platform (`css:--color-action-primary`) | add a term (`tokenCodeName`) | entity | Figma `codeSyntax` (`WEB`, `ANDROID`, `iOS`) [F4]; WordPress `--wp--preset--{category}--{slug}` and `--wp--custom--…` [W2, W3]; Style Dictionary `name` and `prefix` [O4] | documented |
| P5 | A token's deprecation: `true`, or an explanation | add a term (`tokenDeprecated`) | entity | the format's `$deprecated` [D1 §5.2.4]; DSP `build_status_label` "deprecated" [A14] | inferred (DSP is dormant since 2021) |
| P6 | An accessibility check result: what was checked (contrast, alt text, text size), against what (WCAG 1.4.3 at 4.5:1, 1.4.11 at 3:1), and the result. Draft for 0.9 | add a class | observation | Figma "Check designs" (contrast at AA or AAA) [F17]; Canva "Check Design Accessibility" (typography, colour contrast, alternative text) [V18]; Claude Design's review "for accessibility, contrast ratios" [C4]; WCAG [O9] | documented |
| P7 | Breakpoints as a token mode on a `viewport` or `scale` modifier, with the widths as `dimension` tokens. No class | a convention in `tokenMode`'s description | entity | Figma Sites Desktop 1280, Tablet 800, Mobile 375 [F18 (summary)]; WordPress 7.1 `settings.viewport` `mobile` 480px and `tablet` 782px, `@mobile` and `@tablet` [W11]; Material 3 breakpoints Compact to Extra-large [O3 (summary)]; Spectrum `scale` desktop and mobile [A4] | documented |
| P8 | Say how a WordPress block maps: a block is a `DesignComponent` (`artifactUri` to its `block.json`); a block style variation is a `variantOf`; a synced or theme pattern is a `DesignPattern`; a template is a `PageTemplate`; a template part is a `DesignPattern`. No term | description text | entity | [W4, W8, W9, W10] | documented |
| P9 | A design file's pages and frames get no class. A concept's `artifactUri` addresses the frame or page; the tool's id goes in P3 | none (answers an open question) | entity | Figma `CANVAS`, `FRAME`, `SECTION` [F9]; Claude artboards [C4]; Canva pages with a stable `id` [V2]; Express `PageNode` and `ArtboardNode` [A9 (summary)]; Penpot boards and pages [O7] | documented |
| P10 | Atomic-design levels: no scheme. The component, pattern and template ladder already maps to them: atoms and molecules are components, organisms are patterns, templates are templates, pages are a `URL` | none | — | Frost ch. 2 [O8]; no tool uses the levels as data | documented |
| P11 | A handoff state (ready for dev, completed, changed since ready) is not a `designVerdict`. Point at the work module's status for a `WorkItem`, or add a small code list later | none now | — | Figma `devStatus` `READY_FOR_DEV`, `COMPLETED`, plus `NONE` in the OpenAPI spec [F8, F20]; Figma "Changed" [F12]; Canva `ready_to_publish` [V9] | documented |
| P12 | `decidesOn` may also take a whole `Deliverable`: a design approved as a whole, the way Canva and Figma approve | widen the range | interpretation | Canva approval of a design [V9, V17]; Figma approval of a branch [F14] | inferred |
| P13 | `elementKind` `voice` | a new code | — | Canva Brand Voice [V14]; Canva brand check "copy tone" [C11]; Express brand voice [A10 (summary)] | documented (Canva), unconfirmed (Adobe). Waits on Q4 |

## 5. Mapping-file drafts

These rows are written to the shape of `mappings/_template.ttl`.
- **Not committed as files.** Rows whose slot does not exist yet name the slot as *(proposed)*
  in a comment, and would not load until it does.
- **Not loadable as written:** to keep the drafts short, the rows below leave out the
  `skos:inScheme`, `dct:source` and `skos:prefLabel` lines every row needs. Add them before
  this becomes `mappings/figma.ttl` or `mappings/canva.ttl`.
- **Confidence:** `documented` throughout, except where a row says `inferred`.

### `mappings/figma.ttl` (draft)

```turtle
xeos:figma a skos:ConceptScheme ;
    skos:prefLabel "Figma REST API: variables, components, styles, versions"@en ;
    dct:source "developers.figma.com REST API reference and help.figma.com (read 2026-11-20)" ;
    dct:description "Figma variables mapped to DesignToken slots, components and component sets to DesignComponent, and version labels to designSystemVersion. The variables API is Enterprise only." .

xeos:figma-variable-name a skos:Concept ;
    skos:notation "name" ; xeo:fillsSlot xeo:name ; skos:closeMatch xeo:name ;
    skos:definition "The variable's name; '/' separates groups"@en ;
    skos:scopeNote "Figma writes color/brand/primary; the Design Tokens Format path is color.brand.primary. Replace / with . on load."@en ;
    xeo:mappingConfidence "documented" .

xeos:figma-resolvedType a skos:Concept ;
    skos:notation "resolvedType" ; xeo:fillsSlot xeo:tokenType ; skos:closeMatch xeo:tokenType ;
    skos:definition "The variable's type: BOOLEAN, FLOAT, STRING or COLOR (REST); the Plugin API adds EASING and TIMING"@en ;
    skos:scopeNote "COLOR to color; STRING to string, or fontFamily where scopes holds FONT_FAMILY; BOOLEAN to boolean; FLOAT to dimension where scopes holds CORNER_RADIUS, WIDTH_HEIGHT, GAP, FONT_SIZE, LINE_HEIGHT, LETTER_SPACING, PARAGRAPH_SPACING, PARAGRAPH_INDENT or STROKE_FLOAT (unit px implied), fontWeight for FONT_WEIGHT, else number. TIMING to duration (the help centre says milliseconds, the Plugin API seconds: check); EASING to cubicBezier unless a spring, which has no format type."@en ;
    xeo:mappingConfidence "inferred" .

xeos:figma-valuesByMode a skos:Concept ;
    skos:notation "valuesByMode" ; xeo:fillsSlot xeo:tokenValue ; skos:closeMatch xeo:tokenValue ;
    skos:definition "The variable's value in each mode of its collection, keyed by modeId; a value is a literal or a VARIABLE_ALIAS"@en ;
    skos:scopeNote "One DesignToken per modeId, each with tokenMode from the collection's modes. A COLOR is RGBA in 0–1; write it as the format's colour object with colorSpace srgb."@en ;
    xeo:mappingConfidence "documented" .

xeos:figma-modes a skos:Concept ;
    skos:notation "modes" ; xeo:fillsSlot xeo:tokenMode ; skos:exactMatch xeo:tokenMode ;
    skos:definition "A collection's modes, modeId to name; defaultModeId names the default"@en ;
    skos:scopeNote "Store the mode's name, not its modeId. An extended collection's mode has parentModeId and an encoded id. Several collections are several axes (see proposal P2)."@en ;
    xeo:mappingConfidence "documented" .

xeos:figma-VARIABLE_ALIAS a skos:Concept ;
    skos:notation "VARIABLE_ALIAS" ; xeo:fillsSlot xeo:aliasOf ; skos:exactMatch xeo:aliasOf ;
    skos:definition "A value that references another variable by id"@en ;
    skos:scopeNote "Per mode: a variable may be an alias in one mode and a literal in another, which one-token-per-mode carries."@en ;
    xeo:mappingConfidence "documented" .

xeos:figma-style_type a skos:Concept ;
    skos:notation "style_type" ; xeo:fillsSlot xeo:tokenType ; skos:closeMatch xeo:tokenType ;
    skos:definition "A published style's type: FILL, TEXT, EFFECT or GRID"@en ;
    skos:scopeNote "FILL to color or gradient; TEXT to typography; EFFECT to shadow (a blur has no format type); GRID has no token type."@en ;
    xeo:mappingConfidence "inferred" .

xeos:figma-containingComponentSet a skos:Concept ;
    skos:notation "containing_frame.containingComponentSet" ; xeo:fillsSlot xeo:variantOf ; skos:closeMatch xeo:variantOf ;
    skos:definition "The component set a published component (a variant) sits in"@en ;
    skos:scopeNote "The variant points at the DesignComponent that stands for the component set. Its variant property values (componentPropertyDefinitions, VARIANT) have no slot yet (proposal P1)."@en ;
    xeo:mappingConfidence "documented" .

xeos:figma-version-label a skos:Concept ;
    skos:notation "label" ; xeo:fillsSlot xeo:designSystemVersion ; skos:closeMatch xeo:designSystemVersion ;
    skos:definition "The label of a named version in a file's version history"@en ;
    skos:scopeNote "Only where the team labels library releases as versions; an unlabelled autosave is not a system version."@en ;
    xeo:mappingConfidence "inferred" .

# Identifiers, for designRecordRef (proposed, P3); not loadable until that slot exists:
#   file_key / :key  (a branch has its own key; a branch file returns mainFileKey)
#   node_id, component key, component set key, style key
#   variable id and key ("remain stable over the variable's lifetime"); subscribed_id changes on publish
#   collection id and key; modeId; comment id; version id
# Not mapped: scopes, codeSyntax (P4), hiddenFromPublishing, devStatus (P11),
#   comments (no slot: a comment is not a decision), branch review (no REST endpoint).
```

### `mappings/canva.ttl` (draft)

```turtle
xeos:canva a skos:ConceptScheme ;
    skos:prefLabel "Canva Connect API and Apps SDK: designs, assets, Brand Kit colours, approvals"@en ;
    dct:source "canva.dev Connect API reference and Apps SDK reference; canva.com/help (read 2026-11-20)" ;
    dct:description "Canva designs mapped to DesignConcept pointers, assets to DesignAsset, Brand Kit colours to DesignToken, and design approval responses to DesignDecision. Canva's templates are starting designs, not PageTemplates, and are not mapped." .

xeos:canva-design-title a skos:Concept ;
    skos:notation "title" ; xeo:fillsSlot xeo:name ; skos:exactMatch xeo:name ;
    skos:definition "The design's title"@en ;
    xeo:mappingConfidence "documented" .

xeos:canva-design-view_url a skos:Concept ;
    skos:notation "urls.view_url" ; xeo:fillsSlot xeo:artifactUri ; skos:closeMatch xeo:artifactUri ;
    skos:definition "A URL to view the design"@en ;
    skos:scopeNote "For a DesignConcept kept in Canva. Whether view_url and edit_url are durable was not confirmed; prefer the design id (P3) as the join key."@en ;
    xeo:mappingConfidence "inferred" .

xeos:canva-asset-type a skos:Concept ;
    skos:notation "type" ; xeo:fillsSlot xeo:assetKind ; skos:broadMatch xeo:assetKind ;
    skos:definition "The asset's type: image or video"@en ;
    skos:scopeNote "video to video. image is broader than XEO's codes: logo, icon, illustration, photograph or graphic is decided from the Brand Kit category the asset sits in, or by hand."@en ;
    xeo:mappingConfidence "documented" .

xeos:canva-brandKitColor a skos:Concept ;
    skos:notation "palettes[].colors[].color" ; xeo:fillsSlot xeo:tokenValue ; skos:closeMatch xeo:tokenValue ;
    skos:definition "A Brand Kit colour as #hex (Apps SDK getBrandKitColors)"@en ;
    skos:scopeNote "One DesignToken per colour, tokenType color, tokenTier primitive. The Brand Kit gives no token name; the palette name and position stand in. No REST endpoint reads a Brand Kit."@en ;
    xeo:mappingConfidence "inferred" .

xeos:canva-approval-approved a skos:Concept ;
    skos:notation "approval_response.approved" ; xeo:fillsSlot xeo:designVerdict ; skos:closeMatch xeo:designVerdict ;
    skos:definition "Whether the reviewer approved the design (design approval response webhook)"@en ;
    skos:scopeNote "true to approve; false to revise (the help centre calls it Needs changes). The decision is about the whole design: decidesOn the DesignConcept or Deliverable the design holds (see P12)."@en ;
    xeo:mappingConfidence "documented" .

xeos:canva-approval-message a skos:Concept ;
    skos:notation "approval_response.message" ; xeo:fillsSlot xeo:statement ; skos:exactMatch xeo:statement ;
    skos:definition "The reviewer's message with the approval response"@en ;
    xeo:mappingConfidence "documented" .

xeos:canva-approval-responder a skos:Concept ;
    skos:notation "triggering_user" ; xeo:fillsSlot xeo:decidedBy ; skos:closeMatch xeo:decidedBy ;
    skos:definition "The user whose response triggered the notification"@en ;
    skos:scopeNote "responding_groups may name a group; Canva Teams supports individual reviewers only. Resolve the user to a Person by its Canva user id."@en ;
    xeo:mappingConfidence "documented" .

# Identifiers, for designRecordRef (proposed, P3):
#   design id; page id ("unique within the design"); asset id; folder id (reserved: root, uploads);
#   brand template id; comment thread id; export job id (transient, not a record)
# Not mapped: brand templates and autofill (a starting design, not a PageTemplate);
#   comment threads and suggestion status (no slot); exports; ready_to_publish (P11).
```

## 6. Questions for the maintainer

These are only the questions the sources cannot settle. Each is written as a draft card.

| # | Question | Options | Recommendation |
|---|---|---|---|
| Q1 | A token whose value depends on two axes (dark and mobile): how is its mode written? | A. Keep one free-text `tokenMode` (one axis only). B. Allow several `tokenMode` values, written `modifier:context`. C. Add two terms, modifier and context. | **B.** It matches the Resolver's modifiers [D3] and Spectrum's mode sets [A4] without new terms. |
| Q2 | Should what makes a variant (size, state, emphasis) become data? | A. Leave it in the name. B. Add `variantValue`, "property=value", repeated. C. One term per axis. | **B.** Five sources share property=value (P1). C fixes axes that differ by system. |
| Q3 | Where does a tool's own id (a Figma variable key, a Canva design id) go on a node? | A. Only in `artifactUri` URLs. B. Add `designRecordRef` (`tool:file:type:id`), like `crmRecordRef`. C. Keep ids out of the graph. | **B.** Variables and tokens have no URL, so A cannot hold them. |
| Q4 | Is a site's copy tone (voice) a design element under review? | A. Add `voice` to `elementKind`. B. Leave voice to the brand side (`Brand`, visibility). C. Decide when the review page needs it. | **B.** Keep the element review visual. Canva puts voice in the Brand Kit, beside design, not as part of it. |
| Q5 | Rights to an asset (licence, credit, expiry): add now? | A. Add terms now. B. Wait until a project needs them, then align to schema.org. C. Never: keep rights in the asset store. | **B.** No source read here models rights on an asset; schema.org was not read in this pass. |
| Q6 | How is a direction's rank within a proposal kept? | A. Add `directionRank` (an integer). B. Use decisions: `shortlist` and `reject`, with a statement. C. Order inside the Deliverable. | **B.** No tool ranks directions, and a rank is a judgment, which is what `DesignDecision` holds. |
| Q7 | Where does "ready for dev" or "completed" go? | A. A new handoff code list in design. B. The work module's status on a `WorkItem`. C. Not modelled. | **B** (P11). It is a state of the build work, not a call on fit. |
| Q8 | Keep the new verdict code `revise`, made in this pass? | A. Keep `revise`. B. Rename it `changesRequested`. C. Remove it. | **A.** It is a verb like the other codes, and the tools' phrasings are its altLabels. |
| Q9 | Accessibility check results: add an observation class? | A. Add a draft class in 0.9. B. Wait for the design-review PRD. C. Not in XEO. | **A.** Figma, Canva and Claude all run the check (P6), and design review will want the result. |

### What was decided (2026-11-23)

The maintainer took all nine recommendations as given, inside 0.8.0. What that did to the
module:

| # | Taken | In 0.8.0 |
|---|---|---|
| Q1 | B | `tokenMode` may repeat, one value per axis, written `modifier:context`; one token per combination. New shape `DesignTokenModeShape` (P2) |
| Q2 | B | New draft term `variantValue`, `property=value`, repeated (P1) |
| Q3 | B | New draft term `designRecordRef`, `tool:file:objectType:id` (P3) |
| Q4 | B | No `voice` code. `elementKind` says copy tone belongs with the Brand |
| Q5 | B | No rights terms. `DesignAsset` says they wait for a project, then follow schema.org |
| Q6 | B | No rank term. `DesignDirection` says a rank is kept as decisions with a statement |
| Q7 | B | No handoff codes. `designVerdict` says a handoff state belongs with the build work (P11) |
| Q8 | A | `revise` stays |
| Q9 | A | Nothing in 0.8.0: the accessibility check class is planned as a draft for 0.9 (P6) |

Proposals P4, P5, P7, P8 and P12 were not among the nine and are not made. The crosswalk in §2
and the notes in the mapping drafts in §5 are as written on 2026-11-20, before these terms
existed, so they still call `variantValue` and `designRecordRef` proposed.

## 7. Sources (all read 2026-11-20)

**W3C Design Tokens Community Group**
- D1 Design Tokens Format Module 2025.10 (Final Community Group Report, 28 October 2025): https://www.designtokens.org/TR/2025.10/format/ (mirror: https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/)
- D2 Design Tokens Color Module 2025.10: https://www.designtokens.org/TR/2025.10/color/
- D3 Design Tokens Resolver Module 2025.10: https://www.designtokens.org/TR/2025.10/resolver/
- D4 Editor's draft (Draft Community Group Report, 08 September 2026): https://www.designtokens.org/TR/drafts/format/. It makes `$ref` support a MUST throughout, and `$ref` may point at a whole token.
- D5 2025.10 schema, type enum: https://github.com/design-tokens/community-group/blob/main/schemas/src/2025.10/format/tokenType.json

**Figma**
- F1 Variables overview: https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes
- F2 `VariableResolvedDataType`: https://developers.figma.com/docs/plugins/api/VariableResolvedDataType/
- F3 Plugin API Update 133 (EASING, TIMING): https://developers.figma.com/docs/plugins/updates/2026/08/05/version-1-update-133/
- F4 REST variables types: https://developers.figma.com/docs/rest-api/variables-types/
- F5 REST variables endpoints: https://developers.figma.com/docs/rest-api/variables-endpoints/
- F6 Extended collections: https://help.figma.com/hc/en-us/articles/36346281624471-Extend-a-variable-collection
- F7 REST component types: https://developers.figma.com/docs/rest-api/component-types/
- F8 REST file property types: https://developers.figma.com/docs/rest-api/file-property-types/
- F9 REST file node types: https://developers.figma.com/docs/rest-api/file-node-types/
- F10 REST component endpoints: https://developers.figma.com/docs/rest-api/component-endpoints/
- F11 Slots: https://help.figma.com/hc/en-us/articles/38231200344599-Use-slots-to-build-flexible-components-in-Figma
- F12 Dev Mode statuses: https://help.figma.com/hc/en-us/articles/26781702258583-Dev-Mode-statuses-and-notifications
- F13 Code Connect: https://developers.figma.com/docs/code-connect/ and https://developers.figma.com/docs/code-connect/react/
- F14 Branch review: https://help.figma.com/hc/en-us/articles/5691414603543-Request-a-branch-review
- F15 REST comments: https://developers.figma.com/docs/rest-api/comments-endpoints/
- F16 REST versions: https://developers.figma.com/docs/rest-api/version-history-endpoints/
- F17 Check designs: https://help.figma.com/hc/en-us/articles/39592284074263-Check-designs-in-Figma
- F18 Sites breakpoints *(summary)*: https://help.figma.com/hc/en-us/articles/31242797809815-Add-or-delete-breakpoints-in-a-webpage
- F19 Plans and features: https://help.figma.com/hc/en-us/articles/360040328273-Figma-plans-and-features
- F20 OpenAPI spec v0.47.0: https://raw.githubusercontent.com/figma/rest-api-spec/main/openapi/openapi.yaml
- F21 Prototype flows: https://help.figma.com/hc/en-us/articles/360039823894-Create-and-manage-prototype-flows
- F22 Library analytics: https://developers.figma.com/docs/rest-api/library-analytics-endpoints/
- F23 Figma MCP server tools: https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/

**Claude (Anthropic)**
- C1 Artifacts: https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them
- C2 Artifacts admin guide: https://support.claude.com/en/articles/16994751-artifacts-admin-guide-for-team-and-enterprise-plans
- C3 Claude Design: https://claude.com/product/design
- C4 Get started with Claude Design: https://support.claude.com/en/articles/14604416-get-started-with-claude-design
- C5 Set up your design system: https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design
- C6 Claude Code artifacts: https://code.claude.com/docs/en/artifacts
- C7 Claude Code commands (`/design`, `/design-sync`): https://code.claude.com/docs/en/commands
- C8 Skills (`frontend-design`, `canvas-design`, `brand-guidelines`, `theme-factory`): https://github.com/anthropics/skills/tree/main/skills
- C9 Figma connector: https://claude.com/marketplace/connectors/figma
- C10 Canva connector: https://claude.com/marketplace/connectors/canva
- C11 Canva plugin (brand check): https://claude.com/marketplace/plugins/canva
- C12 Comments on artifacts: https://support.claude.com/en/articles/17457950-use-artifacts-with-a-keyboard-or-screen-reader
- C13 Moving from standalone Claude Design: https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude

**Canva**
- V1 Get design: https://www.canva.dev/docs/apps/rest-apis/reference/designs/get-design
- V2 Get design pages: https://www.canva.dev/docs/apps/rest-apis/reference/designs/get-design-pages
- V3 Create design: https://www.canva.dev/docs/apps/rest-apis/reference/designs/create-design
- V4 Create export job: https://www.canva.dev/docs/apps/rest-apis/reference/exports/create-design-export-job
- V5 Assets: https://www.canva.dev/docs/apps/rest-apis/reference/assets and https://www.canva.dev/docs/apps/rest-apis/reference/assets/get-asset
- V6 Folders: https://www.canva.dev/docs/apps/rest-apis/reference/folders
- V7 Brand templates: https://www.canva.dev/docs/apps/rest-apis/reference/brand-templates
- V8 Comment threads: https://www.canva.dev/docs/apps/rest-apis/reference/comments/get-thread
- V9 Design approval response webhook: https://www.canva.dev/docs/apps/rest-apis/webhooks/design-approval-response-notification
- V10 Design Editing API: https://www.canva.dev/docs/apps/design-editing
- V11 `addElementAtPoint`: https://www.canva.dev/docs/apps/api/latest/design-add-element-at-point
- V12 `getBrandKitColors`: https://www.canva.dev/docs/apps/api/latest/design-get-brand-kit-colors
- V13 Brand assets (read through a fetch service, because direct fetch returned 403): https://www.canva.com/help/find-and-manage-brand-assets/
- V14 Brand voice: https://www.canva.com/help/brand-voice/
- V15 Brand controls: https://www.canva.com/help/brand-control/
- V16 Design approval settings: https://www.canva.com/help/design-approval/
- V17 Get approval: https://www.canva.com/help/get-approval/
- V18 Design accessibility: https://www.canva.com/help/using-design-accessibility/
- V19 Connect API reference index: https://www.canva.dev/docs/apps/rest-apis/reference

**Adobe**
- A1 Spectrum design tokens: https://spectrum.adobe.com/page/design-tokens/
- A2 Spectrum design-data taxonomy (tiers): https://github.com/adobe/spectrum-design-data/blob/main/packages/design-data-spec/spec/taxonomy.md
- A3 Spectrum token format (`conceptId`, `$ref`): https://github.com/adobe/spectrum-design-data/blob/main/packages/design-data-spec/spec/token-format.md
- A4 Spectrum mode sets: https://github.com/adobe/spectrum-design-data/tree/main/packages/design-data/mode-sets
- A5 Spectrum legacy tokens (`sets`): https://raw.githubusercontent.com/adobe/spectrum-design-data/main/packages/tokens/src/color-aliases.json
- A6 Spectrum button data: https://raw.githubusercontent.com/adobe/spectrum-design-data/main/packages/design-data/components/button.json
- A7 Spectrum state model: https://github.com/adobe/spectrum-design-data/blob/main/packages/design-data-spec/spec/state-model.md
- A8 React Spectrum Button: https://react-spectrum.adobe.com/v3/Button.html
- A9 Express add-on SDK nodes: https://developer.adobe.com/express/add-ons/docs/references/document-sandbox/document-apis/classes/node. Page and artboard nodes *(summary)*.
- A10 Express brands *(summary; helpx returned 403)*: https://helpx.adobe.com/express/web/brands-libraries-projects/create-manage-brands/create-brand.html
- A11 CC Libraries supported elements: https://developer.adobe.com/creative-cloud-libraries/docs/integrate/guides/working-with-elements/supported-elements/
- A12 CC Libraries API spec: https://raw.githubusercontent.com/AdobeDocs/cc-libraries-api-spec/main/openapi.json
- A13 Adobe XD FAQ (maintenance mode; updated 11 Sep 2026): https://helpx.adobe.com/xd/desktop/introduction/faq.html. XD component states *(summary)*: https://helpx.adobe.com/xd/help/create-component-states.html
- A14 Design System Package: https://github.com/AdobeXD/design-system-package-dsp
- A15 Express template approval *(summary)*: https://helpx.adobe.com/express/web/invite-collaborate/set-template-approval.html
- A16 Frame.io statuses *(summary)*: https://help.frame.io/en/articles/9105311-player-page-features

**WordPress**
- W1 `theme.json` reference (version 3): https://developer.wordpress.org/block-editor/reference-guides/theme-json-reference/theme-json-living/
- W2 Global settings and styles: https://developer.wordpress.org/block-editor/how-to-guides/themes/global-settings-and-styles/
- W3 Custom settings: https://developer.wordpress.org/themes/global-settings-and-styles/settings/custom/
- W4 Block style variations: https://developer.wordpress.org/themes/features/block-style-variations/
- W5 Section styles in 6.6: https://developer.wordpress.org/news/2024/06/styling-sections-nested-elements-and-more-with-block-style-variations-in-wordpress-6-6/
- W6 Style variations: https://developer.wordpress.org/themes/global-settings-and-styles/style-variations/
- W7 Templates: https://developer.wordpress.org/themes/templates/introduction-to-templates/
- W8 Template parts: https://developer.wordpress.org/themes/global-settings-and-styles/template-parts/
- W9 Patterns: https://developer.wordpress.org/themes/patterns/registering-patterns/ and https://developer.wordpress.org/themes/patterns/introduction-to-patterns/
- W10 `block.json`: https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/
- W11 Responsive block styles in 7.1: https://make.wordpress.org/core/2026/08/05/responsive-block-styles-and-configurable-viewports-in-wordpress-7-1/

**Other**
- O1 Material 3 design tokens (read through a fetch service): https://m3.material.io/foundations/design-tokens/overview
- O2 Material 3 colour roles: https://m3.material.io/styles/color/roles
- O3 Material 3 breakpoints *(summary)*: https://m3.material.io/foundations/layout/breakpoints
- O4 Style Dictionary: https://styledictionary.com/info/dtcg/, https://styledictionary.com/info/tokens/, https://styledictionary.com/reference/config/
- O5 Tokens Studio: https://docs.tokens.studio/manage-tokens/token-types, https://docs.tokens.studio/manage-themes/themes-overview, https://docs.tokens.studio/figma/export/themes
- O6 Storybook: https://storybook.js.org/docs/api/csf, https://storybook.js.org/docs/writing-stories, https://storybook.js.org/addons/@storybook/addon-designs
- O7 Penpot: https://help.penpot.app/user-guide/design-tokens/, https://help.penpot.app/user-guide/design-systems/components/, https://help.penpot.app/user-guide/design-systems/variants/
- O8 Atomic design, chapter 2: https://atomicdesign.bradfrost.com/chapter-2/
- O9 WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html. WCAG 3.0 draft (contrast method "yet to be determined"): https://www.w3.org/TR/wcag-3.0/

**Not read or not confirmed**
- **Adobe help pages:** helpx.adobe.com refused direct fetches, so every Adobe Express brand,
  template and review claim, and the XD states, rest on search summaries.
- **Canva and Material pages:** read through a fetch service, not directly.
- **Figma details not confirmed:**
  - TIMING's unit (milliseconds or seconds)
  - whether the REST API returns `EASING` and `TIMING`
  - the URL format of a design file
- **Not read at all:**
  - schema.org's licence and credit properties
  - the Canva Brand Kit's fonts and logos fields
  - a REST API for Figma branch review (none exists in the OpenAPI spec)
