# Cube deep audit — rev0329

## Finding: entry readiness was still contaminated by post-cycle work

Rev0327 correctly introduced `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`. Rev0328 correctly made discovery
first. But the generated owner plan still contained this kind of field: post-cycle attestation after
the cycle. The readiness scorer scans owner-plan placeholders as an entry check. That meant the entry
gate could require a thing that cannot honestly exist until after the cycle.

This is a severe field-execution bug because it punishes the exact behavior the project wants: stop
before learner-facing use, complete the local plan, and then run one bounded cycle. The workaround
would have been to fill a post-cycle-looking field early or add more process. Both are bad.

## Correction

The owner plan now asks for a pre-cycle local attestation route only. The post-cycle decision remains
in `OWNER-DECISION-MEMO.md`, which is part of the post-cycle/owner-review path. The scratch packet now
also contains `CYCLE-RUN-SHEET.md`, and the scorer treats its presence as an entry file check.

## Refactor value

This is not a new control family. It is a boundary correction inside an existing hot-path toolchain:
prepare packet, score readiness, route next action, and hand off the field packet. It removes a false
dependency and gives the human operator one concrete cycle script.

## Remaining highest risks

1. No real teacher/tutor has selected a problem.
2. No accountable local owner has approved participation, fallback, privacy threshold, or protected
   local review.
3. No cycle has run, so there is no aggregate post-cycle record.
4. The cube still contains a large historical control tail that should not be opened before the hot
   path unless a real field event or validator failure requires it.

## Audit result

The archive now better distinguishes three states: prepared but not ready, entry-ready for exactly one
cycle, and post-cycle owner-review-ready. It still has zero field evidence.
