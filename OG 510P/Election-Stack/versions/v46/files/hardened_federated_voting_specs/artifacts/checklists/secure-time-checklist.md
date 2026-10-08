# Secure time checklist

Use this checklist before every election.

## Time sources
- [ ] Configure at least 3 independent secure time servers (e.g., Roughtime).
- [ ] Configure a plausibility window for clients and federation nodes.
- [ ] Verify time proof storage and export in the client.

## Checkpoints
- [ ] Checkpoint policy defines quorum and cadence.
- [ ] Witnesses co-sign checkpoints and gossip STHs.
- [ ] Verify that revote precedence uses log order only.

## Failure modes
- [ ] Simulate time server lying; ensure client surfaces proof and blocks unsafe actions.
- [ ] Simulate clock skew; ensure ballots aren’t incorrectly rejected.
