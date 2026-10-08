# PQC / Crypto-agility migration checklist

**Track:** Shared (cross-cutting)


## Before an election
- [ ] Publish `CryptoPolicy` with allowed suites and cutover rules
- [ ] Implement hybrid signatures for checkpoints (classical + PQ)
- [ ] Generate conformance vectors for both suites
- [ ] Ensure QR/receipt capacity planning for larger signatures
- [ ] Run interop tests across all verifiers

## During an election
- [ ] Monitor for crypto vulnerability advisories
- [ ] Lock suite changes unless emergency process invoked

## After an election
- [ ] Publish verification bundle signed under active suite
- [ ] Publish verifier build hashes and conformance results
- [ ] Record lessons learned and update policy
