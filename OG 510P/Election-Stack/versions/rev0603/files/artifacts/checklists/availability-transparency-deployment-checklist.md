# Availability transparency deployment checklist

**Track:** Shared (cross-cutting)


- [ ] Define ATL scope: endpoints, artifacts, and incident classes.
- [ ] Publish MMDs (outage attestation submission/include deadlines) in EPB.
- [ ] Stand up >= 3 independent witness monitors in distinct ASNs/jurisdictions.
- [ ] Configure multi-perspective probe sources (internal, witness, external).
- [ ] Define SLO thresholds that trigger `DEGRADED` and `PARTITION`.
- [ ] Ensure status UI/API is derived from ATL entries (no separate mutable store).
- [ ] Ensure all ATL objects are content-addressed and anchored into PBB checkpoints.
- [ ] Run game day: simulate regional blocking + verify OA publication within MMD.
