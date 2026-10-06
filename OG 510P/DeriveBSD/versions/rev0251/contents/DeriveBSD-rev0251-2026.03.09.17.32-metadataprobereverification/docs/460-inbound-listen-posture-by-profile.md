# Inbound listen posture by profile

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

Listening on a socket is one of the easiest ways for a system to drift from “derived and explainable” into “mysterious attack surface.”
Servers want published endpoints, workstations want local developer tools, general-purpose systems need pragmatic escape hatches, and regulatory deployments often want *no* listeners unless explicitly justified.

This doc records the smallest durable answer:

> inbound exposure is profile-shaped, not ambient, and loopback is the low-friction default while broader exposure must land in brokered classes, leases, or durable policy.

See `adrs/ADR-0050-inbound-listen-posture-by-profile.md`.

## Baseline rule

Across all profiles:

- workloads do **not** receive ambient “bind/listen and poke the firewall until it works” authority as the design baseline,
- loopback remains the easy local default,
- non-loopback exposure is governed through brokered service classes, leases, or durable policy objects,
- deny/explain is a first-class outcome,
- and any interactive approval must produce a short-lived lease or a durable policy edit that can later be reviewed and revoked.

This keeps inbound exposure aligned with the archive’s wider model: authority is explicit, bounded, and evidenced.

## Profile defaults

| Profile | `network_ingress` default | Practical meaning |
|---|---|---|
| **A fleet_host** | `brokered-service-classes-noninteractive` | Fleet/service listeners are exposed through policy-defined service classes and receipts, not ad-hoc host prompts; low-traffic admin surfaces should prefer on-demand activation when practical. |
| **B workstation** | `loopback-by-default-brokered-exceptions-with-lease` | General interactive apps may expose local loopback services by default, but LAN/public exposure requires a trusted-UI-mediated lease or durable policy object rather than ambient bind+firewall edits. |
| **C general_os** | `brokered-service-classes-explicit-adapter-fallback` | Derived workloads still prefer brokered listen classes, but legacy/dev workflows may use an explicit adapter fallback rather than forcing a fork or pretending every server workflow is broker-ready on day one. |
| **D appliance_factory** | `deny-by-default-offline-or-approved-brokered-service` | Regulatory/offline deployments default to no inbound exposure or tightly approved brokered services; interactive prompts are not the authority model. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## The hard decision hidden inside the table

The archive is now choosing **against** a universal “services can just open ports” mental model.
That means:

- profile **B** may support good trusted-UI prompts, but prompts are not the firewall database,
- profile **A** does not get dragged into workstation-style “temporary” exposure clicks,
- profile **D** does not pretend prompt-driven support holes are acceptable audit posture,
- and profile **C** gets its viability escape hatch explicitly, as an adapter-shaped fallback.

This is the same move made for egress and removable media:
**fallbacks may exist, but they must be named, bounded, and reviewable.**

## Loopback is special, but not ambient policy amnesia

Local-only developer tooling and helper services matter.
DeriveBSD’s baseline is to keep loopback easy *without* letting that turn into accidental LAN/public exposure.

So “run a local dev server” should normally remain a loopback action, while “share this service on the LAN / expose it remotely / open remote assistance” should become:

1. a brokered service class or trusted-UI request,
2. a short TTL grant or a durable policy change,
3. a receipted listener state,
4. and a review surface that can later answer what was exposed, for how long, and why.

This keeps developer viability without normalizing invisible firewall folklore.

## How this fits the workstation boundary

For profile **B**, this composes directly with `ADR-0047` and `ADR-0049`:

- the host remains trusted UI + brokers,
- general apps remain AppVM-first,
- network exposure is another mediated crossing like files/devices/clipboard,
- and both outbound and inbound networking now share the same contract: explicit authority, bounded duration, durable explanation.

That makes “this app wants to accept connections” structurally similar to “this app wants to connect out”: a brokered event, not ambient process power.

## How this fits A and D

### A) Fleet host

A fleet host should not normalize “someone clicked Open Port on prod.”
Its posture is:

- policy-derived service exposure,
- non-interactive by default,
- listener grants/receipts tied to the exposed workload,
- and topology changes handled through derived host networking plans.

### D) Appliance factory / regulatory

For regulated or air-gapped shapes, the right default is not to bolt on prompts.
It is to keep inbound exposure either absent or explicitly approved:

- support/inspection paths should be named and receipted,
- “temporary debug listeners” must not become invisible operational lore,
- and approved service exposure should remain stable enough for audit and factory documentation.

## What remains open

This doc does **not** settle:

- exact TLS termination / reverse-proxy patterns,
- whether a given class uses FD passing, proxy-forwarding, or broker-held sockets,
- evidence budget and retention for listener receipts vs per-connection logs,
- or every developer/remote-support workflow.

Those are narrower follow-on questions.

## Related docs

- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/238-portal-activated-services-and-socket-activation.md`
- `docs/67-pf-anchors-per-instance.md`
- `docs/459-outbound-network-posture-by-profile.md`
- `docs/322-network-topology-and-firewall-as-derived-operations.md`

Last updated: 2026-03-06r189
