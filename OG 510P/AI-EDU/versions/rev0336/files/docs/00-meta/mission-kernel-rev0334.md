# Mission kernel — rev0334

The mission remains learner independence through better teacher/tutor judgment. The AI role is a
teacher-facing move coach: it may suggest a probing question, misconception check, or smallest-useful
hint after a learner attempt, while the human owner chooses, edits, or rejects every move.

## Current hot path

1. Find one real teacher/tutor owner.
2. Select one local instructional problem and concept.
3. Complete the owner plan, including tool/version, participation/fallback, protected local review,
   prompt-unchanged attestation, a numeric small-cell threshold of at least three, and an explicit
   event chronology rule.
4. Keep the generated discovery card, coach prompt, checklist, measure card, and run sheet unchanged;
   regenerate the packet if the run definition changes.
5. Run at most one locally approved feasibility/usability cycle.
6. Record only aggregate rows with ISO dates ordered baseline <= coach-use <= transfer.
7. Stop for human owner review dated on or after the latest session row.
8. If a local result receipt is recorded, mask structured small cells, redact numeric/small-cell
   final-readout free text, verify the owner-reviewed packet hashes still match, ensure the result
   date is on or after owner review, and follow only the bounded local decision map.

## What rev0334 changes

Rev0334 converts a result receipt into a safer operational stop. A completed result now carries a
`decision_followthrough` object: `retire` stops the local line, `repeat-narrower` and
`continue-bounded` require a fresh packet and cannot pool cycles as evidence, and
`escalate-to-pilot-review` requires a separate future gate rather than an automatic import or service
authority change.

## Hard boundary

No educator has been contacted, no route has been accepted, no real cycle has run, no owner review
has occurred, no legitimate result exists, and `FT-0181` remains open.
