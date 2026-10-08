# 466 — Official voter-information missing fragment targets, unresolved section anchors, and fail-open refinding discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where a same-page reference is expected to land on a real answer-bearing section but the referenced target may be missing, renamed, hidden, or otherwise unresolved at the moment a voter follows it**:
copied `#fragment` links,
"On this page" jumps,
section-level help links,
footnote/back-reference style jumps,
accordion/deep-link anchors,
and similar official routes where the page itself may still load successfully while the promised section-level destination quietly fails.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `379`, which governs stale-link and expired-page recovery between pages,
- `438`, which governs whether the whole current URL is safe to keep, copy, or share,
- `442`, which governs whether section targets and in-page navigation are kept stable and aligned in the first place,
- `444`, which governs whether a successful target landing remains visibly unobscured,
- `465`, which governs whether same-document history mutation keeps the browser history stack truthful once the route is already changing state,
- or `473`, which governs quoted-text text-fragment deep links whose highlight behavior may drift or disappear even when the page itself remains current.

It adds one narrow rule:
**if an official voter-information route expects people to arrive through a section-level or fragment-bearing reference, a missing or unresolved target should not silently strand them at a generic shell or top-of-page state; the route should preserve enough visible recovery to identify the failed target, re-find the intended section, or route to a trustworthy fallback.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, hierarchy, accessibility, usability, and accuracy. Digital.gov’s current headings guidance says public pages should use clear descriptive headings and logical structure. USWDS’s current **In-page navigation** guidance says in-page navigation should help users understand the contents of a long page and navigate to the section they need, and its accessibility tests require heading order, current-location cues, and clear announced destinations. MDN’s current **URI fragment** reference says a fragment identifies a specific part of a resource and, in HTML, can point to an element `id` so the browser scrolls to that element. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_headings_page`; xref: `uswds_in_page_navigation_component_page`; xref: `uswds_in_page_navigation_accessibility_tests_page`; xref: `mdn_uri_fragment_page`)

That is enough to justify a compact control here.
A route may pass `442` on paper and still fail the public because:
- the page loads, but an older copied `#deadline` reference no longer resolves to a visible section,
- an "On this page" link or deep link now points into a removed or collapsed region with no clear recovery,
- the browser changes the hash or appears to follow the reference, but the voter receives no truthful cue about which target failed,
- a shared link lands at the top of a long page and makes the reader infer that the wrong page loaded,
- or the target exists only after expansion/injection and the unresolved state leaves the reader with no bounded way to recover the intended official answer.

## This is not the same thing as section-target continuity, unobscured landing, or stale-link recovery

`442` asks whether section targets and in-page navigation were kept stable, aligned, and directly targetable.

`444` asks whether a successful jump lands with the answer-bearing heading visibly unobscured.

`379` asks what happens when an old or superseded page-level destination is gone.

`466` asks a different question:
**when a section-level reference on the current official page fails to resolve to a real destination, does the route tell the truth about that failure and preserve a bounded path to re-find the answer?**

A route may pass the earlier controls and still fail `466` if:
- the page itself is current, but the fragment-bearing reference resolves to no visible target and the reader gets no clue what went wrong,
- the office preserved most targets but one critical answer-bearing section moved and old section links now degrade into a silent top-of-page shell,
- the route keeps navigation labels honest when they work but gives no trustworthy recovery when they miss,
- or the page depends on a hidden/expanded section and a failed deep link gives no explicit refinding cue.

## Silent miss behavior is not good enough for action-changing official pages

MDN’s fragment guidance makes clear that the fragment is a user-facing reference to a specific part of the resource. (xref: `mdn_uri_fragment_page`)
For this archive, that means a failed section-level reference is not merely an authoring mistake.
It is a public-answer failure whenever the missed destination could change what a voter believes or does next.

So on routes where section links matter, the failure posture should not be limited to:
- silently doing nothing,
- dropping the reader at the top with no explanation,
- or leaving the reader to guess whether the page, the link, or the answer changed.

The bounded requirement is not a complex debugger.
It is a truthful recovery posture.

## Preserve the identity of the failed target

The core Micromax-like lesson here is small but important: when a jump action fails, the route should identify the **kind of target that failed** rather than hiding the failure behind a generic "page loaded" shell.

For official voter-information routes, that usually means preserving enough visible context to tell the user:
- that the page loaded but the referenced section could not be found,
- which section label / fragment / destination class was being attempted,
- whether a nearby summary or in-page navigation list can help re-find it,
- and which official fallback now controls if the exact section cannot be recovered safely.

The archive does **not** require exposing raw selector diagnostics, DOM internals, or developer-only debug text.
It does require that the route not collapse a failed section reference into silence.

