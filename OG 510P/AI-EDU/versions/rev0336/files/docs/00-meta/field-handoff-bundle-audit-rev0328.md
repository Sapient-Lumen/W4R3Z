# rev0328 field handoff bundle audit

## Finding

The field handoff bundle was compact but still ordered the secondary owner-evidence rail before the
primary teacher/tutor feasibility rail. That ordering was wasteful because the project’s riskiest
missing object is not another owner-evidence artifact; it is a real educator conversation that selects
a local instructional problem.

## Change

`tools/prepare_field_handoff_bundle.py` now writes `FIELD-HANDOFF.md` with the teacher/tutor discovery
rail first. `tools/prepare_teacher_tutor_micro_pilot_pack.py` now generates
`DISCOVERY-FIRST-CONTACT.md` beside the owner plan, run checklist, measure card, coach prompt, session
log, final readout, and owner decision memo.

The generated discovery card is intentionally small. It asks for one 15-minute conversation and the
minimum answers needed before readiness can pass. It does not collect names, raw work, protected facts,
small cells, screenshots, transcripts, gradebook rows, or credentials.

## Waste corrected

The bundle no longer asks the operator to inspect the administrative rail before the pedagogical rail.
That reduces context switching and makes “ask a teacher/tutor” the obvious first action.

## Remaining waste

Many historical audit and governance surfaces remain in the archive. They are indexed for traceability,
but they should not be opened during the hot path. Future revisions should delete, merge, or cold-park
inactive tails when a safe compression route exists.

## Boundary

The bundle remains scratch-local preparation. It creates no evidence, service authority, custody,
public claim support, real pilot, `SRC2+` packet, or `FT-0181` closure.
