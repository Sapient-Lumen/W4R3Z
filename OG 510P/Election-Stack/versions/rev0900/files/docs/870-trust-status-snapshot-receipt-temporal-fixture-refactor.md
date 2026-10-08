# 870 — Trust-status snapshot receipt temporal fixture refactor

**Track:** Shared / verifier boundary  
**Revision:** v852  
**Status:** synthetic-only verifier hardening

v851 hardened verification-policy publication-receipt temporal order. v852 carries that same discipline into the trust-status snapshot publication receipt fixture and regression path so revocation/status evidence is less replayable.

The status snapshot still comes from the rev0847 snapshot bytes, but the publication receipt fixture is refreshed as a rev0852 temporal receipt:

```text
artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0852.publication-receipt.json
sha256:7172aa632768e8932682ad0597096dbc3614acefd0133a2d8b4d94ca28dfabcc
```

## What is checked

When the trust-status snapshot receipt is required, the verifier now reports and enforces the receipt validity window, snapshot `this_update` / `next_update`, channel publication observations, receipt issuance time, and caller-supplied `--verification-time` coherence. It fails closed when receipt timing is missing, expired, future-dated, predates the snapshot it claims to publish, or has receipt issuance before the latest channel observation.

The public packet verification report exposes these fields so the boundary is inspectable rather than implicit:

```text
trust_status_snapshot_receipt_validity_status
trust_status_snapshot_receipt_channel_time_status
trust_status_snapshot_receipt_temporal_status
trust_status_snapshot_receipt_temporal_snapshot_this_update
trust_status_snapshot_receipt_temporal_snapshot_next_update
trust_status_snapshot_receipt_earliest_published_at
trust_status_snapshot_receipt_latest_published_at
trust_status_snapshot_receipt_external_verification_time
```

## Refactor result

The trust-chain fixture-surface audit now covers ten packet-external byte-pinned fixtures and reports:

```text
failure_count: 0
all_sidecars_match: true
all_fixtures_packet_external: true
```

That is a maintenance refactor, not a doctrine expansion: it keeps the strongest synthetic verifier path visible as a small set of audited external inputs instead of a growing pile of hidden fixtures.

## Boundary

This is not live OCSP, CRL checking, RFC3161 trusted timestamping, production revocation infrastructure, or legal proof of authority. It is an offline synthetic replay/substitution gate for local verifier regression.
