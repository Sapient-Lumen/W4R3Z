# Basis provenance audit

This generated surface checks whether the revision receipt's basis witness names the immediate underlier release instead of silently carrying an older session anchor.
It exists because a package can pass many currentness checks while the innovation packet still inherits stale `basis_witness.expected_head`, `observed_head`, or `session_provenance` fields from an earlier revision.

## Non-authority boundary

This is not a basis-provenance-court, session-underlier-sovereign, reread-notary, anchor-freshness-tribunal, basis-waiver-board, resync-authority-senate, provenance-certification-court, or underlier-currentness-oracle.
Basis provenance is session-underlier hygiene only; it does not certify semantic truth, full historical review, legal status, release legitimacy, minimality, or continuation authority.

## Counts

- Checks: `8`
- Failures: `0`

## Rows
- `expected_head_matches_previous_revision` — status `pass`; expected `rev0373`; observed `rev0373`
- `observed_head_matches_previous_revision` — status `pass`; expected `rev0373`; observed `rev0373`
- `expected_observed_heads_match` — status `pass`; expected `rev0373`; observed `rev0373`
- `anchor_precision_direct_underlier` — status `pass`; expected `direct-underlier`; observed `direct-underlier`
- `basis_state_allows_current_underlier` — status `pass`; expected `['current', 'resynced']`; observed `current`
- `session_provenance_names_current_underlier` — status `pass`; expected `mentions rev0373 and no older source-only carryover`; observed `latest packaged rev0373 plus local rev0374 preanswer-material clamp and score-time chronology edits in this cloudtainer`
- `status_previous_citation_head_matches_previous` — status `pass`; expected `rev0373`; observed `rev0373`
- `manifest_revision_matches_receipt` — status `pass`; expected `rev0374`; observed `rev0374`
