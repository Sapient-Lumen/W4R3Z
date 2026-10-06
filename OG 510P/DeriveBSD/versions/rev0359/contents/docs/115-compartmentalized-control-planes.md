# Compartmentalized control planes (Qubes lessons)

Qubes OS demonstrates a powerful pattern:
- isolate **privileged subsystems** (especially networking)
- chain trust boundaries so a compromise can’t silently disable policy

References:
- Qubes firewall model and chained firewall VMs. https://doc.qubes-os.org/en/latest/user/security-in-qubes/firewall.html

## DeriveBSD direction

Treat parts of the DeriveBSD control plane as *workloads* that can be isolated:

- `net-domain`: owns uplink NICs, L2 bridges, DHCP client, NAT
- `fw-domain`: owns pf policy composition and enforcement anchors
- `fetch-domain`: the only component with outbound network during fetch
- `publish-domain`: holds signing keys and pushes to caches/channels

These can be:
- microVMs (preferred)
- or jails (fallback) — **prefer VNET jails** for networked domains so the compartment has its own network stack.

## Why this fits DeriveBSD

- “treat builders hostile” generalizes to: **treat network-exposed subsystems hostile**.
- pf-composed networking becomes safer: the entity that can change pf is not the entity exposed to the internet.
- improves “why/what/where from”: control plane actions become recorded artifacts.

## Template + disposable microVMs (Qubes storage lesson)

Qubes also uses a “template + private + volatile” disk model to centralize updates and make disposable VMs cheap. (refs: https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html , https://doc.qubes-os.org/en/latest/user/templates/templates.html)

DeriveBSD can use the same pattern for control-plane microVMs and builders:
- base = signed bundle digest (immutable)
- private = per-instance persistent state (optional)
- volatile = per-boot scratch (discarded)

See: `docs/129-template-microvms-and-disposables.md`.


## v1 minimalism

- keep it optional
- start with separating `fetch-domain` + `publish-domain`

If microVM isolation is not available yet, start by realizing these domains as **VNET jails** with `epair(4)` links and policy-composed `pf` anchors.

See: `docs/171-vnet-jails-network-compartments.md`.

See RFC-0083.
