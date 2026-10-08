# rev0321 deep audit

## Audit finding

The cube's central execution risk remains the last inch between preparation and a real owner-reviewed
result. Rev0320 could prove that a blank teacher/tutor packet fails readiness, but its positive path
still depended on a hand-built synthetic scratch packet. That made the completed-run branch less
repeatable than the negative branch.

## Substantive repair in this revision

rev0321 adds `tools/seed_teacher_tutor_micro_pilot_dry_run.py` and the `make micro-pilot-dry-run`
target. The tool fills a scratch/external teacher/tutor packet with synthetic aggregate values,
records `DRY-RUN-TRACE.json`, and preserves a local backup. It requires the confirmation token
`synthetic-aggregate-dry-run-not-evidence` and refuses non-scratch repository paths.

The readiness scorer now distinguishes a real locally completed packet from a synthetic rehearsal. A
passing dry run returns `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`; a future fresh owner-completed packet can
still return `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`.

## What this fixes

Before rev0321, the operator could verify form generation and the `NOT_READY` failure mode, but had to
manually edit several files to smoke-test the passing path. That manual seam is wasteful and brittle.
The dry-run harness makes the positive branch executable without creating evidence or expanding the
release-control plane.

## What it does not fix

The cube still does not contain real owner evidence or a real micro-pilot result. The dry-run harness
is not a data-acceptance tool, evaluator, public summary, custody record, service authorization, or
closure mechanism. A dry-run packet must be deleted or replaced before any real teacher/tutor cycle.

## Audit/refactor note

The audited burden in this pass is hot-path positive-branch burden. Instead of asking maintainers to
hand-complete `OWNER-PLAN.md`, `SESSION-LOG.csv`, `FINAL-READOUT.csv`, and `OWNER-DECISION-MEMO.md` to
verify the completed-packet branch, rev0321 provides one explicit rehearsal command. No new schema,
validator, registry branch, or claim ladder was added.

## Next correction over time

After one real owner packet or one real scored micro-pilot readout, delete or cold-park any surface
that did not change an owner decision, block a concrete harm, or shorten execution. Do not replace
deleted surfaces with equivalent doctrine under new names.
