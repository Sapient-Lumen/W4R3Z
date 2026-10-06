# ADR-0017: pf anchors are the unit of VM firewall policy (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD uses pf anchors as the primary unit of per-instance firewall policy, with deterministic naming and rule digest auditing.

## Consequences
- stable root ruleset with Derive-managed attachment points
- per-instance lifecycle is auditable and testable
