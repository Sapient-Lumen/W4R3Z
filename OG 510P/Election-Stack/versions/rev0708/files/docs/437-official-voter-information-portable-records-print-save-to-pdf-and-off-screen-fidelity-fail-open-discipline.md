# 437 — Official voter-information portable records, print/save-to-PDF, and off-screen fidelity fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where the office expects a voter, helper, observer, or later reviewer to keep a usable record outside the live browser context**:
submission confirmations,
status lookup results,
appointment or meeting details,
polling-place or hours answers,
mail-ballot cure or return instructions,
deadline notices,
and similar official routes where the page can be current and understandable on-screen yet still fail the public because the printable, savable, or off-screen record drops the controlling facts once the live page is gone.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `378`, which governs official document downloads and embedded viewers,
- `381`, which governs QR-code and printed-to-digital handoff posture,
- `396`, which governs publication-date and last-updated cues,
- `430`, which governs whether a submission confirmation actually gives the voter a record worth keeping,
- `435`, which governs temporary-unavailable and degraded-mode posture,
- or `436`, which governs safe exit and shared-device privacy after the voter is done.

It adds one narrow rule:
**if an official voter-information route expects the public to keep, print, save to PDF, or otherwise carry the answer out of the live page, the office should keep the portable record faithful enough that the controlling facts do not disappear, truncate, or become ambiguous once the browser context is gone.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats both printed and online voter-information materials as core election communications and emphasizes clarity, understandability, accessibility, and usability. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, secure by design/default, user-centered, and mobile-first. USWDS’s current **Keep a record** guidance says successful public-service flows should provide a record of successful submission, include site name, URL, and date, include next steps or reference numbers when possible, and test print outputs across printers, print-to-PDF options, and assistive output devices. Section508.gov’s current **Create Accessible PDFs** guidance says agencies should prioritize HTML and use PDFs only when necessary because PDFs are often less accessible and less mobile-friendly. MDN’s current **Printing** guide says print-specific styles control what survives when a webpage is printed on paper or saved as PDF. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_keep_a_record_page`; xref: `section508_create_accessible_pdfs_page`; xref: `mdn_printing_css_guide_page`)

That is enough to justify a compact control here.
A route can be current, clear, and even pass `378`, `396`, `430`, and `436`, yet still fail first contact because:
- the on-screen answer is usable but the print/PDF version drops the polling-place address, hours, or last-verified date,
- the saved record keeps a confirmation headline but loses the reference number, next step, or office contact,
- the page depends on accordions, tabs, hover states, map pins, or sticky headers that do not survive printing,
- a mobile save-to-PDF or share flow crops the key facts or omits the current URL/date context,
- the route forces a PDF download even though the HTML answer was the current authoritative state,
- or the page tells the voter to “keep this for your records” without checking whether the portable output is actually legible and complete.

## This is not the same thing as confirmation existence, downloadable files, or shared-device exit

`430` asks whether a successful or pending route leaves the voter with a record worth keeping at all.

`378` asks whether official files/downloads/viewers are current, deliverable, and not silently substituting stale or broken document flows.

`436` asks whether the voter can leave the route safely on a shared or borrowed device.

`437` asks a different question:
**once the voter tries to carry the answer out of the live page — by printing it, saving it as PDF, screenshotting key details, or otherwise relying on the portable record — does that record still preserve the controlling facts well enough to be useful?**

A route may pass `430` and still fail `437` if:
- the confirmation page exists, but the print/PDF output omits the case number or submission time,
- the current answer depends on content expanded on-screen that vanishes in the portable view,
- the record keeps the address but loses the “through this date only” qualifier,
- or the printable copy looks official but no longer shows which office/service produced it or when it was last verified.

## On-screen success is not enough if the task expects a portable record

USWDS’s current **Keep a record** guidance treats retained records as part of successful form/service completion, not as an optional afterthought. That matters for election routes because many disputes are reconstructed from what the voter could reasonably keep in hand once the live page is gone: a deadline screen, a status result, a cure instruction, a polling-place answer, or a confirmation page with a reference number. (xref: `uswds_keep_a_record_page`)

For this archive, that means the office should decide whether a route is one where an ordinary user is likely to:
- print the page,
- save it as PDF,
- carry it on a phone,
- show it later to a helper or election worker,
- or rely on it after connectivity, login state, or browser context changes.

If yes, the portable view needs bounded review.
The rule is not “every page must become a downloadable packet.”
It is “do not tell people to keep a record unless the record survives leaving the page.”

## Keep the controlling facts in the portable record itself

The portable record should preserve enough context that a later reader can tell what the answer was and why it mattered.
That usually means preserving, when relevant:
- the office or service identity,
- the page title or route purpose,
- the key answer itself,
- the date/time or last-verified cue,
- the URL or equivalent source context,
- the next-step or deadline meaning,
- and any reference number or contact lane the office expects the voter to use later.

For `437`, the office should not assume those facts can safely live only in:
- collapsed panels,
- hover-only disclosures,
- sidebars that disappear in print,
- sticky banners that do not render in saved output,
- map pins with no textual fallback,
- or a live page state that the portable record never captures.

## Print and save-to-PDF deserve explicit review, not folklore

USWDS’s current **Keep a record** guidance says teams should test print outputs, including print-to-PDF, with representative browsers/operating systems and assistive output devices, and notes that mobile users may need extra on-screen guidance. MDN’s current **Printing** guide says print-specific styles determine what survives on paper or in PDF. (xref: `uswds_keep_a_record_page`; xref: `mdn_printing_css_guide_page`)

For this archive, that means the portable record should be reviewed for ordinary failure modes such as:
- clipped addresses, hours, deadlines, or reference numbers,
- text/background combinations that become illegible off-screen,
- hidden sections that never open in print,
- orphaned headings with missing values,
- page-break behavior that separates labels from the data they govern,
- or portable output that drops the source/date context and leaves a later reader unable to tell whether the answer was current.

The rule is not “build a perfect print stylesheet for every route.”
It is “review the portable output for the few facts a real voter may need later.”

## HTML-first remains the safer default when a live page already carries the answer

Section508.gov’s current PDF guidance says agencies should prioritize HTML and use PDFs only when necessary because PDFs are often less accessible and less mobile-friendly. (xref: `section508_create_accessible_pdfs_page`)

That matters here because `437` is **not** a license to turn every live answer into a document download.
Often the safer rule is:
- keep the HTML route authoritative,
- make its portable view faithful enough for ordinary record-keeping,
- and only introduce a downloadable PDF when there is a real operational need.

If a PDF companion exists, the office should keep the relationship clear enough that the public can tell whether:
- the HTML page is the current authoritative surface,
- the PDF is a convenience record,
- or the PDF itself is the official controlled artifact for that route.

## Mobile and low-friction record keeping matter

Digital.gov’s current digital-first posture and USWDS’s current **Keep a record** guidance both imply that portable record-keeping should not assume a desktop printer next to the voter. Mobile users may be saving a PDF, capturing a reference number, or sharing the record forward to a helper. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_keep_a_record_page`)

