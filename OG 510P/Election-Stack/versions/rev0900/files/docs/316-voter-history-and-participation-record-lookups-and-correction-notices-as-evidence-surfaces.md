# 316. Voter history and participation-record lookups and correction notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “does the official participation record now show that this voter participated in election `E`, what participation fields were posted, what lag or correction semantics controlled that answer, and which help path applies if the record is missing or wrong?”** as an **evidence surface**.
The goal is not to publish poll books, ballot images, vote selections, or voter-file dumps. The goal is to make six things hard to fake after the fact:

1. **Which official public path the jurisdiction identified as authoritative** for voter-history / participation-record lookup in election scope `E`,
2. **Which election(s) or posting window the public answer surface covered**,
3. **What public participation fields the surface returned** (for example election date, method, county, or primary-ballot label),
4. **Whether the participation record had not yet posted, later posted, or was later corrected** because of canvass completion, county upload timing, record merge/split, wrong-jurisdiction attribution, or another bounded public correction reason,
5. **Whether the public had an explicit help path** when the participation record appeared missing or wrong, and
6. **Whether the public answer stayed consistent** across the voter portal, related status pages, help pages, and contact-routing surfaces.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already expose a distinct public answer path for **participation history / voting record**, not just live ballot status or registration status. Wisconsin’s current **My Voter Info** page says a voter can search by name to view registration information, voting history, request an absentee ballot, and make registration updates; the same surface tells a voter to contact the municipal clerk if the record cannot be found. Wisconsin’s current **Track My Ballot** page separately says that if a voter is looking to confirm the ballot was counted, that information will appear under **My Voter Info**, and it may take up to 30 days for the voting record to update for the 2026 Spring Primary. North Carolina’s current **Your Voter Record** page says the voter profile includes a distinct **Voter History** section showing election, voting method, voting county, and primary-ballot field; it also says county boards must upload participation information before voter history is assigned and that this may take up to a few weeks after Election Day. Nevada’s current **Voter Registration Search** page says registered voters can verify registration information, update mail-ballot preference, and **view their voting history**. Michigan’s current **Voter Participation Dashboard** explains the official timing semantics that make this surface distinct from live ballot tracking: early-voting participation is updated at cast time, absentee data is updated daily, Election Day voting is uploaded after Election Day, and metrics may change retroactively when clerks upload or correct records or when a voter moves. EAC’s current **Voter FAQs** page reinforces the broader point that election administration is decentralized and that practical voter-information questions must ultimately route to state or local election officials. (xref: `wisconsin_my_voter_info_page`, `wisconsin_track_my_ballot_page`, `north_carolina_your_voter_record_page`, `nevada_voter_registration_search_page`, `michigan_voter_participation_dashboard_page`, `eac_voter_faqs_page`)

That is a distinct dispute surface from adjacent docs. `docs/295` answers **what happened to a returned mail ballot and what action/cure path exists now**. `docs/296` answers **what happened to a provisional ballot and why**. `docs/294` answers **what the registration-status surface currently says about the voter record**. None of those, by themselves, fully capture the bounded public fact of **posted participation record**: whether the official record now shows that the person participated in election `E`, which public participation fields were posted, what lag note or correction reason controlled the answer, and which help path applied when the posted record looked wrong.

This document stays intentionally bounded. It is **not** a voter-file release policy, a pollbook spec, or a contest-by-contest turnout analytics paper. It is a claim that election offices should be able to prove which official public participation-record surface, posting-window semantics, and correction/help path controlled the public answer when a voter or reporter asked, **“does the record now show that I voted?”**

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative participation-record claim:** for election scope `E`, the jurisdiction identified one authoritative public path for voter history / participation-record lookup and one authoritative help path.
2. **Posting-window claim:** the public surface stated whether participation history was expected to post immediately, after Election Day, after county upload, after canvass, or after another bounded official step.
3. **Participation-record claim:** the public surface returned the public participation fields it chose to expose and distinguished them from confidential ballot selections.
4. **Correction/help-path claim:** where a participation record was missing, delayed, or corrected, the public surface stated the bounded reason class or routed the voter to the authoritative help path.
5. **Parity/accessibility claim:** the participation-record answer, lag notes, correction notices, and help path remained reachable in accessible and, where required, language-appropriate form.
6. **Privacy/minimization claim:** the public surface exposed only bounded participation facts needed for the answer, not vote choices, ballot images, or unnecessary personal data.

## Canonical digest artifacts

