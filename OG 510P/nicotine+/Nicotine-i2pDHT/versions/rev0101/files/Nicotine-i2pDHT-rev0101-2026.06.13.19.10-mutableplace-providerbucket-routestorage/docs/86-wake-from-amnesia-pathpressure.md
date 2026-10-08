# Wake from amnesia — rev0010

You are in `rev0010 seedcapture-witnesspoison-pathpressure`.

## Current thesis

The DHT is a mutable control plane over I2P. Mutable records are necessary, but signatures alone are too weak. Acceptance must be pressure-aware.

## New modules

```text
src/i2p_dht_lab/pathpressure.py
src/i2p_dht_lab/witnesspoison.py
src/i2p_dht_lab/seedcapture.py
src/i2p_dht_lab/revocation_pressure.py
src/i2p_dht_lab/succession.py
```

## New test lane

```text
tests/test_rev0010_risk_first.py
```

The lane tests:

```text
fast captured family cannot satisfy early mutable lookup acceptance
post-hoc stale detection when old valid head arrives before new valid head
same-sequence fork pressure and receipts
single-family witness alarm is not quorum
contradictory witness gets quarantined
captured/monoculture seed portfolio gets flagged
selector spreads seed choices across channels/families
revocation memory keeps revoked grant after stale head replay
same-sequence revocation fork unions revoked hashes
co-signed key succession rejects tampering
succession rollback and same-sequence fork detection
```

## Verification

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

At cube build time this passed with 76 tests.

## Next best move

`rev0011 providerpoison-gardenrefusal-churnforge` should test false provider records, garden useful-refusal receipts, colluding path families under churn, and transport-neutral wire transcript fixtures.
