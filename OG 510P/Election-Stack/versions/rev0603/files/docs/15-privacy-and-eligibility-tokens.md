# Privacy & eligibility tokens (design choices)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

## Goal
Prove eligibility **without**:
- letting the PBB learn the voter’s identity, or
- enabling turnout surveillance by correlating credentials to log entries.

## Franchise scope note

This document assumes **human** eligibility and identity proofing.
Non-human franchise / AI standing is explicitly **out of scope** for Track B deployments today (see `docs/167` N‑7) and treated as research (`docs/172.6`).


## Option 1 (simple): credential signature (with privacy wrapper)
Voter signs submission with a credential key.
Operationally simple but risks linkability unless additional measures are taken.

If used, MUST:
- avoid publishing raw credential identifiers,
- publish a clear privacy threat model.

## Option 2 (recommended): spend-once unlinkable tokens
RA issues unlinkable eligibility tokens (e.g., blind-signed).
Casting spends exactly one token:
- PBB checks token validity and non-reuse (double-spend database committed to the log).
- Token spending is unlinkable to issuance (under scheme assumptions).

## Token theft & recovery
If tokens are device-held, malware can steal them.
Mitigations:
- store in hardware-backed secure storage,
- allow in-person re-issuance and revocation,
- supervised override vote cancels any remote ballot.

## Metadata minimization (MUST)
- fixed-size ciphertexts where possible,
- pad proofs to reduce fingerprinting,
- avoid IP logs; allow privacy-preserving relay options.


## v15: Detailed minting flow
See `81-privacy-preserving-eligibility-token-minting-protocol.md` for a concrete, unlinkable token-minting protocol with anti-abuse options.

## Open tension: privacy vs verifiability

Eligibility and revocation surfaces must be publicly checkable *enough* to support dispute resolution,
without enabling turnout surveillance or linkability of individual voters.
This remains an open research item: see `docs/172-open-research-questions-and-experiment-backlog.md` → **172.3.1**.
