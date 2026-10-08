# Incident triage quickcheck (symptom → packet)

**Track:** Shared (cross-cutting)


Reference: `docs/216-incident-triage-and-evidence-quickmap.md`.

## First actions (T+0 to T+30 min)
- ☐ Name the disputed surface (results / comms / pointer freshness / closeout / registration).
- ☐ Classify the worst-credible catastrophe class (C1..C5) and avoid “availability-first” bias.
- ☐ Publish a bounded **PublicNotice** with `next_update_at` (even if it says “we don’t know yet”).
- ☐ Capture *digests not bodies*:
  - ☐ `hfv.coverage.liveness_beacon` (≥2 independent watchers)
  - ☐ and/or `hfv.public.surface_parity_snapshot`
- ☐ If impersonation is plausible: publish/refresh `hfv.public.notice_signing_keyset`.
- ☐ Mirror the packet(s) to ≥2 mirrors; ensure bounded discovery surfaces are updated (`200`, `204`).

## Before you claim resolution
- ☐ Assemble the smallest dispute-legible packet/bundle (claim-first; `211`).
- ☐ Publish a verifier report packet (`hfv.verifier.packet_verification_report`) for the bundle (`193`).
- ☐ If you corrected a prior statement, publish an explicit correction notice (no silent edits).
