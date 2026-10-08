# Structural audit rev0326

## Scope

Rev0326 audits the public-feed acquisition and CAP-lineage surface added after the live evidence-bag preflight work.

## Corrections made

- Added an executable IPAWS/OpenFEMA CAP normalizer that preserves CAP lineage instead of flattening messages into duplicate evidence rows.
- Added county, state-prefix, and geospatial-backstop query sets for the Beaver Valley PA/OH/WV seam.
- Added a false-negative ledger so missing public archive hits do not become a conclusion.
- Added a materialized source canonical URL map so duplicate source IDs cannot inflate evidence independence.
- Added SQLite views proving public/CAP context still cannot auto-close local emergency-preparedness evidence.

## Compatibility retained

Legacy universal nuclear crossproduct tables are retained for compatibility and remain outside the emergency-readiness claim route.

## Residual risk

The package still needs real/anonymized June 2026 public-feed pulls and local alert/channel packets after the exercise window and archive-delay period. No real readiness claim is made.

## Additional integrity refactor

- Added a Merkle-hardened evidence-bag builder and verifier.
- Added a 41-case tamper, replay, redaction, public-archive, and closure-overclaim fixture set.
- Added sensitive-annex/public-surrogate pairing controls.
- Added a chain-of-custody replay risk register.
- Added an alert-archive-to-local-originator firebreak: public CAP archive rows remain context or reopen signals until local originator/export/ack/error/custody evidence exists.

## Integrity residual risk

The verifier is now ready for live/anonymized packets, but no real June 2026 evidence bag has been imported. The first real packet should be run through the rev0326 verifier and then routed to adjudication, not closure.