Publish **digests of the public participation-record surface**, not poll books or voter-file extracts by default.

- **Participation Record Surface Digest (PRSD):** digest of the authoritative public voter-history / participation-record payload for an election scope.
- **Participation Record Correction Notice Digest (PRCND):** per-event digest for delayed posting, corrected participation method/county/primary-ballot field, wrong-jurisdiction attribution, or another bounded public correction.
- **Participation Record Freshness Digest (PRFD):** optional digest describing the current posting/catch-up semantics for the public participation-record surface.
- **Participation Record Help Path Digest (PRHPD):** optional digest of the authoritative path for “my history looks wrong or has not posted yet.”
- **Participation Record Parity Snapshot (PRPS):** optional snapshot binding the effective public state across the voter portal, status/help pages, and official contact-routing surfaces.

## What belongs in the public participation-record payload

Keep the payload **small, election-scoped, and correction-friendly**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_history_uri`
- optional `authoritative_status_context_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `posting_lag_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or maintenance notice

Recommended history-entry fields:
- stable `history_entry_id`
- `election_id` and `election_date`
- `record_state`
- optional `voted_method`
- optional `voted_county`
- optional `primary_ballot_label`
- optional `posted_at`
- optional `correction_reason`
- bounded `plain_language`
- `notice_uri`

Recommended bounded vocabularies:
- `record_state`: `posted`, `pending_posting`, `not_yet_available`, `corrected`, `removed_due_to_public_correction`, `temporarily_unavailable`
- `correction_reason`: `county_upload_pending`, `canvass_not_complete`, `wrong_county_attribution_correction`, `participation_method_correction`, `record_merge_or_split`, `address_or_jurisdiction_correction`, `duplicate_history_reversal`, `other_bounded_public_correction`

Do **not** publish by default:
- ballot selections or contest-level vote choices
- ballot images, envelope images, or pollbook scans
- full voter-file exports when a bounded public answer plus pointer will do
- internal adjudication notes or challenge files
- unnecessary identity fields that are not needed to prove the public participation answer

## Participation-record semantics and anti-retcon rules

Participation-record surfaces should fail **loudly** when posted history changes.

Rules:
- Distinguish **live ballot pipeline status** from **posted participation history**. A ballot can be received or accepted before a voter-history surface is updated.
- Distinguish **registration status** from **participation record**. A voter can remain registered while the posted history for a recent election is still pending or later corrected.
- When the participation record is not expected to be final yet, publish a lag note rather than allowing the public to infer that missing history means non-participation.
- A change to posted participation method, county, primary-ballot field, or election attribution SHOULD produce a new **Participation Record Correction Notice Digest**.
- Silent mutation of posted history SHOULD be treated as a governance failure.
- If the public participation-history surface is unavailable during a time-sensitive dispute window, publish an outage or degraded-service notice with the authoritative fallback help path.

## Accessibility, language access, and fallback paths

A participation-record surface only matters if the affected voter can actually use it.

Minimum publishable facts:
- which languages are provided for the participation-record and help path,
- which accessible formats or assistive paths are supported,
- the fallback office/contact route when the primary lookup fails,
- the effective date/time and posting-lag note for the current public answer surface,
- whether the public answer distinguishes “not yet posted” from “posted and corrected” from “currently unavailable.”

This is not a full compliance dossier. It is the **minimum operational truth surface** needed so missing or corrected voter history does not disappear into rumor, selective anecdotes, or stale screenshots. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for participation-record lookup and one authoritative help path?
- Can we reconstruct what a voter would have been told at time `T` about whether participation history had posted?
- Did official channels distinguish live ballot status from posted voter history?
- Were posting delays and later corrections explicit, or silently edited away?
- Did the public surface preserve ballot secrecy and privacy while still giving a usable next-action path?

These are modest claims. But they are exactly the claims that determine whether a future dispute is about **facts** or about a missing public record.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voter-history-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voter-history-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- Wisconsin Elections Commission: My Voter Info (xref: `wisconsin_my_voter_info_page`)
- Wisconsin Elections Commission: Track My Ballot (xref: `wisconsin_track_my_ballot_page`)
- North Carolina State Board of Elections: Your Voter Record (xref: `north_carolina_your_voter_record_page`)
- Nevada Secretary of State: Voter Registration Search (xref: `nevada_voter_registration_search_page`)
- Michigan Department of State: Voter Participation Dashboard (xref: `michigan_voter_participation_dashboard_page`)
