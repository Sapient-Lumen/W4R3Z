# Verifier Supply-Chain Checklist

**Track:** Shared (cross-cutting)


- [ ] Reproducible build instructions published
- [ ] Provenance statement (VerifierProvenance) includes:
  - [ ] source repo + commit
  - [ ] build environment identity
  - [ ] dependency capture (SBOM where feasible)
  - [ ] output hashes
- [ ] Sign provenance and publish signatures
- [ ] Pin verifier hash(es) in EPB and/or ObserverKit manifest
- [ ] Maintain at least two independent verifier implementations
