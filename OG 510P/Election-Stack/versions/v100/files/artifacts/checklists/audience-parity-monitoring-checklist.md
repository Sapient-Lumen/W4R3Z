# Audience parity monitoring checklist

## Targets
- [ ] Evidence portal (manifest endpoint)
- [ ] At least 3 independent HTTPS mirrors (different providers)
- [ ] Onion mirror (optional but recommended)
- [ ] ENR API + UI canary endpoints
- [ ] Revocation / incident notice endpoints

## Measurements (multi-vantage)
- [ ] DNS answers compared across resolvers/regions (and “resolve on probe” where supported)
- [ ] TLS SPKI fingerprint pinned and compared
- [ ] HTTP body hash for immutable endpoints compared
- [ ] Locale/device canaries checked (at least top 5 locales + mobile/desktop UA)

## Alerting thresholds
- [ ] Any hash mismatch => ParityAlert within 5 minutes
- [ ] Any “RECORDED” receipt without inclusion proof => immediate freeze + incident
- [ ] Mirror reachability < quorum threshold => announce degraded mode and promote onion mirror

## Publication
- [ ] Publish signed ParityReports hourly (or tighter on election day)
- [ ] Anchor ParityReports into PBB checkpoints
- [ ] Provide public dashboard that links to ParityReport hashes and checkpoints
