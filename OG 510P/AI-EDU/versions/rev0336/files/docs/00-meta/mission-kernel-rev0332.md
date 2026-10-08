# Mission kernel — rev0332

The mission remains learner independence through better teacher/tutor judgment. The AI role is a
teacher-facing move coach: it may suggest a probing question, misconception check, or smallest-useful
hint after a learner attempt, while the human owner chooses, edits, or rejects every move.

## Current hot path

1. Find one real teacher/tutor owner.
2. Select one local instructional problem and concept.
3. Complete the owner plan, including tool/version, participation/fallback, protected local review,
   prompt-unchanged attestation, and a numeric small-cell threshold of at least three.
4. Keep the generated discovery card, coach prompt, checklist, measure card, and run sheet unchanged;
   regenerate the packet if the run definition changes.
5. Run at most one locally approved feasibility/usability cycle.
6. Record only aggregate rows, then stop for human owner review.
7. If a local result receipt is recorded, mask structured small cells, redact numeric/small-cell
   final-readout free text, and verify the owner-reviewed packet hashes still match.

## What rev0332 changes

Rev0331 plugged the final-readout narrative leak. Rev0332 plugs the next provenance leak: the packet
now refuses entry readiness if the generated run-definition files drift from `PACK-MANIFEST.json` or
if `COACH-PROMPT.md` no longer matches the prompt-card hash in `OWNER-PLAN.md`. The owner-review stop
record now hash-locks the discovery card, coach prompt, checklist, measure card, and run sheet, so a
later result receipt cannot silently summarize a different intervention than the one reviewed.

## Hard boundary

No educator has been contacted, no route has been accepted, no real cycle has run, no owner review
has occurred, no legitimate result exists, and `FT-0181` remains open.
