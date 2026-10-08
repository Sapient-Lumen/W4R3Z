# Coercion-resistant registration & credentialing (high-risk, high-leverage)

**Track:** B (Remote return / hard-mode research)


Remote voting systems often fail before ballots are cast: **registration** and **credential issuance**
become choke points for coercion, exclusion, and surveillance.

This document focuses on *registration-side* coercion resistance, including “fake credential”
families and recent work on coercion-resistant registration.

## Threats

- Coercer forces a voter to register with coerced credentials or to reveal credentials
- Vote-buying with proof-of-eligibility or “credential escrow”
- Registration authority (RA) compromise enabling targeted denial (revocations, issuance blocks)
- Surveillance via linkable registration events (who registered, when, where)

## Design directions

### A) Unlinkable eligibility tokens (recommended)
- Long-term credential (e.g., WebAuthn) authenticates to RA
- RA issues **unlinkable spend-once eligibility tokens**
- PBB sees only tokens, not long-term identity credentials

### B) Fake-credential / coercion-evasion registration (research-heavy)
Some systems allow the voter to hand a coercer “plausible credentials” that do not count.
Recent work (e.g., TRIP) explores coercion-resistant registration combined with verifiability,
but deployment adds UX and governance risk.

### C) Supervised override
If remote return is allowed at all, provide an in-person override path that cancels prior remote
submissions.

## Requirements (normative)

- Long-term credentials MUST NOT directly sign ballots.
- RA MUST publish transparent revocation/issuance events (as hashes) to detect selective denial.
- Token issuance SHOULD support multiple issuers to reduce capture risk.

## References

- TRIP: Coercion-resistant registration for e-voting (ACM CCS 2025)
- WebAuthn Level 3 (credential properties and phishing resistance)