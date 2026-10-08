# 306. Military and overseas voting paths, FPCA/FWAB, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “if I am a military voter, military family voter, or overseas citizen, which official UOCAVA path applies to me, how do I request and receive a ballot, what backup ballot path exists, how do I track receipt, and what changed if any of those answers moved”** as an **evidence surface**.
The goal is not to publish deployed-service rosters, per-voter military status records, ballot contents, or transport telemetry. The goal is to make six things hard to fake after the fact:

1. **Which authoritative public UOCAVA path the jurisdiction identified** for election scope `E`,
2. **Which covered voter classes the public surface said the path served**,
3. **Which request, delivery, and return options the public surface named for those voters**,
4. **Whether the public surface clearly named the FPCA path, the FWAB backup-ballot path, and the ballot-receipt tracking path**,
5. **When mailing-disruption, deadline, or help-routing guidance changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/262-jurisdictional-policy-surface-registry.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Military and overseas voters often do not fail because there was no legal path. They fail because the **official public answer surface** about that path is fragmented: a generic vote-by-mail page says “request a ballot,” a separate federal page says “use FPCA,” a stale county FAQ omits the FWAB fallback, a hotline omits electronic delivery options, or a disruption notice quietly changes the practical return path without leaving a public trail. That is a distinct integrity problem, not just a sub-bullet under ordinary absentee voting.

Current official guidance makes the distinct UOCAVA lane clear. DOJ’s current UOCAVA page says covered voters include uniformed-service members, their family members, and U.S. citizens residing outside the United States; it highlights the FPCA as the simultaneous registration-and-request path, the FWAB as the backup ballot, electronic request and delivery options, the 45-day federal-ballot transmission rule when requests are timely, and the requirement that voters have free access to a receipt-tracking system. EAC’s current fact sheet and quick-start guide for serving UOCAVA voters reinforce that this is not just “regular absentee voting from far away”: officials must accept ballot requests and send blank ballots electronically, send blank ballots starting at least 45 days before federal Election Day when requested, and provide a free-access system for tracking ballot receipt. (xref: `justice_uocava_page`; xref: `eac_uocava_fact_sheet_2025_pdf`; xref: `eac_uocava_quick_start_guide_pdf`)

FVAP’s current voter-facing paths show why the public surface must be reconstructable as an operational object. Its military-voter overview tells servicemembers to use the FPCA, says that using FPCA helps ensure the ballot is sent at least 45 days before a federal general election, directs voters to contact their election office if the requested ballot has not arrived, and points them to the FWAB if time is short. FVAP’s overseas-citizen overview likewise treats the FPCA as both registration and absentee-ballot request and recommends renewal each year and when moving. FVAP’s mailing-ballot update page then adds live operational value: submit the FPCA early, use the FPCA to unlock electronic ballot-delivery options, use the FWAB as a backup if needed, and watch mail-disruption/election-date updates through official channels. (xref: `fvap_military_voter_overview_page`; xref: `fvap_overseas_citizen_voter_page`; xref: `fvap_mailing_ballots_election_updates_page`; xref: `eac_military_voters_best_practices_2026_pdf`)

