# 50 — Anonymous rate limiting, abuse control, and DDoS posture — draft

**Track:** B (Remote return / hard-mode research)


## Goal
Allow the system to:
- protect ballot submission endpoints from flooding,
- prevent credential stuffing and scripted abuse,
- do basic “per-eligible-voter” throttling,

…without turning anti-abuse into identity tracking.

## Threats addressed
- L7 floods aimed at intake endpoints.
- Adversary uses botnets to degrade service or to “fill” the log with junk (even if invalid ballots are rejected).
- Targeted “denial of ballot inclusion” by exhausting per-IP or per-AS quotas.
- Replay/duplicate submissions intended to overload verifier/validator.

## Design principle
**Rate limits must be enforced using unlinkable tokens, not IP addresses.** IP rate limiting is allowed only as a last-layer safety valve and MUST be coarse.

## Privacy-preserving tokens (recommended)
### Use Privacy Pass-style tokens
Client includes an **anonymous token** with each `SubmitEnvelope`:
- token is one-time or rate-limited (ARC-style),
- token is bound to `election_id` (context binding),
- gateway verifies token without learning voter identity.

### Issuance
Token issuance MUST require strong eligibility proof (e.g., WebAuthn credential) *but issuance MUST be unlinkable to redemption*.
- Issuer(s) SHOULD be independent of Gateway operators.
- Tokens SHOULD be issued in advance (pre-election) and replenished in small batches.

### Redemption
- Gateway validates token before spending CPU on ZK-proof verification.
- Spent-token list MUST be append-only and auditable (to prevent “selective refusal” claims).

## Operational DDoS posture (boring but necessary)
- Anycast + multi-CDN for Relay endpoints; Gateway endpoints behind multiple providers.
- Admission control: reject unauthenticated traffic fast; defer expensive crypto until tokens validated.
- Witness and mirror endpoints MUST be provisioned separately from intake endpoints.

## Evidence and transparency
During an incident:
- publish rate-limit policy changes (signed) to the PBB log,
- publish per-endpoint status (signed) to the public status page template,
- retain packet-level logs only under strict retention policy (avoid surveillance creep).

## References
- Privacy Pass HTTP Authentication Scheme: RFC 9577
- ARC issuance draft (rate-limited anonymous credentials): draft-privacypass-arc-protocol (work in progress)