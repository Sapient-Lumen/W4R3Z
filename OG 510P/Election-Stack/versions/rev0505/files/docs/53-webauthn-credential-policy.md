# 53 — WebAuthn credential policy (citizen keys) — draft

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

## Goal
Use phishing-resistant, hardware-backed authenticators as the root for eligibility,
while preventing the credential from becoming a turnout surveillance identifier.

## Policy (recommended baseline)
- Credential MUST be hardware-backed (platform secure enclave or roaming authenticator).
- Prefer user verification (PIN/biometric).
- No “silent” assertion: require explicit user presence and consent.
- Do not store ballot material in the authenticator.

## Privacy rule (hard requirement)
Long-term WebAuthn credentials MUST be used only to obtain **unlinkable eligibility tokens**
(see `15-privacy-and-eligibility-tokens.md` and `50-anonymous-rate-limiting-and-ddos.md`).

## Attestation
- Use attestation only to enforce minimum security properties; avoid over-collection of device-identifying info.
- Publish allowed authenticator classes and fallback paths (in-person issuance).

## References
- Web Authentication Level 3 (W3C TR)