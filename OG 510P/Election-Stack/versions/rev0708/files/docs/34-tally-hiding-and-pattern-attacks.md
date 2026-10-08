# Tally-hiding and pattern attacks ("Italian attacks")

**Track:** A (Deployable core)


**Human framing:** coercion is not only a crypto failure mode; it is a lived experience of fear and dependency.
If this risk matters in your jurisdiction, read `07-coercion.md` before choosing publication granularity or protocol mitigations.


## The threat
In elections with sufficiently complex ballots, a coercer can ask a voter to embed a unique pattern across low-stakes contests (or ranked positions) that acts like a signature.

If **full decrypted ballots** (or very granular per-precinct breakdowns) are published, the coercer can later confirm compliance by searching for that pattern.

This is often referred to as an "Italian attack" in the e-voting literature.

## Why this matters here
Even if your receipts do **not** reveal vote content, the *published outcome artifacts* can still provide proof-of-vote.

This risk exists in paper elections too (depending on publication granularity), but electronic systems can make it much easier to search and prove.

## Core mitigation: tally hiding
**Tally hiding** means revealing only what must be revealed for the election outcome, while preserving verifiability.

Common approaches:

### A) Homomorphic tally (totals only)
- Add encrypted votes to produce encrypted totals.
- Threshold-decrypt only totals.
- Provide ZK proofs that the totals correspond to posted ciphertexts.

**Pros:** Strong privacy; simple output.
**Cons:** Harder for some contest types (ranked choice, STV) unless you use more complex cryptography/MPC.

### B) MPC / threshold computation for complex tally rules
- Use MPC to compute winners without revealing individual ballots.
- Publish verifiable computation proofs (or audit proofs) of correct winner computation.

**Pros:** Can support complex rules.
**Cons:** Heavy engineering; verification UX is nontrivial.

### C) Hybrid: decrypt only what is required
- Decrypt only enough to determine winners (not full ballots).
- Publish proofs that the decrypted information is sufficient and correctly derived.

## Spec requirements (if remote return exists)
- The system MUST define a **Disclosure Policy**:
  - what is decrypted,
  - what is published,
  - what breakdowns (precinct/demographic/time) are allowed.
- The system MUST publish verifiable evidence that **only** permitted disclosure occurred.
- If tally hiding is not implemented, the system MUST explicitly disclaim coercion-resistance claims and treat vote buying as a realistic risk.

## Operational considerations
- Publishing fine-grained results early can amplify pattern attacks.
- Public observers may demand transparency that conflicts with privacy; your governance doc must pre-commit to the disclosure policy.

## Link to coercion-resistance analysis
See `33-coercion-resistance-deep-dive.md` for how pattern attacks interact with JCJ-style and tracker-based schemes.
