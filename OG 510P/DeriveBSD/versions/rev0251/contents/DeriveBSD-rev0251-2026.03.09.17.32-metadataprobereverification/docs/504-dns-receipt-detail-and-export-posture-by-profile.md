# DNS receipt detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already decided three important things:

- outbound networking is brokered and profile-shaped,
- hostname-based policy only counts when DNS belongs to the governed lane,
- and evidence collection/export are profile-shaped rather than ambient folklore.

This doc decides the smaller but expensive follow-on question:
**how much DNS evidence detail is normal to keep and share in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `network_egress`, `evidence`, and `evidence_exports` posture surfaces.

See also:
- ADR: `adrs/ADR-0094-dns-receipt-detail-and-export-posture-by-profile.md`
- outbound network posture: `docs/459-outbound-network-posture-by-profile.md`
- DNS mediation boundary: `docs/305-dns-mediation-and-hostname-binding.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- telemetry boundary: `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`

## Why this needs a hard decision

Brokered DNS is the right enforcement shape, but DNS evidence is unusually sensitive.
If the archive keeps full per-query DNS receipts everywhere, it quietly creates an ambient browsing / namespace history.
If it avoids DNS receipts entirely, hostname-based egress policy becomes much harder to explain during incidents.

So the archive needs a durable answer to three questions:

- is `net-flow-receipt` or `net-dns-query-receipt` the normal review/export surface?
- when is full qname detail normal locally?
- when may qname detail leave the machine or organization boundary?

## Accepted baseline

Across all profiles:

- `net-flow-receipt` remains the **normal explainability/export surface** for governed egress,
- `net-dns-query-receipt` is scoped to **broker-governed hostname resolution** rather than an ambient whole-host DNS tap,
- full qname detail is **local-first and bounded**,
- off-box sharing of DNS detail defaults to **deterministic redaction, aggregation, or omission**,
- and split-horizon/internal names are treated as sensitive by default.

This keeps hostname policy real without normalizing ambient resolver surveillance.

## Product-shape defaults

| Profile | Local DNS-detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `bounded-full-detail-for-governed-hostname-lanes` | `redacted-by-default-full-qname-export-needs-incident-scope-and-stronger-approval` | Fleet/service incidents can reconstruct name→address decisions without turning raw namespace history into a routine export artifact. |
| **B workstation** | `short-window-local-detail-for-governed-app-flows` | `trusted-ui-visible-redacted-sharing-full-qname-disclosure-explicit` | Workstations keep enough local detail to explain brokered app flows, but support sharing should not quietly become browsing-history export. |
| **C general_os** | `bounded-local-detail-for-derived-workloads-adapter-gaps-explicit` | `explicit-redacted-export` | Derived/brokered workloads keep useful local DNS evidence, while compatibility adapters remain visible provenance gaps instead of pretending they inherit the full governed story. |
| **D appliance_factory** | `aggregate-only-or-absent-in-production-detailed-capture-in-approved-maintenance-or-incident-lanes` | `minimal-redacted-bundle-only` | Production/factory images avoid ambient namespace logging; detailed per-query DNS capture exists only when an approved maintenance/incident lane truly needs it. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of existing evidence/export/egress posture when DNS evidence is in play.

## What this fixes by profile

### A) Secure fleet host

Default: bounded full local detail, redacted export by default.

- Fleet operators need credible answers to *what hostname was resolved for this flow at that time?*
- That does justify local detailed DNS evidence in governed hostname lanes.
- It does **not** justify routine off-box export of raw namespace history.
- So A keeps detailed DNS receipts locally within bounded retention, while exported evidence defaults to deterministic redaction unless stronger incident/ticket scope approves full detail.

### B) Secure workstation

Default: short-window local detail, trusted-UI-visible redacted sharing.

- Workstations are where DNS evidence most easily turns into privacy-toxic browsing history.
- The archive still needs explainability for brokered app flows and support cases.
- So B keeps local short-window detail for governed flows, but the normal share/support path is redacted and recipient-visible in the trusted UI.
- Full qname disclosure is an explicit escalation, not an invisible support default.

### C) General-purpose OS

Default: bounded local detail for derived workloads, explicit redacted export.

- C needs practical local operability without assuming a vendor collector or permanent support backend.
- Derived/brokered workloads keep bounded local detail so governed hostname policy remains explainable.
- Explicit adapter fallback is allowed, but that fallback must remain visible as a provenance gap rather than silently inheriting the stronger brokered-DNS evidence claims.

### D) Appliance factory / regulatory

Default: aggregate-only or absent detail in production, detailed capture only in approved maintenance/incident lanes.

- D often runs offline, fixed-policy, or low-change service graphs where the privacy/regulatory cost of ambient detailed namespace logging is higher than the day-to-day value.
- Production images therefore avoid routine detailed per-query DNS retention by default.
- When a maintenance or incident workflow truly needs detailed DNS capture, it happens in an explicit approved lane with retained evidence and minimal/redacted export.

## Cross-profile invariants

Regardless of profile:

- hostname policy still requires broker-owned DNS resolution in the governed lane,
- `net-dns-query-receipt` is never a justification for ambient raw resolver access by workloads,
- any exported redacted DNS receipt should carry `redaction_transform_digest`,
- support bundles should prefer the smallest DNS detail that still explains the incident,
- and raw internal/split-horizon names should not leave the local evidence store by default.

## What remains open

This doc does **not** freeze:

- exact retention windows for flow vs DNS receipts,
- exact deterministic transform vocabulary for exported qnames,
- exact aggregate summary artifact shapes,
- or the exact promotion rules from normal flow evidence to richer DNS detail in learn/audit or incident workflows.

Those are future implementation/spec questions.
The product-shape default is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a subsystem expansion.
It accepts that DNS evidence is both useful and sensitive, then fixes a profile-shaped default that future specs can implement without quietly reinventing telemetry, packet-capture folklore, or hidden support logging.

Last updated: 2026-03-08r233
