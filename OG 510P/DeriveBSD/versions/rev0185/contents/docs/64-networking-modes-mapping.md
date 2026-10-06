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
- default deny inbound
- explicit egress allowlists for microVMs and fetcher
- per-instance pf anchor naming and lifecycle is audited
- host substrate (links/addresses/routes/pf root ruleset) is applied via `net.topology.plan` → `net.topology.receipt`

See RFC-0040

See also: `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`.
Last updated: 2026-02-26
