# Mission kernel — rev0331

The mission remains learner independence through better teacher/tutor judgment. The AI role is a
teacher-facing move coach: it may suggest a probing question, misconception check, or
smallest-useful hint after a learner attempt, while the human owner chooses, edits, or rejects every
move.

## Current hot path

1. Find one real teacher/tutor owner.
2. Select one local instructional problem and concept.
3. Complete the owner plan, including tool/version, participation/fallback, protected local review,
   and a numeric small-cell threshold of at least three.
4. Run at most one locally approved feasibility/usability cycle.
5. Record only aggregate rows, then stop for human owner review.
6. If a local result receipt is recorded, mask structured small cells and redact numeric/small-cell
   final-readout free text before the receipt travels.

## What rev0331 changes

Rev0330 made structured result rows suppression-aware. Rev0331 plugs the narrative readout leak: the
result receipt no longer copies final-readout numeric free text that could reveal tiny local cells.
The receipt can support only a local stop, redesign, narrower repeat, or separate future review
planning decision.

## Hard boundary

No educator has been contacted, no route has been accepted, no real cycle has run, no owner review
has occurred, no legitimate result exists, and `FT-0181` remains open.
