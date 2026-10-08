# 314. Candidate withdrawal, death, disqualification, and replacement notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “did the candidate field for this office change, does a withdrawn/disqualified/deceased candidate still appear anywhere official, was a replacement or reopened filing window created, and which notice now controls?”** as an **evidence surface**.
The goal is not to publish internal candidate-vetting files, litigation work product, or campaign-finance records. The goal is to make six things hard to fake after the fact:

1. **Which official public path the jurisdiction identified as authoritative** for candidate-field changes in election scope `E`,
2. **Which office or race the change applied to**,
3. **What event changed the public answer** (withdrawal, death, disqualification/ineligibility, nomination set-aside, replacement nomination, reopened filing window, or equivalent jurisdiction-specific event),
4. **Whether the candidate remained on any public surface after the event** and, if so, which superseding notice told voters how to interpret that fact,
5. **Whether a replacement path, reopened filing window, write-in window change, or other remedial public step was created**, and
6. **Whether candidate lists, sample ballots, voters’ guides, FAQs, hotline scripts, and signed notices stayed consistent about the changed field**.

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
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`
- `docs/312-runoff-and-special-election-participation-district-scope-and-change-notices-as-evidence-surfaces.md`
- `docs/313-ballot-measure-explanatory-texts-official-voter-guides-and-voters-pamphlets-as-evidence-surfaces.md`

## Why this exists (bounded)

Candidate-field changes are not just a candidate-filing issue. They become a voter-facing evidence problem the moment a voter, helper, journalist, poll worker, or court has to answer **“who is actually in this race now, what stale material may still exist, and which official notice superseded it?”** Current official election sources already expose this as a distinct public surface. Washington’s current elections calendar publishes a candidate withdrawal deadline followed immediately by candidate certification and voters’ pamphlet milestones, and Washington’s current withdrawal page says a signed withdrawal must be received by the filing office by 5 p.m. on the Monday following filing to remove the candidate’s name from the ballot. Texas’s current 2026 advisory on vacancies and replacement nominees says death, withdrawal, or ineligibility can trigger extended filing deadlines, requires notice of that extended deadline within 24 hours, requires a supplemental electronic list of new candidates, and separately defines when a replacement nominee may be selected because the original nominee’s name will not appear on the general-election ballot. Virginia’s current public **Candidates & Referendums** page likewise tells the public that if a political-party nominee dies, withdraws, or has the nomination set aside, a new candidate and party filing window opens for that office with a new filing deadline, while pointing voters to the applicable public one-pager and local registrar for office-specific details. (xref: `washington_elections_calendar_page`, `washington_withdrawal_of_candidacy_page`, `texas_deadlines_vacancies_and_replacement_nominees_2026_page`, `virginia_candidates_and_referendums_page`)

That is a distinct dispute surface from adjacent docs. `docs/293` answers **what ballot style or sample-ballot answer was published for a voter or address**. `docs/308` answers **which dates and deadline windows controlled action**. `docs/313` answers **which explanatory-guide or pamphlet materials accompanied a race or measure**. None of those fully capture the bounded public facts created when the candidate field changes after filing: whether a stale sample ballot or guide still lists the departed candidate, whether a new filing window or replacement nomination opened, whether a candidate list was reissued, whether a write-in or party-substitution path changed, and what superseding notice told the public how to interpret the mismatch. Those correction semantics are the reason this deserves a separate surface rather than a footnote inside `293` or `308`.

This document stays intentionally bounded. It is **not** a guide to ballot-access law in all fifty states. It is a claim that election offices should be able to prove which official public notice, candidate list, correction chain, and fallback help path controlled the public answer after the candidate field changed.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative candidate-change claim:** for election scope `E`, the jurisdiction identified one authoritative public path for candidate-field changes and one authoritative help path.
2. **Affected-race claim:** each public event identified the office, district, or race whose candidate field changed.
3. **Event-type claim:** the public surface stated whether the change was a withdrawal, death, disqualification/ineligibility, nomination set-aside, replacement nomination, reopened filing window, write-in deadline change, or another bounded jurisdiction-defined event.
4. **Surface-effect claim:** the public surface stated whether the affected candidate would still appear on any ballot, sample ballot, candidate list, guide, or pamphlet artifact, and which superseding notice now controlled voter interpretation.
5. **Remedial-path claim:** where law created a replacement nomination, reopened filing window, supplemental candidate list, or similar remedial path, the public surface stated that path and its deadline semantics.
6. **Parity/accessibility claim:** candidate lists, current-election pages, sample ballots, guides/pamphlets, FAQs, hotline/help scripts, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate form.

## Canonical digest artifacts

Publish **digests of the public candidate-change surface**, not internal challenge files.

- **Candidate Field Change Surface Digest (CFCSD):** digest of the authoritative public candidate-change payload for an election scope.
- **Candidate Field Change Notice Digest (CFCND):** per-event digest for a withdrawal, death, disqualification, nomination set-aside, replacement nomination, or reopened filing event.
- **Candidate List Update Digest (CLUD):** optional digest binding the updated public candidate list or supplemental candidate list to the change notice.
- **Candidate Replacement / Reopened Filing Digest (CRRFD):** optional digest binding a replacement nomination path, reopened filing window, or related remedial public action.
- **Candidate Change Parity Snapshot (CCPS):** optional snapshot binding the effective public state across candidate lists, sample ballots, guides, calendars, and signed notices.
- **Candidate Change Help Path Digest (CCHPD):** optional digest of the authoritative help path when the public cannot safely infer the current candidate field from stale printed or cached material.

## What belongs in the public candidate-change payload

Keep the payload **small, office-specific, and correction-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_candidate_change_uri`
- optional `authoritative_candidate_list_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or maintenance notice

Recommended change-event fields:
- stable `event_id`
- `office_or_race_label`
- optional `district_scope_note`
- `affected_candidate_name`
- `event_type`
- `event_effect_on_public_surface`
- optional `replacement_path_uri`
- optional `reopened_filing_window`
- optional `write_in_window_change`
- optional `candidate_list_update_uri`
- optional `sample_ballot_ref`
- optional `guide_or_pamphlet_ref`
- bounded `plain_language`
- `notice_uri`

Recommended bounded vocabularies:
- `event_type`: `withdrawal`, `death`, `disqualification`, `ineligibility`, `nomination_set_aside`, `replacement_nomination`, `reopened_filing_window`, `write_in_window_change`, `other_bounded_public_event`
- `event_effect_on_public_surface`: `removed_before_certification`, `may_remain_on_printed_or_cached_material`, `replacement_candidate_to_be_listed`, `reopened_filing_window`, `supplemental_candidate_list_expected`, `local_office_contact_required`, `other_public_effect`

Do **not** publish by default:
- internal candidate-vetting memoranda or litigation work product
- campaign-finance files or personal contact details beyond the already-public help path
- copied statewide ballot-access treatises when a bounded summary plus pointer will do
- unverified social-media rumors about candidate status
- internal reasons for disqualification beyond the bounded public notice

## Candidate-change semantics and anti-retcon rules

Candidate-field changes should fail **loudly** when the public answer changes.

Rules:
- A withdrawal, death, disqualification/ineligibility, nomination set-aside, replacement nomination, or reopened filing event SHOULD produce a new change notice digest.
- If the public answer changes because an affected candidate will still appear on a previously printed or cached ballot, sample ballot, pamphlet, or candidate list, the notice SHOULD say so plainly rather than pretending all channels updated at once.
- If law creates a replacement nomination, reopened filing window, supplemental candidate list, or extended write-in path, that remedial public step SHOULD be published as part of the same change family rather than left implicit in a candidate guide for insiders.
- Silent replacement of a candidate list PDF, silent rewrite of a sample-ballot page, or silent deletion of a candidate statement SHOULD be treated as a governance failure.
- Where different offices control the public answer (for example state filing officer versus local registrar), the surface SHOULD say which office is authoritative for the affected race and point to the fallback help path.
- If calendars, candidate lists, sample ballots, or pamphlets diverge during a correction window, publish a parity snapshot (`201`) and a signed correction notice.
- This surface SHOULD point outward to `293`, `308`, `312`, or `313` where needed instead of swallowing those domains.

## Accessibility, translation, and public reach

Candidate-change answers often reach the public through several channels at once: current-election page, candidate-list PDF, sample ballot, guide/pamphlet, FAQ, registrar notice, hotline script, or signed web notice.

Minimum publishable facts:
- which office/race changed,
- what event changed the public answer,
- whether the affected candidate remains on any public artifact,
- whether a replacement path or reopened filing window exists,
- which office/help path now controls,
- which signed notice superseded the prior answer.

A jurisdiction does not get to count a stale sample ballot or archived guide as the whole answer once a candidate-field change becomes official.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public candidate-change surface at time `T`?
- Which office or race changed, and what event caused the change?
- Did the public surface say whether the affected candidate still appeared on any ballot, sample ballot, candidate list, or guide artifact?
- If a replacement, reopened filing window, or extended write-in path existed, was it published clearly and in time?
- Did candidate lists, calendars, sample ballots, guides, and help channels converge on the same effective public state?
- Were corrections explicit and timestamped, or silently edited away?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/candidate-change-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/candidate-change-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Washington Secretary of State: Elections Calendar (xref: `washington_elections_calendar_page`)
- Washington Secretary of State: Withdrawal of Candidacy (xref: `washington_withdrawal_of_candidacy_page`)
- Texas Secretary of State: Deadlines for Vacancies and Replacement Nominees for the General Election for State and County Officers (November 3, 2026) (xref: `texas_deadlines_vacancies_and_replacement_nominees_2026_page`)
- Virginia Department of Elections: Candidates & Referendums (xref: `virginia_candidates_and_referendums_page`)
