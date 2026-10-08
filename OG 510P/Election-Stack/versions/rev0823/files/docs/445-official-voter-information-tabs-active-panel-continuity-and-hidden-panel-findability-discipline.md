# 445 — Official voter-information tabs, active-panel continuity, and hidden-panel findability discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that place answer-bearing content inside tabbed interfaces where one panel is visible at a time and other panels remain hidden until a tab is selected or activated**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `421`, which governs touch targets, hover-revealed content, and pointer operability,
- `438`, which governs bookmark/share/revisit continuity,
- `439`, which governs history restore and hidden-return freshness,
- `441`, which governs browser-tab and history-entry identity,
- `442`, which governs section anchors and fragment-target continuity,
- `443`, which governs accordions, disclosures, and collapsed-answer reveal continuity,
- or `444`, which governs unobscured target landing under sticky or fixed chrome,
- or `474`, which governs ordinary browser find-in-page posture and first-match truthfulness across a route rather than tab-specific active-panel continuity itself.

It adds one narrow rule:
**if an official voter-information route expects people to learn or act on an answer inside tabs, the controlling answer should not depend on guessing which tab is active, on vague tab labels, or on hidden panels that ordinary users cannot reliably reveal, re-find, or deep-link into.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes hierarchy, structure, clarity, accessibility, usability, and accuracy. WAI’s current **Tabs Pattern** says a tabbed interface is a set of layered tab panels that display one panel at a time and that activating a tab hides the previously displayed panel while making the new panel visible. MDN’s current `tab` role reference says the active tab should expose `aria-selected="true"`, inactive associated panels should stay hidden until selected, and keyboard users may move through the tablist with arrow keys and activate a tab with `Enter` or `Space`. MDN’s current `tabpanel` role reference says all inactive tabpanels must be hidden to all users, that the active tabpanel should remain keyboard-reachable, and that the tab and tabpanel should stay explicitly associated. WAI’s current **Tabs with Manual Activation** example says manual activation is recommended unless panel content is instant because keyboard users otherwise need a separate focus step and activation step before the panel changes. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_aria_apg_tabs_pattern_page`; xref: `mdn_tab_role_page`; xref: `mdn_tabpanel_role_page`; xref: `w3c_wai_aria_apg_tabs_manual_example_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the correct answer is on the page but only inside a nondefault tab with a vague label such as “More” or “Details”,
- the heading and page title imply one answer while the currently visible panel shows a different mode, county, or voting channel,
- the keyboard focus can reach the tablist but the decisive panel does not change until an extra activation step the route never signals,
- the page can be copied or revisited but the visible default tab on reopen is not the answer-bearing panel,
- or the route technically contains the right panel while ordinary findability paths still leave that panel hidden.

## This is not the same thing as section targets, disclosures, or browser chrome identity

`442` asks whether the correct section on a page can be targeted and re-found.

`443` asks whether collapsed content in an accordion or disclosure can be revealed.

`441` asks whether the route is distinguishable as a tab title or history entry.

`445` asks a different question:
**when one page contains several peer panels, does the route keep the answer-bearing panel legible, discoverable, and continuously reachable instead of burying it behind the wrong active tab state?**

A route may pass the earlier controls and still fail `445` if:
- fragments and jump links work, but they only land inside the currently visible tab and not the answer-bearing one,
- the tab labels exist, but they do not tell voters which panel contains the operative rule,
- the page reopens correctly while silently resetting to a default tab that does not reflect the current answer,
- or a manual-activation tablist leaves keyboard users focused on the right label while the visible panel still shows the wrong content.

## Tab labels are part of the answer-delivery surface

In this archive, tabs are not merely cosmetic layout.
If a voter needs to distinguish “Vote by mail,” “Early voting,” “Election Day,” “Military and overseas,” or “Students,” then the tab labels themselves are part of the official answer path.

That means the route should not make the public infer the governing answer from opaque tab names, decorative abbreviations, or panel arrangements that only make sense to maintainers.
A tabbed route should help people identify:
- which panel is active now,
- which panel controls the current question,
- whether the other panels are alternatives, exceptions, or adjacent tasks,
- and how to get back to help or a broader official overview when the current panel is not the right one.

## Focus and selection can diverge in tabs

WAI’s tabs guidance and example matter here because a tab may receive keyboard focus before its panel becomes visible when the implementation uses manual activation. MDN’s tabs guidance likewise distinguishes focus movement from selection and panel display. (xref: `w3c_wai_aria_apg_tabs_pattern_page`; xref: `w3c_wai_aria_apg_tabs_manual_example_page`; xref: `mdn_tab_role_page`; xref: `mdn_tabpanel_role_page`)

