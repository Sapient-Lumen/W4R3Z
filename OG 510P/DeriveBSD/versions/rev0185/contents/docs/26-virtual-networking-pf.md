# Virtual networking + firewall (pf-first)

If runtime is VM-centric, networking becomes a core product feature.

## Requirements
- declarative topology
- per-VM isolation options
- safe defaults (deny inbound, explicit egress)
- composable firewall rules

## Attachments
A VM declares one or more attachments:
- `isolated` (no egress unless routed)
- `nat` (egress NAT via host, inbound blocked by default)
- `bridged` (L2 presence, explicit pf policy required)

## pf anchors
- Every VM gets its own anchor:
  - `derivebsd/vm/<name>`
- Host policy composes anchors; workloads never write pf directly.

## Routing isolation (optional)

pf controls filtering, but some blast-radius boundaries want separate routing tables.
DeriveBSD can optionally bind compartments to dedicated FIBs (per-process routing tables) under policy.

See: `docs/144-routing-isolation-fibs-setfib.md`.

## Observability
- per-VM counters
- logs routed to host sink without granting host shell access

## Ecosystem note

There has been active work in the FreeBSD ecosystem around pf-based NAT networking for bhyve/libvirt (useful as a reference point even if DeriveBSD implements its own pf anchor composition): https://www.freebsd.org/status/report-2025-04-2025-06/

## Networking modes mapping

See `docs/64-networking-modes-mapping.md` (RFC-0040) for deterministic mapping to tap/bridge/pf anchors.


Last updated: 2026-02-23
