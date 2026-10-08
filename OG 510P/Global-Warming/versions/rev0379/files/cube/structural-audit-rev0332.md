# Structural audit rev0332

Rev0332 adds the upstream dose-assessment, field-monitoring, and PAR/PAD decision trace layer without deleting compatibility surfaces.

## Main correction

The cube now separates public guidance/model context from local dose-assessment closure. Public PAG material, NRC emergency-classification pages, RASCAL public pages, NUREG-0654 context, exercise schedules, or field-operations course pages can create a demand or reopen signal. They cannot close a local dose/PAR row.

## Query route

`source term/met inputs -> dose-model run lineage -> field measurement custody -> PAG/PAR decision trace -> change/retraction clock -> validator -> CAP/retest/verifier -> public claim gate`

## Compatibility

Legacy universal nuclear crossproduct tables remain present for compatibility, but rev0332 emergency-readiness queries route through sparse/local evidence and rev0332 dose-field proof surfaces.
