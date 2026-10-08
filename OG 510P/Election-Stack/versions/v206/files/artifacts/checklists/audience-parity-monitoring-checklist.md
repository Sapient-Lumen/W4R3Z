# Audience parity monitoring checklist

## Targets
- [ ] Evidence portal (manifest endpoint)
- [ ] At least 3 independent HTTPS mirrors (different providers)
- [ ] Onion mirror (optional but recommended)
- [ ] ENR API + UI canary endpoints
- [ ] Revocation / incident notice endpoints
- [ ] PublicNotice latest feed stable endpoint(s) (docs/200) across all official comms surfaces

## Measurements (multi-vantage)
- [ ] DNS answers compared across resolvers/regions (and “resolve on probe” where supported)
- [ ] TLS SPKI fingerprint pinned and compared
- [ ] HTTP body hash for immutable endpoints compared
- [ ] For freshness-sensitive pointer surfaces (well-known/directory/feed/keyset), record cache headers (`ETag`, `Cache-Control`, `Age`, `Last-Modified`) and compare across vantages; capture them in `LivenessBeacon.observations[].headers` when publishing beacons (docs/205, docs/210).
- [ ] Locale/device canaries checked (at least top 5 locales + mobile/desktop UA)
- [ ] Publish (and later cite) a `ProbeCohortPlan` describing monitor diversity constraints; include its payload digest in each LivenessBeacon when available (docs/127, docs/210).
- [ ] Include coarse `vantage` metadata (at least ASN + country) in LivenessBeacons; avoid IP addresses.

## Alerting thresholds
- [ ] Any hash mismatch => ParityAlert within 5 minutes
- [ ] Any “RECORDED” receipt without inclusion proof => immediate freeze + incident
- [ ] Mirror reachability < quorum threshold => announce degraded mode and promote onion mirror

## Publication
- [ ] Publish signed ParityReports hourly (or tighter on election day)
- [ ] Publish receipted+gossiped **LivenessBeacons** (`hfv.coverage.liveness_beacon`) for the comms pointer surfaces (well-known/directory/feed/keyset), especially during incidents (docs/210).
- [ ] Anchor ParityReports into PBB checkpoints
- [ ] Provide public dashboard that links to ParityReport hashes and checkpoints
- [ ] On mismatch, publish a receipted+gossiped `hfv.public.surface_parity_snapshot` and cite its digest in a PublicNotice (docs/201)
- [ ] When a mismatch is suspected or disputed, issue a `PublicInspectionChallenge` for the affected endpoint(s) and request independent monitors to publish parity snapshots (docs/202; template: `artifacts/templates/public-inspection-challenge-endpoint-parity.json`).
- [ ] Ensure monitors link their snapshot digests into `MonitorAttestation` so missing responses become inspectable (docs/140, docs/202).
