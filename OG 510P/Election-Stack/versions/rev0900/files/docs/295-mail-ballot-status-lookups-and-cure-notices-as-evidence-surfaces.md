# 295. Mail-ballot status lookups and cure notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for a voter asking “what is happening with my mail ballot?”** as an **evidence surface**.
The goal is not to expose per-voter records. The goal is to make five things reconstructable later:

1. **What statuses the official public surface used**,
2. **What next step the voter was told to take** when action was needed,
3. **When a cure opportunity, outage, or correction was announced**,
4. **Whether official channels converged on the same effective answer**, and
5. **Whether accessibility and language-access paths were preserved** when the answer changed.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/219-uncertainty-safe-public-updates.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`
- `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`
- `docs/272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Mail voting disputes often collapse into a narrow operational question: **what did the official system tell the voter, and what action path was offered, at a specific time?**
EAC voter guidance explicitly tells voters that state rules differ and that the practical source of voting information is the voter’s state or local election office; EAC’s vote-by-mail materials also tell voters to contact election officials to verify whether a ballot was received in time to be counted. NASS’s nonpartisan **Can I Vote** project likewise routes absentee and early-voting questions to state election officials because rules vary greatly by state. (xref: `eac_voter_faqs_page`, `eac_voting_by_mail_101_pdf`, `nass_absentee_early_voting_page`)

That makes the status lookup surface part of the legitimacy boundary. A later dispute may not require disclosure of the voter file or ballot envelope image. It may require a bounded public record of the **status vocabulary**, the **help path**, the **effective deadline/cure notice**, and any **corrections or outages** that changed what voters were told.

