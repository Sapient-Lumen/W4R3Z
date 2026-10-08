# 533 — Nuclear Emergency Preparedness CAP Lineage, Feed Acquisition, and Source Canonicalization Refactor — Compact Canon

## What this revision fixes

Rev0325 made live/anonymized evidence bags operational, but the public-feed side still had a dangerous weak spot: an IPAWS/OpenFEMA archive pull, NRC/FEMA schedule row, PI feed, action-matrix row, public event notice, or duplicate source ID could be over-read as evidence that local alerting or emergency preparedness was closed.

Rev0326 adds a concrete acquisition and normalization path for public feeds while preserving the main safety invariant: **public feeds discover, time-stamp, triangulate, contradict, reopen, cap, or route evidence demands; they do not close local emergency-readiness evidence.**

## New executable surfaces

- `tools/acquire_nuclear_emergency_bvps_public_feeds_rev0326.py`
- `tools/normalize_ipaws_cap_archive_rev0326.py`
- `tools/validate_nuclear_emergency_bvps_feed_acquisition_rev0326.py`
- `cube/nuclear-emergency-bvps-public-feed-acquisition-live-contract-rev0326.csv`
- `cube/nuclear-emergency-bvps-ipaws-archive-query-set-rev0326.csv`
- `cube/nuclear-emergency-bvps-cap-lineage-state-machine-rev0326.csv`
- `cube/nuclear-emergency-bvps-cap-normalized-fixture-output-rev0326.csv`
- `cube/source-canonical-url-map-rev0326.csv`

## CAP lineage rule

The normalizer treats CAP `Update`, `Cancel`, `Ack`, `Error`, duplicate archive rows, missing geocodes, expired messages, and `Exercise`/`Test` status as stateful evidence conditions. A CAP message is not a flat row that can be counted once and forgotten. The cube must answer: what was the latest message in the lineage, what was superseded, what was cancelled, what errored, what was missing, and what local packet corroborates it?

## False-negative rule

An empty public archive query is not proof that no alert existed. Rev0326 records archive lag, geocode mismatch, polygon-only messages, county/state fallback gaps, pagination, proprietary county systems, and channel split as explicit false-negative risks. Missing public archive evidence creates a hold/cap, not a clean bill of health and not a failure claim.

## Source canonicalization rule

The source register now has a materialized canonical URL map. Duplicate source IDs that point to the same canonical URL count once for independence. This prevents source-register growth from turning into artificial corroboration.

## Claim boundary

This revision makes no Beaver Valley, Pennsylvania, West Virginia, Ohio, county, facility, or plant readiness claim. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0326 only improves public-feed acquisition, CAP lineage parsing, false-negative handling, source-independence controls, and no-closure gates.

## Rev0326 integrity addendum: Merkle evidence-bag gate

The feed-acquisition path is now paired with a stricter evidence-bag integrity gate. A public feed can create a context row, false-negative hold, contradiction, source-clock clue, or acquisition task; a local/anonymized evidence bag can become only a candidate for adjudication after hash and Merkle verification. Neither path can close readiness by itself.

New integrity files added in this revision:

- `tools/build_nuclear_emergency_bvps_evidence_bag_merkle_rev0326.py`
- `tools/verify_nuclear_emergency_bvps_evidence_bag_rev0326.py`
- `cube/nuclear-emergency-bvps-evidence-bag-integrity-verification-profile-rev0326.csv`
- `cube/nuclear-emergency-bvps-evidence-bag-integrity-fixture-rev0326.csv`
- `cube/nuclear-emergency-bvps-evidence-bag-integrity-result-rev0326.csv`
- `cube/nuclear-emergency-bvps-evidence-bag-merkle-manifest-rev0326.csv`
- `cube/nuclear-emergency-bvps-evidence-bag-tamper-replay-negative-control-rev0326.csv`
- `cube/nuclear-emergency-bvps-redaction-leakage-control-rev0326.csv`
- `cube/nuclear-emergency-bvps-chain-of-custody-replay-risk-register-rev0326.csv`
- `cube/nuclear-emergency-bvps-sensitive-annex-public-surrogate-pairing-rev0326.csv`
- `cube/nuclear-emergency-bvps-alert-archive-to-local-originator-firebreak-rev0326.csv`

The verifier runs 41 fixture tests. The clean synthetic Merkle bag is accepted only as `candidate_for_adjudication_not_closure`. Tamper, duplicate-entry, row-hash, Merkle, redaction, stale-replay, closure-language, and public-archive overclaim cases are rejected, held, or routed as context/reopen signals. Public-context-to-local-closure leaks remain zero.

## Integrity query route

`public feed / evidence bag → source-clock check → CAP lineage / manifest hash → row hash → payload hash → Merkle root → redaction surrogate pair → public archive firebreak → replay/counterevidence gate → adjudication queue → CAP/retest/verifier → public claim gate`

The unsafe path remains forbidden:

`feed row or bag exists → readiness closed`
