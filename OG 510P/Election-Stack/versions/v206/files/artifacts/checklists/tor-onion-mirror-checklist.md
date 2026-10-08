# Tor onion mirror checklist

- [ ] Onion mirror serves only immutable, content-addressed bundles
- [ ] Onion address published in EPB and EvidenceBundleManifest
- [ ] Monitoring: parity probes include onion reachability checks
- [ ] Operational: no dynamic code paths; strict caching; read-only filesystem where possible
- [ ] Announcement: publish onion address through multiple independent channels (hash-only announcements)
