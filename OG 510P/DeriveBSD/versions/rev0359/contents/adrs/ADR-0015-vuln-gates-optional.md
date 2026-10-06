# ADR-0015: Vulnerability intelligence + deploy gates are optional; policy-gated (proposed)

- Status: proposed
- Date: 2026-02-23

## Context

Vulnerability data is **useful** but it is not a trust root.
It is incomplete, noisy, and changes over time.

If DeriveBSD makes vulnerability gating a baseline requirement, we create avoidable failure modes:

- **Online dependency leaks into verification** ("can’t deploy because OSV is down")
- **Airgapped fleets become second-class**
- **False positives become outages** (inventory ≠ exploitability)
- **Unreplayable decisions** (a policy gate can’t be re-evaluated later if it depended on "latest" data)

At the same time, high-assurance environments *do* want policy to incorporate:
- known-exploited lists
- severity thresholds
- signed VEX statements ("not exploitable here")
- explicit risk acceptance with expiry

## Decision

Vulnerability intelligence is an **optional evidence lane** and any gate is **policy-controlled**.

1) **Baseline DeriveBSD does not require vulnerability feeds**
- A system must be able to evaluate, build, verify, and boot using locally available material.

2) **If vulnerability data is used, it must be snapshot-addressed**
- Feeds are ingested as content-addressed snapshots (`vuln.db.snapshot`).
- Policy binds to snapshot digests (not "latest").

3) **Inventory is not exploitability**
- If policy gates on vulnerabilities, it should accept VEX inputs (CycloneDX VEX or OpenVEX) to suppress noise.
- VEX is time-bounded and must be bound to the policy decision record digest.

4) **Gate results are receipts, not side effects**
- Deterministic query results are recorded (`vuln.query.receipt`).
- Gate outcomes are recorded (`vuln-gate-receipt`) and referenced by the policy decision record.

## Consequences

- Fleets can choose between:
  - no vulnerability lane
  - warnings only
  - hard gates for specific channels/targets

- Offline environments can satisfy vulnerability requirements by mirroring:
  - vulnerability DB snapshots
  - VEX statements (with explicit validity windows)

- The archive must provide:
  - a clear *data model* for snapshots, query receipts, and gate receipts
  - an override model (risk acceptance) with expiry + justification

## Notes / references

- FreeBSD ports vulnerabilities are documented in the VuXML database: https://vuxml.freebsd.org/
- OSV provides a cross-ecosystem vulnerability schema and API: https://google.github.io/osv.dev/api/
- CycloneDX supports VEX-shaped exploitability context: https://cyclonedx.org/capabilities/vex/
- OpenVEX is a minimal VEX format designed to embed cleanly in attestations: https://github.com/openvex/spec

