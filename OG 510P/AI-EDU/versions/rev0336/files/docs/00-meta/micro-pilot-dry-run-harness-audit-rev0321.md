# Micro-pilot dry-run harness audit rev0321

## Finding

The rev0320 hot path could produce a blank teacher/tutor packet and score it as `NOT_READY`, but the
positive path was still informal. The only known passing completed-packet readiness smoke was a
hand-built synthetic scratch packet recorded in the revision receipt. That was too fragile for the
next operator: the cube had a reliable negative gate but no repeatable rehearsal of a locally complete
aggregate readout.

## Risk

Without a repeatable dry run, the next agent or maintainer could spend time inspecting governance
tails or manually editing CSV rows instead of learning whether the packet, scoring rules, and owner
memo actually compose. Worse, a hand-built positive smoke can drift from the tool-generated packet and
let a real owner encounter errors that should have been caught locally.

## Refactor

Rev0321 adds `tools/seed_teacher_tutor_micro_pilot_dry_run.py` and `make micro-pilot-dry-run`. The
command requires the explicit confirmation token `synthetic-aggregate-dry-run-not-evidence`, writes
only under `scratch/` or outside the repository, refuses non-scratch repository paths, preserves a
local backup, and writes `DRY-RUN-TRACE.json`.

The readiness scorer now detects `DRY-RUN-TRACE.json`. A passing synthetic rehearsal returns
`SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`; a genuine completed local packet without that trace can still
return `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`.

## Substance gained

The first pedagogical path now has four executable states:

1. packet generated: `PREPARED_NOT_RUN` / `NOT_EVIDENCE`;
2. blank packet scored: `NOT_READY`;
3. synthetic aggregate rehearsal scored: `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`;
4. future real owner-completed packet scored: `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`.

That sequence is still not evidence, but it is real forward motion because it proves the operator path
can be rehearsed before asking a teacher/tutor owner to use it.

## Burden removed

The operator no longer has to hand-edit `OWNER-PLAN.md`, `SESSION-LOG.csv`, `FINAL-READOUT.csv`, and
`OWNER-DECISION-MEMO.md` just to verify the positive readiness branch. This trims the hot path without
adding a validator, schema, registry branch, or public-claim surface.

## Remaining blocker

The highest-risk unfinished work is unchanged: a human must send the bounded `FT-0181` owner request
or record a route block, and a real teacher/tutor owner must run a fresh packet before any local
readout can be considered for an evidence route.
