# ADR-0094: DNS receipt detail and export posture by profile

- Status: Accepted
- Date: 2026-03-08

## Context

`docs/459-outbound-network-posture-by-profile.md` already decided that hostname-based policy only counts when
resolution belongs to the brokered lane.
`docs/478-evidence-collection-posture-by-profile.md` and `docs/466-export-boundary-posture-by-profile.md`
already decided that evidence and export are profile-shaped.

One expensive ambiguity still remained open:
what is the default posture for **DNS evidence detail** across A–D?

If we keep full per-query DNS receipts everywhere, the archive quietly grows a privacy-toxic ambient browsing and namespace log.
If we never keep them, hostname policy and exfil explanation collapse back into folklore.

This needs a narrower answer than “telemetry” because the archive already decided that observability posture is composed from
`evidence`, `evidence_exports`, and `network_egress` rather than a separate profile key.
DNS receipt posture should follow that same rule.

## Decision

1. Keep `net-flow-receipt` as the normal exported explainability surface for governed egress.
   It answers *which subject talked to which address/port under which grant*.

2. Keep `net-dns-query-receipt` scoped to **broker-governed hostname resolution**.
   It is not an ambient whole-host DNS tap and it is not the default export artifact.

3. Make detailed DNS evidence **local-first and bounded** by default.
   Full qnames may exist locally for governed hostname lanes, but external sharing defaults to deterministic redaction,
   aggregation, or omission unless a stronger incident/maintenance lane explicitly approves full-name disclosure.

4. Fix the product-shape defaults as follows:
   - **A:** bounded full-detail local DNS receipts are normal for governed hostname lanes; external sharing defaults to redaction,
     and full qname export requires incident/ticket scope plus stronger approval.
   - **B:** short-window local detail is allowed for governed app flows; support/export defaults to recipient-visible redacted sharing,
     and full qname disclosure requires explicit trusted-UI expansion.
   - **C:** bounded local detail remains normal for derived/brokered workloads; external sharing stays explicit and redacted,
     while compatibility adapters remain visible provenance gaps rather than silently inheriting brokered DNS evidence promises.
   - **D:** production posture defaults to aggregate-only or absent per-query DNS retention; detailed per-query capture is reserved for approved
     maintenance/incident lanes, and external sharing remains minimal and redacted.

5. Treat split-horizon/internal names as sensitive by default.
   Off-box sharing must not leak raw internal names unless a stronger explicit lane approves that disclosure.

## Consequences

- The archive gets a real answer to the DNS-privacy vs explainability tradeoff without adding a new product-profile key.
- `docs/305-dns-mediation-and-hostname-binding.md` can stop treating DNS evidence posture as fully open.
- `docs/459-outbound-network-posture-by-profile.md` can treat DNS evidence defaults as a settled companion boundary.
- Future learn/audit work should build on this posture rather than assuming packet captures or ambient resolver logs.

## Why this is narrow enough

This ADR does **not** standardize:
- exact retention windows,
- exact redaction transform vocabulary,
- exact aggregate summary artifact shapes,
- or exact learn/audit mode promotion triggers.

It only fixes the product-shape default so future schemas and code have a coherent target.
