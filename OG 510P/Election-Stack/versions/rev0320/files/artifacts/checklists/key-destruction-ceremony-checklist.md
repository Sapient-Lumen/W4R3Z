# Key destruction ceremony checklist

**Track:** Shared (cross-cutting)


## Preconditions
- [ ] Final checkpoint published and witness quorum verified
- [ ] Tally completed and proofs published
- [ ] Paper/RLA complete (if paper-of-record)
- [ ] Verification window end date reached or authority-approved closure

## Ceremony
- [ ] Independent observers present (multi-stakeholder)
- [ ] Verify device/HSM identifiers match published roster
- [ ] Verify access controls: dual control, no network where feasible
- [ ] Execute destruction method per trustee (HSM zeroize / physical destruction)
- [ ] Collect logs/photographic evidence where legally allowed

## Publication
- [ ] Produce `KeyDestructionAttestation`
- [ ] Trustees sign attestation
- [ ] Witness quorum cosigns
- [ ] Append to transparency log as `PARAMS` or `CLOSE`-adjacent entry
