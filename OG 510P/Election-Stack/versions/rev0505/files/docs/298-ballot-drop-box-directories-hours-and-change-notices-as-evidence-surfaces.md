# 298. Ballot drop-box directories, hours, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “where can I return my completed mail ballot, until when, and what changed?”** as an **evidence surface**.
The goal is not to expose collection routes, camera layouts, or internal security procedures. The goal is to make five things hard to fake after the fact:

1. **Which ballot drop boxes the jurisdiction told voters were official** for a given election scope,
2. **When each drop box was available for deposits** and what the effective deadline semantics were,
3. **When a closure, move, temporary disablement, or hours change was announced**,
4. **What alternate official path the voter was given** if the original drop box was unavailable, and
5. **Whether official channels stayed consistent, accessible, and language-complete** during the change.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A ballot drop box is not just a logistics object. For the voter, it is a **public return-channel surface**: a location, a time window, and a trust signal. Later disputes are often narrower than “were drop boxes secure?” The practical question is: **what did the official public surface tell voters at time `T` about which drop boxes were official, where they were, and whether they were still accepting ballots?**

Current official guidance makes that a distinct voter-information problem. EAC’s current voter-facing drop-box FAQ says some states allow voters to return mail ballots in secure drop boxes, tells voters to make sure the box is clearly marked as belonging to their county/city/township, says ballots should be returned no later than the close of polls on Election Day, and directs voters to official state or territory election websites to confirm availability in their area. EAC’s general vote-by-mail FAQ likewise says return options vary by jurisdiction and tells voters to carefully read return instructions and check official state resources. NASS’s **Can I Vote** absentee/early-voting page repeats that state laws vary greatly and directs voters to information provided by election officials or the local election office. (source: `eac_how_do_drop_boxes_work_page`, `eac_how_do_i_vote_by_mail_page`, `nass_absentee_early_voting_page`)

That means the public drop-box surface needs tighter anti-retcon discipline than a generic “mail voting exists” page. The EAC ballot-drop-box quick-start guide says officials should follow state statutes on permissible locations, choose accessible locations, provide a list or map of drop box locations on the website and with mail-ballot instructions, and have teams present as the ballot-return deadline passes so voters in line by the deadline may still deposit ballots before the box is locked. Those are operational details, but they also imply a bounded **public facts surface**: list/map, effective availability, clear deadline semantics, and explicit updates when a box is moved, closed, or taken out of service. (source: `eac_ballot_drop_boxes_qsg_pdf`)

