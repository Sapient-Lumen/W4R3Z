# Observer Kit Checklist

## Pre-election
- [ ] Publish election description, trust model, and Observer Kit documentation.
- [ ] Publish EPB (ElectionParameterBundle) and its hash.
- [ ] Publish witness/quorum policy and public keys.
- [ ] Publish test vectors and ≥2 independent verifier options.

## During voting
- [ ] Publish checkpoint feed at fixed cadence.
- [ ] Ensure “RECORDED” receipts are backed by inclusion proofs against a checkpoint.
- [ ] Mirror bundles across ≥3 independent domains/operators.

## After close
- [ ] Publish ResultsReleasePackage and final certified package.
- [ ] Publish ObserverKit bundles with manifests and signatures for each reporting interval.
- [ ] Provide reproducible build metadata for verifiers used in public claims.

## If something goes wrong
- [ ] Publish signed IncidentCommsPackage with bundle/checkpoint IDs and hashes.
- [ ] Publish drift/fork evidence objects (ForkProof / DriftAlert).
- [ ] Trigger paper-of-record + RLA recovery path if integrity cannot be established.
