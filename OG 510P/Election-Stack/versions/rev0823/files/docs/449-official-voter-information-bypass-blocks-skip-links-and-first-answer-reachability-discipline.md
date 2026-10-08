# 449 — Official voter-information bypass blocks, skip links, and first-answer reachability discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that place repeated site chrome before the answer-bearing main content — including government banners, site headers, megamenus, utility navigation, search modules, breadcrumb trails, alert rails, repeated action bars, or other blocks a sequential user must traverse before reaching the current official answer/help lane**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `380`, which governs site alerts, banners, and interstitial posture,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `440`, which governs reader mode and extracted-main-content posture,
- `441`, which governs page-title and browser-chrome identity,
- `444`, which governs unobscured landing under sticky or fixed chrome,
- `445`, which governs tabbed-panel answer continuity,
- `448`, which governs source order, visual order, and focus-order continuity,
- or the underlying help/contact and special-case authority floors in `344–357`.

It adds one narrow rule:
**if an official voter-information route places repeated navigation or government chrome before the answer-bearing main content, the route should provide a reliable way to bypass those repeated blocks and land at the beginning of the main answer/help lane without making the public tab through the same header burden on every visit.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and audience-aware design. Section508.gov’s current **Guide to Accessible Web Design & Development** says a mechanism should be available to bypass repeated blocks of content, says teams should identify the repetitive content and the location where the skip mechanism should land, says multiple repeated blocks may need bypass mechanisms, and says the link can be invisible until focus so sighted keyboard users can still use it. W3C’s current understanding page for **Bypass Blocks** says the goal is to provide a means of skipping repeating content so users who navigate sequentially can reach the primary content more directly. W3C’s current Technique **G1** says the first interactive item can be a link to the beginning of main content and that activating it should set focus beyond the repeated material. MDN’s current `<a>` reference says a skip link should appear as early as possible in the body, point to the beginning of main content, and is especially useful for keyboard and assistive-technology users. USWDS’s current header guidance matters because header packages depend on `usa-skipnav`, and USWDS’s current banner guidance says the banner should directly follow the `skipnav` component. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wcag21_bypass_blocks_page`; xref: `w3c_wcag21_g1_skip_link_page`; xref: `mdn_html_anchor_element_page`; xref: `uswds_header_component_page`; xref: `uswds_banner_component_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the page has the right answer, but a keyboard user must tab through a long government banner, site header, utility nav, search box, megamenu trigger set, and alert rail before reaching it,
- a nominal “Skip to main content” link exists but lands on an empty wrapper, hidden heading, or non-answer shell that still leaves the user before the real answer lane,
- a mobile menu button, sticky utility header, or expanded banner makes the repeated-block burden materially worse on small screens,
- landmarks exist for some assistive technologies while ordinary sequential focus users still lack a direct entry path,
- or the skip mechanism works on one template but quietly disappears on another page that voters actually use under deadline pressure.

## This is not the same thing as landmarks, unobscured landing, or order continuity

`418` asks whether semantic landmarks, labels, and nonvisual structure make the route understandable.

`444` asks whether the landing target remains visible once the route jumps there.

`448` asks whether visible order, source order, and focus order tell the same story.

`449` asks a different question:
**before a user even reaches the answer lane, can they bypass the repeated page chrome in a bounded, reliable way?**

A route may pass the earlier controls and still fail `449` if:
- the page has a valid `<main>` landmark but no practical way for a sequential keyboard user to reach it quickly,
- the skip target is technically correct yet lands above another repeated control cluster the voter still must traverse,
- the target is visible and unobscured once reached, but the bypass mechanism is absent, broken, or inconsistent across templates,
- or the order is perfectly logical while still forcing the user through dozens of repeated links every time.

## Repeated government chrome is part of the task cost

Election routes often begin with legitimate repeated material:
- the official government banner,
- the site header and identity block,
- utility navigation,
- a sitewide search control,
- megamenu navigation,
- emergency or status rails,
- breadcrumb trails,
- and repeated action strips.

Those elements are not inherently wrong.
But for this archive, they become part of the **public answer-delivery cost** when a voter who already knows the route must still traverse them before reaching the answer-bearing main content.

When the public task is “Where do I vote today?”, “Can I cure this ballot?”, “What ID is required?”, or “Which office handles this special case?”, repeated chrome is not neutral decoration.
It is either a bounded burden with a bypass path, or it is part of the failure surface.

## The bypass target should be the beginning of the main answer lane, not a decorative shell

Section508.gov’s current guide explicitly says teams should identify the location where the skip mechanism should land. W3C’s current Technique G1 says the link should go directly to the main content area. MDN’s current anchor reference likewise shows the skip link targeting the beginning of main content. (xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wcag21_g1_skip_link_page`; xref: `mdn_html_anchor_element_page`)

For this archive, that means the office should review whether the bypass target lands at:
- the start of the main answer/help lane,
- the controlling heading for the current page state,
- the start of the decisive lookup/result area,
- or another clearly justified main-content entry point.

It should **not** quietly land on:
- an empty container,
- a decorative hero shell,
- a wrapper above more repeated controls,
- a hidden element,
- or a heading that still leaves the voter before the actual current answer.

## One skip link is not always enough when the repeated-block structure is heavier

Section508.gov’s current guide says that if there are multiple repeated blocks of content, provide a mechanism to bypass each block. W3C’s current bypass-blocks understanding page also frames repeated blocks more broadly than one navigation bar. (xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wcag21_bypass_blocks_page`)

