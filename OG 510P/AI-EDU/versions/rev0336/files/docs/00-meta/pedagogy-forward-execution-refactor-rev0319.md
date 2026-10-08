# rev0319 pedagogy-forward execution refactor

## Refactor target

The first teacher/tutor micro-pilot was still too easy to postpone because the packet was ready but
the first concept measure was not concrete. Rev0319 refactors the rail from packet preparation toward
first-cycle execution.

## Changes

- Added `docs/30-operations/teacher-tutor-micro-pilot-measure-card-equality-one-step.md`.
- Extended `tools/prepare_teacher_tutor_micro_pilot_pack.py` with `--concept-kit`.
- Extended `make micro-pilot-pack` with `CONCEPT_KIT=equality-one-step`.
- Generated packets now include `MEASURE-CARD.md` and `OWNER-DECISION-MEMO.md` in addition to the
  owner plan, session log, final readout, coach prompt, checklist, and manifest.
- Updated the run card and service record so the default first cycle has a concrete construct,
  baseline, coach-use move menu, misconception watchlist, no-AI transfer check, and continue/stop
  threshold.

## Why this is not more bureaucracy

No schema, validator, release lane, branch family, or public-claim surface was added. The new file is
a concept-level execution card and the existing utility writes two more working files to scratch. The
purpose is to reduce the gap between reading and running.

## Carry-forward rule

If a real owner chooses a different concept, replace the concept card locally. Do not expand the
archive with a concept-card family until at least one real run shows that reusable cards change the
owner decision or prevent a concrete harm.

## Claim boundary

This refactor does not run a pilot, accept evidence, prove learning, authorize service use, upgrade
public claims, create custody, or close `FT-0181`.
