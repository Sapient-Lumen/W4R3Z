# Secure time checklist

Use this checklist before every election.

See: `docs/38-secure-time-and-ordering.md` and `docs/192-time-attestation-and-timestamping-as-evidence.md`.

## Time sources
- [ ] Configure at least 3 independent authenticated time sources.
  - Managed fleets: NTS-secured NTP.
  - Hostile/bootstrapping scenarios: Roughtime (multi-server).
- [ ] Configure a plausibility window for clients and federation nodes (reject large time jumps without loud alarms).
- [ ] Verify time-proof storage/export in the client (transcripts as detached objects).

## Checkpoints
- [ ] Checkpoint policy defines quorum and cadence.
- [ ] Witnesses co-sign checkpoints and gossip STHs.
- [ ] Verify that revote precedence uses log order only.

## Time attestations as evidence
- [ ] Publish time beacons (e.g., `hfv.time.beacon`) for each checkpoint epoch (signed by the enclosing EvidenceEnvelope).
- [ ] If you use TSAs (RFC3161), ensure tokens time-bind the intended digest (`tbs_digest` or `payload_digest`) and are shipped as detached attachments.

## Failure modes
- [ ] Simulate time server lying; ensure client surfaces proof and blocks unsafe actions.
- [ ] Simulate clock skew; ensure ballots aren’t incorrectly rejected.