For this archive, the office does **not** need a maximal skip-link catalog on every page.
It does need to notice when one top-of-page bypass is insufficient because the route still presents another large repeated block before the answer lane, such as:
- a government banner plus a large site header plus a megamenu,
- a route-local in-page navigation rail before the answer content,
- or a repeated task-selector strip that appears before every answer view.

The bounded question is whether the public can reach the answer lane without repetitive traversal, not whether the page technically contains one link named “skip.”

## Mobile headers, megamenus, and banners can make bypass failures worse

USWDS’s current header guidance is useful here because common federal-style headers depend on `usa-skipnav`, and its banner guidance explicitly says the banner should directly follow the skipnav component. (xref: `uswds_header_component_page`; xref: `uswds_banner_component_page`)

That matters because repeated-block burden is often worse on smaller screens and stressed contexts:
- the mobile menu button comes before the answer lane,
- the header occupies more vertical space,
- the government banner expands,
- utility actions stack above content,
- and the first-focus path may become much longer than on desktop.

A route that is tolerable on a wide screen may still fail `449` when the actual first-contact keyboard path on mobile or zoomed views is dominated by repeated chrome.

## Landmarks help, but they do not erase the sequential-entry question

Nonvisual landmarks remain important and are governed in `418`.
But this surface is narrower and more practical:
**does the route provide a bounded first-entry path into main content for users who navigate sequentially through interactive content?**

The office may rely on semantic structure as part of the answer.
It should still review whether the route offers a real operational bypass path rather than assuming every user will use a landmark rotor, browser extension, or assistive-technology-specific command set.

## Preserve bounded bypass evidence, not individualized traversal exhaust

The evidence posture here is about reconstructing whether repeated-block burden was reviewed.
The archive should preserve:
- which official routes were checked,
- which repeated blocks were considered material,
- where the primary bypass path lands,
- whether mobile/header/banner variants were reviewed,
- whether the first-focus path into main content was reviewed,
- and when the review last occurred.

It should **not** require preserving:
- named-user keystroke logs,
- raw session replay,
- individualized assistive-technology traces,
- per-user focus telemetry,
- or full navigation exhaust when bounded bypass evidence is sufficient.

## Canonical digest artifacts

Publish **small digests of bypass posture**, not interaction exhaust.

- **Bypass Reachability Surface Digest (BRSD):** digest of the bounded repeated-block / skip-to-answer posture for the official route.
- **Main Entry Target Digest (METD):** optional digest describing where the primary bypass path lands and why that target is treated as the answer-bearing entry point.
- **Repeated Block Inventory Digest (RBID):** optional digest describing which repeated blocks were deemed material for the route.

## What belongs in the public bypass-blocks payload

Keep the payload **small, route-aware, and entry-path-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `bypass_blocks_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `repeated_blocks[]`
- `primary_bypass_paths[]`
- `main_entry_target_note`
- `first_focusable_item_note`
- `mobile_header_and_banner_note`
- `route_local_repeated_block_note`
- `landmark_and_skipnav_interplay_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user focus traces,
- raw keyboard recordings,
- individualized assistive-technology logs,
- exhaustive DOM dumps for every template,
- or telemetry whose only purpose is to prove users tabbed a lot.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify which routes place significant repeated blocks before the main answer lane?
- Is there a practical bypass mechanism that lands at the start of main content rather than at a decorative or non-answer wrapper?
- Were mobile/header/banner variants checked where the repeated-block burden is often worse?
- Is the route relying on landmarks or semantics alone when a sequential entry path still matters?
- Did the office preserve a compact public record of the bypass review without retaining user-level interaction exhaust?

## How this fits the family map

Bypass blocks, skip links, and first-answer reachability is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if repeated government or site chrome sits in front of a current official answer, the route should offer a bounded way to bypass that repeated burden and enter the answer lane directly.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-bypass-blocks-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-bypass-blocks-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Section508.gov: Guide to Accessible Web Design & Development (xref: `section508_guide_accessible_web_design_development_page`)
- W3C WAI: Understanding SC 2.4.1 Bypass Blocks (xref: `w3c_wcag21_bypass_blocks_page`)
- W3C WAI Technique G1: link at top of page to main content (xref: `w3c_wcag21_g1_skip_link_page`)
- MDN: `<a>` element / skip links guidance (xref: `mdn_html_anchor_element_page`)
- USWDS: Header (xref: `uswds_header_component_page`)
- USWDS: Banner (xref: `uswds_banner_component_page`)
