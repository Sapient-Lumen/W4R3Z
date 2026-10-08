# 315. Precinct, district, and jurisdiction lookups and assignment change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “which precinct, voting districts, and local election jurisdiction apply to this address or voter record right now, what downstream election scope follows from that assignment, and which notice controls if that answer changed?”** as an **evidence surface**.
The goal is not to publish full GIS boundary files, internal geocoding logic, or statewide district-law treatises. The goal is to make six things hard to fake after the fact:

1. **Which official public path the jurisdiction identified as authoritative** for precinct / district / jurisdiction assignment in election scope `E`,
2. **What public input basis controlled the answer** (registered-voter record, residential-address lookup, county+address lookup, or another bounded public input),
3. **Which precinct, districts, and local election office/jurisdiction the public surface returned**,
4. **Whether the assignment answer changed** because of address correction, residential move update, precinct reassignment, district-boundary update, special-election scope update, or another bounded public change,
5. **Whether downstream pages stayed consistent** about polling place, ballot style, special-election scope, elected-official lookup, or local-board routing after the assignment changed, and
6. **Whether the public had an explicit fallback help path** when the assignment answer could not be safely inferred from stale or partial material.

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
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/312-runoff-and-special-election-participation-district-scope-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **assignment and scope**, not just for polling places or sample ballots. Maryland’s current **Voter Lookup** says the tool can show a voter’s registration record, polling place, voting districts, local board of elections, mail-in/provisional ballot status, and sample ballot; Maryland’s current **Voting Location Lookup** likewise says an address-based lookup can show where to vote, voting districts, and the local board, and warns that the site is updated daily from the voter registration database so display lag can occur after data entry. North Carolina’s current **Checking Your Registration** page says the Voter Search can show registration status, Election Day polling place, sample ballot, and voting districts; the current **Voter Search** page separately says the search returns jurisdictions, polling place, sample ballot when available, absentee-ballot information, and voter history. Florida’s current **Voter Precinct Lookup** page is a separate statewide surface for finding a precinct within a county, and Florida’s current **Election Day Voting** page says a voter who votes on Election Day must vote at the voter’s assigned precinct/polling location. Washington’s current **Elected Officials** page tells voters to use VoteWA to view elected officials based on address, and Washington’s current **Current Election Information** page says whether a voter is eligible for a special election depends on the address at which the voter is registered and what is happening in the voter’s community. (xref: `maryland_voter_lookup_page`, `maryland_voting_location_lookup_page`, `north_carolina_checking_your_registration_page`, `north_carolina_voter_search_page`, `florida_voter_precinct_lookup_page`, `florida_election_day_voting_page`, `washington_elected_officials_page`, `washington_current_election_information_page`)

That is a distinct dispute surface from adjacent docs. `docs/292` answers **where the jurisdiction designated a voter to go**. `docs/293` answers **what ballot-style or sample-ballot answer was published**. `docs/294` answers **what the registration-status surface currently says about the voter record**. `docs/312` answers **whether a runoff or special election exists for a voter’s district and which carry-forward participation rules control that exception**. None of those, by themselves, fully capture the bounded public fact of **assignment**: which precinct, districts, and local election jurisdiction the public answer path said applied to the address or voter record, what changed when that assignment was corrected, and which downstream pages had to be treated as stale or superseded.

This document stays intentionally bounded. It is **not** a general redistricting digest, a GIS interchange spec, or a statewide pollbook design paper. It is a claim that election offices should be able to prove which official public assignment surface, correction chain, and fallback help path controlled the public answer when precinct/district/jurisdiction assignment mattered.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative assignment claim:** for election scope `E`, the jurisdiction identified one authoritative public path for precinct / district / jurisdiction assignment and one authoritative help path.
2. **Input-basis claim:** the public surface stated what bounded public input controlled the answer.
3. **Assignment-result claim:** the public surface returned the precinct label or identifier, the relevant districts/jurisdictions, and the local election office or equivalent authoritative jurisdiction-routing answer.
4. **Assignment-change claim:** where the answer changed, the public surface stated the effective change and the bounded reason class.
5. **Downstream-consistency claim:** polling-place, ballot-style, special-election, elected-official, and help-path surfaces converged on the same effective assignment answer.
6. **Parity/accessibility claim:** the assignment answer, correction notices, and fallback help path remained reachable in accessible and, where required, language-appropriate form.

## Canonical digest artifacts

Publish **digests of the public assignment surface**, not internal GIS or registration-engine files.

