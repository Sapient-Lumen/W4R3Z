# FT-0181 live-window stop and rollback card

Use this only after the first-packet decision board and post-decision change ticket. The change ticket says what may change. This card says how the first live window stays small, how it stops, and how the owner rolls back without waiting for another archive pass.

The card exists because the riskiest drift now happens after a bounded ticket: a maintainer can keep the public claim ceiling intact on paper while users, date ranges, prompts, notices, or evidence reads expand in practice.

## Executable local card gate

The live-window recorder is scratch-only. Do not create a live-window
card by editing release docs or examples. After a valid `active_change` post-decision change ticket, rerun the router. rev0298 first emits `make owner-activation-live-window-brief ...`; execute that bridge, rerun the router, and then execute only the emitted `make owner-live-window-card ...` command. A ready-for-real-packet ticket must stop at the activation-entry brief until a valid same-source activation receipt exists. Example:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-post-decision-ticket
# execute only the emitted make owner-activation-live-window-brief ... command
# then rerun and execute only the emitted make owner-live-window-card ... command
```

The recorder writes `scratch/.../live-window-card.json` plus a local summary. The
card stores only source-ticket hash, window state, count classes, no-expansion,
human-pause, fallback-route controls, and route boundaries. It is `NOT_ACCEPTED`,
`not_evidence`, and cannot modify service records, lifecycle state, custody,
public summaries, or closure.

## Entry rule

Open a live-window card only when all of these facts are available:

| Required fact | Minimum answer |
|---|---|
| source truth | guarded `active_change` ticket sourced from a valid activation receipt, or a blocked no-real-packet rehearsal |
| decision board | authority, evidence, construct, public-summary, protected/security, and lifecycle slices completed |
| change ticket | `active_change` only after activation receipt; allowed/prohibited changes, rollback owner, triggers, claim ceiling, and closure boundary named |
| service scope | one service, one owner path, one short date range, one source system, and no raw learner trace transfer |
| human coverage | classroom/service owner and record owner can pause or roll back without vendor permission |

If any fact is missing, the live-window state is `blocked_no_real_packet` or `blocked_incomplete_ticket`. Do not start, expand, or publicly claim a live pilot from that state.

## Card fields

| Field | Required answer |
|---|---|
| window id | `LWC-...` tied to the change ticket |
| service | one service only; default `AIEDU-SR-003`, fallback `AIEDU-SR-001`, reserved `AIEDU-SR-004` only with aggregate no-trace evidence |
| window state | `blocked_no_real_packet`, `blocked_incomplete_ticket`, `staged`, `active`, `paused`, `rolled_back`, `completed_no_closure`, or `quarantined` |
| window scope | named users/cohort, date range, source system, owner path, and no-expansion rule |
| allowed during window | exact service or public-summary behavior allowed during the window |
| prohibited during window | new users, new data classes, new tools/writes, stronger claims, raw traces, protected facts, security payloads, or schema expansion unless the ticket already allowed them |
| stop triggers | events that pause or roll back immediately |
| rollback owner | role/person who can reverse the change without waiting for a committee |
| rollback steps | concrete steps to return to the prior sandbox/fallback state |
| evidence readouts | the few aggregate signals to read at the end of the window |
| public claim freeze | maximum language while the window is running |

## Default no-real-data card

Until a real `SRC2+` owner packet exists, the only valid card for the first-contact reminder workflow is a blocked rehearsal:

```text
Window state: blocked_no_real_packet
Allowed during window: no live expansion; only rehearse packet review and rollback steps.
Prohibited during window: no new users, no raw learner traces, no protected-route transfer, no public outcome claim, no schema expansion.
Stop triggers: any request for raw learner work, small cells, protected facts, security payloads, or final-answer behavior.
Rollback owner: record owner plus teacher-of-record reviewer.
Rollback steps: keep service at sandbox/example-only; use ordinary practice sheets and teacher hints.
Evidence readouts: none from real learners; only rehearsal gaps and field-survival notes.
Public claim freeze: example-only, no outcome claim.
Closure boundary: does not close FT-0181.
```

## Stop triggers for the first real window

Use these as defaults for `AIEDU-SR-003` unless the real owner packet justifies a stricter threshold.

| Trigger | Immediate action |
|---|---|
| workflow sends, writes, or triggers penalties without human review | pause tool, preserve aggregate incident note, return to ordinary staff reminders |
| reminder status can be inferred at named-student level outside the owner route | disable the affected prompt/workflow path |
| staff review burden exceeds the named window budget | pause expansion and either add coverage or narrow the service |
| fallback route is unavailable or penalized | pause required use and restore non-AI route |
| protected/support fact is needed to interpret the packet | keep local or quarantine; do not normalize into examples |
| small-cell or identifiable subgroup signal appears | suppress or aggregate before any review artifact leaves the owner route |
| security/tool boundary changes or raw payload is needed | pause and route to security owner with abstracted class labels only |
| public summary would exceed ticket ceiling | suppress public language and repair the claim record before continuing |

## Evidence readouts

The first window should end with a short readout, not a new study design. Read only what can change the next decision:

- whether eligible reminders were drafted only after the owner-defined condition;
- whether staff-reviewed samples show correct draft/discard/fallback/correction behavior;
- aggregate fallback, opt-out, correction, pause, or stop-trigger counts above local privacy thresholds;
- staff review, correction, and escalation minutes separated from preparation minutes;
- whether the public/staff notice and non-AI/manual route were actually available;
- whether any field requested for the packet was trimmed because it did not change a decision.

Do not convert usage volume, satisfaction, or preparation speed into learning, safety, access, compliance, or workload claims without the claim-family evidence ladder and reviewer agreement.

## No-expansion rule

No new cohort, date range, source system, tool permission, memory, public claim, schema field, or vendor-written outcome language may be added during the first live window unless the post-decision change ticket explicitly allowed it and the rollback owner can reverse it.

If the window ends cleanly, the default card outcome is `completed_no_closure`, not closure. In rev0288 the next required executable steps are the router-emitted `make owner-live-window-readout ...` command and then `make owner-post-readout-action ...`; together they write bounded scratch artifacts before any service-record, lifecycle, public-language, custody, acceptance, or closure step may open. The prose gate in [`ft0181-end-of-window-readout-disposition-gate.md`](ft0181-end-of-window-readout-disposition-gate.md) explains the disposition logic, but the local artifact is the firebreak. `FT-0181` still needs acceptance, decision delta, public render, lifecycle decision, closeout minutes, signoff, control coverage, assurance update, and a closure-ready checklist.

## Copyable card

```text
Window ID:
Service:
Post-decision ticket reference:
Window state:
Window scope:
No-expansion rule:
Allowed during window:
Prohibited during window:
Stop triggers:
Rollback owner:
Rollback steps:
Evidence readouts:
Public claim freeze:
End-of-window disposition:
Reason FT-0181 remains live or closure-ready:
```

## Closure boundary

A live-window card can pause, roll back, complete a bounded window, or prove that a change should not expand. It must hand any paused, rolled-back, or completed window to the end-of-window readout gate before lifecycle, public-summary, or closeout language changes. It cannot make synthetic examples real, cannot prove outcome claims by itself, cannot substitute for source custody, and cannot close `FT-0181` without the full real-import closeout path.
