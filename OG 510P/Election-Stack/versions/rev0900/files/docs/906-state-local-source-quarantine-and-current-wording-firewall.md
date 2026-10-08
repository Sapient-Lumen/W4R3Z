# rev0868 state/local source quarantine and current-wording firewall

**Track:** Shared / source maintenance / voter-facing public-answer safety  
Status: synthetic release-maintenance artifact  
Release date: 2026-06-10

## What changed

rev0868 addresses the riskiest unfinished source queue left after rev0867: `70` mutable state/local jurisdiction rows whose pages are useful examples and official routes, but dangerous if treated as live voter instructions.

The fix is deliberately practical:

- quarantine the remaining state/local rows as example/routing `xref` context;
- keep a row-level watchlist instead of deleting or hiding them;
- remove ambiguous “current state/county page says” phrasing from high-risk surface docs that cite unpinned jurisdiction rows;
- add a release-gate checker that fails if that ambiguous wording returns or if quarantined rows lose their non-instruction boundary;
- refactor current-authority classification so quarantined non-instruction rows cannot silently re-enter the authority queue before adopter-specific promotion.

No byte pins were added. No state, county, city, or local source was promoted to current law, current voter instruction, legal advice, live-pilot evidence, or certification evidence.

## Queue movement

Before this pass, the shared current-authority classifier showed `70` state/local authority rows due within the 45-day review horizon on the 2026-06-10 review date.

After this pass:

| Measure | rev0868 |
|---|---:|
| State/local rows quarantined | `70` |
| 45-day current-authority queue | `0` |
| State/local source-byte pins added | `0` |
| Pin-first candidates preserved in watchlist | `8` |
| High-risk docs lines rewritten | `26` |
| New quarantine review date | `2026-07-25` |

Machine-readable records:

- `artifacts/reports/state-local-jurisdiction-quarantine-rev0868.json`
- `artifacts/reports/state-local-jurisdiction-quarantine-rev0868.csv`
- `artifacts/reports/current-authority-source-queue-45day-rev0868.json`
- `artifacts/reports/current-authority-burndown-batches-45day-rev0868.json`
- `artifacts/reports/source-review-pressure-current-rev0868.json`

## Why quarantine instead of blanket refresh

The remaining rows are not generic background references. They include jurisdiction-specific examples for provisional ballots, registration status, confidential registration, no-fixed-address voting, in-custody voting, facility-assisted voting, youth preregistration, challenged voters, ballot return by another person, emergency absentee paths, and other high-risk public-answer surfaces.

Those rows should be useful as examples while developing evidence-surface patterns. They should not be copied into a public answer as “what the voter should do now” unless a real jurisdiction/adopter review has captured the exact current text, timestamp, local help route, and approval boundary.

The broader authority context supports that split: the EAC explicitly says each state and territory administers elections differently and that voters must verify summary information through linked state and local sources; EAC FAQ guidance similarly says local election officials are the best source of practical registration and voting information. (xref: `eac_register_and_vote_in_your_state_page`; xref: `eac_best_practices_faqs_election_officials_page`)

## Wording refactor

The audit found `26` high-risk markdown lines where unpinned state/local xrefs appeared inside wording such as “current California page says” or “current county page says.” That phrasing is too easy to misread as a currentness claim.

Those lines were rewritten to say the cited rows are **example official routes only, not current voter instruction**. Where a line still uses the word “current” as part of that negative boundary, the release-gate checker allows it only because the line also contains the explicit `not current voter instruction` phrase.

New checker:

- `scripts/check_state_local_xref_quarantine.py`

The checker fails if:

1. a quarantined state/local lockfile row lacks the `not current voter instruction` note boundary;
2. a quarantined row's review date moves back inside the 30-day source-review pressure window; or
3. markdown cites an unpinned state/local `xref:` and uses “current” without the non-instruction boundary.

## Remaining high-value work

This pass reduces near-term release risk, but it does not finish the real-world authority work. The next useful work is adopter-specific, not global:

1. choose one real or synthetic jurisdiction scope;
2. replace the relevant state/local `xref` rows with captured/pinned text or byte artifacts where possible;
3. attach `last_verified_at`, local office/help route, and human approval evidence;
4. fail closed if a voter-facing answer attempts a rights-affecting conclusion from an unpinned example row.

Generated JSON reports were compacted after digest-bearing handoff regeneration to keep the carrier inside the release size budget without deleting the machine-readable watchlist.

Boundary: rev0868 remains synthetic-only. The quarantine is a fail-safer source-use decision. It is not current state/local law, current voter instruction, legal advice, source-byte cache completeness, certification, independent validation, production signer authority, publication governance, or live-pilot authorization.
