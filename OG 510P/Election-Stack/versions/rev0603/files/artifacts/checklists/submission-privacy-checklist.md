# Submission privacy checklist (OHTTP/ODoH profile)

**Track:** Shared (cross-cutting)


- [ ] At least **2 independent relay operators** (different org + network provider).
- [ ] Relay and Gateway keys/configs are **signed and logged** on the PBB and mirrored.
- [ ] Client uses **fixed-size envelopes** with deterministic padding buckets.
- [ ] Client implements **poll/cover traffic** to reduce “I voted now” leakage.
- [ ] ODoH enabled for relay/gateway resolution where DNS is used.
- [ ] Direct HTTPS fallback is clearly labeled as **metadata-exposing**.
- [ ] Monitoring confirms no stable identifiers in envelopes (no device IDs, no persistent cookies).
- [ ] Red-team test: can an observer distinguish cast vs spoil vs poll by size/timing?
