# 442 — Official voter-information section anchors, in-page navigation, and fragment-target continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **section headings with stable targets, jump links, in-page navigation lists, same-page “On this page” menus, copied fragment links, and other section-level ways of re-finding the exact place on a long official voter-information page where the controlling answer lives**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search and autocomplete,
- `379`, which governs redirects, expired pages, and stale-link recovery,
- `417`, which governs keyboard focus order and visibility,
- `418`, which governs screen-reader landmarks, labels, and live updates,
- `438`, which governs whether the current official URL is safe to bookmark, copy, or share at all,
- `440`, which governs what survives when a browser extracts a simplified reading surface,
- or `441`, which governs whether the route is distinguishable in browser/app chrome.

It adds one narrow rule:
**if an official voter-information answer lives on a long or sectioned page and the office expects people to land on, copy, or re-find a specific section, that route should expose legible section targets, keep fragment/jump-link behavior aligned with the actual heading structure, and avoid letting ordinary revisions silently strand section-level references at the wrong place or no place at all.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes hierarchy, structure, clarity, accessibility, usability, and accuracy. Digital.gov’s current plain-language design guidance says federal web content should help people get information and follow requirements, and says pages should be logically structured with key information at the top, use heading levels consistently and appropriately to create hierarchy, and use heading terms that are clear and descriptive. USWDS’s current **In-page navigation** guidance says in-page navigation helps users understand the contents of a lengthy page and navigate to the section they need to read, and its current accessibility tests say heading order, link purpose, logical sequence, and current-location cues have to be verified in implementation. USWDS’s current **Summary box** guidance says that if you are listing headings for internal page navigation, you should use jump links or side navigation rather than a summary box, and that when linking to more information on the same page you should explain where the anchor link will take the reader. MDN’s current **URI fragment** reference says the fragment identifies a specific part of a resource, is processed by the browser after retrieval, and can point to an element `id` so the browser scrolls to that location. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_headings_page`; xref: `uswds_in_page_navigation_component_page`; xref: `uswds_in_page_navigation_accessibility_tests_page`; xref: `uswds_summary_box_component_page`; xref: `mdn_uri_fragment_page`)

That is enough to justify a compact control here.
A route may pass `438`, `440`, and `441` yet still fail the public because:
- the page URL is safe to keep, but the copied section link lands at the top of a long page with no obvious way to find the controlling section again,
- the browser tab/title is correct, but the answer itself is buried halfway down a dense page with no stable section target,
- the page exposes a same-page navigation list whose labels, order, or current-location cues no longer match the live headings,
- a heading text change or content reorganization silently breaks previously shared fragment targets,
- or the office hides action-changing content inside collapsed, injected, or otherwise untargetable sections without a direct section target or clear top-level fallback.

## This is not the same thing as URL portability, stale-link recovery, or reader mode

`438` asks whether the **whole official URL** is safe to bookmark, copy, or share.

`379` asks what happens when an old page or link target is gone or superseded.

`440` asks whether the controlling answer survives browser/app extraction into a simplified reading surface.

`442` asks a different question:
**once a person is already on the right official page, can they reliably land on, cite, and re-find the specific answer-bearing section of that page without guesswork?**

A route may pass the earlier controls and still fail `442` if:
- the page itself is current but the important section cannot be linked or re-found cleanly,
- a previously copied fragment now dumps the user into a generic top-of-page shell,
- an “On this page” list exists but no longer maps cleanly to the actual heading structure,
- or a same-page summary promises navigation into the detailed answer but the anchor destination is vague, stale, or inaccessible.

## Long pages are common voter-information surfaces

Election offices often publish long pages that combine deadlines, ID rules, eligibility notes, cure steps, exception cases, and office contacts on one route.
For this archive, that makes section-level navigation a public-surface concern rather than mere editorial polish.

When the voter is hurried, stressed, or acting through a helper, “the right answer is somewhere on this page” is often not good enough.
The page needs a bounded way to help people re-find the answer-bearing section itself.

## Section targets are public references, not just authoring conveniences

MDN’s current URI-fragment guidance says a fragment can point to an element `id` and the browser will scroll to that location after the page is retrieved. (xref: `mdn_uri_fragment_page`)

That means a section target is part of the user-facing reference surface.
People may:
- copy a same-page link to send to another voter,
- keep a bookmark to the “ID requirements” or “ballot cure” section of a long page,
- use an “On this page” list to move around without re-reading everything,
- or re-open the same official page later and expect the fragment-bearing reference to still land near the same answer.

For `442`, the office should treat that section-target behavior as a maintained delivery surface, not a disposable authoring artifact.

## In-page navigation should follow real heading structure

USWDS’s current in-page navigation guidance says the component helps users understand the contents of a lengthy page and navigate to the section they need to read. Its current accessibility tests say heading order should match the order displayed on the page, screen readers should announce the navigation region and link text clearly, and current location should be legible rather than implied only by color. (xref: `uswds_in_page_navigation_component_page`; xref: `uswds_in_page_navigation_accessibility_tests_page`)

For this archive, that implies a bounded posture:
- if a page is long enough to need same-page navigation, the navigation should reflect the real section structure,
- heading labels in the navigation should describe destinations clearly,
- and current-location cues should stay honest when the user moves through the page.

What fails `442` is not “the page is long.”
What fails `442` is offering section navigation that drifts away from the actual official content structure.

## Critical answer sections should be targetable without scavenger-hunt behavior

Digital.gov’s current guidance says government pages should be logically structured, keep key information near the top, and use clear descriptive headings. USWDS’s current summary-box guidance says same-page links should explain where they lead and that internal navigation belongs in jump links or side navigation rather than vague recap boxes. (xref: `digital_gov_headings_page`; xref: `uswds_summary_box_component_page`)

For official voter-information pages, that means a voter should not have to:
- expand multiple unrelated sections before finding the controlling answer,
- interpret several near-duplicate heading labels,
- or guess whether the “details below” link actually lands on the operative section.

A page does **not** need a fragment link for every sentence.
But when a section changes what the voter believes or does next, that section should be readily targetable or clearly summarized near the top with a trustworthy path to the fuller answer.

## Ordinary revisions should not silently strand section-level references

Because a fragment target is handled on the client after the page loads, section-link continuity can break even when the underlying page URL still works. (xref: `mdn_uri_fragment_page`)

So the bounded discipline here is not “never change headings.”
It is:
- do not casually break widely used or operationally important section targets,
- preserve or consciously review stable section `id`s where practical,
- and when a major section move changes where the controlling answer now lives, give the page enough structural clarity that an old same-page reference does not degrade into a scavenger hunt.

This is a continuity problem inside the page, not just a stale-link problem between pages.

## Hidden, collapsed, or late-rendered sections need an explicit boundary

A route may look fine in a static review and still fail `442` if the answer-bearing section:
- only appears after a script-driven expansion,
- sits inside a collapsed accordion with no direct target or state cue,
- receives a fragment but leaves the user without visible confirmation of where they landed,
- or is injected late enough that same-page navigation and heading order become misleading.

The archive does not forbid progressive disclosure.
But if the controlling answer depends on a hidden or delayed section, the route should preserve a legible direct path to that section or provide a clear top-level fallback that tells the voter how to reach it safely.

## Preserve bounded section-target review evidence, not clickstream exhaust

The evidence posture here is about reconstructing whether section-level navigation and fragment continuity were reviewed.
The archive should preserve:
- which official routes were reviewed for section-target continuity,
- which sections were deemed critical enough to stay directly targetable,
- whether the page exposed in-page navigation or jump links,
- whether navigation labels matched heading text/order,
- whether fragment behavior and current-location cues were checked,
- whether important section targets were intentionally preserved across revisions,
- and when the review last occurred.

It should **not** require preserving:
- named-user clickstreams,
- per-user scroll telemetry,
- full browser histories,
- raw session-replay archives,
- or individualized anchor-follow logs when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of section-target posture**, not click analytics.

- **Section Target Surface Digest (STSD):** digest of the bounded section-level navigation and fragment-target posture for the official route.
- **In-Page Navigation Policy Digest (IPND):** optional digest describing how jump links, “On this page” navigation, and heading structure are kept aligned.
- **Fragment Continuity Review Digest (FCRD):** optional digest describing which critical section targets were checked for stability across ordinary revisions.

## What belongs in the public section-target payload

Keep the payload **small, route-aware, and section-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `section_target_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_section_targets[]`
- `in_page_navigation_note`
- `section_heading_policy_note`
- `fragment_continuity_note`
- `critical_answer_targetability_note`
- `summary_or_topline_navigation_note`
- `collapsed_content_boundary_note`
- `history_or_share_fragment_note`
- `accessibility_alignment_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user click paths,
- scroll-depth analytics,
- raw session-replay captures,
- individualized anchor-follow logs,
- draft heading taxonomies that were never published,
- or speculative browser-debug traces that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether critical answer-bearing sections on long official pages can be reached and re-found through jump links, in-page navigation, or fragment-bearing references?
- Do navigation labels and heading structure tell the same truth about where each section link goes?
- Are critical sections directly targetable, or clearly summarized with a trustworthy path to the detailed answer?
- Did ordinary page revisions preserve or consciously review important fragment targets instead of silently stranding shared section-level references?
- Did the office preserve bounded review evidence without collecting named-user clickstream exhaust?

## How this fits the family map

Section anchors, in-page navigation, and fragment-target continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over long or sectioned official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route expects people to rely on section-level navigation or fragment-bearing references, the route should keep those section targets legible, aligned, and durable enough that the right answer-bearing section remains reachable without scavenger-hunt behavior.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-section-target-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-section-target-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Headings guidance (xref: `digital_gov_headings_page`)
- USWDS: In-page navigation (xref: `uswds_in_page_navigation_component_page`)
- USWDS: In-page navigation accessibility tests (xref: `uswds_in_page_navigation_accessibility_tests_page`)
- USWDS: Summary box guidance (xref: `uswds_summary_box_component_page`)
- MDN: URI fragment reference (xref: `mdn_uri_fragment_page`)