That means a route can look keyboard-capable while still hiding the actual answer from a user who has only focused the tab label and has not yet triggered selection.
For this archive, the question is not merely “can focus enter the tablist?”
It is:
**does the route keep the answer-bearing panel continuously understandable when focus, selection, and visible content are not the same thing?**

## Hidden panels should not become dead zones for public findability

MDN’s current `hidden` global-attribute guidance says hidden content is not presented to the user, that hidden content should generally not be linked from visible elements, and that `hidden="until-found"` is a special case that can be revealed by find-in-page or fragment navigation. MDN’s current `beforematch` guidance says the browser can reveal `hidden="until-found"` content before scrolling to it, but also notes this is a recently available feature that works across the latest browsers and devices only since December 2025. (xref: `mdn_hidden_global_attribute_page`; xref: `mdn_beforematch_event_page`)

For this archive, that means offices should **not** assume that hidden tab panels will magically become discoverable through copied fragments, search-in-page, or browser affordances.
A route may choose to support advanced hidden-panel reveal behavior, but it should not make that the only recovery path for decisive public information.
If the answer matters enough to be part of the current official route, the route should provide a plain, ordinary way to expose the right panel.

## Default-visible posture matters when the page first opens or later reopens

Because tabs show one panel at a time, the default visible panel and any restored active-panel state are part of the effective public answer.
If the route presents a generic overview panel first while the real operative rule sits in another tab, the office should either:
- make that structure explicit,
- direct people clearly to the controlling tab,
- or avoid tabs for that answer lane.

This archive does **not** require one universal design pattern.
It does require the public not be forced into trial-and-error panel hunting when the route claims to answer a concrete voting question.

## Preserve bounded active-panel evidence, not panel-by-panel user analytics

The evidence posture here is about reconstructing whether tabbed answer delivery was reviewed.
The archive should preserve:
- which official routes use tabs for answer-bearing content,
- which tab sets contain decisive deadlines, exceptions, or next-step instructions,
- which panel is default-visible,
- whether keyboard focus, selection, and visible panel behavior were reviewed,
- whether copied/reopened/deep-linked states were reviewed where relevant,
- and when the review last occurred.

It should **not** require preserving:
- named-user clickstream traces,
- individualized panel-switch analytics,
- raw session-replay archives,
- per-user hover telemetry,
- or full navigation histories when bounded active-panel evidence is sufficient.

## Canonical digest artifacts

Publish **small digests of tabbed-answer posture**, not interaction exhaust.

- **Tabbed Answer Surface Digest (TASD):** digest of the bounded tabs / active-panel posture for the official route.
- **Active Panel Continuity Digest (APCD):** optional digest describing default-visible, restored, and explicitly selected panel continuity for key routes.
- **Hidden Panel Recovery Digest (HPRD):** optional digest describing how answer-bearing hidden panels are revealed through ordinary public paths.

## What belongs in the public tabbed-answer payload

Keep the payload **small, route-aware, and panel-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `tabbed_answer_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `tab_sets[]`
- `default_visible_panel_note`
- `label_clarity_note`
- `keyboard_activation_note`
- `deep_link_or_direct_reveal_note`
- `hidden_panel_findability_note`
- `state_restore_alignment_note`
- `mobile_variant_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user panel histories,
- raw per-user click analytics,
- individualized assistive-technology traces,
- exhaustive front-end debug logs,
- or speculative behavior traces that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether decisive voter information is hidden inside tabs at all?
- Are the tab labels meaningful enough to tell users which panel carries the operative answer?
- When keyboard focus reaches the tablist, does the answer-bearing panel become visible in a way the route makes understandable?
- If the route is copied, reopened, or linked into a specific answer lane, is there an ordinary way to reveal the right panel without trial and error?
- Did the office preserve bounded active-panel evidence without collecting individualized browsing telemetry?

## How this fits the family map

Tabs, active-panel continuity, and hidden-panel findability is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses tabs to present peer answer panels, the route should keep the controlling panel meaningfully visible and discoverable instead of making the public guess which hidden panel contains the real rule.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-tab-panel-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-tab-panel-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- WAI APG: Tabs Pattern (xref: `w3c_wai_aria_apg_tabs_pattern_page`)
- MDN: `tab` role reference (xref: `mdn_tab_role_page`)
- MDN: `tabpanel` role reference (xref: `mdn_tabpanel_role_page`)
- WAI APG: Tabs with Manual Activation example (xref: `w3c_wai_aria_apg_tabs_manual_example_page`)
- MDN: HTML `hidden` global attribute (xref: `mdn_hidden_global_attribute_page`)
- MDN: `beforematch` event (xref: `mdn_beforematch_event_page`)
