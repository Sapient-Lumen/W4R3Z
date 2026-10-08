# 483 — Official voter-information user-overridden text spacing, clipped or overlapped content, and readability-recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose current answer/help lane must remain readable and usable when a voter increases line, paragraph, word, or letter spacing through a user stylesheet, bookmarklet, extension, application, or assistive/browser text-spacing setting**:
lookup forms,
status pages,
office/contact cards,
filters and result chips,
breadcrumbs and navigation labels,
inline warnings and validation text,
and similar routes where the page may remain technically present yet still lose meaning once text spacing expands beyond the author’s default assumptions.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `416`, which governs broader reflow, text-resize, and small-viewport survivability,
- `419`, which governs color, contrast, and non-color meaning cues,
- `422`, which governs field purpose, input hints, paste/autofill posture, and ordinary entry recovery,
- `482`, which governs keyboard-open visual-viewport shrink and obscured-control recovery while typing,
- `484`, which governs forced-colors / high-contrast system-palette override when the palette is replaced rather than the text metrics being expanded,
- or `440`, which governs reader-mode / simplified-view extraction rather than author-CSS spacing override resilience.

It adds one narrow rule:
**if an official voter-information route contains text the voter must read to decide or complete the current public step, the route should remain readable and functional when text spacing is increased within reviewed bounds, and it should not quietly rely on fixed-height, hidden-overflow, or brittle positioned text containers that clip, overlap, or erase the answer/help lane once spacing expands.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats voter-information materials and posted instructions as core public communications whose clarity and usability affect whether voters can act correctly. Digital.gov’s current digital-first public-experience guidance says federal digital services should be accessible, authoritative, user-centered, and mobile-first. W3C’s current understanding guidance for **Text Spacing** says users may increase spacing via a user stylesheet, bookmarklet, extension, or application, that users need the flexibility to adjust spacing within the success-criterion bounds without loss of content or functionality, and that content does **not** need to implement its own spacing mechanism in order to meet that rule. W3C’s current Technique `C36` says increased paragraph/line/word/character spacing benefits people with low vision or some cognitive disabilities and that text containers need room to expand or otherwise accommodate the spacing change. W3C’s current Failure `F104` makes the practical failure mode explicit: content can clip or overlap when spacing is increased because the text lives in size-constrained blocks, hidden-overflow boxes, or brittle positioned layouts. Section508.gov’s current typography guidance also says government websites need clear and consistent headings and highly legible text, and that typography choices have a huge impact on accessibility. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `w3c_wcag21_text_spacing_page`; xref: `w3c_wcag22_c36_text_spacing_override_page`; xref: `w3c_wcag22_f104_text_spacing_failure_page`; xref: `section508_accessible_fonts_typography_page`)

That is enough to justify a compact control here.
A route can pass ordinary mobile, zoom, contrast, and field-label review and still fail first contact because:
- a filter chip, tab label, breadcrumb, or button wraps into unreadable overlap when spacing increases,
- a fixed-height notice card clips the current deadline or office number,
- inline error text or explanatory copy is truncated by `overflow:hidden`,
- absolutely positioned helper text collides with adjacent controls,
- or the page keeps the same viewport width but still loses the answer lane because spacing growth, not screen width, was the real stressor.

## This is not the same thing as generic reflow, contrast, field-entry hints, or keyboard-open recovery

`416` asks whether the route survives small viewports, text enlargement, and ordinary zoom/reflow.

`419` asks whether the route remains readable when color or contrast perception is limited.

`422` asks whether people can tell what to enter and recover from normal input mistakes.

`482` asks whether the route remains usable while the on-screen keyboard changes what is visible during focused entry.

`483` asks a different question:
**when a voter increases text spacing within reviewed bounds, does the text-bearing answer/help lane still expand, wrap, and remain readable, or do clipped boxes, overlapped labels, and brittle positioned strings quietly break the official route even though nothing else about the page obviously changed?**

A route may pass the earlier controls and still fail `483` if:
- the viewport is wide enough, but a fixed-height banner cuts off the operative sentence once line height grows,
- contrast is fine, but the words physically overlap,
- field labels are accurate at default spacing, but spacing expansion makes them collide with inputs or helper text,
- or keyboard-open posture is acceptable, yet the same form still becomes unreadable under user-overridden spacing even before the keyboard appears.

If the text metrics stay acceptable but the visual state/boundary cues disappear only after forced-colors / high-contrast mode replaces the authored palette, that belongs to `484` rather than to `483`.

