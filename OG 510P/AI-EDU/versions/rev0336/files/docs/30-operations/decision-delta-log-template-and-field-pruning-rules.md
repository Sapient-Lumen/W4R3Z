# Decision-delta log template and field-pruning rules

Real pilot imports should make the service-record schema sharper, not larger by default. A
`decision-delta` log records which imported facts changed an approval, pause, redaction, authority,
renewal, or retirement decision. The post-decision change ticket turns those deltas into a bounded allowed-change/prohibited-change and rollback record before any service, public, lifecycle, schema, or closure update. If that change reaches a live window, the stop/rollback card names the no-expansion rule and end-of-window readouts.

If a field never changes a decision, never prevents overclaiming, never protects a learner, and
never clarifies ownership, it is a candidate for trimming.

## Delta classes

| Code | Meaning | Default action |
|---|---|---|
| `DD0` | Descriptive only; did not affect decision | Do not promote to required schema field. |
| `DD1` | Clarified owner, route, or contact | Keep if it prevents orphan handoff. |
| `DD2` | Changed action-authority ceiling or rollback | Keep; may require schema or validator change. |
| `DD3` | Changed memory, retention, or protected-record treatment | Keep; review for public redaction. |
| `DD4` | Changed evidence grade, expiry, or public claim | Keep; update public summary and renewal clock. |
| `DD5` | Changed construct/proof, disclosure, or cognitive-effort posture | Keep; update assessment crosswalk. |
| `DD6` | Revealed protected leakage, unsafe source, or security risk | Quarantine or stop; do not normalize raw detail. |

## Required log fields

For each real import candidate, write a compact table with these columns:

| Field | Required content |
|---|---|
| source field | Local source field or packet section after minimization. |
| target field | Candidate AI-EDU service-record field. |
| delta class | `DD0-DD6`. |
| decision changed? | Yes/no plus the affected decision. |
| public effect | Whether a public claim, redaction profile, or sector adapter changed. |
| protected/security handling | Whether detail was kept local, abstracted, or quarantined. |
| disposition | keep, trim, add validator, revise schema, quarantine, or write/change a post-decision ticket. |

## Post-decision ticket rule

Before changing public summary, lifecycle state, service-record authority, schema requirements, or closeout posture, write the compact ticket in [`ft0181-post-decision-change-ticket.md`](ft0181-post-decision-change-ticket.md). A decision delta without a ticket can justify trimming or further owner questions, but not broader claims.

## Schema-change rule

Add a schema field only if the delta shows one of these effects:

- hidden action authority became visible;
- protected-route leakage was prevented;
- an evidence claim was narrowed, expired, or removed from public summary;
- a learner-safe continuity route changed;
- a human owner, rollback path, or appeal route became identifiable;
- a security/tool-boundary risk changed the service decision.

Do not add schema fields merely because the local export contains them.

## Trim rule

A field should be removed from examples, templates, or future schema proposals when all are true:

1. it maps to `DD0` in at least two realistic or real records;
2. no sector adapter requires it;
3. no redaction profile needs it;
4. no stop trigger, rollback, appeal, evidence expiry, or protected-route decision uses it;
5. it increases import burden or public confusion.

## Minimal decision-delta note

```text
Import candidate:
Source truth class:
Record owner:
Date reviewed:

Decision before import:
Decision after import:
Changed decision fields:
Fields trimmed or kept local:
Public summary changes:
Lifecycle decision effect:
Protected/security exclusions:
Schema/validator changes proposed:
Post-decision change ticket:
Live-window stop/rollback card:
Reason FT-0181 can or cannot close:
```

## Current archive bet

The first real import should decide what to delete as much as what to add. Maximal records often
look safer, but they can hide the few fields that actually protect learners and teachers.

See [`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
[`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md),
[`service-record-backtest-results-and-field-trim.md`](service-record-backtest-results-and-field-trim.md),
and `AS-0228`.


## Rev0236 readout delta

After a live window, decision deltas must separate window disposition from claim strength. Usage, satisfaction, or clean operation can support a bounded process decision only when reviewers explain why learning, access, safety, workload, compliance, or scale claims remain unmade or unchanged.
