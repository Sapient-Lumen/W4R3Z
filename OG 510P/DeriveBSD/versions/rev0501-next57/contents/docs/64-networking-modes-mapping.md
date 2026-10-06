# Networking modes mapping (pf + tap/bridge + VNET)

DeriveBSD must translate runtime network intent into FreeBSD primitives deterministically.

## Modes (v1)
- isolated: no network device, or device on a dead-end switch
- nat: guest on a private bridge; pf performs NAT/egress allowlist
- bridged: guest tap on a host bridge (explicit allow)

## Primitives
- bhyve uses tap/virtio-net devices
- bridges connect taps
- pf anchors compose rules per instance (see `docs/26-virtual-networking-pf.md`)
- VNET jails can host network namespaces for build sandboxes (optional)

## Policy surface
- Profile default: host topology posture is now product-shaped rather than implicit. A stays activation-first/commit-confirmed with maintenance leases, B keeps risky host-topology changes trusted-UI-visible and confirmable, C keeps derived networking preferred with explicit local-admin fallback, and D keeps production topology sealed and maintenance-window-shaped (see `docs/477-network-topology-posture-by-profile.md`).
- default deny inbound
- explicit egress allowlists for microVMs and fetcher
- per-instance pf anchor naming and lifecycle is audited
- host substrate (links/addresses/routes/pf root ruleset) is applied via `net.topology.plan` → `net.topology.receipt`

See RFC-0040

See also: `docs/322-network-topology-and-firewall-as-derived-operations.md`, `docs/477-network-topology-posture-by-profile.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`.
Last updated: 2026-03-06r207
