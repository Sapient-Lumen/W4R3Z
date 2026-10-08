# rev0321 hot-path positive-branch burden audit

## Finding

Rev0320 eliminated one waste pattern: blank packets could no longer masquerade as completed work. But
it left another: checking the positive branch required hand-completing several local packet files. That
made the passing path less reproducible than the failing path.

## Correction

Rev0321 consolidates positive-branch rehearsal into `tools/seed_teacher_tutor_micro_pilot_dry_run.py`.
The utility is registered as a scratch/external operator aid, not a release-control validator. Its
outputs stay in scratch and are explicitly labeled synthetic.

## Waste avoided

The correction avoids a new governance branch, a new schema family, and a new evidence-status ladder.
It turns an operator rehearsal into a command and lets the readiness scorer distinguish real local
owner review from synthetic smoke.

## Remaining waste

The archive still has large governance and meta tails. They should be consulted only through the
indexes or after real evidence or a validator failure creates a concrete need.
