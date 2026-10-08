# Service lifecycle, deprecation, and archive-exit rules

A schema-valid AI service record is not a permanent permission slip. Evidence expires, workflows
change, models drift, staff capacity changes, and public claims can outlive the facts that once made
them acceptable.

The rule is: **a service must have an exit path before it becomes recurring infrastructure**.
Retirement, downgrade, teach-out, and public-claim removal are normal lifecycle states, not failures
to be hidden.

## Lifecycle states

| Code | Meaning | Default decision |
|---|---|---|
| `SLC0` | idea or intake only | No learner-facing use. |
| `SLC1` | sandbox with realistic or synthetic records | Example only; no effectiveness claim. |
| `SLC2` | limited pilot with local owner | Use only inside named conditions and stop triggers. |
| `SLC3` | recurring bounded service | Require evidence clocks, public summary, fallback, and renewal. |
| `SLC4` | scaled service | Require stronger evidence, sector adapters, incident review, and external watch. |
| `SLC5` | watch / repair | Freeze promotion, narrow claims, and add reviewer cadence. |
| `SLC6` | deprecate / teach out | Preserve learner-safe continuity while removing or replacing the service. |
| `SLC7` | archive-only residue | Keep minimal decision record; remove public active-service claims. |
| `SLCX` | stop / quarantine | Disable, preserve protected local evidence as required, and do not publicize details. |

Services should move backward as readily as forward. A service can return from `SLC5` to `SLC3`, but
only after the reason for watch is resolved and the public summary is corrected.

## Deprecation triggers

A recurring service should downgrade, pause, or retire when any of these appear:

- evidence expiry passes without renewal;
- model, prompt, retrieval corpus, tool permission, memory, or data flow changes the service beyond
  its change budget;
- public claims cannot be supported at their published evidence grade;
- teacher, support, security, or appeal burden exceeds the service record;
- fallback or non-AI path is unavailable when required;
- protected-route separation fails;
- incident review reveals hidden action authority or record-bearing effect;
- external standards, law, assessment guidance, or security risks invalidate a claim family.

## Public claim removal

Deprecation must update public-facing language, not merely disable an internal service flag. Remove
or revise claims when the claim family is no longer supported:

| Claim family | Remove or narrow when |
|---|---|
| learning | no durable learning or transfer evidence supports the claim; cognitive effort is weakened; construct shifts. |
| access | fallback, accessibility, or protected-route owner is missing. |
| workload | human review or repair burden exceeds the advertised saving. |
| safety/security | prompt injection, data disclosure, excessive agency, or incident recovery exceeds the stated posture. |
| validity/assessment | AI use changes the construct or proof route without a construct map update. |
| compliance | statutory, policy, or sector-adapter duty changes. |

When a service retires, public summaries may say that a pilot ended and name the ordinary alternative
route. They should not imply failure by the learner or reveal protected or security details.

## Lifecycle decision record

Lifecycle decisions live in `examples/service-lifecycle-decisions/`. A decision names the service
record, lifecycle state, evidence-expiry result, authority ceiling, public-summary action, continuity
plan, retirement triggers, decision-board reference, post-decision change ticket, live-window stop/rollback control, and next review.

`tools/check_service_lifecycle_decisions.py` verifies that the decision references a known service
record, uses a valid lifecycle state, names public-summary and continuity actions, requires a compact change ticket plus live-window control with no-expansion rule, stop triggers, rollback steps, evidence readouts, and public-claim freeze, and does not keep
an active public claim when the decision is retirement or quarantine.

## Link to the real-import gate

Real import should not only decide whether a schema field is useful. It should also decide whether a
service is eligible for recurring use, needs watch, should be retired, or should remain example-only.
A closure-ready `FT-0181` import should therefore have a lifecycle decision plus a post-decision change ticket, or an explicit reason
that lifecycle action is not yet possible. The ticket prevents a decision board from becoming an unbounded permission slip. The live-window control prevents the bounded ticket from drifting once real users, dates, data, tools, or public notices are involved.

## Current archive bet

Exit rules reduce hype pressure. A project that can deprecate services cleanly is more trustworthy
than one that only accumulates pilots, examples, and public claims.

See [`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
[`ft0181-post-decision-change-ticket.md`](ft0181-post-decision-change-ticket.md),
[`ft0181-live-window-stop-rollback-card.md`](ft0181-live-window-stop-rollback-card.md),
[`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md),
and `AS-0237`.
