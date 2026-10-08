# 460. Official voter-information navigation menus, fly-outs, and destination-continuity discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes where the controlling destination, office page, or current answer lane is reached through site navigation menus rather than through the ordinary visible page body** — for example a header dropdown, fly-out menu, hamburger/drawer navigation, mega-menu, or similar expandable navigation structure — where:

- the right official destination already exists on the official site,
- but it is hard to discover, distinguish, or re-find because it sits behind an expandable navigation posture,
- the navigation makes hover, timing, or precision movement feel like the real gate to the answer,
- or the menu semantics misstate whether a control is a page link, a submenu toggle, or an application-style command menu.

The concern here is not simply that a site has navigation.
It is the narrower failure mode where a voter is already using the right official site, but the route to the controlling page is trapped in a navigation posture that makes the destination harder to discover, interpret, recover, or trust as a durable official path.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Header** guidance matters because it says top-level navigation items should receive tab focus and that teams should avoid using hover to expand dropdown lists, since hover is difficult for some users and does not work on touch screens. WAI’s current **Menus Tutorial** matters because it treats menus as critical parts of page operability, says their structure and states should be marked up and styled clearly, and says fly-out menus should work for both mouse and keyboard users. WAI’s current **Fly-out Menus** guidance matters because it says fly-out menus provide an overview of site hierarchy, can be difficult or impossible for some users with reduced dexterity, and should provide other ways to reach submenu items such as repeating them on the parent page. WAI APG’s current **Disclosure Navigation Menu** example matters because it says ordinary site navigation should generally use disclosure-style navigation rather than the ARIA `menu` role, and because it uses `Esc`/focus-out closure behavior to keep dropdown posture bounded and predictable. MDN’s current **ARIA `menu` role** reference matters because it says site navigation should not use the `menu` role; ordinary website navigation should use native `nav` / lists of links, while `menu` is reserved for composite widgets that need application-style focus management. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_header_component_page`; xref: `w3c_wai_menus_tutorial_page`; xref: `w3c_wai_flyout_menus_page`; xref: `w3c_wai_aria_apg_disclosure_navigation_example_page`; xref: `mdn_menu_role_page`)

So this archive treats navigation menus as their own public-surface problem:
**the right official destination may already exist on the site, but only inside a navigation structure whose hover dependence, label ambiguity, submenu posture, or weak parent-page fallback makes the answer route harder to find and trust.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `417` keyboard navigation, focus visibility, and logical order, which governs broader sequential operability;
- `421` touch target size, hover-revealed content, and pointer operability, which governs coarse-pointer and hover-only exposure hazards across the whole route;
- `442` section anchors and fragment-target continuity, which governs in-page navigation within a page already reached;
- `449` bypass blocks and skip links, which governs getting past repeated chrome to the main answer lane;
- `454` breadcrumb trails, which govern parent-path continuity after a page is already open;
- or `459` answer overlays/dialogs/drawers, which govern answer-bearing content placed in transient overlay layers.

`460` exists only for the case where the answer-bearing **destination** is concealed or destabilized by a navigation menu posture — dropdown, fly-out, mega-menu, hamburger menu, or related structure — and the voter needs the path to remain honest about what expands, what links, what is current, and how to reach the same destination again.

## Menu expansion should be deliberate, not hover-gated

USWDS’s current header guidance says teams should avoid using hover to expand dropdown lists and instead expand them on click or with keyboard navigation. WAI’s current menus tutorial and fly-out menus guidance matters because fly-out menus should work for mouse and keyboard users and because users with reduced dexterity may have trouble or be unable to operate menus that disappear with small pointer movement. (xref: `uswds_header_component_page`; xref: `w3c_wai_menus_tutorial_page`; xref: `w3c_wai_flyout_menus_page`)

For this archive, official navigation should not:

- make a critical voter-information destination appear only during brief pointer hover,
- require fine-grained pointer dwell to keep a submenu open,
- hide the real destination behind a hover-only mega-menu on desktop while presenting a different path on touch/mobile,
- or make a submenu vanish so quickly that the voter cannot inspect the available official destinations.

A voter should be able to tell, in bounded form:

- which top-level item opens a submenu,
- which item is a direct link versus a disclosure/toggle,
- whether the current official page sits within that navigation branch,
- and how to reach the same destination again without reproducing fragile pointer choreography.

## Parent pages should remain useful when submenus are hard to operate

WAI’s current fly-out menus guidance says other ways to reach submenu items should be provided, for example by repeating them on the page of the parent menu item. That matters because a voter may know roughly which official section they need without being able to keep a fly-out open long enough to choose the exact nested destination. (xref: `w3c_wai_flyout_menus_page`)

So for this archive, a navigation menu should be cautious about making the submenu the **only** practical route to a controlling official destination when:

- the destination is high value or time sensitive,
- the submenu contains several closely spaced options,
- the menu posture differs materially between desktop and mobile,
- or the voter may arrive needing a broad category first and the exact page second.

This document does **not** ban nested navigation.
It says the archive wants an honest distinction between **site overview** and **precision submenu targeting**.
If the submenu contains controlling election destinations, the parent page should usually remain a usable way station rather than a decorative dead end.

## Use ordinary site-navigation semantics, not application-menu semantics

MDN’s current `menu`-role reference says site navigation should not use `role="menu"`; instead, ordinary website navigation should use native `nav` or lists of links, and `menu` should be reserved for composite widgets requiring focus management. APG’s current disclosure-navigation example reinforces that ordinary site navigation does not need all the complex keyboard interactions expected from ARIA menu and menubar widgets. (xref: `mdn_menu_role_page`; xref: `w3c_wai_aria_apg_disclosure_navigation_example_page`)

For this archive, a navigation menu fails this surface when:

- site links are presented with application-menu semantics that imply desktop-style command behavior rather than ordinary page navigation,
- submenu toggles and destination links are not distinguishable,
- keyboard expectations become inconsistent because a site-navigation bar imitates an app menubar without fully behaving like one,
- or the semantics hide the actual page hierarchy instead of clarifying it.

The goal is not ARIA maximalism.
The goal is that the site’s ordinary election-navigation structure tells one coherent story about where destinations live and how they open.

## Current location and same-destination refindability should stay legible

WAI’s current menus tutorial says people with limited attention or short-term memory benefit from clear and distinct menus with easily identifiable states, such as the current page. APG’s current disclosure-navigation example uses a named navigation landmark and preserves predictable dropdown closure when focus leaves the region or `Esc` is pressed. (xref: `w3c_wai_menus_tutorial_page`; xref: `w3c_wai_aria_apg_disclosure_navigation_example_page`)

A route fails this surface when the navigation is visually large but directionally vague:

- the voter cannot tell which menu branch contains the current page,
- the menu opens without showing which item is current or selected,
- closing the menu leaves no stable clue about what section the voter is in,
- or compact/mobile navigation changes labels or hierarchy enough that re-finding the same official destination becomes guesswork.

For this archive, navigation should preserve enough bounded context that a voter can tell:

- what section or branch they are in,
- what submenu is open,
- what destination is current,
- and how to reopen the same branch or parent route without browsing the whole site again.

## Compact/mobile navigation should not silently fork the answer path

USWDS’s current header guidance, plus the general federal emphasis on touch and keyboard operability, matters here because the same official navigation often changes from a horizontal header to a hamburger button, drawer, or accordion navigation at smaller widths. The archive should treat that as a presentation change, not an excuse for destination drift. (xref: `uswds_header_component_page`)

So this archive wants extra caution when navigation compresses across layouts:

- hamburger labels should still communicate that official destinations live inside,
- mobile drawers should preserve the same section naming and hierarchy truth as desktop navigation,
- compact navigation should not remove the only visible route to key offices, deadlines, or help pages,
- and the voter should not have to infer that a desktop submenu destination moved somewhere entirely different on mobile.

## Preserve bounded navigation evidence, not per-user menu telemetry

The evidence posture here is about whether the official site kept menu-based destinations discoverable and recoverable.
The archive should preserve:

- which official routes rely on expandable navigation to expose controlling destinations,
- whether the navigation uses hover, click, disclosure buttons, or compact/mobile drawers,
- whether parent pages remain usable fallback routes,
- whether site-navigation semantics remain ordinary and truthful,
- whether current-location and same-destination refindability stay legible across layouts,
- and whether keyboard/touch/compact variants preserve the same bounded route meaning.

It should **not** require preserving:

- per-user click trails through menus,
- hover telemetry,
- pointer-path recordings,
- session replay,
- or individualized menu-open histories merely to prove that the destination once existed in a dropdown.

## Canonical digest artifacts

Publish **small digests of navigation-menu posture**, not interaction exhaust.

- **Navigation Menu Surface Digest (NMSD):** digest of the bounded navigation posture for an official route family.
- **Destination Continuity Digest (DCD):** optional digest describing parent-page fallback, current-branch identity, and same-destination re-findability.
- **Navigation Semantics Integrity Digest (NSID):** optional digest describing whether ordinary site-navigation semantics remain truthful across desktop and compact variants.

## What belongs in the public navigation-menu payload

Keep the payload **small, route-aware, and destination-focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `navigation_menu_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `navigation_menu_routes[]`
- `menu_trigger_posture_note`
- `submenu_indicator_note`
- `site_navigation_semantics_note`
- `parent_page_fallback_note`
- `current_location_note`
- `hover_and_touch_note`
- `keyboard_and_escape_note`
- `compact_mobile_note`
- `same_destination_refindability_note`
- `direct_link_visibility_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- individualized menu-open histories,
- hover telemetry,
- named-user click sequences,
- session replay,
- or internal experimentation notes that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official voter-information destinations are exposed mainly through expandable site navigation menus?
- Does the navigation open deliberately through click/tap/keyboard rather than fragile hover-only posture?
- Can the voter tell which items are direct links, which items open submenus, and which section or page is current?
- If the submenu is hard to operate, does a usable parent page or other official path still expose the same destination family?
- Do compact/mobile navigation variants preserve the same section naming and destination continuity as desktop navigation?
- Did the office preserve bounded navigation evidence without retaining individualized interaction exhaust?

## How this fits the family map

Navigation menus, fly-outs, and destination continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information site places the controlling destination inside expandable navigation, the route should remain honest enough that “it’s in the menu” does not silently become “the path is hover-fragile, semantically misleading, and hard to find again.”

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-navigation-menu-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-navigation-menu-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Header (xref: `uswds_header_component_page`)
- WAI: Menus Tutorial (xref: `w3c_wai_menus_tutorial_page`)
- WAI: Fly-out Menus (xref: `w3c_wai_flyout_menus_page`)
- WAI APG: Disclosure Navigation Menu example (xref: `w3c_wai_aria_apg_disclosure_navigation_example_page`)
- MDN: ARIA `menu` role (xref: `mdn_menu_role_page`)
