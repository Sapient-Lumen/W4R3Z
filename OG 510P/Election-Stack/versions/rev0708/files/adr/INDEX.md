# ADR index (decision registry)

**Track:** Shared (cross-cutting)


This file is the **single, stable decision register** for this archive.

Rules:
- Keep this small. Prefer **one paragraph** per ADR.
- If a decision changes **claims, trust assumptions, or external interfaces**, record an ADR.
- If an ADR changes any schema or verifier-visible behavior, update:
  - `docs/153-open-decisions-and-freeze-plan.md`
  - `artifacts/claims/claim-evidence-matrix.csv` (if a claim is impacted)
  - release notes (`CHANGELOG.md`)

See also:
- Change protocol: `docs/150-maintainer-bootstrap-and-change-protocol.md`
- ADR + claims posture: `docs/152-adr-process-claims-and-evidence.md`

## ADR list

| ADR | Title | Status | Notes |
|---:|---|---|---|
| 0001 | Adopt ADRs and change control | Accepted | Establishes decision recording + review discipline. |
| 0002 | Public communications as evidence via PublicNotice | Accepted | Canonical comms surface: PublicNotice + channel registry + explicit corrections. |
| 0003 | Institutional volatility as a first-class risk (Track A threat surface) | Accepted | Names certification/ecosystem compromise explicitly; binds dependence to evidence without expanding claims. |
| 0004 | ResultsReleasePackage signed via EvidenceEnvelope (avoid signature layering) | Accepted | Makes RRP publication single-path: envelope signatures + PBB leaf commits to payload digest. |

## Open decisions (non-ADR)

This is not a substitute for ADRs. It is a pointer set for “things we know are unresolved.”

- See: `docs/153-open-decisions-and-freeze-plan.md`
