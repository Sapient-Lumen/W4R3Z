# Multi-perspective endpoint validation checklist

**Track:** Shared (cross-cutting)


- [ ] Define target endpoints (portal + mirrors + ENR)
- [ ] Define quorum rule (k-of-n agreement)
- [ ] Collect perspective measurements from independent networks
- [ ] Compare:
  - [ ] DNS answers
  - [ ] TLS SPKI fingerprints
  - [ ] HTTP body hash (immutable endpoints)
- [ ] Publish EndpointValidationReport signed + anchored
- [ ] If divergence:
  - [ ] publish ParityAlert + `hfv.public.notice` PublicNotice (notice_type: incident_advisory)
  - [ ] prefer onion mirror and known-good mirrors
