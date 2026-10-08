# VRDB hardening checklist (Tier‑0)

- [ ] Inventory VRDB assets, dependencies, and third parties (hosting/CDN/DNS/managed services)
- [ ] Enforce MFA + least privilege + just-in-time admin access
- [ ] Immutable audit logs + tamper-evident retention
- [ ] Backup/restore tested (RTO/RPO defined) and offline copies available
- [ ] Publish signed daily `VRDBSnapshot` roots + witness cosigns
- [ ] Continuous monitoring for integrity/availability anomalies
- [ ] Election-day offline pollbook snapshots + reconciliation plan
- [ ] Incident playbooks and public evidence bundle templates ready
