# 58 — Anonymous Anti-Abuse Tokens (Fairness under DDoS)

**Track:** B (Remote return / hard-mode research)


## Why this exists (paranoid assumption)
Under election-day conditions, you must expect:
- DDoS and bot floods
- targeted suppression via throttling
- discriminatory defenses that accidentally disenfranchise

You need a way to **throttle abuse** without relying on IP address reputation or requiring identity disclosure.

## Approach
Use anonymous tokens for access control and rate limiting:
- Privacy Pass-style redemption as an HTTP authentication scheme
- ARC-style rate-limited credentials (optional)

Tokens can be issued via:
- puzzle/challenge (anti-bot)
- eligibility-authorized issuance (for per-voter quotas)

## Normative requirements
1. Anti-abuse controls MUST be designed to avoid disparate impact:
   - no geo/IP blocks as primary control
   - no reliance on commercial “bot scores” without audit
2. Token issuance MUST support multiple issuers to avoid a single point of censorship.
3. Token redemption MUST be compatible with privacy-partitioned submission (OHTTP profile).
4. If token infrastructure fails, the system MUST degrade to:
   - verifiable “intake receipts” with explicit PENDING status
   - clearly communicated fallback channels

## Artifact: `RateLimitToken`
See schema. Tokens MUST be bound to:
- election_id
- endpoint context
- limited lifetime

## Security notes
- Token issuer compromise can become a censorship tool.
- Mitigate via issuer diversity, independent monitoring, and audit logs.