- **Assignment Scope Surface Digest (ASSD):** digest of the authoritative public precinct / district / jurisdiction payload for an election scope.
- **Assignment Change Notice Digest (ACND):** per-event digest for an assignment correction, precinct reassignment, district-boundary update, special-election-scope update, or other bounded public change.
- **Assignment Map / Reference Digest (AMRD):** optional digest binding a public district map, precinct reference page, or other bounded public reference artifact that explains the scope answer.
- **Assignment Parity Snapshot (APS):** optional snapshot binding the effective public state across assignment lookup, polling-place, ballot-style, special-election, and help-path surfaces.
- **Assignment Help Path Digest (AHPD):** optional digest of the authoritative fallback help path when the public cannot safely infer the current assignment answer from stale or partial material.

## What belongs in the public assignment payload

Keep the payload **small, scope-oriented, and correction-friendly**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_assignment_uri`
- optional `authoritative_map_or_reference_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or maintenance notice

Recommended assignment-entry fields:
- stable `assignment_id`
- `input_basis`
- `assignment_scope_note`
- `precinct_label`
- optional `precinct_id`
- `districts` (small list of district labels / bounded scope objects)
- optional `local_election_office_uri`
- optional `polling_place_ref`
- optional `ballot_style_ref`
- optional `special_election_scope_ref`
- optional `map_or_reference_uri`
- optional `change_reason`
- bounded `plain_language`
- `notice_uri`

Recommended bounded vocabularies:
- `input_basis`: `registered_voter_record`, `residential_address_lookup`, `county_and_address_lookup`, `authenticated_voter_portal_lookup`, `other_bounded_public_input`
- `change_reason`: `address_correction`, `residential_move_update`, `precinct_reassignment`, `district_boundary_update`, `special_election_scope_update`, `data_correction`, `other_bounded_public_change`

Do **not** publish by default:
- full geocoding rules or internal address-normalization logic
- full GIS boundary datasets when a bounded public answer plus pointer will do
- voter history, birth dates, or other identity details not needed to prove the public assignment answer
- internal pollbook routing tables or style-mapping logic
- silent “we fixed it in the database” assertions without a public correction note when the public answer materially changed

## Assignment semantics and anti-retcon rules

Precinct / district / jurisdiction answers should fail **loudly** when the public answer changes.

Rules:
- A correction to precinct assignment, district assignment, local-board routing, or special-election scope SHOULD produce a new change notice digest.
- If the assignment answer changed because of redistricting, precinct renumbering, consolidated locations, address correction, or database repair, the notice SHOULD say so plainly rather than making downstream voters infer the change from a new polling-place or sample-ballot page alone.
- If polling-place, ballot-style, special-election, or elected-official surfaces lag behind the corrected assignment answer, publish a parity snapshot (`201`) and an explicit superseding notice.
- Silent replacement of an assignment lookup result, silent precinct-code changes, or silent removal of an outdated district label SHOULD be treated as a governance failure.
- If the public answer requires authenticated access to a voter portal, the surface SHOULD still expose a bounded public help path for people who cannot authenticate or who suspect the visible answer is stale.
- This surface SHOULD point outward to `292`, `293`, `294`, `305`, or `312` where needed instead of swallowing those domains.

## Accessibility, translation, and public reach

Assignment answers often reach the public through several channels at once: public voter lookup, address lookup, current-election page, special-election FAQ, district map/reference page, polling-place page, or county-board help route.

Minimum publishable facts:
- which public input basis controlled the answer,
- which precinct / districts / jurisdiction the surface said applied,
- what changed if the answer was corrected,
- which downstream page or help path should now control,
- and which signed notice superseded the prior answer.

A jurisdiction does not get to count a stale polling-place locator or sample-ballot page as the whole answer once the underlying assignment answer changed.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public assignment surface at time `T`?
- What bounded input basis controlled the visible answer?
- Which precinct, districts, and local election jurisdiction did the public surface say applied?
- If the assignment changed, was the change explicit and timestamped?
- Did polling-place, ballot-style, special-election, and help-path pages converge on the same effective assignment answer?
- Were corrections explicit, or silently edited away?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/assignment-scope-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/assignment-scope-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Maryland State Board of Elections: Voter Lookup (xref: `maryland_voter_lookup_page`)
- Maryland State Board of Elections: Voting Location Lookup (xref: `maryland_voting_location_lookup_page`)
- North Carolina State Board of Elections: Checking Your Registration (xref: `north_carolina_checking_your_registration_page`)
- North Carolina State Board of Elections: Voter Search (xref: `north_carolina_voter_search_page`)
- Florida Division of Elections: Voter Precinct Lookup (xref: `florida_voter_precinct_lookup_page`)
- Florida Division of Elections: Election Day Voting (xref: `florida_election_day_voting_page`)
- Washington Secretary of State: Elected Officials (xref: `washington_elected_officials_page`)
- Washington Secretary of State: Current Election Information (xref: `washington_current_election_information_page`)
