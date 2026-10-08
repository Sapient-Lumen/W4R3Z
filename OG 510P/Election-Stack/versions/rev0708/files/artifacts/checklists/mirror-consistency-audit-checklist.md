# Mirror Consistency Audit Checklist

**Track:** Shared (cross-cutting)


Goal: detect **selective delivery** (split views) across portals, CDNs, and mirrors.

- [ ] For each public endpoint, fetch `ObserverKitManifest` / latest `Checkpoint`.
- [ ] Verify witness-quorum signatures.
- [ ] Verify that the `checkpoint_hash` matches across all endpoints.
- [ ] For each priority bundle manifest hash, fetch the bundle from each endpoint and compare:
  - [ ] manifest hash
  - [ ] manifest signature
  - [ ] referenced checkpoint + inclusion proof

## Alert conditions
- [ ] Same `tree_size` but different `root_hash` (probable equivocation).
- [ ] Different manifest hashes for the same logical bundle label (probable selective delivery).
- [ ] Missing fork/drift alert bundle on any endpoint after grace period.

## Evidence capture
- [ ] Save raw HTTP responses + timestamps.
- [ ] Save signatures, proofs, and checkpoints.
- [ ] Produce and publish a `DriftAlert` or `ForkProof` bundle if divergence is confirmed.

