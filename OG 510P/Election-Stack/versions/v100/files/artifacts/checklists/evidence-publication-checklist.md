# Evidence publication checklist (court-proof bundle)

## Before polls open
- [ ] Publish election parameters (PK, ballot definition hashes, crypto suite IDs) via ≥3 independent channels.
- [ ] Publish witness roster and quorum policy; publish witness public keys.
- [ ] Publish Disclosure Policy (granularity, tally-hiding stance, publication schedule).
- [ ] Publish Audit Plan (RLA type, sampling rules, escalation triggers).
- [ ] Publish verifier tooling: ≥2 independent implementations + test vectors + build hashes.

## During voting
- [ ] Archive Signed Tree Heads (STHs) and witness checkpoints at regular cadence.
- [ ] Monitor for equivocation (ForkProof objects) and censorship signals (missed intake deadlines).
- [ ] Publish status dashboards that distinguish PENDING vs RECORDED vs FINAL.

## After close
- [ ] Freeze final checkpoint (witness quorum) and publish final STH + signatures.
- [ ] Publish tally proofs (mixnet/homomorphic/MPC) and verifier outputs.
- [ ] Publish EvidenceBundleManifest + signatures.
- [ ] Run and publish audit results (RLA report).

## If disputes occur
- [ ] Publish minimal, consistent evidence updates; avoid ad-hoc disclosures.
- [ ] Follow incident communications template; keep claim hygiene strict.
