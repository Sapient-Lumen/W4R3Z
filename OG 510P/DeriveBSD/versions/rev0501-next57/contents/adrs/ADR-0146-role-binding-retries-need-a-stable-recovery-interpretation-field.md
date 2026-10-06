# ADR-0146: Role-binding retries need a stable recovery interpretation field

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/216-incident-snapshots-and-support-bundles.md`

## Context

ADR-0144 made `policy-consumed` denials point at the earlier successful consuming event through `consumed_by_event_id`.
ADR-0145 then fixed when that denial may collapse to **already-applied**: only when the joined consuming success proves the same exact mutation tuple.

That leaves one more practical ambiguity.
The archive can already derive the right retry story, but it still leaves client UIs, support bundles, and exports to recompute that interpretation from raw event joins.
If implementations expose that summary differently, operability drifts even when the underlying evidence agrees.

## Decision

For remembered-role non-interactive `policy-consumed` denials:

- `intent.role.binding.event` now carries `recovery_interpretation`
- the field is **evidence-only** and does not override `action = write-denied` or `reason_code = policy-consumed`
- allowed values are:
  - `policy-consumed` — no exact-match recovery collapse was proven
  - `already-applied` — the denial joined a consuming success that matched the same exact mutation tuple
- `recovery_interpretation` is required whenever `reason_code = policy-consumed`
- `already-applied` is allowed only when `consumed_by_event_id` resolves and the consuming success matches the exact tuple from ADR-0145

## Consequences

- support bundles and deterministic exports can show a stable one-line recovery story without changing the durable denial reason
- client/reconcile/admin tooling can query one field instead of re-deriving the interpretation from notes or ad-hoc logic
- the archive stays small: no new event action, no new receipt family, and no generic transaction subsystem
- the underlying evidence contract stays intact because `policy-consumed` plus the consuming-event join remains the authoritative basis

## Not decided here

- a generic derived-outcome field for every mutable subsystem
- cross-replica result synthesis beyond the existing consuming-event join
- whether future UIs collapse `policy-consumed` + `already-applied` visually by default or only on demand
- any broader idempotency-token family

## Follow-ups

- add `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` as the implementer-facing rule
- tighten `spec/intent.role.binding.event.schema.json` and `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- update the canonical policy-window denial example to carry `recovery_interpretation = already-applied`
- wire the rule through support/evidence/risk/runbook/discovery surfaces
- guard the rule with `tools/check_role_binding_policy_recovery_interpretation_contract.py`
