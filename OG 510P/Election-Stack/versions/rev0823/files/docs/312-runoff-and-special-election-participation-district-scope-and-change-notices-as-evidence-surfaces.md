# 312. Runoff and special-election participation, district scope, and change notices as evidence surfaces

**Track:** Shared

This document treats the **public answer surface for “is there a runoff or special election for my district, which contest or vacancy does it cover, may I participate, which prior-round rules carry forward, and what changed?”** as an **evidence surface**.
The goal is not to publish full candidate-filing packets, district-shape GIS data, or a fifty-state digest of runoff law. The goal is to make six things hard to fake after the fact:

1. **Which public surface the jurisdiction identified as authoritative** for a runoff or special election affecting scope `E`,
2. **Which election type and geographic scope the public said applied** (for example `primary_runoff`, `special_election`, `special_runoff`, or local runoff),
3. **Whether ordinary registration, party-affiliation carry-forward, prior-round participation, or another bounded rule controlled eligibility**,
4. **Whether district/territory scope, registration timing, or prior-round semantics materially changed voter actionability**,
5. **Whether the public answer clearly distinguished “is this election for me at all?” from adjacent questions about ballot style, calendar dates, or generic primary rules**, and
6. **When participation scope, deadlines, district coverage, or carry-forward semantics changed across official channels.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`
- `docs/309-primary-election-participation-party-affiliation-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter can know the ordinary primary model or the general election calendar and still be misled about a **runoff or special election that only partially overlaps the usual electorate**. The practical question is often not just “when is the election?” but “is there actually a special or runoff election for *my* district, does my ordinary registration suffice, did my party choice in the prior round constrain this runoff, and what changed after the call, proclamation, or court order?” If those facts are scattered across mutable notices, candidate pages, and calendars, later disputes turn into arguments about memory instead of evidence.

Current official guidance and practice make that problem concrete. EAC’s current **Voter FAQs** page says election administration is highly decentralized and that the best source of practical registration and voting information is the local elections office. Texas’s current **Current Election Information** page separately lists special runoff elections, primary elections, and the linked law-calendar material for the current cycle. Texas’s current **Party Affiliation Questions and Answers** advisory explains that a voter who did not vote in the general primary may still vote in the subsequent primary runoff, while a voter who voted in one party’s primary may vote only in that party’s runoff during the same calendar year. Georgia’s current **Call for Special Election — U.S. House District 14** page publicly states the special-election date, the affected counties and partial-county scope, the “special runoff if needed” date, and the voter-registration deadline for that election. (xref: `eac_voter_faqs_page`, `texas_current_elections_information_page`, `texas_party_affiliation_questions_answers_advisory_2022_11_page`, `georgia_call_for_special_election_us_house_district_14_page`)

That is exactly why this surface should stay compact. The archive should not become a fifty-state treatise on runoffs, vacancy law, or redistricting edge cases. It should instead preserve the bounded public facts that controlled actionability at time `T`: what kind of election the public said this was, which district or territory it covered, whether party carry-forward or prior-round facts mattered, whether a voter-registration deadline or district-scope clarification materially changed the answer, and where the official detailed help path lived.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative runoff/special-election claim:** for election scope `E`, the jurisdiction identified one authoritative public path for runoff/special-election participation rules and one authoritative help path.
2. **Election-type/scope claim:** the public surface stated what kind of election this was (`primary_runoff`, `special_election`, `special_runoff`, `uniform_runoff`, or other locally-described type) and what territory it covered.
3. **Participation-basis claim:** the public surface stated whether ordinary registration in the covered territory was enough, whether party-affiliation carry-forward mattered, whether prior-round participation mattered, or whether another clearly described rule controlled participation.
4. **Timing claim:** if a registration deadline, affiliation deadline, district-scope change, or other timing rule materially affected participation, the public surface stated that timing and pointed to the authoritative detailed rule.
5. **Carry-forward claim:** if the runoff or special election inherited a prior-round party linkage, ballot path, or district-scope relation, the public surface explained that clearly enough to avoid false assumptions.
6. **Change-log/parity claim:** corrections to election type, district scope, registration timing, or carry-forward semantics were published as explicit superseding events rather than silent edits, and official channels converged on the same effective public answer.

## Canonical digest artifacts

Publish **digests of the public runoff/special-election participation surface**, not individualized voter histories or district assignments.

- **Runoff/Special Election Participation Surface Digest (RSEPSD):** digest of the authoritative public payload for a scope.
- **Runoff/Special Election Change Notice Digest (RSECND):** per-event digest for changed election type, district scope, registration timing, or carry-forward semantics.
- **Runoff/Special Election Scope Advisory Digest (RSESAD):** optional digest for bounded court-order, vacancy, cancellation, merger, or territorial-scope advisories.
- **Runoff/Special Election Parity Snapshot (RSEPS):** optional snapshot binding the effective public answer surface across declared official channels.
- **Runoff/Special Election Help Path Digest (RSEHPD):** optional digest of the current official escalation path when a voter cannot determine whether the election is in scope for them.

