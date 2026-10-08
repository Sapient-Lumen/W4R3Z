# ENR security checklist (unofficial results publishing)

This checklist compresses common ENR security recommendations into an operator-focused list.

## Scope & separation
- [ ] ENR system is logically and operationally separated from EMS/tabulation.
- [ ] ENR ingest is one-way from protected environment (export → import), with integrity checks.

## Integrity & transparency
- [ ] Every ENR update is signed; clients can verify signatures offline.
- [ ] Updates form a hash chain (prev_hash) and are anchored to the PBB / checkpoints.
- [ ] A public, immutable results bundle is published at defined intervals.

## Availability
- [ ] Static-first architecture; API is rate-limited and cached where possible.
- [ ] Multi-region hosting; multi-provider DNS; monitored for hijack anomalies.
- [ ] DDoS plan tested (synthetic load + failover).

## Human factors
- [ ] Prominent banner: “Unofficial results; certification timeline; why totals change.”
- [ ] Social posting uses pre-approved language; accounts protected with hardware keys.

## Monitoring & incident response
- [ ] Alert on unsigned update, hash-chain break, or unexpected deltas.
- [ ] Rollback procedure publishes an explicit “correction” object (not silent edits).
