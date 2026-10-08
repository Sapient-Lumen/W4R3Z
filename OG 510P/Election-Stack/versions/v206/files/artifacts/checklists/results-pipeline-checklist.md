# Results pipeline checklist (operational)

## Pre-election
- [ ] EPB published and witness-quorum checkpointed (includes BD hash + DisclosurePolicy hash)
- [ ] Results API contract published and pinned by hash
- [ ] Results-reporting signing keys generated, stored in HSM, and ceremony recorded
- [ ] Mirrors configured and tested (index.json agrees across mirrors)

## During reporting
- [ ] Every update produces an RRP (CRO + EVO + ENRUpdate + signatures + PBB anchor)
- [ ] ENR UI displays CRO hash + checkpoint ID
- [ ] API returns CRO hash + checkpoint ID
- [ ] Corrections only via signed, anchored updates with structured reason

## Monitoring
- [ ] ≥3 independent monitors running in distinct networks
- [ ] Drift detectors enabled (UI/API/localization/region)
- [ ] Alert publication path tested (DriftAlert anchored into PBB)

## Post-election
- [ ] Final “unofficial” package sealed and notarized
- [ ] Certified results package published separately and clearly labeled
- [ ] Audit artifacts published per plan (RLA, seed, reports)