## Refinding must stay bounded and official

If the exact section cannot be resolved, the route should preserve one or more bounded recovery aids such as:
- a visible top-of-page summary that names the major sections now present,
- an in-page navigation list that still reflects the current heading structure,
- a clear heading or note saying the linked section has moved or no longer exists,
- a trustworthy pointer to the current notice, FAQ, or office/help path,
- or a safe search/filter/jump aid whose scope is limited to the current official page or route family.

What fails `466` is not "the page needed some recovery."
What fails `466` is leaving the voter in an undifferentiated page shell where the original target disappeared and no bounded official refinding path takes over.

If the problem is specifically a browser-generated highlighted-text deep link whose quote no longer matches or is no longer being highlighted, `473` carries that more specific posture.

## Hidden, collapsed, or deferred sections need an explicit miss posture

A same-page reference may fail even when the content still exists somewhere in the route because the section:
- sits inside a collapsed accordion,
- appears only after script-driven expansion or late rendering,
- was renamed while old hashes still circulate,
- or moved into another route/state that no longer honors the old target.

In those cases, the route should not force the reader to discover the hidden recovery path by trial and error.
If the target cannot resolve directly, the page should either:
- expand/reveal the relevant region,
- direct the user to a trustworthy current summary or replacement section,
- or say that the referenced section is unavailable and route the user to the official fallback that now controls.

## Current-location truth still matters after a miss

USWDS’s current accessibility tests for in-page navigation require clear current-location cues and announced destinations. (xref: `uswds_in_page_navigation_accessibility_tests_page`)
That matters here because a failed section jump can otherwise leave the page implying a successful arrival.

For this archive, after a miss the route should avoid cues that falsely suggest:
- the destination section is active,
- the current heading is the requested target,
- or the browser’s hash/state alone proves that the reader is looking at the controlling section.

A truthful miss posture is better than a false sense of successful arrival.

## Preserve bounded evidence, not clickstream exhaust

The evidence posture here is about reconstructing whether unresolved section-level references were reviewed and given a bounded recovery path.
The archive should preserve:
- which routes were reviewed for fragment/section-reference misses,
- which targets or target classes were considered critical,
- what visible miss feedback the route provides,
- what official refinding or fallback path controls after a miss,
- whether hidden/collapsed sections were reviewed for miss behavior,
- and when the review last occurred.

It should **not** require preserving:
- named-user scroll trails,
- raw browser histories,
- per-user anchor-follow analytics,
- session-replay archives,
- or developer-console traces from real voters.

## Canonical digest artifacts

Publish **small digests of unresolved-target policy**, not raw interaction exhaust.

- **Fragment-Miss Surface Digest (FMSD):** digest of the bounded unresolved-fragment / unresolved-section-target posture for the official route.
- **Section-Refinding Policy Digest (SRPD):** optional digest describing the visible recovery aids and trusted fallback path after a same-page target miss.
- **Hidden-Target Recovery Digest (HTRD):** optional digest describing how collapsed, injected, or deferred sections are handled when an old or unresolved reference points at them.

## What belongs in the public fragment-miss payload

Keep the payload **small, route-aware, and miss-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `fragment_miss_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_fragment_targets[]`
- `target_resolution_policy_note`
- `unresolved_target_feedback_note`
- `refinding_fallback_note`
- `top_of_page_summary_recovery_note`
- `collapsed_or_hidden_target_policy_note`
- `current_location_truthfulness_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user anchor-follow logs,
- clickstream exhaust,
- raw DOM/selector debug traces,
- browser-history dumps,
- or individualized reproduction logs from real voters.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review what happens when a copied `#fragment`, in-page jump, or section-level reference on a current official page points nowhere or no longer resolves cleanly?
- When the target missed, did the route tell the truth about that miss instead of silently leaving the reader in a generic page shell?
- Was the failed target or destination class still identifiable enough for the reader to understand what was being attempted?
- Did the route preserve a bounded official refinding or fallback path when the exact section could not be recovered directly?
- Did the archive preserve bounded evidence of that policy without collecting clickstream exhaust from real users?

## How this fits the family map

Missing fragment targets, unresolved section anchors, and fail-open refinding is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if the office expects voters to rely on section-level references, the route should fail honestly and recover safely when one of those references no longer resolves.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-fragment-miss-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-fragment-miss-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Headings guidance (xref: `digital_gov_headings_page`)
- USWDS: In-page navigation (xref: `uswds_in_page_navigation_component_page`)
- USWDS: In-page navigation accessibility tests (xref: `uswds_in_page_navigation_accessibility_tests_page`)
- MDN: URI fragment reference (xref: `mdn_uri_fragment_page`)