## What belongs in the public runoff/special-election payload

Keep the payload **small, action-relevant, and explicit about scope/carry-forward semantics**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_scope_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `election_type`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended scope/participation fields:
- stable `scope_rule_id`
- `office_or_measure_label`
- `district_scope_description`
- `geographic_coverage`
- `participation_basis`
- optional `registration_deadline`
- optional `party_carry_forward_rule`
- optional `prior_round_participation_required`
- optional `mail_ballot_continuity_note`
- `detail_surface_uri` or `detail_surface_ref`
- bounded `plain_language`
- optional `notice_uri`

Suggested `election_type` values:
- `primary_runoff`
- `special_election`
- `special_runoff`
- `uniform_runoff`
- `local_runoff`
- `special_primary`
- `other_local_model`

Suggested `participation_basis` values:
- `registered_voter_in_scope`
- `registered_voter_in_scope_with_party_carry_forward`
- `registered_voter_in_scope_no_prior_round_required`
- `registered_voter_in_scope_prior_round_required`
- `see_detailed_rule`

Do **not** publish by default:
- individualized district-lookup histories or geolocation traces
- prior-round party rosters or individualized participation histories
- copied state statutes or vacancy law digests when a bounded summary plus pointer will do
- full candidate qualifying packets or internal election-order drafts
- ballot-style details already owned by `docs/293`

## Semantics and anti-retcon rules

This surface should fail **loudly** when scope or participation semantics change.

Rules:
- A change that affects whether a runoff or special election exists for a voter’s covered territory SHOULD produce a new change notice digest.
- A change that affects district coverage, county coverage, precinct scope, or vacancy scope SHOULD produce a new change notice digest.
- A change that affects whether prior primary affiliation, same-party carry-forward, or no prior-round participation controls eligibility SHOULD produce a new change notice digest.
- The surface SHOULD distinguish **ordinary primary model** from **runoff-specific carry-forward semantics**.
- The surface SHOULD distinguish **calendar timing** from **in-scope participation semantics**.
- If a special election includes only part of a county or district, the public surface SHOULD say so clearly enough to avoid a false countywide answer.
- If the election is cancelled, merged, or replaced by a superseding order, the public surface SHOULD publish an explicit advisory rather than quietly disappearing the older answer.
- Silent mutation of district scope, registration deadline language, or runoff participation semantics without a superseding event SHOULD be treated as a governance failure.
- If different audiences are sent to different participation answers, publish a parity snapshot (`201`) and follow it with a signed correction notice.

## Overlap rules (to keep the surface bounded)

### `308` is the date synthesis surface; `312` is the scope/participation surface

`308` answers: **which dates, windows, and deadline semantics control action right now?**
`312` answers: **is this runoff or special election actually in scope for me, and do any special carry-forward participation rules apply?**

Do not collapse them. A correct calendar with the wrong district or runoff-eligibility semantics still fails voters.

### `309` handles ordinary primary-participation models; `312` handles exceptional election-type carry-forward and district scope

`309` answers: **which primary model applies, and how do party affiliation/declaration rules usually control ballot eligibility?**
`312` answers: **for a runoff or special election, what changed about scope, district coverage, or prior-round participation semantics?**

Do not collapse them. A jurisdiction can have correct standing primary rules and still confuse voters about a special runoff affecting only part of the electorate.

### `293` owns ballot style; `312` owns “is this election for me at all?”

If the voter needs the detailed ballot contents, use `293`.
If the voter first needs to know whether the runoff or special election is in scope for their district or prior-round status, use `312`.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public runoff/special-election participation surface at time `T`?
- Can we reconstruct which election type, district scope, and counties/territories the public was told were covered?
- Did the public surface say whether ordinary registration, party carry-forward, or prior-round participation controlled eligibility?
- Were registration deadlines, “if needed” runoff dates, and scope clarifications explicit rather than implied?
- Did website, FAQ, proclamation/call notice, downloadable guidance, and help scripts converge on the same effective answer?
- Were late corrections explicit, or quietly edited into mutable pages after disputes arose?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/runoff-and-special-election-participation-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/runoff-and-special-election-participation-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- Texas Secretary of State: Current Election Information (xref: `texas_current_elections_information_page`)
- Texas Secretary of State: Party Affiliation Questions and Answers — Advisory 2022-11 (xref: `texas_party_affiliation_questions_answers_advisory_2022_11_page`)
- Georgia Secretary of State: Call for Special Election — U.S. House District 14 (xref: `georgia_call_for_special_election_us_house_district_14_page`)
