# rev0326 field handoff bundle audit

## Defect found

Rev0325's preferred handoff lived under `scratch/field-handoff/rev0325/...`, while several active
operations documents and tool defaults still pointed to
`scratch/pedagogy/teacher-tutor-micro-pilot/...`. The release suite passed because no check compared
human-copyable startup commands with the actual generator default.

## Repair

- `micro-pilot-pack`, readiness, and next-action defaults now share the revisioned field-handoff root.
- The default packet is `teacher-selected-concept` and requires local discovery.
- Active operation docs use the same paths.
- The existing re-entry validator rejects the obsolete scratch path in active docs and micro-pilot
  tools.
- The bundle remains scratch-only and excluded from release packaging.

## Method repair

The packet now identifies itself as feasibility/usability only, captures intervention version and
learner participation fields, and treats transfer as descriptive rather than a causal effect.

## Boundary

A repaired handoff is still not a field event or evidence.