The help path is also part of the public surface. FVAP’s current contact page publishes support hours plus official routes to Installation Voter Assistance Offices, embassy/consulate contacts, and election-office search tools. That means a trustworthy UOCAVA surface cannot collapse into one ambiguous “contact us” footer. It should say which help path is authoritative for which problem, and which fallback applies if the main route fails. Pair that with `docs/305` rather than treating it as a replacement. (xref: `fvap_contact_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative UOCAVA path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for military/overseas absentee-voting information.
2. **Coverage claim:** the public surface stated which voter classes the path covers and where a voter should go if a different path applies.
3. **FPCA/request-and-delivery claim:** the public surface stated the official request/registration path, including whether FPCA is accepted and how delivery options are described.
4. **FWAB/tracking claim:** the public surface stated the backup-ballot path and the official ballot-receipt tracking path.
5. **Disruption/advisory claim:** the public surface stated where mailing disruptions, election-date updates, or alternate return guidance would be published.
6. **Change-log/parity claim:** changes to help routing, request methods, delivery options, deadlines, or backup-ballot guidance were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public UOCAVA help surface**, not per-voter military records or ballot-tracking logs.

- **UOCAVA Voting Path Surface Digest (UVPSD):** digest of the authoritative public UOCAVA payload for a scope.
- **UOCAVA Change Notice Digest (UVCND):** per-event digest for changed help paths, request options, delivery options, or eligibility wording.
- **UOCAVA Transmission / Return Advisory Digest (UTRAD):** per-event digest for mail disruptions, date shifts, or alternate return guidance.
- **UOCAVA Backup Ballot Notice Digest (UBBND):** optional digest when the public surface changes how voters are told to use or find the FWAB.
- **UOCAVA Surface Parity Snapshot (UVSPS):** optional snapshot binding the effective UOCAVA answer surface across declared official channels.

## What belongs in the public UOCAVA payload

Keep the payload **small, action-relevant, and role-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_uocava_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed disruption or correction notice

Recommended UOCAVA-specific fields:
- `covered_voter_classes`
- `request_and_registration_paths`
- `ballot_delivery_options`
- `backup_ballot_path`
- `tracking_path`
- `mailing_or_disruption_updates_uri`
- `service_assistance_paths`
- `local_election_office_path`
- bounded `deadline_semantics`
- bounded `state_specific_notes`

Do **not** publish by default:
- per-voter military status records or deployment details
- individualized ballot-tracking events
- internal election-office exception queues
- passport, ID, or signature images
- embassy, VAO, or office internal escalation trees beyond the public help surface

## Routing semantics and anti-retcon rules

The UOCAVA surface should fail **loudly** when the voter-help path changes.

Rules:
- A change that affects the authoritative UOCAVA page, the FPCA/FWAB path, help routing, delivery options, or tracking instructions SHOULD produce a new change notice digest.
- Silent mutation of the public answer about whether FPCA is accepted, whether electronic delivery is available, or how a voter reaches the backup-ballot path SHOULD be treated as a governance failure.
- The public surface SHOULD separate **federal baseline protections** from **state-specific additional conditions**.
- If local practice differs for military voters, overseas citizens, family members, or never-resided voters, the public surface SHOULD say so explicitly.
- If mail disruptions, court-ordered date shifts, or transport constraints change the practical return path, publish an advisory notice with the effective window and official fallback.
- If the public surface mentions the FWAB, it SHOULD also state the official conditions or help path for using it rather than implying it is a generic second ballot for everyone.

## Accessibility, language access, and next-step clarity

A UOCAVA page only matters if a remote voter can act on it without guesswork.

Minimum publishable facts:
- who the path covers,
- which official request/registration path applies,
- which delivery and return options are publicly described,
- where the backup-ballot path lives,
- where the receipt-tracking path lives,
- which help desk, installation office, embassy/consulate, or local election-office path is authoritative for case-specific problems,
- which notice superseded the prior public answer.

This is not a full UOCAVA compliance manual. It is the **minimum operational truth surface** needed so military and overseas voters are not forced to triangulate among stale PDFs, generic absentee pages, unofficial screenshots, or after-the-fact claims that the FPCA/FWAB path “was always available.” Pair it with `docs/304` for ordinary request-path publication and `docs/295` for status/cure surfaces. (xref: `justice_uocava_page`; xref: `fvap_military_voter_overview_page`; xref: `fvap_fwab_backup_ballot_page`; xref: `fvap_contact_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public UOCAVA path at time `T`?
- Can we reconstruct what a military or overseas voter would have been told at time `T` about FPCA, FWAB, and ballot-receipt tracking?
- Did the public surface distinguish federal baseline protections from state-specific details clearly enough to guide action?
- Were mailing-disruption or date-shift advisories explicit and time-bounded, or quietly folded into mutable pages?
- Did official channels converge on the same effective UOCAVA answer surface?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/uocava-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/uocava-voting-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- DOJ: UOCAVA overview and MOVE Act protections (xref: `justice_uocava_page`)
- EAC: Fact Sheet — Serving UOCAVA Voters (xref: `eac_uocava_fact_sheet_2025_pdf`)
- EAC: Best Practices for Serving Military Voters (xref: `eac_military_voters_best_practices_2026_pdf`)
- EAC: Quick Start Guide — Serving UOCAVA Voters (xref: `eac_uocava_quick_start_guide_pdf`)
- FVAP: How to Vote Absentee in the Military (xref: `fvap_military_voter_overview_page`)
- FVAP: Overseas Citizen Voters (xref: `fvap_overseas_citizen_voter_page`)
- FVAP: FWAB backup-ballot path (xref: `fvap_fwab_backup_ballot_page`)
- FVAP: Mailing Ballots and Election Date Updates (xref: `fvap_mailing_ballots_election_updates_page`)
- FVAP: Contact / support routing (xref: `fvap_contact_page`)
