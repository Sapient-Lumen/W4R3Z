# Digital credentials & citizen keys (hardware-backed, privacy-preserving)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This document narrows the hand‑wavey assumption “citizens have private keys” into an
**operationally survivable** credentialing system that does not quietly create a turnout‑surveillance
machine.

## Non-negotiable goals

1. **Hardware-backed** private keys (non-exportable).
2. **Recoverable** (lost device does not permanently disenfranchise).
3. **Privacy-preserving** (credential use does not become a universal identifier).
4. **Revocable** (rapid revocation + re-issuance).
5. **Phishing-resistant** (origin-bound; no “sign this random blob” UI).

## Threats (credential layer)

- **Key theft / cloning** (malware, insider at issuance, weak device storage).
- **Account takeover** of recovery channel (SIM swap, email compromise).
- **Tracking via attestation / stable identifiers** (privacy leakage).
- **Credential issuer compromise** (mass fraudulent issuance, revocation suppression).
- **Selective disenfranchisement** (revocation abuse, targeted outages in re-issuance).

## Credential model options

### A) Roaming security key (recommended high assurance)
- FIDO2/WebAuthn roaming authenticator (USB/NFC), **PIN + touch**.
- Private key is non-exportable and scoped to a relying party origin (phishing resistance).

### B) Platform authenticator (medium assurance)
- TPM/Secure Enclave/Android hardware keystore keys.
- Convenience is higher; assurance varies; attestation may be weaker or absent.

### C) Smartcard national ID (high assurance, heavy governance)
- Very strong, but ties you to national ID infrastructure and legal frameworks.

## Passkeys / sync (explicit risk)
If you permit cloud-synced passkeys, you are accepting:
- provider compromise risk,
- cross-device cloning risk (by design),
- complex legal discovery/compulsion questions.

For “paranoid mode” elections, default to **non-sync** hardware credentials for casting.
Sync may be acceptable for low-stakes participation, not for binding ballot casting.

## Privacy: do not sign ballots with the long-term credential

The **credential should authenticate eligibility**, but the **ballot should be unlinkable**.

Recommended pattern:
1. Voter authenticates with credential to the Registration Authority (RA).
2. RA issues an **unlinkable, spend-once eligibility token** (blind-signed or ZK membership proof).
3. The voter uses the token to authorize **ballot submission** to the bulletin board.

This prevents the bulletin board (and its operators) from learning a stable “voter identifier”.

## Attestation (use carefully)

Attestation can prove “this key lives in certified hardware,” but it can also create tracking identifiers.
Requirements:
- Attestation must be **optional** and **privacy-preserving** (batch attestations, device class proofs).
- Never require unique device certificates per voter if you can avoid it.

## Issuance & recovery

- **In-person issuance / re-issuance** is the cleanest recovery story.
- Remote recovery must be treated as high-risk and gated (multi-factor + cooling-off + audit trail).
- Lost credential → revoke old credential, issue new, publish revocation update.

## Revocation & transparency

- Revocation lists must be **public, append-only, and mirrored** (same transparency pattern as ballots).
- Publish signed revocation updates frequently; auditors should monitor for suppression.

## Minimal compliance checklist

- [ ] Non-exportable key storage.
- [ ] Origin-bound authentication (phishing resistance).
- [ ] In-person recovery path.
- [ ] Unlinkable eligibility tokens for ballot casting.
- [ ] Public revocation transparency.

## Primary references
See `references.md` for WebAuthn/FIDO specs and implementation considerations.


## v15 notes
For detailed lifecycle and recovery specs, see:
- `79-credential-lifecycle-and-recovery.md`
- `80-identity-proofing-and-equity.md`
- `81-privacy-preserving-eligibility-token-minting-protocol.md`
- `82-credential-loss-theft-and-rapid-reissuance.md`
- `83-credential-compromise-detection-and-mass-incident.md`
- `84-mdl-and-verifiable-credentials-optional-path.md`
- `85-credential-governance-and-oversight.md`
