# 296. Provisional-ballot status lookups and reason notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public provisional-ballot free-access system** as an **evidence surface**.
The goal is not to expose case files or adjudication internals. The goal is to make five things hard to fake after the fact:

1. **What a provisional voter was told** about whether the ballot counted,
2. **What reason was given** if it did not count,
3. **Which official path** existed to check status or provide additional information,
4. **When that public answer changed**, and
5. **Whether the answer stayed private, accessible, and channel-consistent**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

HAVA does more than require provisional ballots in defined cases. It also requires a **free access system** — such as a toll-free phone number or website — so a provisional voter can learn whether the ballot was counted and, if not, why not. The same section also requires reasonable procedures to protect the security, confidentiality, and integrity of personal information, and restricts access to information about an individual provisional ballot to the individual who cast it. (xref: `uscode_52_usc_21082_provisional_voting_page`)

That makes the public provisional-ballot status surface unusually important: it is both a **voter-rights surface** and a **privacy surface**. If it drifts, goes stale, disappears, or silently changes its reason language, later disputes are no longer about a missing record in the back office. They are about a broken public-rights interface. EAC’s current provisional-voting materials emphasize transparent, public, and uniform standards; publicizing how many provisional ballots were issued, counted, and not counted; and using tracking/free-access communications so provisional voters can understand outcomes. (xref: `eac_provisional_voting_page`, `eac_best_practices_provisional_voting_2023_pdf`)

This surface also has to work for real voters under stress. EAC best practices recommend web and social media information, toll-free office contact, printed information explaining how to check whether a provisional ballot was counted, public posting of provisional-voting rights and complaint procedures, status/cure instructions for poll workers, and accessible ballot-marking / alternative-language support where applicable. DOJ’s Section 203 guidance remains a load-bearing reminder that when covered jurisdictions provide election notices, forms, instructions, assistance, or other materials or information, they must provide them in the applicable minority language as well as English. (xref: `eac_best_practices_provisional_voting_2023_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative status-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for provisional-ballot status lookup and one authoritative public help path for next steps or complaints.
2. **Free-access/privacy claim:** the surface declared the voter-access method while preserving the rule that only the individual provisional voter should gain access to the individual ballot-status answer.
3. **Reason-vocabulary claim:** the public surface published the status labels and not-counted reason language a voter may encounter in plain language.
4. **Correction/outage claim:** stale-status conditions, outage windows, reason-language corrections, and deadline/help-path changes were published as explicit superseding events rather than silent edits.
5. **Accessibility/language claim:** the status/help surface was published in accessible formats and, where legally required, in the applicable minority language(s).
6. **Channel-parity claim:** website, toll-free instructions, voter handouts, hotline/help scripts, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public answer surface**, not per-voter case histories by default.

- **Provisional Ballot Status Surface Digest (PBSSD):** digest of the authoritative public lookup contract, status vocabulary, reason vocabulary, help paths, and effective window for a jurisdiction/scope.
- **Provisional Ballot Reason Notice Digest (PBRND):** per-event digest for reason-language changes, deadline/help-path corrections, status-surface outages, or other changes that affect what a provisional voter is told.
- **Provisional Ballot Help Path Digest (PBHPD):** optional digest of the current public flow for outcomes such as `counted`, `not_counted`, `needs_more_information`, `contact_office`, or `status_unavailable`.
- **Provisional Ballot Status Parity Snapshot (PBSPS):** optional snapshot binding the effective provisional-ballot status/help surface across declared official channels.
- **Provisional Ballot Status Availability Snapshot (PBSAS):** optional digest for bounded uptime/degradation facts when the free-access system is unavailable or lagging.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public provisional-ballot-status payload

Keep the payload **small, decision-relevant, and privacy-first**.

Recommended fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_lookup_uri` or `authoritative_lookup_phone`
- `lookup_modes` (for example `portal`, `toll_free_phone`, `local_office_contact`)
- public `status_terms` with plain-language explanations
- public `not_counted_reason_terms` with plain-language explanations
- `effective_from` and optional `effective_until`
- `help_paths` / complaint pointer
- accessibility-format indicators
- `language_set`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Optional but useful:
- a freshness note describing update cadence or known lag
- explicit distinction between **received for review**, **counted**, **not counted**, and **additional information may still be accepted** where local law provides such a step
- a statement of the identifiers or affirmation facts a voter may need to present to access the answer, without disclosing matching logic or secrets

Do **not** publish by default:
- per-voter histories or searchable lists of provisional voters
- scanned affidavits, IDs, signatures, challenge statements, or envelope images
- eligibility heuristics, investigative notes, law-enforcement referrals, or fraud flags
- internal queue state, poll-worker discipline notes, or tiny-cell analytics that could facilitate harassment or re-identification

## Reason-vocabulary discipline

This archive does **not** standardize state law or impose one national reason-code set. It does require that the public surface make its own vocabulary legible.

Recommended discipline:
- publish the exact voter-facing labels a provisional voter may encounter,
- attach plain-language explanations,
- distinguish **“not yet resolved”** from **“not counted”** from **“counted”**,
- distinguish a missing-status or degraded-service condition from a final disposition,
- preserve a superseding trail when labels or explanations change.

The point is not one national taxonomy. The point is that later disputes should be about an explicit, timestamped public answer surface — not a silently changing portal or call-center script.

## Free-access, privacy, and anti-retcon rules

This evidence surface should fail **loudly** when voter actionability or privacy posture changes.

Rules:
- A change that affects whether or how a voter can learn the ballot’s status SHOULD produce a new **Provisional Ballot Reason Notice Digest**.
- Silent mutation of not-counted reason language, free-access instructions, or complaint/help paths SHOULD be treated as a governance failure.
- If the public status surface is delayed, unavailable, or known to be stale during a time-sensitive period, publish an outage or degraded-service notice with the alternate official path.
- If official channels disagree about the meaning of a status label, a reason label, or a deadline for providing additional information, publish a parity snapshot or explicit correction note.
- Every superseding event SHOULD identify the replaced surface/version and the replacement effective state.
- The public surface SHOULD explain access steps without expanding visibility beyond the individual provisional voter.

## Accessibility, language access, and next-step clarity

A provisional-ballot status surface only matters if the affected voter can actually use it.

Minimum publishable facts:
- which languages are provided for the status/help path,
- which accessible formats or assistive paths are supported,
- the fallback contact or in-person office path when the primary free-access system fails,
- the effective date/time for the current public answer surface,
- whether the voter-facing materials explain what to do next after a `not_counted` or `needs_more_information` answer.

This is not a full compliance dossier. It is the **minimum operational truth surface** needed so provisional-ballot disputes do not disappear into rumor, selective anecdotes, or silent portal edits. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (xref: `eac_best_practices_provisional_voting_2023_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for checking provisional-ballot status for the scope?
- Could a provisional voter learn whether the ballot counted and, if not, why not?
- Did the public surface preserve privacy while still giving a usable answer path?
- Were reason labels and help instructions explicit, or silently edited away?
- Did official channels converge on the same effective public state?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken public-rights interface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/provisional-ballot-status-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/provisional-ballot-status-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- 52 U.S.C. § 21082 / HAVA provisional-voting and free-access requirements (xref: `uscode_52_usc_21082_provisional_voting_page`)
- EAC: Provisional Voting overview and transparency/accountability recommendations (xref: `eac_provisional_voting_page`)
- EAC: Best Practices: Provisional Voting (2023) (source: `eac_best_practices_provisional_voting_2023_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
