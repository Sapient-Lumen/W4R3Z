# Outage attestation checklist (operator + witnesses)

**Track:** Shared (cross-cutting)


- [ ] Collect APR samples from >= K perspectives (distinct ASN/region).
- [ ] Confirm artifact hashes (if SPLIT_VIEW) and attach evidence hashes.
- [ ] Draft `OutageAttestation` with scope, times, and rollup stats.
- [ ] Witnesses independently reproduce at least one APR sample each.
- [ ] Countersign OA and submit to ATL within MMD.
- [ ] Publish public statement that references OA hash + checkpoint hash.
- [ ] On recovery: produce `RecoveryAttestation` + post-recovery APR samples.
