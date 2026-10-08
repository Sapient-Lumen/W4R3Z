# 49 — Anonymous submission layer (OHTTP/ODoH) — draft

**Track:** B (Remote return / hard-mode research)


## Goal
Reduce *metadata* leakage (IP address, timing, routing vantage) so that the Public Bulletin Board (PBB) and its operators cannot easily learn **who** submitted a ballot, **when**, or from **where**.

This document specifies an *optional but strongly recommended* submission transport profile that uses privacy-partitioning relays (Oblivious HTTP) and DNS privacy (Oblivious DoH).

## Threats addressed
- Targeted voter suppression by identifying voters (or neighborhoods) attempting to vote and selectively degrading service.
- Turnout surveillance by PBB operators, federation nodes, or their upstream providers.
- Correlating “cast vs spoil vs re-vote” via packet size or request patterns.
- Legal/physical coercion supported by “proof you voted at time T from IP X”.

## Non-goals
- Strong anonymity against a global passive adversary watching both client access networks and relay egress.
- Coercion resistance (see `07-coercion.md` and `33-coercion-resistance-deep-dive.md`).

## Architecture (privacy partitioning)
### Parties
- **Client**: voter application.
- **Relay**: sees client IP, but not request content.
- **Gateway**: sees request content, but not client IP (receives via Relay).
- **PBB Gateway**: the logical endpoint that accepts `BallotSubmission` or `IntakeReceipt` polling; can be co-located with the PBB *but MUST NOT be co-operated with the Relay*.

### Transport
- Use **Oblivious HTTP (OHTTP)** for ballot submission and receipt queries.
- Client chooses a Relay from a configured set, with rotation and randomization.
- Gateway is the PBB front-end (or a dedicated gateway service) that speaks to the internal PBB append path.

### DNS
- Client SHOULD resolve Relay and Gateway endpoints via **Oblivious DNS over HTTPS (ODoH)**.
- Clients MAY ship with pinned Relay/Gateway configs to avoid DNS entirely, but MUST support emergency rotation.

## Protocol profile
### Message classes (all fixed-shape)
To prevent length/timing inference, the client MUST send constant-shape envelopes:
- `SubmitEnvelope`: encapsulates `BallotSubmission` (or `CastOrSpoilChallenge`) padded to a fixed bucket.
- `PollEnvelope`: encapsulates a receipt status query padded to the same bucket.
- `CoverEnvelope`: indistinguishable from the above, with dummy payload.

All three MUST be indistinguishable to:
- a passive observer on the client’s link,
- the Relay,
- the Gateway (aside from decrypted content).

### Timing equalization
- Client SHOULD add randomized delay and batching windows (e.g., 1–5s) before sending.
- Client SHOULD maintain background cover traffic during the voting period (at a low rate) to reduce “I voted now” signals.

### Failure handling
- If OHTTP path fails, client MAY fall back to:
  - alternate Relay,
  - alternate Gateway,
  - direct HTTPS *only if* UI explicitly warns that metadata exposure increases.
- Clients MUST keep “RECORDED” semantics strict: no claim of recorded-unless-inclusion-proof.

## Key management
- Relay and Gateway public key configs (for OHTTP HPKE) MUST be distributed via the Evidence Bundle channel:
  - signed by a Federation policy key,
  - logged on the PBB,
  - mirrored by witnesses.

## Implementation notes
- Treat Relays as **independent operators** (NGO/university/opposition party/industry).
- Prefer HTTP/3 (QUIC) where feasible; avoid leaking ALPN/UA fingerprints by standardizing client stacks.

## References
- OHTTP: RFC 9458
- ODoH: RFC 9230