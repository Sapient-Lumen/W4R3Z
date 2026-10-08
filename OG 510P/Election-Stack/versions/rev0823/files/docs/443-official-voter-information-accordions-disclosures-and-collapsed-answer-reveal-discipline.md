# 443 — Official voter-information accordions, disclosures, and collapsed-answer reveal discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that place answer-bearing content inside accordions, disclosure widgets, expandable FAQ items, collapsed policy sections, or similar hide/reveal containers**:
registration or eligibility explainers,
mail-ballot instruction pages,
polling-place and hours answers,
ID requirement pages,
ballot-cure or replacement workflows,
and similar official routes where the page may be current and even section-targetable, but the controlling answer still stays hidden behind a collapsed panel, generic reveal label, or script-dependent disclosure state.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `403`, which governs progressive-enhancement and JavaScript-dependency fail-open posture for the route as a whole,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, labels, and live-update accessibility,
- `440`, which governs reader-mode and simplified-view extraction,
- `441`, which governs browser-tab and history-entry identity,
- or `442`, which governs section anchors, in-page navigation, and fragment-target continuity on long pages,
- or `474`, which governs ordinary browser find-in-page posture and first-match truthfulness rather than disclosure-specific reveal continuity.

It adds one narrow rule:
**if an official voter-information route hides a controlling answer, qualifier, or next-step boundary inside an accordion or disclosure container, the route should either expose the needed answer without guesswork or ensure the relevant panel is clearly labeled, safely revealable, and recoverable on direct entry, revisit, and degraded-script paths.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes hierarchy, structure, clarity, accessibility, usability, and accuracy. USWDS’s current accordion guidance says accordions are for cases where users only need a few specific pieces of content or where space is limited, and says teams should consider something else when users need to see most or all information because accordions increase cognitive load and interaction cost. The same USWDS guidance says accordion headers should be coded as buttons with meaningful labels and warns teams not to manually set `hidden` on content areas because content should remain accessible if JavaScript does not load or is disabled. WAI’s current ARIA APG says accordions are interactive headings that reveal or hide associated sections of content and are commonly used to reduce scrolling on a page. MDN’s current `<details>` and `<summary>` references say disclosure content is visible only when open, that the closed state shows only the summary/label, and that the summary toggles the open/closed state. USWDS’s current accordion accessibility tests also say teams need to test the component in the context of their own site and treat heading-level correctness as implementation-dependent. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_accordion_component_page`; xref: `uswds_accordion_accessibility_tests_page`; xref: `w3c_wai_aria_apg_accordion_pattern_page`; xref: `mdn_details_element_page`; xref: `mdn_summary_element_page`)

That is enough to justify a compact control here.
A route may pass `403`, `417`, `418`, `440`, and `442` yet still fail the public because:
- the right section is targetable but lands in a still-collapsed panel,
- the only visible label is a vague toggle like “More information” rather than the question the voter needs answered,
- a deadline, exception, or disqualifying condition lives only inside a collapsed disclosure even though most readers need it,
- JavaScript failure leaves all critical panels closed or mislabeled,
- the route reopens through history or a copied link but the answer-bearing disclosure state is lost,
- or the page technically exposes the answer yet makes the voter guess which of many closed panels controls what to do now.

## This is not the same thing as section anchors, reader mode, or generic progressive enhancement

`442` asks whether the right answer-bearing section can be targeted and re-found on a long page.

`440` asks whether extracted or simplified reading surfaces preserve the controlling answer and help boundary.

`403` asks whether the route survives when JavaScript is absent, delayed, or broken.

`443` asks a different question:
**when an official answer is placed inside a hide/reveal container, does the voter have a trustworthy, low-guesswork path to the controlling panel and its meaning across ordinary entry, direct targeting, revisit, and degraded-script conditions?**

A route may pass the earlier controls and still fail `443` if:
- a fragment or same-page link lands near the right region but leaves the controlling panel closed,
- reader mode is fine because the prose is linearized, yet the ordinary live page still hides the crucial answer behind ambiguous disclosure labels,
- the page mostly works without JavaScript, but the no-script fallback does not preserve the same answer visibility or control labeling,
- or the route remains keyboard/screen-reader operable in theory while still requiring too much guessing about which panel to open to find the authoritative answer.

## If most users need most of the information, do not bury it in a collapse-first shell

USWDS’s accordion guidance is especially useful here:
if users need to see most or all of the information, use well-formatted text instead of turning the page into a stack of guessing-oriented reveal controls. (xref: `uswds_accordion_component_page`)

For this archive, that means an official route should not default to collapse-first presentation when:
- nearly every voter needs the same controlling rule,
- a deadline or requirement changes the next action for most readers,
- the top-level summary would be misleading without the hidden qualifier,
- or the route is effectively a mandatory instruction sheet rather than an optional-details page.

The point is not “never use accordions.”
The point is to keep the controlling answer visible enough that the page still behaves like official guidance rather than a scavenger hunt.

## Critical answers should not live only behind generic reveal labels

A disclosure label is part of the answer surface.
If the visible label is weak, the page can fail before the voter ever opens the panel.

For `443`, an official route should prefer labels that expose the real question or condition:
- “Who can return my ballot?”
- “What ID can I use?”
- “What if I moved after the deadline?”
- “How do I fix a rejected signature?”

Weak labels such as “More info,” “Details,” “Expand,” or “Additional resources” are especially dangerous when several collapsed panels sit together and only one actually controls what the voter should do next.

## Reveal-state classes matter

This archive should not flatten all collapsed-content patterns into one bucket. At least four classes matter here:

1. **Native disclosure widgets** — e.g., `<details>/<summary>` where the default closed state visibly hides the body content until the user opens it.
2. **Scripted accordions** — one-or-many-open panel sets controlled by JavaScript and ARIA/button semantics.
3. **Critical-panel-open defaults** — routes that intentionally open the controlling panel by default because most readers need that answer immediately.
4. **Direct-target / revisit reveal behavior** — routes that reopen or reveal the relevant panel when entered through a same-page link, fragment-bearing reference, or ordinary return path.

Those are different states.
A route may work in one and fail another.
The evidence posture should preserve which classes were reviewed and what bounded reveal policy controlled each.

## Direct targeting should reveal the right panel, not just arrive nearby

A copied link, in-page navigation item, or summary jump can correctly identify the answer-bearing section while still leaving the critical disclosure collapsed.

For `443`, a route should review whether direct targeting:
- opens the target panel automatically,
- or exposes an unmistakable, immediately adjacent, meaningful reveal control,
- and does so consistently enough that the voter does not land near the answer but still have to guess how to make it appear.

This is adjacent to `442`, but not the same problem.
A section can be targetable and still fail once the decisive text remains hidden behind a closed panel.

## Degraded-script posture matters because collapse is often implemented by code

USWDS’s current accordion guidance explicitly warns teams not to manually set `hidden` on accordion content areas, because content should remain accessible if JavaScript does not load or is disabled. (xref: `uswds_accordion_component_page`)

That makes `443` partly a degraded-answer-visibility discipline:
if the page uses script-controlled collapse, maintainers should check whether ordinary failure leaves critical content:
- still visible,
- or still revealable with truthful labeling,
- or replaced by a bounded full-view/help instruction instead of a blank shell.

The archive does **not** require every implementation to use the same technical pattern.
It does require the public route to keep the controlling answer from disappearing behind a code-dependent reveal trick.

## Heading structure and disclosure structure have to tell the same truth

USWDS’s accordion accessibility tests say heading levels and consistency have to be tested in the real page context, not assumed from the component alone. (xref: `uswds_accordion_accessibility_tests_page`)

For `443`, maintainers should review whether:
- accordion headers fit the page outline rather than interrupting or flattening it,
- the visible disclosure labels match the page’s real information architecture,
- and assistive-technology users can understand the hidden-vs-visible structure without losing the question they are trying to answer.

A disclosure control that is semantically operable but structurally confusing can still fail the public-answer mission.

## Must-survive facts for collapse-first routes

When an official route uses accordions or disclosures, the following facts should remain visible or be revealable without guesswork whenever they materially change what the voter should do next:
- the question or condition each panel answers,
- the controlling answer or top-line result,
- any deadline, exception, or jurisdiction qualifier that changes meaning,
- the next-step or help path,
- whether the current panel is the operative answer versus optional background,
- and whether the page requires the full live route rather than the collapsed summary alone.

Not every route needs every field.
But if the route expects a voter to rely on collapsed containers, the facts that change the decision should not depend on blind panel-opening behavior.

## Preserve bounded reveal-policy evidence, not user-behavior exhaust

The evidence posture here is about reconstructing whether collapsed-answer routes were reviewed.
The archive should preserve:
- which official routes used accordions or disclosures for answer-bearing content,
- which panels were deemed critical enough to open by default or reveal directly,
- whether labels were reviewed for specificity,
- whether direct-target and revisit behavior were checked,
- whether degraded-script and no-JS posture were reviewed,
- and when the review last occurred.

It should **not** require preserving:
- named-user click telemetry for panel opens,
- individualized expansion histories,
- full session-replay archives of every disclosure interaction,
- or fine-grained behavioral exhaust when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of collapsed-answer posture**, not disclosure-click analytics.

- **Collapsed Answer Surface Digest (CASD):** digest of the bounded disclosure / accordion posture for the official route.
- **Disclosure Reveal Policy Digest (DRPD):** optional digest describing which panels open by default, which require explicit reveal, and which must auto-open on direct targeting.
- **Accordion State Continuity Digest (ASCD):** optional digest describing revisit, fragment-target, and degraded-script reveal checks for critical panels.

## What belongs in the public collapsed-answer payload

Keep the payload **small, route-aware, and reveal-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `collapsed_answer_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_disclosures[]`
- `default_open_policy_note`
- `disclosure_label_specificity_note`
- `direct_target_reveal_note`
- `summary_vs_full_answer_note`
- `no_js_or_failed_js_note`
- `heading_and_outline_alignment_note`
- `keyboard_and_screen_reader_note`
- `zoom_and_small_viewport_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user panel-open telemetry,
- individualized expansion histories,
- full session-replay traces,
- raw frontend debugging logs,
- or speculative interaction analytics that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether controlling answers hidden in accordions or disclosures are actually reachable without guesswork?
- Are the visible disclosure labels specific enough that a voter can predict which panel contains the answer?
- If a link, jump target, or revisit path points to a collapsed answer, does the route reveal the relevant panel or leave a clear reveal control in place?
- Did the office review degraded-script and no-JS posture for critical collapsed content instead of assuming the component library handled it?
- Did the office preserve bounded reveal-policy evidence without collecting user-behavior exhaust?

## How this fits the family map

Accordions, disclosures, and collapsed-answer reveal posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route hides operational meaning behind a reveal control, the route should keep that reveal lane specific, durable, and low-guesswork enough that the right answer does not remain technically present but practically concealed.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-collapsed-answer-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-collapsed-answer-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Accordion component guidance (xref: `uswds_accordion_component_page`)
- USWDS: Accordion accessibility tests (xref: `uswds_accordion_accessibility_tests_page`)
- WAI APG: Accordion pattern (xref: `w3c_wai_aria_apg_accordion_pattern_page`)
- MDN: `<details>` element reference (xref: `mdn_details_element_page`)
- MDN: `<summary>` element reference (xref: `mdn_summary_element_page`)
