# Privacy & eligibility tokens (design choices)

**Track:** B (Remote return / hard-mode research)


## Goal
Prove eligibility **without**:
- letting the PBB learn the voter’s identity, or
- enabling turnout surveillance by correlating credentials to log entries.

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