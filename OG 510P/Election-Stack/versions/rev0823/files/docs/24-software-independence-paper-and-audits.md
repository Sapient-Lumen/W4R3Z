# Software independence, paper-of-record, and audits (recovery anchor)

**Track:** A (Deployable core)


Cryptographic verifiability is powerful, but real elections need a recovery anchor that does not depend on software.

## Baseline principle
For high-stakes public elections, **human-readable paper ballots** (or voter-verifiable paper records)
should remain the **ballot of record**, and outcomes should be confirmable by **risk-limiting audits (RLAs)**.

This pack treats the crypto layer as:
- an integrity *detector* and public evidence generator, and
- a way to expose failures earlier,
not as a substitute for paper/audits.

## Required properties
1. **Software independence**: a software fault cannot cause an undetectable outcome change.
2. **Evidence hierarchy**:
   - if crypto evidence and paper evidence disagree, paper + audit procedures govern.
3. **Auditability at scale**:
   - RLAs and ballot accounting are specified and funded before deployment.

## Integrating PBB evidence with audits
- Publish a **CVR commitment** per ballot (or per batch), with proofs it corresponds to posted ciphertexts.
- Audit samples paper ballots and checks consistency with the committed CVR set.

## When crypto helps audits
- Detects missing/duplicated ballots earlier (ballot accounting).
- Detects tally miscomputations (public proofs).
- Gives voters a “recorded” check (inclusion proofs).

## What crypto does not solve
- Coercion and vote-selling for unsupervised remote voting.
- Malware on the voting device.
- Turnout surveillance via metadata without additional mitigations.