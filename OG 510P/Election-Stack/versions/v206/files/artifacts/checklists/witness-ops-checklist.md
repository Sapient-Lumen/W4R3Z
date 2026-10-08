# Witness operations checklist (minimum viable)

## Independence & diversity
- [ ] Legal/organizational independence from the log operator(s)
- [ ] Diverse hosting/provider/region/ASN compared to other witnesses
- [ ] Public contact + signing key with transparent rotation

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

