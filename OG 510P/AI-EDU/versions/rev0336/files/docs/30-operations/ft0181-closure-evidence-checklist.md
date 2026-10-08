# FT-0181 closure evidence checklist

This is the final pre-import checklist for the only live followthrough item. It lists the evidence
that must exist before `FT-0181` can move from queued to done.

The checklist is intentionally not closure-ready in rev0222. It names what is missing so a future
maintainer does not close the item by appealing to schema validity, examples, release audits, or
control coverage.

## Checklist states

| Code | Meaning |
|---|---|
| `CL0` | no checklist exists |
| `CL1` | closure evidence is prose-only |
| `CL2` | required evidence families are machine-readable |
| `CL3` | missing evidence and available pre-import controls are separated |
| `CL4` | all required evidence is present and closeout is eligible |
| `CLX` | checklist contradicts queue state or permits fake closure |

## Required closure evidence

`FT-0181` closure requires all of the following:

1. minimized `SRC2+` real pilot packet with owner review;
2. source data dictionary and import map;
3. real import-readiness manifest marked closure-ready;
4. acceptance/calibration packet with reviewer role separation;
5. public-summary render checks using the relevant redaction profile;
6. service lifecycle decision;
7. decision-delta log showing which fields changed decisions and which were pruned;
8. post-decision change ticket with allowed/prohibited changes, rollback owner, rollback triggers, and public claim ceiling;
9. closeout-board minutes;
10. signoff quorum with no unresolved conflicts;
11. control-coverage review against the actual import;
12. release audit and assurance case updated after the import;
13. no active waiver bypassing non-waivable controls.

## Current status

rev0235 remains `CL3`: pre-import controls are strong, but required real evidence is missing. The
correct action is to run the first pilot sprint, request the minimum real data packet, fill the first-packet decision board, write the post-decision change ticket, and refuse
raw/protected overcollection, not to close the queue.

See `docs/30-operations/ft0181-first-pilot-sprint-execution-pack.md`,
`examples/closure-checklists/no-real-data-ft0181-closure-checklist.json`, and
`tools/check_ft0181_closure_checklists.py`.


## Rev0237 post-readout dispatch requirement

Closure evidence now includes a real post-readout action dispatch and due-date recheck after the end-of-window readout.
The dispatch must be tied to a real `LWR-...` readout, name the owner action, allowed/prohibited next
actions, next evidence ask, fields to re-ask, fields to drop, public-language action, and recheck
date. A blocked `SRC0` dispatch is useful rehearsal only and does not close `FT-0181`.
