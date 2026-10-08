# rev0318 pedagogy-forward execution refactor

## Refactor target

Rev0317 made the teacher/tutor micro-pilot readable. Rev0318 makes it buildable. The target is a
real owner plan and aggregate run packet, not a larger governance envelope.

## Refactor performed

- Added `tools/prepare_teacher_tutor_micro_pilot_pack.py`.
- Added `make micro-pilot-pack` as the one-command packet path.
- The generated packet contains an owner plan, session log, final eight-row readout, coach prompt,
  run checklist, and manifest.
- The utility writes under `scratch/` or outside the repository, refuses obvious raw/protected or
  identifying argument terms, and marks the packet `PREPARED_NOT_RUN` / `NOT_EVIDENCE`.
- Updated the teacher/tutor run card so operators no longer need to assemble the packet manually.

## Refactor rule carried forward

Do not add another pre-import control until one of these happens:

- a real owner packet exposes a concrete uncovered failure;
- a real micro-pilot readout exposes learner harm, access harm, privacy leakage, false-claim risk,
  or workload reversal that existing controls cannot block;
- a release check demonstrates a reproducible packaging or source-truth defect.

Otherwise, spend the next cycle on human contact, the first teacher/tutor run, consolidation, or
deletion.

## Claim boundary

This refactor supplies execution materials. It does not send email, accept owner evidence, run a
micro-pilot, authorize service use, upgrade public language, or close `FT-0181`.
