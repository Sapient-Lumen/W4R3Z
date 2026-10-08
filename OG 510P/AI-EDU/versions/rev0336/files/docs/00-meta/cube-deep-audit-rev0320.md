# rev0320 deep audit

## Audit finding

The cube's central execution risk is now the last inch between preparation and a real owner-reviewed
result. The owner rail can prepare and route a bounded request. The teacher/tutor rail can prepare a
concrete equality-one-step packet. The remaining failure mode is that humans do not send, block, run,
attest, or decide, while the archive keeps making more well-formed surfaces.

## Substantive repair in this revision

rev0320 adds `tools/score_teacher_tutor_micro_pilot_readiness.py` and the `make micro-pilot-readiness`
target. The tool reads only scratch/external packets and writes a scratch-local scorecard when asked.
It checks the packet manifest, owner plan, aggregate session log, final eight-row readout, raw-data
markers, stop-trigger counts, and owner decision memo.

A newly generated blank packet should fail as `NOT_READY`; that failure is useful. It prevents the
archive from counting packet generation as a run. A locally completed aggregate packet can advance to
`READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`, which still carries no public claim or evidence import.

## What this fixes

Before rev0320, the first teacher/tutor packet could be prepared but the operator still had to manually
decide whether the local plan, session rows, final readout, and owner decision were actually ready for
review. That manual seam invites delay and doctrinal drift. The readiness gate turns that seam into a
small executable check with explicit next actions.

## What it does not fix

The cube still does not contain real owner evidence or a real micro-pilot result. The scorecard is not
a data-acceptance tool, evaluator, public summary, custody record, service authorization, or closure
mechanism. It cannot invent a run and should report `NOT_READY` for blank generated packets.

## Audit/refactor note

The audited burden in this pass is hot-path inspection burden. Instead of asking maintainers to read
the run card, measure card, session log, readout template, decision memo, and claim boundary manually
after every local packet, rev0320 provides one command that surfaces the missing execution steps. The
large governance and branch tails remain cold retrieval.

## Next correction over time

After one real owner packet or one real scored micro-pilot readout, delete or cold-park any surface
that did not change an owner decision, block a concrete harm, or shorten execution. Do not replace
deleted surfaces with equivalent doctrine under new names.
