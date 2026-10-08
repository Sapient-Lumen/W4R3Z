# 292. Polling-place directory and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public list of polling places / vote centers / early-vote sites** as an **evidence surface**.
The goal is not to publish every operational detail. The goal is to make three things hard to fake after the fact:

1. **What the jurisdiction told voters** about where/when/how to vote in person,
2. **When that information changed**, and
3. **Whether official channels stayed consistent** when sites closed, moved, consolidated, or changed hours.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/276-contingency-planning-and-continuity-of-operations-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`

## Why this exists (bounded)

In-person voting legitimacy is partly a **directory-integrity** problem. Voters, campaigns, media, courts, and observers need a stable answer to: **which sites were official, when were they open, and what was the accessible/translated path when conditions changed?**

That answer often fragments across websites, PDFs, press releases, social posts, emailed alerts, and ad hoc hotline scripts. When a site closes or moves, disputes are not only about the operational decision; they are also about whether the public received a **clear, time-bounded, consistent, and authentic** notice of the change. (source: `eac_enhancing_election_security_public_comms_2024_pdf`, `cisa_dotgov_domain_fact_sheet_2022_pdf`)

Accessibility is part of the integrity boundary, not an afterthought. DOJ’s ADA voting guidance treats polling-place selection and voter communications as part of the obligation to provide equal voting opportunity, and the DOJ checklist frames accessibility as a field-checkable path from arrival to the voting area. (source: `ada_voting_and_polling_places_page`, `ada_polling_places_checklist_page`)

Operationally, jurisdictions also need a bounded way to describe temporary locations, capacity assumptions, and wait-time mitigation without publishing sensitive floor plans, staffing rosters, or exploitable site details. EAC materials emphasize that site viability depends on space, layout, line management, and resource allocation, and EAC’s newer calculator is explicitly aimed at estimating bottlenecks and wait times at voting locations. (source: `eac_finding_voting_locations_poll_workers_2020_pdf`, `eac_voting_location_resource_calculator_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Directory claim:** for election scope `E`, the jurisdiction published the authoritative list of in-person voting sites in a bounded machine-readable form.
2. **Effective-time claim:** each site record declares the time window during which it was intended to be valid.
3. **Change-log claim:** closures, relocations, consolidations, and hour changes are published as explicit superseding events rather than silent edits.
4. **Channel-parity claim:** the same effective state was carried across declared official channels (website, mirror, status page, hotline script packet, signed notice feed).
5. **Accessibility/language claim:** each site record publishes the minimal accessibility/language facts voters need to act, plus the alternate path if a site becomes unusable.
6. **Capacity-bounds claim:** if wait-time or capacity guidance is published, it is presented as bounded planning information, not as a false guarantee.

## Canonical digest artifacts

Publish **digests of the directory surface**, not internal spreadsheets by default.

- **Voting Location Directory Digest (VLDD):** digest of the full authoritative directory payload for a scope.
- **Location Change Notice Digest (LCND):** per-event digest for closure, move, consolidation, reopening, or hours change.
- **Site Capability Snapshot Digest (SCSD):** optional digest of bounded site facts that matter publicly: accessible station present, curbside availability if offered, ballot-drop availability if applicable, language-support classes, and effective hours.
- **Hotline Script Digest (HSD):** optional digest of the current voter-contact script or FAQ excerpt when call centers are an official channel.
- **Channel Parity Snapshot (CPS):** bind the directory/version shown on each declared official channel and detect silent divergence (`docs/201`).

Use `PublicNotice` or the digest-first bulletin lane for change events that matter publicly (`docs/186`, `docs/290`).

## What belongs in the public directory payload

Keep the authoritative payload **small and decision-relevant**.

Recommended per-site fields:
- stable `site_id`
- `site_kind` (`polling_place`, `vote_center`, `early_vote`, `temporary_site`)
- human-facing name
- public address / directions pointer
- effective open/close timestamps or dates
- status (`scheduled`, `open`, `moved`, `closed`, `superseded`)
- replacement site pointer when applicable
- accessibility flags (wheelchair route confirmed, accessible station available, curbside/alternate process if offered)
- language-support summary
- public contact/help pointer
- notes field for bounded voter-facing clarifications

Optional but useful:
- a coarse **capacity class** or wait-time planning band
- a “last verified” timestamp
- pointer to a signed notice that announced the most recent change

Do **not** publish by default:
- security camera placement, alarm details, or floor plans
- exact staffing counts/shifts
- sensitive delivery/custody timings
- per-hour turnout by tiny site when it materially raises intimidation or targeting risk

## Change semantics (anti-retcon)

A voter-information surface should fail **loudly** when conditions change.

Rules:
- A change that affects voter actionability (site closed, moved, hours changed, accessibility path changed, wrong-site rumor corrected) SHOULD produce a new **Location Change Notice Digest** plus a signed `PublicNotice`.
- Silent mutation of the main directory without a superseding event SHOULD be treated as a governance failure.
- Every change SHOULD identify the superseded site/version and the replacement destination or alternate path.
- Corrections should preserve a stable audit trail: what changed, when, why, and who approved it.

## Accessibility and alternate-path minimums

If a site is inaccessible or becomes unusable, the public artifact should answer the voter’s next question without making them decode a legal memo.

Minimum publishable facts:
- whether the site was assessed as accessible for the relevant use path,
- whether at least one accessible voting station is planned/present,
- whether curbside or another alternate process is offered when legally available,
- the replacement or alternate site/process if the original site cannot serve voters.

This is not a full civil-rights compliance record. It is the **minimum operational truth surface** that keeps accessibility failures from disappearing into rumor. Pair it with the tighter control set in `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `ada_voting_and_polling_places_page`, `ada_polling_places_checklist_page`)

## Capacity and wait-time discipline

Directory integrity does **not** require publishing exact queue predictions. But if the jurisdiction tells the public that a site is a vote center, a temporary site, or a high-capacity replacement site, it should be able to point to a bounded planning basis. EAC’s calculator is useful here because it frames wait times as a resource-allocation and bottleneck problem, not as a PR promise. (source: `eac_voting_location_resource_calculator_page`)

Recommended public discipline:
- publish coarse planning bands or advisory language, not exact guarantees;
- log major site-class changes (e.g., precinct site → consolidated vote center);
- record the approval event that authorized the change.

## Verification questions for third parties

A verifier or observer should be able to answer:
- Was there one authoritative directory for the scope?
- Can we reconstruct what voters were told at time `T`?
- Were site changes explicit and signed, or silently edited away?
- Did official channels converge on the same effective state?
- Did accessibility/alternate-path notices travel with closures and relocations?

These are modest claims, but they matter. Many election rumors are really claims about **public-state inconsistency**.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voting-location-directory-payload.json`
- Operator quickcheck: `artifacts/checklists/polling-place-directory-and-change-log-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- DOJ ADA: voting and polling places overview (source: `ada_voting_and_polling_places_page`)
- DOJ ADA: checklist for polling places (source: `ada_polling_places_checklist_page`)
- EAC/CISA: Enhancing Election Security Through Public Communications (source: `eac_enhancing_election_security_public_comms_2024_pdf`)
- CISA: `.gov` domain fact sheet for election officials (source: `cisa_dotgov_domain_fact_sheet_2022_pdf`)
- EAC: Voting Location Resource Calculator (source: `eac_voting_location_resource_calculator_page`)
- EAC / GCC-SCC working group: Finding Voting Locations and Poll Workers (source: `eac_finding_voting_locations_poll_workers_2020_pdf`)