## The office does not need to build a spacing widget, but it must not depend on brittle default typography

W3C’s current understanding guidance for **Text Spacing** says content does not fail merely because it lacks its own built-in spacing controls and also does not fail if a platform or user agent does not provide that mechanism. The requirement is narrower: users need flexibility to adjust spacing within the success-criterion bounds **without loss of content or functionality**, and the content must not actively or purposely prevent those properties from being applied. (xref: `w3c_wcag21_text_spacing_page`)

For this archive, that means:
- the office does **not** need to invent a dedicated “increase spacing” feature,
- but it does need to review whether the public answer/help lane survives when spacing is overridden by ordinary accessibility tools,
- and it should not write CSS/layout that quietly assumes the default line height, letter spacing, or word spacing is the only legitimate reading posture.

This is a humility rule, not a demand for bespoke typography tooling.

## Fixed-height boxes, hidden overflow, and brittle positioning are the main risk class

W3C’s current Technique `C36` says text containers need room to expand or otherwise accommodate increased spacing, and its current Failure `F104` says clipping or overlap commonly appears when text is placed in size-constrained blocks, hidden-overflow containers, or brittle positioned layouts. (xref: `w3c_wcag22_c36_text_spacing_override_page`; xref: `w3c_wcag22_f104_text_spacing_failure_page`)

So `483` is especially concerned with text that lives inside:
- fixed-height cards,
- badges, pills, tabs, or chips with tight line-height assumptions,
- positioned labels or helper text,
- overflow-hidden containers,
- cramped inline validation/help lanes,
- or navigation structures whose text can wrap but was never reviewed after wrapping.

The archive does **not** require every short string to stay on one line.
It requires that the public route stay readable and functional when those strings wrap, expand, or otherwise need more room.

## The reviewed bounds are explicit and modest

W3C’s current Failure `F104` lists the review metrics used for the success criterion: line height at least `1.5` times font size, paragraph spacing at least `2` times font size, letter spacing at least `0.12` times font size, and word spacing at least `0.16` times font size. (xref: `w3c_wcag22_f104_text_spacing_failure_page`)

For this archive, those metrics are useful not because every voter will apply them manually, but because they define a clear, bounded stress test for whether the official answer/help lane is robust to common spacing overrides.

This document does **not** say the office must support arbitrary unlimited typography mutation.
It says that, within the recognized review bounds, the route should not collapse into clipped or overlapping text that changes whether the voter can understand or complete the public step.

## Language and script humility still matters

W3C’s current understanding guidance says some spacing metrics may be inapplicable for some languages and scripts and that authors may rely on locally available readability guidance when relevant. (xref: `w3c_wcag21_text_spacing_page`)

That means `483` should stay explicit about scope.
When a route supports multiple languages or scripts:
- review the applicable spacing posture for the relevant language/script,
- avoid silently assuming one Latin-script spacing model governs every locale,
- and keep the public explanation bounded when a particular metric is not meaningful for the language/script in question.

This composes with `377` and `397`.
The point here is not translation equivalence.
It is that the text the voter must actually read should remain readable in the relevant script when spacing overrides are applied.

## Labels, helper text, warnings, and short control text are the danger zone

Long paragraphs often reveal spacing failures visibly because they wrap and collide.
But public-service routes also fail on **short strings**:
- a breadcrumb that truncates the decisive page label,
- a pill-shaped filter whose wrapped text overlaps its close affordance,
- a selected-office card whose hours line is clipped,
- an inline validation note that becomes unreadable,
- or a tiny “Call this office” / “Bring ID” string that disappears from a fixed-height alert box.

This is why `483` belongs in the public-surface family at all.
On election routes, short text often carries the action-changing meaning.
When spacing expansion hides or garbles that text, the route may still look polished while no longer telling the truth in a practically readable way.

## Minimal text-spacing state taxonomy

A compact state taxonomy is enough:

1. **Default author-spacing state** — the route is viewed with ordinary authored spacing.
2. **Reviewed spacing-override state** — text spacing is increased within the bounded review metrics.
3. **Expansion-without-loss state** — text wraps or expands, but the answer/help lane remains readable and functional.
4. **Clipped-or-overlapped risk state** — spacing growth threatens to hide, overlap, or erase critical meaning.
5. **Recovered spaced-text state** — the route still exposes the current answer/help path after the spacing change.
6. **Spaced-text lane remains usable** — the current public step can still be understood and completed without guessing from damaged typography.

