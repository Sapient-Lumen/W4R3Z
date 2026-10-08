# rev0316 pedagogy-forward execution refactor

## Refactor target

The hot path had been over-weighted toward `FT-0181` import mechanics. Rev0316 keeps that rail, but
adds the missing adjacent execution surface: a teacher/tutor augmentation micro-pilot that can
produce real pedagogical judgment without creating a new schema or release gate.

## Refactor performed

- Added `docs/30-operations/teacher-tutor-augmentation-micro-pilot.md`.
- Added `templates/teacher-tutor-augmentation-micro-pilot-template.csv`.
- Added `examples/service-records/teacher-tutor-move-coach-sandbox.json` as `AIEDU-SR-005`.
- Updated the pilot-packet surface to prefer the teacher/tutor-facing move coach before autonomous
  student-facing hint delivery.
- Updated the `FT-0181` first-sprint pack to separate the safest owner-contact target from the
  first pedagogical substance target.
- Refactored generated startup context so an operator sees the current micro-pilot plan instead of
  only the prior lint-defect repair.

## Audit result

A cold-history audit counted 102 branch-tail / hot-exam-like markdown files at about 208,057 words.
Those files may remain useful as searchable history, but they should not govern current execution.
They are now explicitly treated as cold retrieval through indexes, not as first-read doctrine.

## Claim boundary

No real field event occurred. This refactor creates an actionable pedagogical next step and lowers
operator burden. It does not prove learning, accept evidence, upgrade public claims, or close
`FT-0181`.
