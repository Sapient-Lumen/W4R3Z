# 378 — Official voter-information document downloads, embedded viewers, and file-delivery boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information download links, non-HTML file handoffs, embedded document/PDF viewers, and alternate-format fallback paths** that election offices expose to the public.

It does **not** ban PDFs or other downloadable files.
It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `293`, which governs sample-ballot publication,
- `305`, which governs the authoritative office/help route,
- `308`, which governs election-calendar and key-date surfaces,
- `365`, which governs official FAQ/help article editioning,
- `368`, which governs printable/downloadable voter-information artifacts,
- `370`, which governs voter-information emails and attachments,
- `373`, which governs action forms, applications, and affidavits,
- `375`, which governs site-search ranking,
- or `377`, which governs language selectors and locale fallback.

It adds one narrow rule:
**if an election office expects the public to rely on a download link or embedded file viewer to reach action-changing voting information, that file-delivery layer should make file type and current edition visible, keep HTML/help fallbacks recoverable, prevent stale files or viewer states from silently becoming the rule source, and preserve a bounded trace of what file state was actually presented.**

## Why this is a distinct surface

Current official guidance is enough to justify a narrow control here.
EAC's current **Effective Design for the Administration of Federal Elections** page says online voter-information materials should be clear, understandable, accessible, usable, and accurate.
EAC's current **Accessibility Checklist: Accessible Communications** treats electronic documents as a real election-communications lane and says election offices should use plain language while delivering accessible communications across channels.
The federal Section 508 program's current **Create Accessible PDFs** guidance says PDFs are still used across government but are often not the most accessible or mobile-friendly option, and it says agencies should prioritize HTML and use PDFs only when necessary.
USWDS's current **Link** guidance adds the delivery-layer rule for non-HTML handoffs: indicate file type and size, tell users if a link may trigger a download, and whenever possible create HTML pages instead of linking only to files such as PDFs.
Digital.gov's current plain-language guidance on **Links** and **Special cases** reinforces that a downloadable file should be described in the link or description page rather than treated as a context-free click target. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; source: `eac_accessibility_checklist_accessible_communications_2024_pdf`; xref: `section508_create_accessible_pdfs_page`; xref: `uswds_link_component_page`; xref: `digital_gov_plain_language_links_page`; xref: `digital_gov_plain_language_special_cases_page`)

That means a file handoff is not just generic CMS plumbing.
It is often the **delivery boundary** that decides whether the public sees the current HTML answer, a stale PDF, an inaccessible inline viewer, an unlabeled download, or a detached document that no longer matches the current official page.

## File delivery is a handoff layer, not a rule source

A public download link or embedded viewer MAY help people retrieve an official sample ballot, calendar, FAQ handout, affidavit packet, or translated election document.
It MUST NOT silently become a hidden authority layer above the current official page, signed notice, help route, or superseding edition.

The controlling artifact remains the current official page, notice, office/help route, or current editioned file that the jurisdiction actually stands behind.
That means the handoff layer should preserve enough context that the voter can still tell:
- what file type they are opening,
- whether the file is current for this election/scope,
- whether the HTML page or file is primary,
- and where the current official help path is if the file is inaccessible, stale, or ambiguous.

## HTML-first / file-when-needed discipline

This archive does **not** claim every election-information artifact must be HTML-only.
Many election offices will continue to publish PDFs, downloadable forms, printable guides, and document packets.

But the combined current federal guidance does imply a bounded preference order:
- use HTML or other directly accessible web content when that can safely carry the answer,
- use downloadable files when a portable packet, printable artifact, signed form, or retained record is actually needed,
- and do not let file convenience quietly replace accessible, current, mobile-usable public routing when the voter mainly needs the next step rather than a detached document. (xref: `section508_create_accessible_pdfs_page`; xref: `uswds_link_component_page`; xref: `digital_gov_plain_language_special_cases_page`)

## File-type disclosure and expectation-setting