Accessibility and language access are load-bearing here. EAC’s current accessibility guidance for voting by mail says the process must be accessible and highlights barriers that can prevent equal access for voters with disabilities. DOJ’s language-minority guidance explains that federal law protects voters who need information in minority languages and treats translated election information and materials as part of effective participation. (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`, `justice_language_minority_citizens_page`)

Cure workflows also need privacy discipline. EAC/CISA guidance on signature verification and cure emphasizes ballot/batch tracking, reconciliation with the voter-registration system, and extra precautions because cure documents and exchanged information are likely to contain personally identifying information. (source: `eac_signature_verification_cure_process_pdf`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative status-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for checking mail-ballot status and one authoritative path for cure/help instructions.
2. **Effective-state claim:** the public surface declared the status vocabulary in use and the time window for which the answer was intended to be valid.
3. **Actionability claim:** if the voter-facing answer required action, the public surface published a bounded next step (for example cure affidavit portal, office contact, replacement-ballot request path, or in-person fallback where applicable under local law).
4. **Correction/outage claim:** outages, stale-status conditions, deadline corrections, and cure-policy/help-path changes were published as explicit superseding events rather than silent edits.
5. **Accessibility/language claim:** the status and cure surfaces were published in accessible formats and, where legally required, in the applicable minority language(s).
6. **Channel-parity claim:** website, state portal, mirrored information pages, hotline/help scripts, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public answer surface**, not per-voter tracking histories by default.

- **Mail Ballot Status Surface Digest (MBSSD):** digest of the authoritative public status vocabulary, lookup contract, help paths, and effective window for a jurisdiction/scope.
- **Mail Ballot Cure Notice Digest (MBCND):** per-event digest for cure windows, accepted cure channels, deadline clarifications, stale-status corrections, or public-status taxonomy changes that affect voter actionability.
- **Mail Ballot Help Path Digest (MBHPD):** optional digest of the current public flow for “what should I do now?” outcomes such as `needs_action`, `contact_office`, or `ballot_not_found`.
- **Mail Ballot Status Parity Snapshot (MBSPS):** optional snapshot binding the effective mail-ballot status/cure guidance across declared official channels.
- **Mail Ballot Status Availability Snapshot (MBSAS):** optional digest for bounded uptime/degradation facts when the public lookup service is unavailable or lagging.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public mail-ballot-status payload

Keep the payload **small, decision-relevant, and privacy-first**.

Recommended fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_lookup_uri`
- `lookup_modes` (for example `portal`, `sms-info-page`, `office-contact`, `state-info-page`)
- public `status_terms` with plain-language explanations
- `effective_from` and optional `effective_until`
- public `cure_paths` / escalation pointer
- accessibility-format indicators
- `language_set`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Optional but useful:
- freshness note describing update cadence or known lag
- explicit distinction between **received**, **accepted**, **needs action**, **not found**, and **final rejection**
- bounded statement of the identifiers a voter may need to present, without disclosing matching thresholds or verification secrets

Do **not** publish by default:
- per-voter event histories
- signature images, cure affidavits, IDs, or uploaded documents
- matching heuristics, challenge thresholds, fraud signals, or queue-internal notes
- internal staff comments or adjudication work queues unless moved into controlled disclosure
- tiny-cell analytics that could facilitate intimidation, targeting, or voter-file reconstruction

## Status vocabulary discipline

This archive does **not** try to standardize state law or vendor products. It does require that the public surface make its own vocabulary legible.

Recommended discipline:
- publish the exact voter-facing labels the person may see,
- attach plain-language explanations,
- distinguish **“ballot sent”** from **“ballot received”** from **“ballot accepted”** from **“you must act now”**,
- distinguish **temporary uncertainty / lag** from **final rejection**,
- preserve a superseding trail when labels or explanations change.

The point is not one national taxonomy. The point is that later disputes should be about an explicit, timestamped public answer surface — not about a silently changing portal.

## Cure notices, deadlines, and anti-retcon rules

This evidence surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects whether or how a voter must act SHOULD produce a new **Mail Ballot Cure Notice Digest**.
- Silent mutation of cure deadlines, accepted cure channels, or the meaning of a status label SHOULD be treated as a governance failure.
- If the public status surface is delayed, unavailable, or known to be stale during a time-sensitive window, publish an outage or degraded-service notice with the alternate official path.
- If official channels disagree about a cure deadline or accepted remediation path, publish a parity snapshot or explicit correction note.
- Every superseding event SHOULD identify the replaced surface/version and the replacement effective state.

## Accessibility, language access, and fallback paths

A mail-ballot status surface only matters if an affected voter can actually use it.

Minimum publishable facts:
- which languages are provided for the status/cure/help path,
- which accessible formats or assistive paths are supported,
- the fallback contact or in-person path when the primary lookup fails,
- the effective date/time for the current public answer surface,
- whether cure materials or assistance are available through alternate channels for voters who cannot use the primary digital flow.

This is not a full compliance dossier. It is the **minimum operational truth surface** needed so status/cure failures do not disappear into rumor, selective anecdotes, or blame-shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for mail-ballot status and one authoritative path for cure/help guidance for the scope?
- Can we reconstruct what a voter would have been told at time `T`?
- Were cure deadlines and action paths explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the public surface preserve privacy while still giving a usable next-action path?

These are modest claims. But they are exactly the claims that determine whether a future dispute is about **facts** or about a missing public record.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/mail-ballot-status-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/mail-ballot-status-and-cure-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (local election office as practical source of state-specific voting information) (xref: `eac_voter_faqs_page`)
- EAC: Voting by Mail 101 (contact officials to verify whether a ballot was received in time to be counted) (xref: `eac_voting_by_mail_101_pdf`)
- EAC: Signature Verification and Cure Process (tracking, reconciliation, and PII-sensitive cure handling) (source: `eac_signature_verification_cure_process_pdf`)
- EAC: Best Practices: Accessibility for Voting by Mail (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`)
- EAC: Clearinghouse Resources on Election Mail (xref: `eac_election_mail_resources_page`)
- NASS: Can I Vote — Absentee & Early Voting (xref: `nass_absentee_early_voting_page`)
- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
