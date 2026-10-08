# ENR drift monitoring checklist

**Track:** Shared (cross-cutting)


## Data sources to poll
- [ ] Web UI (HTML)
- [ ] Public JSON API
- [ ] Downloaded CRO/ERR payload from evidence portal
- [ ] At least 2 mirrors (different providers)
- [ ] At least 3 regions/ASNs

## Checks
- [ ] Signatures validate
- [ ] CRO hash matches checkpointed RRP
- [ ] UI/API declared CRO hash matches downloaded CRO hash
- [ ] Monotonicity constraints (no decreases without correction)
- [ ] Reporting unit IDs stable or changes anchored
- [ ] DisclosurePolicy compliance

## On drift detection
- [ ] Capture artifacts (hash snapshots)
- [ ] Create DriftAlert (include expected CRO hash + evidence)
- [ ] Anchor DriftAlert into PBB
- [ ] Notify incident comms channel