## Preserve bounded reconstruction, not individualized reading telemetry

What matters here is bounded reconstruction of the office’s text-spacing posture:
- which public routes were reviewed under increased spacing,
- which text-bearing components were considered critical,
- whether the route expanded cleanly or showed clipping/overlap risk,
- whether warnings, labels, help text, and next-step controls remained readable,
- and when the review last occurred.

Do **not** preserve by default:
- individualized accessibility-preference telemetry,
- per-user extension inventories,
- detailed reader-style fingerprints,
- or session-replay archives merely to prove the route was reviewed under spacing overrides.

## Claims this control should support

1. **Spacing-override review claim:** the office reviewed important public routes with text spacing increased within bounded published metrics.
2. **No-clipped-answer-lane claim:** the current answer/help lane does not lose critical text to fixed-height clipping, hidden overflow, or overlapping typography under reviewed spacing overrides.
3. **Control-label resilience claim:** navigation labels, buttons, chips, tabs, warnings, and helper text remain readable enough to preserve the public step.
4. **No-custom-widget requirement claim:** the office does not pretend a bespoke spacing toggle is required, but it also does not rely on brittle default typography as the only reading posture.
5. **Language/script humility claim:** any language/script-specific applicability limits are treated explicitly rather than buried inside generic English-only assumptions.
6. **Recovery-boundary claim:** spacing-induced readability failure is kept distinct from generic small-screen, contrast, field-entry, or keyboard-open failures so the route can be repaired at the right layer.

## Canonical digest artifacts

Publish **small digests of text-spacing posture**, not user-style telemetry.

- **Text Spacing Surface Digest (TSSD):** digest of reviewed routes, reviewed spacing bounds, and last review time.
- **Clipped/Overlapped Text Risk Digest (COTRD):** optional digest naming components that were reviewed for fixed-height, overflow, or positioning risk.
- **Readable Control Label Digest (RCLD):** optional digest of short control/label classes reviewed to ensure wrapped or expanded text still preserves action meaning.

## What belongs in the public text-spacing payload

Keep the payload **small, route-aware, and explicit about spacing-override posture**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `text_spacing_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_spacing_bounds`
- `reviewed_route_classes[]`
- `critical_text_components[]`
- `overflow_and_positioning_risk_note`
- `label_and_helper_text_note`
- `language_or_script_applicability_note`
- `no_custom_widget_requirement_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- per-user accessibility settings,
- extension/plugin inventories,
- raw session replays,
- or individualized typography telemetry.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which public routes were reviewed with increased text spacing?
- What reviewed spacing bounds were used?
- Did any critical text clip, overlap, truncate, or become unreadable under those spacing changes?
- Did navigation labels, warnings, helper text, and next-step controls remain understandable after wrapping/expansion?
- Did the office keep text-spacing failure separate from ordinary small-screen, contrast, and keyboard-open issues?
- If a language/script needs different applicability treatment, did the office say so explicitly rather than silently ignoring the issue?

## How this fits the family map

User-overridden text spacing is **not** a new underlying voter-question family bucket.
It is a shared public-surface control that can apply to many voter-information routes whenever the first-contact failure appears only after spacing overrides expand the text beyond the author’s default assumptions.

Use it when the route is basically the right one, but the text-bearing answer/help lane still breaks once a voter increases spacing.
Keep using:
- `416` for broader viewport/zoom/reflow posture,
- `419` for contrast and non-color visual meaning,
- `422` for input-purpose and generic entry recovery,
- `482` for keyboard-open visibility changes,
- and `440` for reader-mode / simplified-view extraction.

This document only says that, if an office expects the public to read decisive text on an official voter-information route, that text should remain readable and non-destructive under bounded spacing overrides rather than quietly clipping, overlapping, or vanishing inside brittle layout boxes.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- W3C: Understanding SC 1.4.12 Text Spacing (xref: `w3c_wcag21_text_spacing_page`)
- W3C: Technique C36, allowing for text spacing override (xref: `w3c_wcag22_c36_text_spacing_override_page`)
- W3C: Failure F104, clipped or overlapped content when text spacing is adjusted (xref: `w3c_wcag22_f104_text_spacing_failure_page`)
- Section508.gov: accessible fonts and typography guidance (xref: `section508_accessible_fonts_typography_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-text-spacing-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-text-spacing-surface-checklist.md`
