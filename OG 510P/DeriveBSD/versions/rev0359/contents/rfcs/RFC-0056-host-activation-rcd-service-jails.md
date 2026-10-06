# RFC-0056: Host activation backend (rc.d + service jails)

- Status: draft
- Created: 2026-02-23

## Summary
Standardize host activation as:
- ZFS boot environment generation
- rc.conf + rc.d enablement as the service orchestration layer
- optional service jails for control-plane hardening

## Goals
- atomic rollbackable activation (bectl)
- auditable service knobs
- minimize blast radius (service jails)

## References
- FreeBSD rc.d scripting article
- FreeBSD Handbook: jails/service jails
- rc.conf(5), rc.subr(8), service(8)
