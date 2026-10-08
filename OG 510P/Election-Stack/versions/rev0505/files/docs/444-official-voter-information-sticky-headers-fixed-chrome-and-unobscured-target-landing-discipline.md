# 444 — Official voter-information sticky headers, fixed chrome, and unobscured target landing discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that use sticky headers, fixed banners, persistent in-page navigation, cookie or emergency bars, or scripted scroll-to-section behavior that can partially cover the answer-bearing heading or top lines of a targeted section after a jump, fragment navigation, or same-page reveal action**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `414`, which governs embedded browsers, webviews, and constrained-container posture,
- `417`, which governs keyboard focus order and visibility,
- `421`, which governs touch targets, hover-revealed content, and pointer operability,
- `441`, which governs browser-tab and history-entry identity,
- `442`, which governs section anchors, in-page navigation, and fragment-target continuity,
- or `443`, which governs accordions, disclosures, and collapsed-answer reveal continuity.

It adds one narrow rule:
**if an official voter-information route expects people to reach an answer by jumping, scrolling, or revealing a targeted section, persistent chrome should not cover the section heading, first controlling lines, or the reveal control the voter needs to act on that answer.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes structure, clarity, accessibility, and usability. USWDS’s current **In-page navigation** guidance says the component helps users navigate long pages and is displayed in a sticky container that remains fixed while the page scrolls. MDN’s current `scroll-padding-top` reference says authors can define offsets for the optimal viewing region to exclude areas obscured by fixed-positioned toolbars or sidebars. MDN’s current `scroll-margin-top` reference says the property can create custom spacing when using `scrollIntoView()`, and its current `scrollIntoView()` documentation says that spacing is often useful when there is a fixed header on the page. WAI’s WCAG 2.2 Technique C43 gives a concrete accessibility technique for using CSS `scroll-padding` to un-obscure content under a fixed-position banner. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_in_page_navigation_component_page`; xref: `mdn_scroll_padding_top_property_page`; xref: `mdn_scroll_margin_top_property_page`; xref: `mdn_scroll_into_view_method_page`; xref: `w3c_wcag22_c43_scroll_padding_unobscure_content_page`)

That is enough to justify a compact control here.
A route may pass `442` and still fail the public because:
- the copied fragment lands on the right section but the heading is hidden under a sticky header,
- the page opens the right disclosure panel but a fixed banner covers the first line that changes what the voter should do,
- a persistent in-page navigation rail or toolbar makes the page *look* as if the jump missed,
- a responsive header becomes taller on mobile or zoomed views and silently obscures the target,
- or scripted `scrollIntoView()` behavior puts the right element at the very top edge even though the page’s own chrome sits on top of it.

## This is not the same thing as section-target continuity or collapsed-answer reveal

`442` asks whether the right answer-bearing section can be targeted and re-found.

`443` asks whether the controlling answer stays revealable when it lives inside an accordion or disclosure.

`444` asks a different question:
**once the route does target or reveal the right place, is that place actually visible, legible, and not physically covered by persistent chrome?**

A route may pass the earlier controls and still fail `444` if:
- the fragment target exists and is stable, but the landing position hides the heading under a sticky masthead,
- the controlling panel opens, but a cookie or emergency bar covers the first operative sentence,
- the target is technically in view for the browser while still not meaningfully visible to the voter,
- or mobile/zoom layouts change header height so a formerly safe landing offset becomes unsafe.

## Fixed chrome is part of the answer-delivery surface

For this archive, persistent page chrome is not just decoration.
If a voter is told to “jump to ID requirements,” “open ballot cure steps,” or “review the late-mail-ballot exception,” then the top of that destination needs to remain visibly above any fixed or sticky interface.

This is especially important when the first one or two lines of a target section carry the operative qualifier, such as:
- a deadline basis,
- a jurisdiction-specific exception,
- a warning that the section applies only to some voters,
- or the button/summary control that must be activated to see the rest of the answer.

## Sticky or fixed UI can make a correct jump look like a broken jump

USWDS’s in-page navigation guidance explicitly describes sticky navigation on long pages. MDN’s scroll-padding and scroll-margin guidance explicitly describes fixed-position toolbars and fixed headers as sources of obscured content. (xref: `uswds_in_page_navigation_component_page`; xref: `mdn_scroll_padding_top_property_page`; xref: `mdn_scroll_margin_top_property_page`)

That means this failure mode should be treated as ordinary public-surface breakage, not frontend trivia.
A voter can be on the right page and at the right section while still perceiving the site as wrong because the heading, opening lines, or reveal control are tucked underneath persistent UI.

## Offset policy should follow the live chrome, not a remembered desktop header size

A bounded review here should check whether the landing offset reflects the chrome that is actually present in the real route state:
- desktop and mobile header variants,
- zoomed or reflowed layouts,
- emergency or maintenance banners,
- sticky “On this page” navigation,
- and other persistent bars that appear only after scrolling or interaction.

The archive does **not** require a single technical mechanism.
It does require the page to keep the target unobscured in the conditions voters are likely to encounter.

## Scripted scroll behavior and fragment navigation must tell the same truth

MDN’s `scrollIntoView()` documentation says authors can use `scroll-margin-top` to create custom spacing, often for pages with fixed headers. MDN’s `scroll-padding-top` documentation says the target region can exclude obscured areas such as fixed-positioned toolbars. (xref: `mdn_scroll_into_view_method_page`; xref: `mdn_scroll_margin_top_property_page`; xref: `mdn_scroll_padding_top_property_page`)

For this archive, that means maintainers should review whether:
- browser-native fragment jumps,
- same-page navigation links,
- programmatic “jump to section” buttons,
- and panel-open / reveal code that scrolls the page

all land the voter in a meaningfully visible place instead of relying on different offset assumptions.

## The answer-bearing top lines should survive zoom, small screens, and banner changes

WAI’s Technique C43 is useful because it frames unobscured content as an accessibility problem, not merely a cosmetic one. (xref: `w3c_wcag22_c43_scroll_padding_unobscure_content_page`)

For `444`, a route should review whether the top of the target remains visible when:
- zoom increases header height,
- a small-screen navigation bar occupies more vertical space,
- a sticky in-page navigation element appears,
- or a temporary banner is present during a live election period.

A route that works only when no extra chrome is active is too brittle for official public-service use.

## Preserve bounded landing-visibility evidence, not user scroll telemetry

The evidence posture here is about reconstructing whether unobscured target landing was reviewed.
The archive should preserve:
- which official routes were checked for sticky/fixed chrome overlap,
- which critical jump or reveal targets were deemed answer-bearing,
- which persistent UI elements were included in the landing-visibility review,
- whether mobile/zoom/banner variants were checked,
- whether fragment and scripted scroll behavior were both reviewed,
- and when the review last occurred.

It should **not** require preserving:
- named-user scroll telemetry,
- individualized viewport recordings,
- raw session-replay archives,
- precise per-user intersection traces,
- or heatmaps when bounded landing-visibility evidence is sufficient.

## Canonical digest artifacts

Publish **small digests of unobscured-target posture**, not scroll analytics.

- **Unobscured Target Surface Digest (UTSD):** digest of the bounded sticky-header / fixed-chrome landing posture for the official route.
- **Landing Offset Review Digest (LORD):** optional digest describing which persistent UI elements were included in landing-offset checks.
- **Target Visibility Continuity Digest (TVCD):** optional digest describing whether critical fragment, jump-link, and reveal-trigger landings stay visibly above persistent chrome across ordinary layout variants.

## What belongs in the public unobscured-target payload

Keep the payload **small, route-aware, and landing-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `unobscured_target_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_targets[]`
- `persistent_chrome_inventory[]`
- `fragment_landing_visibility_note`
- `scripted_scroll_visibility_note`
- `mobile_and_zoom_offset_note`
- `banner_or_alert_overlap_note`
- `collapsed_or_revealed_target_note`
- `accessibility_alignment_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user scroll traces,
- raw viewport recordings,
- fine-grained heatmaps,
- individualized device fingerprints,
- or speculative animation/debug logs that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether sticky headers, fixed banners, or persistent navigation obscure answer-bearing section landings?
- Were critical fragment targets and scripted scroll/reveal actions checked for meaningful visibility, not just technical target resolution?
- Did the office review mobile, zoom, and temporary-banner variants rather than assuming one desktop header height?
- If the route opens a collapsed answer or jumps to a section, does the heading and first controlling lines remain visible above persistent chrome?
- Did the office preserve bounded landing-visibility evidence without collecting user scroll telemetry?

## How this fits the family map

Sticky headers, fixed chrome, and unobscured target landing is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route expects the public to land on or reveal a specific answer-bearing target, the route should keep that target visibly clear of persistent chrome instead of allowing a correct landing to look broken or incomplete.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-unobscured-target-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-unobscured-target-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: In-page navigation (xref: `uswds_in_page_navigation_component_page`)
- MDN: `scroll-padding-top` reference (xref: `mdn_scroll_padding_top_property_page`)
- MDN: `scroll-margin-top` reference (xref: `mdn_scroll_margin_top_property_page`)
- MDN: `scrollIntoView()` method (xref: `mdn_scroll_into_view_method_page`)
- WAI: WCAG 2.2 Technique C43 (xref: `w3c_wcag22_c43_scroll_padding_unobscure_content_page`)