Accessibility and language access remain load-bearing. EAC’s accessibility guidance for voting by mail emphasizes that voting outside the polling place still must be accessible, and DOJ’s Section 203 guidance explains that when covered jurisdictions provide election notices, forms, instructions, assistance, or other election-related materials or information, they must provide them in the applicable minority language as well as English. A drop-box change notice is exactly the kind of operational information that cannot disappear into an inaccessible or English-only side channel. (source: `eac_best_practices_accessibility_voting_by_mail_page`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative drop-box directory claim:** for election scope `E`, the jurisdiction identified one authoritative public path for ballot drop-box locations and availability.
2. **Availability-window claim:** each drop-box record declared the effective dates/times during which voter deposits were intended to be accepted.
3. **Deadline-semantics claim:** the public surface declared the operative deposit cutoff semantics for each box or class of boxes (for example close of polls, building close, or box-specific final deposit time where lawful).
4. **Change-log claim:** closures, relocations, temporary disablements, overflow notices, and hours changes were published as explicit superseding events rather than silent edits.
5. **Alternate-path claim:** if a drop box became unavailable or risky to use, the public surface named the replacement box, local office return option, mail path, or other official help path.
6. **Accessibility/language/parity claim:** website, downloadable instructions, mailed instruction sheet, hotline/help script, and signed notices converged on the same effective public state and remained accessible and language-complete where required.

## Canonical digest artifacts

Publish **digests of the public drop-box surface**, not collection routes, camera layouts, or custody worksheets by default.

- **Ballot Drop Box Directory Digest (BDBDD):** digest of the authoritative public drop-box directory payload for a scope.
- **Ballot Drop Box Change Notice Digest (BDBCND):** per-event digest for closure, relocation, temporary disablement, corrected hours, or deadline clarification.
- **Ballot Drop Box Help Path Digest (BDBHPD):** optional digest of the current public fallback path when a voter encounters a full box, inaccessible path, stale listing, or last-minute closure.
- **Ballot Drop Box Parity Snapshot (BDBPS):** optional snapshot binding the effective drop-box directory/help surface across declared official channels.
- **Ballot Drop Box Availability Snapshot (BDBAS):** optional digest for bounded uptime/degradation facts when the directory/map is unavailable or stale.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public drop-box payload

Keep the payload **small, decision-relevant, and deadline-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_directory_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended per-drop-box fields:
- stable `drop_box_id`
- human-facing name
- `status` (`available`, `temporarily_unavailable`, `moved`, `closed`, `superseded`)
- host facility / coarse location context
- public address / directions pointer
- `availability_windows` as explicit date/time ranges rather than prose alone
- `deposit_deadline_at` or `deposit_deadline_rule`
- `official_marking_text` or official ownership hint where useful for voters
- accessibility summary
- language-support summary
- replacement drop-box pointer when applicable
- public contact/help pointer
- bounded notes field for same-day clarifications

Optional but useful:
- `indoor_or_outdoor` / building-access qualifier when it changes deadline semantics
- weather/emergency exception label
- pointer to the most recent signed notice that changed the location, hours, or availability

Do **not** publish by default:
- exact collection routes, schedules, or vehicle details
- security camera placement, alarm details, or internal access-control information
- chain-of-custody logs with signatures or other operational-security detail
- incident channels, harassment reports, or tiny-cell usage analytics that materially raise targeting risk

## Deadline semantics and anti-retcon rules

A voter-information surface should fail **loudly** when a return option changes.

Rules:
- A change that affects whether, where, or until when a voter can deposit a ballot SHOULD produce a new **Ballot Drop Box Change Notice Digest**.
- Silent mutation of a drop-box directory or map without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD distinguish **directory availability** from **deposit acceptance**. If a building remains open after ballot deposit ends, or a box is inside a building that closes early, that distinction must be explicit.
- Same-day disablements or overflow/maintenance events SHOULD include the effective time of the change and the replacement path.
- If official channels disagree about whether a box is official, accessible, or still accepting deposits, publish a parity snapshot or explicit correction note.

The point is not one national rule. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable webpage or social post “used to say.”

## Accessibility, language access, and next-step clarity

A drop-box directory only matters if a voter can act on it without guesswork.

Minimum publishable facts:
- which languages are provided for the directory/help path,
- which accessible path or alternate return option is available,
- the effective date/time for the current public answer surface,
- the operative deposit deadline semantics,
- the fallback official path if a box is unavailable, inaccessible, or no longer accepting deposits.

This is not a full security dossier or compliance file. It is the **minimum operational truth surface** needed so drop-box confusion does not disappear into rumor, selective screenshots, or after-the-fact blame shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `eac_best_practices_accessibility_voting_by_mail_page`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for official ballot drop boxes for the scope?
- Can we reconstruct what a voter would have been told at time `T` about whether a specific box was official and still accepting deposits?
- Were closures, moves, temporary disablements, and deadline clarifications explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the public surface preserve accessibility and language-complete alternate paths when a change mattered?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken public return-channel surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/ballot-drop-box-directory-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/ballot-drop-box-directory-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: How do drop boxes work? (source: `eac_how_do_drop_boxes_work_page`)
- EAC: How do I vote by mail? (source: `eac_how_do_i_vote_by_mail_page`)
- NASS: Can I Vote — Absentee & Early Voting (source: `nass_absentee_early_voting_page`)
- EAC: Ballot Drop Boxes quick-start guide (source: `eac_ballot_drop_boxes_qsg_pdf`)
- EAC: Best Practices: Accessibility for Voting by Mail (source: `eac_best_practices_accessibility_voting_by_mail_page`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
