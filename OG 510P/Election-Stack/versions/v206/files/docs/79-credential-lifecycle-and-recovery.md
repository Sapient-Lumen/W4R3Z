# 79 — Credential lifecycle and recovery (citizen keys)

**Track:** B (Remote return / hard-mode research)


This pack assumes **citizens hold private keys**, but treats the credential subsystem as an election-critical attack surface.

**Non-negotiable invariant:** the long-lived citizen credential MUST NOT be used to directly sign ballots or ballot ciphertexts. It is used only to obtain **unlinkable, spend-once eligibility tokens** (see `15-privacy-and-eligibility-tokens.md` and `81-privacy-preserving-eligibility-token-minting-protocol.md`).

## Goals
- Provide strong authentication for eligibility token minting.
- Provide *safe* recovery paths that do not disenfranchise voters and do not create a turnout-surveillance oracle.
- Make mass credential incidents **detectable** and **recoverable** (with explicit ceremonies and public evidence).

## Threats
- **Phishing and account takeover** of credential portals.
- **Coerced enrollment / coerced recovery** (abuser forces victim to enroll/recover on abuser-controlled device).
- **Lost/stolen devices** on election week.
- **Vendor compromise** (passkey sync, identity provider, RA back-office).
- **Insider abuse** (silent revocation, selective delays).
- **Discrimination & inequity** (proofing requirements exclude eligible voters).
- **Participation inference via metadata:** RA/CSP logs (time, IP, device) can reveal who sought credentials or tokens even if ballots remain private.

## Credential roles (separation of powers)
- **Credential Service Provider (CSP)**: performs enrollment, binds authenticators, issues *proof-of-eligibility* assertions for token minting.
- **Eligibility Token Issuer (ETI)**: mints unlinkable tokens based on CSP assertions (ideally a separate operator, possibly thresholded).
- **Registration Authority (RA)/VRDB**: authoritative voter registration and eligibility epochs (`75-revocation-and-eligibility-transparency.md`).

**Design bias:** keep ETI blind to voter identity; keep CSP unable to learn vote casting.

## Lifecycle stages (normative)
### A. Enrollment
- MUST support **in-person enrollment** as a high-assurance path.
- SHOULD support enrollment on *multiple authenticators* (primary + backup) to reduce single-point loss.
- MUST publish a **credential policy** (accepted authenticator classes, loss/recovery SLAs, appeal paths).

### B. Binding authenticators
- SHOULD use WebAuthn/FIDO2 authenticators with user verification (UV) where possible.
- MUST bind authenticators to a subscriber account at an assurance level appropriate for eligibility.

### C. Normal operation (token minting)
- Voter authenticates to CSP and obtains a short-lived **mint authorization**.
- Voter presents authorization to ETI via a privacy-partitioned channel (OHTTP recommended) to mint eligibility tokens.

### D. Rotation
- MUST support key rotation without changing eligibility.
- Rotation events MUST be logged in an append-only credential event log (privacy-preserving; see schemas).

### E. Loss / recovery
- MUST support emergency **loss reporting** and revocation with clear UX.
- MUST provide an **in-person recovery** path that does not depend on existing devices.
- SHOULD provide a remote recovery path only if it meets explicitly stated proofing requirements and equity constraints (see `80-identity-proofing-and-equity.md`).

### F. Revocation and reissuance
- MUST publish revocation/epoch updates with a “mass-change” alarm threshold.
- Reissuance MUST create a **new** credential identifier (avoid linkability over time).

## Safety constraints (coercion-aware)
- Recovery flows MUST include an **abuse-safe option**: “I cannot safely use my current device” → forces a higher-friction but safer recovery path.
- MUST avoid allowing a coercer to verify the victim’s enrollment/recovery completion through any transferable artifact.

## Minimum evidence for disputes
For disputes about eligibility tokens / credential revocation / recovery denial, the system MUST be able to produce a privacy-preserving evidence bundle:
- signed policy version
- anonymized event log inclusion proof
- eligibility epoch checkpoint
- (where appropriate) redacted administrative records

See `59-dispute-resolution-and-adjudication.md`.