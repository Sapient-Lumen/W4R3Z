# Witness operations checklist (minimum viable)

**Track:** Shared (cross-cutting)


## Independence & diversity
- [ ] Legal/organizational independence from the log operator(s)
- [ ] Diverse hosting/provider/region/ASN compared to other witnesses
- [ ] Public contact + signing key with transparent rotation
- [ ] Publish a human‑legible profile (`TEMPLATE:artifacts/templates/witness-profile.md`) including a representation‑duty statement + material floor/accessibility commitments

## Monitoring duties
- [ ] Fetch STHs from >= 2 endpoints (sequencer + mirror)
- [ ] Verify STH signatures, inclusion proofs, consistency proofs
- [ ] Gossip latest STHs to peer witnesses on schedule
- [ ] Persist signed evidence for fork proofs and missing-checkpoint events

## Alerting
- [ ] Publish signed alerts to >= 2 public channels
- [ ] Provide machine-readable fork proof bundles

## Operational security
- [ ] Hardware-backed signing key
- [ ] Dual control for key use
- [ ] Immutable logs, time sync, and backups

## Cross-checkpointing (recommended)
- [ ] Cross-log checkpoints to at least one independent archive/log
- [ ] Publish inclusion proof for cross-logged checkpoint

## Privacy hygiene
- [ ] Do not retain raw client network identifiers beyond policy limits
- [ ] Publish only aggregated operational metrics (no fine-grained turnout or IP-derived stats)
## Behavioral health (publishable)
- [ ] Publish an election-cycle independent summary (signed; digest-addressed).
- [ ] Participate in at least one drill/incident attestation window with bounded, replayable attestations (see `DOC:docs/135-...` WIT‑7; `SCHEMA:schemas/MonitorAttestation.json`).
- [ ] Update `artifacts/registries/witness-health-log.csv` with the liveness score + bounded pointers (no long appendices).