For `437`, that means a route should not quietly fail portable use by assuming:
- access to a printer,
- a wide desktop layout,
- a second device to transcribe key details,
- or perfect memory after the page closes.

When practical, the route should keep the few must-keep facts visible in ordinary text before any print/save action begins.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough portable-record posture to reconstruct what the official route promised and whether the portable output was reviewed.
That can include:
- which routes are expected to support ordinary record-keeping,
- which key facts were designated as must-survive in portable form,
- which output modes were reviewed,
- whether HTML-vs-PDF authority posture was documented,
- and when the portable-record review last occurred.

It should **not** require preserving:
- real voters’ saved PDFs,
- screenshots of personal status pages,
- full browser print logs,
- downloaded personal records,
- or broad telemetry about what individual voters printed or saved.

## Canonical digest artifacts

Publish **small digests of portable-record posture**, not whole saved records.

- **Portable Record Surface Digest (PRSD):** digest of the bounded portable-record policy payload for the official route.
- **Print/PDF Fidelity Review Digest (PFRD):** optional digest describing which print/save-to-PDF modes were reviewed and what must-survive fields were checked.
- **Authority and Record Relationship Digest (ARRD):** optional digest describing whether HTML, PDF, or both carry the authoritative/current-state burden for the route.

## What belongs in the public portable-record payload

Keep the payload **small, route-aware, and off-screen-survivability focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `portable_record_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `portable_record_required_note`
- `must_survive_fields[]`
- `reviewed_output_modes[]`
- `onscreen_vs_portable_equivalence_note`
- `html_vs_pdf_authority_note`
- `portable_record_next_step_note`
- `portable_record_help_route_note`
- `mobile_recordkeeping_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- real voter records,
- personal confirmation PDFs,
- screenshots of personalized answer lanes,
- raw browser print diagnostics,
- or per-user save/share telemetry.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- If the office told the public to keep a record, did the portable record actually preserve the controlling facts?
- Did print/save-to-PDF output keep the office/service identity, key answer, timing context, and next-step meaning when those mattered?
- Did critical information survive without requiring hover states, expanded UI, or a live interactive map/widget?
- If both HTML and PDF existed, was it clear which one was authoritative and current?
- Could a mobile or bandwidth-constrained user still keep a usable record without depending on a desktop printer?
- Did the archive preserve bounded portable-record policy evidence without collecting personal saved records?

## How this fits the family map

Portable-record fidelity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if a jurisdiction expects a voter to carry an official answer out of the live page, the record should remain faithful enough off-screen that the useful facts do not evaporate the moment the browser context ends.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-portable-record-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-portable-record-surface-checklist.md`
