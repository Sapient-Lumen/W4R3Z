# 440 — Official voter-information reader mode, simplified view, and main-content extraction discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters may read through browser or app reader modes, simplified/clutter-reduced views, extracted-main-content presentations, or similar transformations that suppress surrounding chrome**:
status lookups,
registration or ballot-help explainers,
polling-place or hours answers,
submission follow-up pages,
deadline or requirement pages,
and similar official routes where the page may be correct in ordinary browsing but lose controlling facts, qualifiers, or next-step/help meaning when the browser decides to show only the "main" reading surface.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `377`, which governs language selectors, locale paths, and machine-translation boundaries,
- `380`, which governs site alerts, banners, and interstitials on the ordinary live page,
- `418`, which governs screen-reader semantics and live-update accessibility,
- `437`, which governs portable records once an answer is printed, saved, or otherwise carried off-screen,
- `438`, which governs whether the current URL can be safely bookmarked, copied, or shared,
- or `439`, which governs whether an already-open route stays current when the user returns through history, restore, or duplicate tabs.

It adds one narrow rule:
**if an official voter-information route may be consumed through reader mode, simplified view, or extracted-main-content presentation, the route should either keep the controlling facts and safe next-step/help path inside the extractable main content or clearly say that the full official view is required before the voter acts on the answer.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes hierarchy, structure, clarity, accessibility, usability, and accuracy. Digital.gov’s current digital-first public-experience guidance says government digital services should provide content that is authoritative and easy to understand, and should scale across mobile contexts. Digital.gov’s current plain-language guidance says headings should provide structure and orient the reader, that pages should stand on their own, and that the most important information should come first. USWDS’s current documentation-page guidance says page headlines should be precise and copy should stay concise. MDN’s current `<main>` documentation says browser reader mode functionality looks for the `<main>` element along with headings and sectioning elements when converting content into a specialized reader view. WebKit’s current Safari 18 feature guidance says semantic HTML such as `<main>` and `<article>` helps ensure Safari Reader and Safari Viewer work best. Mozilla’s current Firefox support guidance says Reader View strips away clutter like buttons, ads, background images, and videos, and that simplified printing likewise strips away buttons, ads, and background images. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_headings_page`; xref: `digital_gov_plain_language_web_writing_tips_page`; xref: `uswds_documentation_page_template_page`; xref: `mdn_main_element_page`; xref: `webkit_safari_18_reader_semantic_html_page`; xref: `firefox_reader_view_help_page`; xref: `firefox_print_simplified_pages_help_page`)

That is enough to justify a compact control here.
A route may pass `380`, `418`, `437`, and `439` yet still fail the public because:
- the deadline caveat or "this changed today" note lives only in a banner, badge, or sidebar that disappears in reader mode,
- the office identity, jurisdiction scope, or help lane lives only in header/navigation chrome that the extracted view removes,
- the main prose survives but the critical next-step link, phone number, or "use the full page to continue" boundary does not,
- a status or eligibility answer survives as text while its controlling as-of date or last-checked cue is lost,
- the page becomes readable in a simplified view but the reader cannot tell whether the simplified text is still the full authoritative action surface,
- or the browser/app exposes a clutter-reduced view that looks official enough to trust even though key action controls or qualifiers were never part of the extractable main content.

## This is not the same thing as print fidelity, machine translation, or return-state freshness

`437` asks whether the kept record remains faithful once the answer leaves the live page and becomes a printed or saved artifact.

`377` asks whether language routing and machine-translation convenience layers overstate official equivalence.

`439` asks whether an already-open route stays current when the user returns through history, restore, or duplicate tabs.

`440` asks a different question:
**if the browser or app extracts a simplified reading surface from the current page, does that extracted view still carry the controlling answer, authority cues, timing qualifiers, and safe action/help boundary?**

A route may pass the earlier controls and still fail `440` if:
- the printed/PDF output is fine but the on-screen reader view drops the only visible help or escalation path,
- the language path is correct yet the simplified reading view removes the qualifier that says the answer is partial or conditional,
- the live page is fresh on return but the extracted reading surface still omits the warning that full view is required before acting,
- or the page looks clear in ordinary browsing while the browser’s simplified extraction silently discards the facts the voter most needs to keep in view.

## The controlling facts cannot live only in removable chrome

Reader and simplified views are designed to privilege the main reading surface, not every piece of surrounding interface chrome.
For this archive, that means an official route should not place the controlling public facts only in:
- sticky alerts outside the main reading region,
- sidebar-only qualifications,
- header-only office identity,
- footer-only deadline or help cues,
- hover-revealed hints,
- or decorative cards that disappear when the browser extracts the page’s main content.

If a fact changes what the voter should do now, that fact should either survive inside the main extractable content or the page should clearly tell the voter to return to the full official view before relying on the answer.

## Reader-friendly is not the same thing as action-complete

Some official routes can safely support reader-mode consumption because the controlling answer is essentially informational.
Others are inherently full-view routes because the action depends on controls, live status widgets, authenticated context, or multi-step interaction.

`440` does **not** require every route to become fully operable inside reader mode.
It does require the office to choose and expose a bounded posture:
- **Reader-safe informational view** — the simplified extraction still contains the controlling answer and the ordinary next-step/help path.
- **Reader-safe summary only** — the simplified extraction preserves the answer summary plus a visible instruction to return to the full official view for action.
- **Full-view required** — the simplified extraction is not sufficient for action, and the page says so clearly enough that the voter does not mistake it for the complete operative route.

What fails `440` is not “reader mode exists.”
What fails `440` is letting a convenience reading surface silently masquerade as the full actionable official route when critical qualifiers or controls did not survive extraction.

## Reader/simplified classes matter

This archive should not flatten all simplified presentations into one bucket. At least four classes matter here:

1. **Browser reader mode** — a browser such as Firefox or Safari exposes a simplified reading view of the page.
2. **Simplified print preview before print/save** — the browser shows a clutter-reduced pre-print view that the voter may read before deciding whether to print or save.
3. **In-app or embedded reader presentation** — a container or viewing surface requests a reader-like presentation when available.
4. **Extraction-unavailable or partial fallback** — the browser cannot produce a reader view, or the extracted output is visibly partial.

Those are different states.
A route may work in one class and fail another.
The evidence posture should preserve which classes were reviewed and what bounded authority/action posture controlled each.

## Must-survive facts for simplified reading surfaces

For this archive, the following facts should remain visible in the simplified/main-content reading surface whenever they materially control what the voter should do next:
- the responsible office or official program identity,
- the jurisdiction or scope the answer covers,
- the controlling answer itself,
- any as-of, last-updated, last-checked, or timing qualifier that changes meaning,
- the critical condition or exception that limits the answer,
- the next-step or help path,
- and the full-view-required boundary when the simplified surface is not action-complete.

Not every page needs every field.
But if the office expects a voter to rely on the simplified reading surface, the facts that change the decision should not vanish with the surrounding chrome.

## Reader extraction should preserve meaning, not merely prose fragments

A simplified reading surface can look calm and readable while still being misleading.
The archive should therefore care about meaning, not just whether text remains on screen.

For `440`, a route should review whether simplified extraction:
- preserves the page headline and the route’s actual topic,
- keeps headings and section order coherent,
- leaves qualifiers attached to the statements they govern,
- preserves the help/escalation path when the answer is conditional or incomplete,
- and avoids producing a prose-only surface that strips away the only ordinary action boundary.

A clean text extract is not enough if it quietly detaches the answer from its scope, time basis, or official next-step meaning.

## When the simplified view is insufficient, say so clearly

Some official pages should remain readable in simplified form but should not be treated as the full operative route.
That is acceptable if the page says so clearly enough that the voter does not confuse readability with action completeness.

Good bounded substitutes include:
- a visible "return to the full official page before submitting or acting" cue,
- a stable help/contact path inside the main extracted content,
- a reference number, office name, or route label the voter can carry back to the full page or to live help,
- or a concise summary that names the controlling next step instead of pretending the simplified surface is the whole workflow.

## Preserve bounded evidence, not reader-analytics exhaust

The evidence posture here is about reconstructing whether simplified-reading behavior was reviewed and bounded.
The archive should preserve:
- which routes were reviewed for browser/app reader or simplified-view behavior,
- which reader/simplified classes were checked,
- whether the controlling facts survived in extractable main content,
- whether the route was reader-safe, summary-only, or full-view-required,
- what help or full-view return cue controlled when extraction was insufficient,
- and when the review last occurred.

It should **not** require preserving:
- per-user reader-mode telemetry,
- full reading-history logs,
- named-user customization states,
- raw browser-extension data,
- or individualized viewing traces when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of simplified-reading posture**, not individualized reading traces.

- **Reader-Mode Surface Digest (RMSD):** digest of the bounded reader/simplified-view policy payload for the official route.
- **Main-Content Survival Digest (MCSD):** optional digest describing which controlling facts survive in extractable main content.
- **Full-View Boundary Digest (FVBD):** optional digest describing when the simplified surface is informational only and when the user must return to the full official route.

## What belongs in the public reader-mode payload

Keep the payload **small, route-aware, and extraction-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `reader_mode_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_reader_routes[]`
- `reader_view_modalities[]`
- `main_content_authority_note`
- `must_survive_facts[]`
- `reader_view_action_boundary_note`
- `critical_help_or_return_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- user-level reader-mode telemetry,
- personalized reading preferences,
- browser-extension inventories,
- individualized simplified-view traces,
- or copied full-page HTML when bounded policy evidence is enough.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review what happens when the page is shown in browser/app reader mode or another simplified extracted view?
- If the simplified reading surface was usable, did the controlling answer, authority, timing qualifiers, and next-step/help path survive inside the extractable main content?
- If the simplified reading surface was not action-complete, did the page clearly say that full view or live help was required before acting?
- Did the route preserve meaning and qualifiers rather than merely leaving behind disconnected prose fragments?
- Did the office preserve bounded reader/simplified-view policy evidence without collecting individualized reader analytics?

## How this fits the family map

Reader mode, simplified view, and main-content extraction is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official route may be consumed through a browser/app’s simplified reading surface, the controlling facts and safe action/help boundary should survive extraction — or the page should clearly warn that the voter must return to the full official view.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-reader-mode-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-reader-mode-surface-checklist.md`
