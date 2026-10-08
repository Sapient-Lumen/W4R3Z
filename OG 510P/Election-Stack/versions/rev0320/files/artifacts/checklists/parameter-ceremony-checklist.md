# Parameter Ceremony Checklist (EPB / PKT)

**Track:** Shared (cross-cutting)


## Before
- [ ] Ballot definition finalized and reviewed (legal + accessibility + ordering rules)
- [ ] CryptoPolicy selected (suite IDs; PQC/hybrid policy)
- [ ] Trustee roster + threshold confirmed (diversity constraints checked)
- [ ] Witness roster + cosign threshold confirmed
- [ ] Receipt policy + deadlines confirmed
- [ ] DisclosurePolicy (tally granularity / privacy budget) confirmed

## Build
- [ ] Deterministic build of ballot definition artifact(s)
- [ ] Compute SHA-256 for ballot definition + each ballot style
- [ ] Construct ElectionParameterBundle (EPB) with version number
- [ ] Collect signatures from required signers (election authority + trustees/witnesses as policy)

## Publish
- [ ] Submit EPB to PBB; obtain inclusion proof
- [ ] Wait for witness-quorum checkpoint that includes EPB
- [ ] Publish EPB hash via out-of-band channels (public notice, press, posted QR)

## Verify
- [ ] Independent monitors confirm EPB consistency and archive proofs
- [ ] Run verifier test vectors against EPB

## After
- [ ] Archive EPB + proofs in EvidenceBundle
- [ ] Anchor EPB hash per NotarizationPolicy (optional)
