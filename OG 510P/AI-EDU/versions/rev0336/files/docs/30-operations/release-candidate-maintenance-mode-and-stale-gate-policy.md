# Release-candidate maintenance mode and stale-gate policy

## Purpose

A ready-but-not-closed release can age. If no real `SRC2+` pilot packet arrives, the archive should not keep claiming the same release candidate indefinitely without checking whether external evidence, schemas, validators, public summaries, and open gates have gone stale.

This surface defines the maintenance state for `FT-0181` while the archive waits for real data.

## Maintenance states

| State | Meaning | Allowed claim |
|---|---|---|
| `MM0` | not in maintenance | ordinary active development |
| `MM1` | fresh ready-but-not-closed | pre-import controls are current |
| `MM2` | watched | external evidence or validators near review date |
| `MM3` | stale-gated | no closure or public expansion until refresh passes |
| `MM4` | suspended | release candidate must be downgraded or replaced |
| `MMX` | inconsistent | maintenance record conflicts with queue or receipt |

rev0223 places the external-data gate in `MM1`: fresh maintenance mode. The next maintainer should refresh the maintenance record when any of these occur:

- an `SRC2+` real pilot packet arrives;
- a watched external source becomes stale or materially changes;
- a validator, schema, or service-record field changes;
- public summaries are edited;
- a policy exception is requested;
- the release is being used to support an implementation decision.

## Stale-gate defaults

- If the evidence-refresh calendar is stale, public claims must downgrade before packaging.
- If the synthetic-example declaration does not cover all examples, release must block.
- If a real-data request is older than the local request window, request status becomes stale; that does not close or fail `FT-0181`, but it prevents claims that a real import is imminent.
- If a validator cannot run, the release candidate is `MM3` or worse until the failure is explained.
- If real evidence arrives but cannot be traced through source dictionary, acceptance, redaction, decision delta, lifecycle, closeout, quorum, audit, and assurance, `FT-0181` remains live.

## Maintainer cadence

A maintainer should perform a lightweight maintenance review before any new package and a deeper review before any real-data import. The review should update the release candidate, audit manifest, synthetic declaration, control saturation record, maintenance record, evidence refresh calendar, and assurance case.

Related: [`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md), [`evidence-refresh-calendar-and-staleness-gates.md`](evidence-refresh-calendar-and-staleness-gates.md), [`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md).
