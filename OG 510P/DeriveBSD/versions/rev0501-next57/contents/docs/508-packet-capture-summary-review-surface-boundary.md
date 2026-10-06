# Packet capture summary review-surface boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

`docs/507-packet-capture-session-and-summary-first-export-boundary.md` already fixed the session/export posture:
packet capture is bounded and summary-first by default.
This doc fixes the next practical question:
**what is the canonical compact object we review and share instead of a raw packet blob?**

See also:
- ADR: `adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- packet-capture selector compiler boundary: `docs/509-packet-capture-selector-compiler-boundary.md`
- raw-packet authority boundary: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- learned-network convergence contract: `docs/505-network-learn-audit-convergence-contract.md`
- export boundary posture: `docs/466-export-boundary-posture-by-profile.md`
- evidence spine: `docs/229-evidence-spine-overview.md`
- schema: `spec/packet.capture.summary.schema.json`
- example: `spec/examples/packet.capture.summary.json`

## Why this needs a hard decision

Without a typed summary artifact, packet capture still tends to regress into tool output:

- a `.pcap` or `.pcapng` file becomes the real handoff object,
- each capture tool invents different metadata and naming conventions,
- support/export workflows lose a stable review surface,
- and `net-flow-summary` gets overloaded with a job it was not designed for.

DeriveBSD needs a narrower answer than “summarize somehow”:
**packet capture should have its own evidence-only summary object, and that object should be the default review/share surface.**

## Accepted boundary

Across all profiles:

- `packet.capture.session` remains the authoritative bounded capture-session object,
- `packet.capture.summary` is the canonical compact evidence object for reviewing the result of that session,
- `net-flow-summary` remains the separate learn/audit artifact for candidate network-policy convergence,
- incident/support bundles should prefer `packet.capture.summary` plus session metadata over raw packet payloads,
- and raw packet payload export remains a stronger explicit exception even when local raw artifacts exist.

## Canonical summary shape

A `packet.capture.summary` records enough structure to review the capture result without reopening raw packet bytes:

- **session join** — which `packet.capture.session` produced the summary
- **bounded window** — start/end times, observed packet/byte totals, and whether bounds truncated the capture
- **protocol totals** — compact counts by transport/protocol class
- **top conversations** — a small set of representative conversation aggregates for review/debugging
- **artifact references** — local raw capture artifact digests, storage posture, `metadata_posture`, and `retention_until`
- **export verdict** — whether the session stayed summary-only, metadata-only, or required an explicit raw-export exception

The point is not to replace raw bytes for every imaginable lab workflow.
The point is to make the normal review/export surface typed, compact, and predictable, while keeping any retained packet file on the strict `packet-records-only` default unless a stronger compatibility/import lane is explicitly admitted.
That stronger lane is now the typed safe-open packet-capture import profile in `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, which normalizes before ordinary promotion/export.

## Why not reuse `net-flow-summary`

`net-flow-summary` already has a clear job:
it summarizes bounded learn/audit sessions so operators can review candidate `net-egress-policy` changes before enforcement.

Packet capture has a different default job:
incident triage, support review, and controlled export.

Keeping those surfaces separate reduces entropy:

- policy convergence keeps one bounded evidence object,
- packet capture keeps one bounded evidence object,
- and neither lane has to smuggle its semantics through the other.

If a packet-capture session later informs a learned network-policy suggestion, that is an explicit secondary relationship.
It is not the default meaning of packet-capture summary.

## Product-shape defaults

| Profile | Default packet-capture summary posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `brokered-summary-default-export-review` | Incident/canary packet capture remains viable, but the ordinary oncall handoff is the compact summary plus session metadata. |
| **B workstation** | `trusted-ui-visible-summary-first` | Trusted-host troubleshooting can summarize capture results without normalizing stealth packet-file sharing. |
| **C general_os** | `explicit-local-admin-summary-first` | Local-admin compatibility remains possible, but the archive still has one Derive-shaped review object. |
| **D appliance_factory** | `production-summary-reference-only` | Production appliance workflows can point at packet evidence by digest and summary without defaulting to raw payload export. |

## Review guidance

When reviewing a packet-capture summary, ask:

1. Does it point back to a bounded `packet.capture.session`?
2. Does it make clear whether capture bounds truncated the observation?
3. Does it expose enough protocol/conversation structure to answer the incident/support question without reopening raw bytes first?
4. Does it clearly say whether raw packet payloads stayed local or were exported under stronger approval, including `metadata_posture` and `retention_until` for any retained local artifact?
5. Is it being used as evidence/review only, rather than quietly becoming policy or authority?

## Why this is worth locking now

This is not a new subsystem.
It is a coherence cut that keeps the raw-packet lane from slipping back into “the packet file is the product.”

That helps every product shape:

- A keeps incident-grade capture explainable,
- B keeps trusted-host troubleshooting visible,
- C keeps compatibility possible without archive drift,
- D keeps the regulatory/appliance story credible.

Last updated: 2026-03-09r240