A voter-information file handoff should not behave like an unlabeled trapdoor.
The public should be able to tell, before clicking, whether the destination is HTML, PDF, DOCX, spreadsheet, calendar file, or another non-HTML object.
Where practical, the public should also be able to see size/context cues and understand whether the destination will download, open in a browser viewer, or hand off to another application. (xref: `uswds_link_component_page`; xref: `digital_gov_plain_language_links_page`; xref: `digital_gov_plain_language_special_cases_page`)

That is not cosmetic.
For election information, file-type ambiguity can change whether a voter on a phone, assistive technology stack, low-bandwidth connection, shared computer, or locked-down workplace device can actually reach the answer.

## Embedded-viewer boundary discipline

An inline PDF or document viewer does not dissolve the file-delivery boundary.
It only hides it.

So if a jurisdiction uses an embedded viewer, the bounded rule should be:
- keep the file's edition/date/scope visible,
- keep a direct download and current official page/help route recoverable,
- keep an accessible or HTML fallback visible when the viewer is unsupported or fails,
- and do not let a cached or stale viewer state silently outrank a newer superseding notice or current page.

This viewer-specific rule is an inference from the combined official posture above:
if government web guidance says non-HTML handoffs should be disclosed, HTML should be preferred when possible, and electronic documents must remain accessible, those expectations do not disappear merely because the file opens inside the browser chrome instead of as a separate download. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`; xref: `section508_create_accessible_pdfs_page`; xref: `uswds_link_component_page`)

## Edition parity and stale-file control

A public HTML page, linked PDF, mirrored attachment, and embedded viewer can drift into different effective answers.
That drift matters when the document carries action-changing facts such as:
- deadlines,
- office hours,
- polling-place or drop-box locations,
- accepted ID alternatives,
- return instructions,
- signature/witness rules,
- affidavit text,
- or special-case voter routing.

So the file-delivery layer should make edition/current-state discipline visible:
- current files should identify issue date, edition marker, or election scope,
- superseded files should be visibly marked, withdrawn, demoted, or routed through an explicit superseding notice,
- HTML summary pages and file artifacts should not quietly disagree on the controlling answer,
- and a broken viewer should not strand the voter without a visible current help path.

## File-result state classes

A public file-delivery surface should not flatten every handoff into one generic “download.”
A small state taxonomy is enough:

1. **Current HTML-primary with file companion** — the current official web page is primary and the file is a companion or printable copy.
2. **Current file-primary with HTML summary/help wrapper** — the file is the action artifact or retained packet, but the wrapper page states scope, file type, current edition, and help path.
3. **Superseded/withdrawn file state** — the older file remains reachable only with explicit superseding context, archival labeling, or removal from ordinary public routing.
4. **Unsupported/accessibility fallback** — the file or viewer cannot safely serve the user, so the surface routes the user to the current accessible/help alternative.

That taxonomy prevents a polished viewer or generic “download” button from hiding whether the file still controls.

## Bounded file-trace minimum

The archive does **not** need indefinite per-user download histories.
But for accountability, reproducibility, and dispute resolution, a public voter-information file-delivery surface should preserve a bounded **file trace** for action-changing file states.

At minimum, that trace should make it possible to reconstruct:
- which file-delivery policy version was in force,
- which file edition or object identifier was promoted,
- whether the public was shown an HTML-primary page, direct download, or embedded viewer path,
- what file type/size label or wrapper context was presented,
- what result-state class the handoff produced,
- when that state was generated,
- and which official help path remained available.

Prefer **surface-policy versions, file/object identifiers, edition labels, result-state classes, and timestamps** over indefinite retention of raw download IP histories, cookie-level document trails, or other telemetry that is not needed for public-answer accountability.

## Privacy and minimization floor

Document handoffs can quietly become analytics surfaces even when the public thinks they are just opening a file.
That matters because voter-help documents may imply language needs, disability-related requests, incarceration/facility status, protected-address issues, or other sensitive edge-case facts.

So the file-delivery layer should default to minimization:
- do not retain detailed per-user download or viewer telemetry longer than the published policy requires,
- do not bind public document-open behavior to voter records absent a separately disclosed authority,
- do not treat document-view analytics as a shadow case-management system,
- and keep the secure official help path visible when the matter requires record-specific facts.

The file handoff should help the voter reach the right official artifact; it should not become a silent profiling surface.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official file-delivery-surface claim:** the office identified one or more public download/viewer/wrapper surfaces as official for scope `E`.
2. **File-disclosure claim:** non-HTML handoffs identify file type and relevant wrapper context before or at handoff.
3. **Edition-parity claim:** current HTML wrappers, embedded viewers, and linked files stay aligned on the controlling edition/state for action-changing content.
4. **Viewer-boundary claim:** embedded viewers do not hide the current page/help path or silently strand users when the viewer fails.
5. **Accessibility-fallback claim:** when a file or viewer is not the safest accessible route, the surface keeps an accessible/current alternative visible.
6. **File-trace claim:** action-changing file states are reconstructible through bounded policy-version, file-edition, modality, state-class, and timestamp evidence.
7. **Privacy-minimization claim:** download/viewer telemetry is not retained or linked longer than the published policy requires.
8. **Superseding claim:** material file or viewer changes produce an explicit update/superseding state rather than silent drift.

## Canonical digest artifacts

Publish **digests of the file-delivery surface and state**, not full per-user download logs.

- **Voter File Delivery Surface Digest (VFS-D):** digest of the bounded public file-delivery payload for a scope.
- **File Edition Policy Digest (FEPD):** digest of the current edition/supersession policy for public voter-information files.
- **Viewer State Snapshot Digest (VSSD-File):** optional digest proving what bounded file/viewer state the public would have encountered for a documented entrypoint at time `T`.

## What belongs in the public file-delivery payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `file_delivery_surface_label`
- `entrypoints[]`
- `file_modalities[]`
- `covered_question_classes[]`
- `underlying_surface_refs[]`
- `official_source_anchors[]`
- `html_primary_policy_note`
- `file_type_disclosure_policy_note`
- `viewer_boundary_policy_note`
- `alternate_format_policy_note`
- `edition_parity_policy_note`
- `result_state_classes[]`
- `file_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw per-user download logs,
- viewer session replays,
- detailed third-party analytics exports,
- draft/remediation copies,
- internal accessibility QA notes,
- or copied legal research that is not needed for the public answer surface.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official file-delivery surface was in force at time `T`?
- Was the public told what file type or handoff state they were entering?
- Which edition or current file/object was promoted?
- Did the wrapper page, embedded viewer, and downloadable artifact agree on the controlling current state?
- Was a stale or withdrawn file still reachable as if current?
- If the viewer failed or the file was inaccessible, was the current official fallback/help route still visible?
- Could a third party reconstruct the bounded file state without needing invasive user telemetry?

## How this fits the family map

An official file-download / embedded-viewer surface is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing voter-question families already modeled in `292–343`.

So the family question remains:
- `293` governs sample-ballot publication when the public opens ballot files,
- `308` governs calendars and key-date surfaces when they ship downloadable packets,
- `365` governs FAQ/help articles that may hand off to PDFs or DOCX attachments,
- `368` governs printable handouts and detached public guides,
- `370` governs email-delivered attachments and linked documents,
- `373` governs forms, applications, affidavits, and other action packets,
- `375` governs search when users discover the file through on-site search,
- and `377` governs language routing when the file handoff varies by language path.

This document only says that, if an office uses file downloads or embedded viewers as a trusted public delivery layer, that layer should remain bounded, explicit about file state, accessible, current-state-aware, and later-reconstructible instead of functioning as a silent rule-making surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-file-delivery-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-file-delivery-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: Accessibility Checklist: Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- Section 508: Create Accessible PDFs (xref: `section508_create_accessible_pdfs_page`)
- USWDS: Link component (xref: `uswds_link_component_page`)
- Digital.gov: Links (xref: `digital_gov_plain_language_links_page`)
- Digital.gov: Special cases (xref: `digital_gov_plain_language_special_cases_page`)
