# AI-EDU datacube

This archive is optimized for one narrow field move: help a teacher/tutor decide whether a teacher-facing move coach is locally usable for one selected concept, while protecting learner independence and preventing internal paperwork from becoming a fake outcome.

## Current revision

`rev0336` closes the next execution gap in the teacher/tutor hot path. Rev0335 made repeat/continue decisions require a local follow-through seed; rev0336 makes the next fresh packet executable through a source-result hash link instead of a generic repeat command.

## Hot path

```bash
make field-handoff-bundle OVERWRITE=1
make micro-pilot-readiness PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
make micro-pilot-next PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
```

Open the generated discovery card, owner plan, cycle run sheet, and decision memo. The owner-evidence/FT-0181 rail remains live but secondary until there is a real owner route or returned owner packet.

The secondary owner-field rail is only for the unresolved `FT-0181` route, not for local pilot claims or a real pilot shortcut. Keep it explicit and router-first when owner material arrives:

```bash
make owner-field-work OVERWRITE=1
make owner-field-report OVERWRITE=1
make owner-field-next csv=/path/to/real-owner-return.csv OVERWRITE=1
```

## Run, result, and follow-through boundary

A local cycle may proceed only when the packet has a completed owner plan, a usable small-cell threshold, stable generated run-definition files, and no raw/protected payload. A local result receipt is descriptive and suppression-aware. It masks structured counts/rates below the owner threshold and redacts numeric/small-cell-sensitive final-readout free text.

After a non-retire result, repeat/continue work must use:

```bash
make micro-pilot-followthrough-pack SOURCE_RESULT=scratch/.../MICRO-PILOT-RESULT.json CONFIRM=source-result-read-for-local-followthrough-not-evidence ...
```

The fresh packet records only a source result hash link and non-evidence boundary. It does not copy the owner seed text or previous local observations, and it cannot pool cycles, infer trend/effect, update service authority, support public claims, or close `FT-0181`.

## Non-claims

This archive has not contacted an educator, run a cycle, accepted `SRC2+` evidence, recorded owner review, recorded a legitimate result, proven learning/workload/access/safety/fairness benefit, updated service authority, or closed `FT-0181`.

## Evidence-grade and real import boundary

The evidence grade remains local judgment only. Any real import must use a separate accepted evidence route and cannot be inferred from a generated packet, run sheet, readiness score, synthetic dry run, owner-review stop, hash-locked run definition, redacted local result receipt, or source-result-linked follow-through packet.
