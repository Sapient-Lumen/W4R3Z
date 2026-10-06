# Packet capture session and summary-first export boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` already fixed the authority question:
packet capture is stronger than ordinary networking.
This doc fixes the next practical question:
**when capture is allowed, what shape keeps it bounded, reviewable, and export-safe?**

See also:
- ADR: `adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md`
- stronger raw-packet authority lane: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- temporary authority contract: `docs/493-temporary-authority-grant-lease-and-use-boundary.md`
- export boundary posture: `docs/466-export-boundary-posture-by-profile.md`
- export portal: `docs/251-export-policies-and-support-bundle-portal.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- packet-capture summary surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- session schema: `spec/packet.capture.session.schema.json`
- session example: `spec/examples/packet.capture.session.json`
- summary schema: `spec/packet.capture.summary.schema.json`
- summary example: `spec/examples/packet.capture.summary.json`

## Why this needs a hard decision

Once packet capture is admitted at all, archives usually drift into a familiar anti-pattern:
operators run a capture tool, save a raw packet file, and the file itself becomes the de facto workflow.
That is expensive in all the wrong ways:

- authority is implicit rather than session-bounded,
- support/export posture becomes whatever the tool happened to write,
- workstations and fleets silently normalize raw packet sharing,
- and regulated/appliance deployments lose their claim that evidence/export is deterministic and reviewable.

DeriveBSD needs a narrower answer than "packet capture is dangerous":
**capture must itself be a typed temporary-authority session, and export must remain summary-first by default.**

## Accepted baseline

Across all profiles:

- bounded packet capture uses an authoritative `packet.capture.session` object,
- the session is the thing lease metadata and lease issue/use evidence point at,
- the session must name scope, a typed selector posture, and explicit time/packet/byte bounds,
- local packet bytes may exist inside that bounded lane,
- any Derive-managed retained raw artifact is opaque local evidence rather than a naming or metadata surface,
- `retention.max_local_retention_seconds` sets the reviewable upper bound for how long that local artifact may survive after capture ends,
- but the normal review/share surfaces are session metadata, `packet.capture.summary`, and `incident.bundle` evidence,
- and raw packet payload export is a stronger explicit exception rather than the default support handoff.

## Canonical session shape

A `packet.capture.session` records enough structure to review the request *before* capture starts:

- **purpose** — incident, canary, maintenance, trusted-host admin, lab, or another explicitly named reason
- **scope** — host plus interface(s), and optional service / jail / VM selector when capture is narrower than whole-host
- **capture settings** — backend, typed `packet.capture.selector`, snaplen, and whether promiscuous capture is requested
- **bounds** — maximum duration, maximum packets, and maximum bytes
- **retention / export posture** — whether local raw bytes are ephemeral vs sealed-local, the `max_local_retention_seconds` budget for any retained local artifact, and whether default export is metadata-only or summary-only
- **review expectation** — `packet.capture.summary` is the normal capture review surface; `net-flow-summary` remains the separate learn/audit artifact when packet evidence later informs policy convergence

The point is not perfect future-proofing.
The point is to make packet capture a reviewable object instead of a shell incantation, and to keep any retained packet file an opaque local evidence object instead of the real workflow.

## Export posture: summary first

The archive already says export is a separate policy-governed step.
Packet capture should follow that rule even more strictly than ordinary logs.

Default posture:

- incident bundles may include capture-session metadata, `packet.capture.summary` digests, selectors, budgets, and summary metadata,
- incident bundles may reference local raw packet artifacts by digest,
- but they should **not** include raw packet payloads by default,
- and support/export flows should prefer `packet.capture.summary`, timeline context, and deterministic transforms over shipping packet blobs.

When raw packet bytes are exported anyway, that should read as a stronger exception:

- explicit export policy,
- explicit approval/consent when required,
- explicit encryption / recipient / ticket constraints,
- and receipts that show raw payload export happened on purpose.

## Product-shape defaults

| Profile | Default capture-session posture | Default raw-payload export posture | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `broker-owned-incident-canary-maintenance-bounded-session` | `summary-only-default-raw-explicit` | Fleet capture is allowed when incident or canary analysis justifies it, but the normal handoff remains summary-first. |
| **B workstation** | `trusted-host-admin-bounded-session` | `trusted-ui-visible-summary-first` | Local trusted-host troubleshooting remains viable, but raw packet sharing stays deliberate and visible rather than ambient. |
| **C general_os** | `explicit-local-admin-session-derived-workloads-stay-strict` | `summary-first-compatibility-exception` | General-purpose compatibility stays possible without redefining the stricter default for derived workloads. |
| **D appliance_factory** | `approved-maintenance-lab-session-only` | `production-none-summary-reference-only` | Production appliances should reference or summarize packet evidence, not quietly export packet payloads. |

## Review guidance

When reviewing a packet-capture proposal, ask:

1. Is a packet capture session actually necessary, or would existing receipts / summaries / tracing answer the question?
2. Is the scope as narrow as possible (interface, service, jail, VM, incident window)?
3. Are the session bounds explicit and small enough to be believable under incident pressure?
4. Does the default export remain metadata-only or summary-only for the target profile?
5. If raw packet bytes may leave the box, is that called out as a stronger export exception rather than hidden inside support tooling?

## Why this is worth locking now

This is not a new subsystem.
It is a coherence cut that makes the already-accepted raw-packet boundary implementable:

- A keeps incident-grade capture without normalizing raw packet exports,
- B keeps trusted-host troubleshooting without ambient app visibility,
- C keeps compatibility viable without laundering it into the derived-workload default,
- D keeps a real production/regulatory story instead of secret `.pcap` folklore.

That is enough to guide future broker, CLI, and receipt work while staying narrow.

Last updated: 2026-03-09r242
