# Teacher/tutor feasibility dry-run harness

The dry-run harness fills a fresh scratch packet with synthetic aggregate values so operators can
exercise the positive readiness path without pretending a real educator or learner participated.

## Sequence

```bash
make field-handoff-bundle OVERWRITE=1
make micro-pilot-dry-run \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  CONFIRM=synthetic-aggregate-dry-run-not-evidence \
  DECISION=repeat-narrower \
  OVERWRITE=1
make micro-pilot-next \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  WRITE=1
```

A coherent rehearsal should produce `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE` and route to
`DISCARD_SYNTHETIC_AND_REGENERATE`. Delete or regenerate the packet before any real local work.
Owner-review and result recorders must refuse a packet containing `DRY-RUN-TRACE.json`.

The harness writes synthetic owner-plan, session-log, final-readout, decision-memo, trace, and backup
files under scratch. Release packaging excludes scratch.

## Boundary

The harness proves only that the packet and checks can execute on synthetic values. It runs no real
cycle, estimates no efficacy, accepts no evidence, authorizes no service, supports no public claim,
and does not close `FT-0181`.

## rev0336 synthetic follow-through seed

The synthetic dry-run harness fills a synthetic follow-through seed so the readiness gate can rehearse the new post-cycle check. The trace remains `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`; it must be discarded before real owner work.
