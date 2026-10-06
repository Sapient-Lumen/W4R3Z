# Packet capture selector compiler boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt  

`docs/507-packet-capture-session-and-summary-first-export-boundary.md` already fixed the session/export posture,
and `docs/508-packet-capture-summary-review-surface-boundary.md` fixed the compact review object.
This doc fixes the next practical implementation seam:
**what exactly do we review before capture starts — a typed selector, or a backend-specific filter string?**

See also:
- ADR: `adrs/ADR-0099-packet-capture-selector-compiler-boundary.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- packet-capture summary review surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- raw-packet authority boundary: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- selector schema: `spec/packet.capture.selector.schema.json`
- selector example: `spec/examples/packet.capture.selector.json`
- session schema: `spec/packet.capture.session.schema.json`
- session example: `spec/examples/packet.capture.session.json`

## Why this needs a hard decision

A free-form capture filter string looks convenient, but it is the wrong authoritative surface for DeriveBSD:

- the review object starts depending on libpcap / tcpdump syntax,
- available syntax can vary with the installed capture library version,
- backend-specific arithmetic and extensions leak into the archive contract,
- and session diffs become parser folklore instead of typed intent.

DeriveBSD needs a narrower answer than “store whatever filter works on this machine”:
**the authoritative session should carry a typed selector, and backend filter expressions should be compiled consequences.**

## Accepted boundary

Across all profiles:

- `packet.capture.session` remains the authoritative bounded capture-session object,
- `packet.capture.selector` is the canonical typed selector embedded in that session,
- backend-specific capture-filter expressions are implementation detail rather than the review surface,
- and broadening selector vocabulary requires explicit archive change rather than accidental backend inheritance.

## Canonical selector shape

A `packet.capture.selector` records the smallest durable set of reviewable capture intent:

- **direction** — ingress, egress, or either
- **family set** — `ipv4`, `ipv6`, `arp`, or another explicitly allowed portable class
- **transport set** — `tcp`, `udp`, `icmp`, `icmpv6`, `arp`, or `any`
- **host matches** — host / CIDR / hostname with explicit source/destination/either role
- **port matches** — source/destination/either port constraints
- **small bounded extras** — optional VLAN ids and simple TCP flag constraints when they are operationally justified

The point is not to represent the whole libpcap grammar.
The point is to make the durable review object portable, compact, and explainable.

## Compiler posture

DeriveBSD still needs real backends.
FreeBSD `bpf(4)` capture and libpcap/tcpdump-style filtering remain practical implementation choices.
But the selector boundary says:

- the reviewed object is the typed selector,
- the backend compiler is a narrow translation step,
- and the compiled backend filter should not become the authoritative archive object.

That leaves room for different backend implementations while keeping one stable session shape.

## Product-shape defaults

| Profile | Default selector posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `typed-broker-reviewed-minimal-selector` | Fleet incident/canary capture stays reviewable and portable instead of depending on oncall-specific tcpdump strings. |
| **B workstation** | `trusted-ui-visible-typed-selector` | Trusted-host troubleshooting remains viable, but what is approved is clear capture intent rather than shell syntax. |
| **C general_os** | `typed-selector-with-admin-compat-compiler` | General OS can still compile to familiar tooling, but the archive surface stays Derive-shaped. |
| **D appliance_factory** | `typed-approved-maintenance-selector-only` | Factory/regulatory shapes keep capture selectors narrow, reviewable, and easier to justify in audit/change review. |

## Review guidance

When reviewing a packet-capture session, ask:

1. Is the selector as small and typed as possible, rather than a backend string nobody wants to reason about?
2. Would this selector compile to the needed backend without relying on niche backend-only tricks?
3. Does the selector stay stable enough that diffs tell you what capture intent changed?
4. Is any future compiled backend filter treated as execution detail or receipt detail rather than authority?

## Why this is worth locking now

This is not a new subsystem.
It is an entropy cut that stops the raw-packet lane from quietly inheriting libpcap grammar as product law.

That helps every product shape:

- A gets portable operational review,
- B gets visible trusted-host capture intent,
- C keeps compatibility without ceding the archive boundary,
- D gets a more auditable maintenance lane.

Last updated: 2026-03-08r238
