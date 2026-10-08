# 293. Ballot-style lookups and sample ballots as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **ballot-style lookup / sample-ballot publication surface** as an **evidence surface**.
The goal is not to expose voter files, districting internals, or contest-drafting workpapers. The goal is to make four things hard to fake after the fact:

1. **What ballot style a voter was told to expect** before voting,
2. **Which public lookup inputs were used** to generate that answer,
3. **When the public answer changed** because of corrections, redistricting, contest fixes, or site assignment changes, and
4. **Whether the voter-facing sample ballot stayed accessible, language-appropriate, and consistent with the rest of the official information surface.**

It composes with:
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md`
- `docs/262-jurisdictional-policy-surface-registry.md`
- `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Election offices increasingly use websites to answer the most operational voter questions: **am I registered, where do I vote, and what is on my ballot?** EAC’s Election Management Guidelines frame official websites as a primary voter-information channel and explicitly treat **viewing sample ballots**, checking registration, finding polling places, and tracking ballots as core website services. (source: `eac_election_management_guidelines_2023_pdf`)

That makes the ballot-style lookup surface part of the legitimacy boundary. If a jurisdiction cannot later show **which public ballot style / sample ballot was presented, when it was effective, and whether corrections were explicit**, disputes become harder to resolve. Some “the ballot was wrong” stories are really claims about **public-state inconsistency**: stale lookups, silent edits, inaccessible sample ballots, wrong district joins, or different answers across channels.

The public side should stay small. This archive is not trying to publish full voter files, full districting joins, or every intermediate artifact in ballot-building. It is trying to publish a bounded, checkable record of the **voter-facing answer surface**.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Lookup availability claim:** there is one authoritative public method to determine a voter’s ballot style or view the correct sample ballot for election scope `E`.
2. **Style/version claim:** each sample ballot / ballot-style answer identifies the ballot-style identifier and the version effective at time `T`.
3. **Input-basis claim:** the public lookup declares, at a coarse level, what the answer depends on (for example address or precinct assignment) without exposing sensitive matching logic.
4. **Supersession claim:** corrections to ballot style, contest content, district assignment, or display are published as explicit superseding events rather than silent replacement.
5. **Accessibility/language claim:** the voter-facing sample ballot path is published in an accessible format and, where legally required, with corresponding minority-language materials.
6. **Parity claim:** website, mirror, downloadable sample-ballot file, hotline script, and status/correction feeds converge on the same effective state.

## Canonical digest artifacts

Publish **digests of the voter-facing ballot-information surface**, not internal election-management databases by default.

- **Ballot Style Directory Digest (BSDD):** digest of the authoritative mapping from public style identifiers to voter-facing sample-ballot artifacts and effective windows.
- **Sample Ballot Artifact Digest (SBAD):** per-style digest for the canonical voter-facing sample ballot artifact (HTML, PDF, accessible document bundle, or equivalent).
- **Ballot Lookup Policy Digest (BLPD):** digest of the public lookup contract: accepted input classes, lookup scope, freshness rules, fallback/help path, and caveats.
- **Ballot Surface Correction Digest (BSCD):** per-event digest for superseding corrections such as wrong district joins, contest text fixes, withdrawn-candidate notices, or replacement sample-ballot files.
- **Ballot Surface Parity Snapshot (BSPS):** optional snapshot binding the effective ballot-style answer across declared official channels.

Where a public correction materially changes voter actionability, pair the correction digest with a signed `PublicNotice` or digest-first public bulletin (`docs/200`, `docs/290`).

## What belongs in the public ballot-style payload

Keep the payload **small and voter-actionable**.

Recommended per-style fields:
- stable `ballot_style_id`
- `election_id` / election scope
- `effective_from` and optional `effective_until`
- `sample_ballot_uri` or packaged artifact pointer
- canonical digest for the current sample-ballot artifact
- coarse `lookup_basis` description (for example `address`, `precinct_assignment`, `vote_center_style_group`)
- `language_set` published for that style
- accessibility-format indicators (HTML, tagged PDF, large print, audio/BMD compatibility note when relevant)
- supersedes / superseded-by pointers
- voter-help contact / escalation pointer

Optional but useful:
- `style_family` or district bundle pointer when many styles share the same contest frame
- a “last verified” timestamp
- pointer to the most recent signed correction notice

Do **not** publish by default:
- voter-registration records or voter-file excerpts
- full district-join logic, geocoding internals, or address-normalization rules when they would expose sensitive attack surface
- tiny-cell usage analytics that materially raise intimidation or targeting risk
- internal proofing annotations, redline drafts, or vendor issue trackers unless they move into controlled disclosure

## Accessibility and language-access minimums

This surface is not only about correctness; it is also about **reachability by the affected voter**.

EAC’s 2024 voter-education materials emphasize that voter communications should be **relevant, timely, and accessible**, and its accessible-communications checklist says election offices are required to provide effective communications and should use plain language across electronic documents, social media, videos, and in-person materials. (source: `eac_voter_education_design_toolkit_page`, `eac_accessibility_checklist_accessible_communications_2024_pdf`)

DOJ’s Section 203 guidance states that where a covered jurisdiction provides registration or voting notices, forms, instructions, assistance, or other election-related materials or information, it must provide them in the applicable minority language as well as English. That includes ballot-related voter information, not only the in-person act of voting. (source: `justice_language_minority_citizens_page`)

Minimum publishable facts for this evidence surface:
- which languages are provided for the public ballot-style / sample-ballot path,
- which accessibility-oriented formats are provided,
- the fallback help path when the primary lookup fails or is inaccessible,
- the effective date/time for the currently published style answer.

## Supersession and anti-retcon rules

Corrections to ballot-style lookups should fail **loudly**.

Rules:
- A correction that changes what a voter would reasonably think appears on their ballot SHOULD produce a new **Ballot Surface Correction Digest**.
- Silent replacement of a sample-ballot file without a superseding event SHOULD be treated as a governance failure.
- Every correction SHOULD identify the superseded style/version or artifact digest and the replacement digest.
- If the correction could change voter actionability, the notice SHOULD also point to the correct polling-place / vote-center path and any relevant deadlines.
- If the public answer differed across official channels, publish a parity snapshot or correction note that makes the divergence legible.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public ballot-style lookup or sample-ballot directory for the scope?
- Can we reconstruct what a voter would have been shown at time `T`?
- Were corrections explicit and timestamped, or silently edited away?
- Did sample-ballot artifacts remain accessible and language-appropriate?
- Did the ballot-style surface stay consistent with directory, registration-status, and correction channels?

These are modest claims. But they are exactly the claims that determine whether a future dispute is about **facts** or about a missing public record.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/ballot-style-directory-payload.json`
- Operator quickcheck: `artifacts/checklists/ballot-style-and-sample-ballot-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Election Management Guidelines (official websites, sample ballots, voter tools) (source: `eac_election_management_guidelines_2023_pdf`)
- EAC: Voter Education Design Toolkit (relevant, timely, accessible voter education materials) (source: `eac_voter_education_design_toolkit_page`)
- EAC: Editable Content Document — Voter Education Topics (links to voting location lookup, registration status, key dates, and voter help paths) (source: `eac_editable_content_document_voter_education_topics_2024_pdf`)
- EAC: Accessibility Checklist — Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
- EAC: Voter Information Web Sites Study (historic but still directly relevant outside-view on top voter website tasks) (source: `eac_voter_information_websites_study_pdf`)
