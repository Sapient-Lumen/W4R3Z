# Notarization & Timestamping Checklist

**Track:** Shared (cross-cutting)


- [ ] Pre-publish accepted timestamp authorities (TSAs) and/or transparency logs.
- [ ] For each high-value artifact (EPB, checkpoints, results packages, ObserverKit bundles):
  - [ ] compute SHA-256 digest
  - [ ] obtain RFC 3161 Time-Stamp Token (TST) or equivalent
  - [ ] store token + verification metadata in bundle
- [ ] Publish notarization objects (BundleNotarization) for each artifact.
- [ ] Mirror notarization proofs across independent domains.
- [ ] Verify: timestamps do not include voter PII.
