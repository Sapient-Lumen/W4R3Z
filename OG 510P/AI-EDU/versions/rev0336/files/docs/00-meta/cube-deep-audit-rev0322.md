# rev0322 deep audit

## Audit finding

The cube's central execution risk remains the last inch between preparation and a real owner-reviewed
result. Rev0321 made the synthetic positive branch repeatable, but the state machine was still spread
across packet generation, readiness scoring, dry-run seeding, and human memory. That is a practical
risk: a maintainer can spend the session deciding which already-documented command comes next.

## Substantive repair in this revision

rev0322 adds `tools/decide_teacher_tutor_micro_pilot_next_action.py` and the `make micro-pilot-next`
target. The router reads the packet directory, calls the readiness scorer when a packet exists, and
emits one next action:

- prepare the packet;
- complete local aggregate fields or optionally dry-run;
- discard and regenerate a synthetic packet;
- stop for local owner review without evidence import;
- stop on unknown state.

When `WRITE=1` is set, it writes a scratch-only `MICRO-PILOT-NEXT-ACTION` JSON/Markdown pair. If the
packet is missing, it writes to a scratch next-action directory instead of failing into a manual search.

## What this fixes

Before rev0322, the operator had to inspect a readiness scorecard and remember the safe command chain.
The router removes that inspection burden without adding a validator, schema, branch family, public
claim, or service-authority surface.

## What it does not fix

The cube still does not contain real owner evidence or a real micro-pilot result. The router is not an
evidence route, outcome evaluator, custody record, service authorization, public summary, or closure
mechanism. A dry-run packet must still be deleted or replaced before any real teacher/tutor cycle.

## Audit/refactor note

The audited burden in this pass is hot-path state-selection burden. The correction moves state
selection into one small utility and demotes manual startup inspection. No release-control validator
was added because the control plane is already saturated and the uncovered risk is execution, not
schema conformance.

## Next correction over time

After one real owner packet or one real scored micro-pilot readout, delete or cold-park any surface
that did not change an owner decision, block a concrete harm, or shorten execution. Do not replace
deleted surfaces with equivalent doctrine under new names.
