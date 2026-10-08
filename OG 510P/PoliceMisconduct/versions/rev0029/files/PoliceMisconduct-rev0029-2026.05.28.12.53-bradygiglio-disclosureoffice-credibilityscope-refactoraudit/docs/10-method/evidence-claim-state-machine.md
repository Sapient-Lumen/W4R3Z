# Evidence claim state machine

The state ladder in `EVIDENCE-LADDER.json` governs field-level confidence and display. It is not a moral severity score.

## State transition sketch

- `Q → S0`: lead discovered.
- `S0 → S1`: source locator recorded.
- `S1 → S2`: source version/custody recorded and fields extracted.
- `S2 → S3`: corroboration, official record support, or conflict map added.
- `S3 → S4`: specific outcome/adjudication/disposition source added.
- `S4 → S5`: privacy/display/correction/rollback route complete.

## No ambient promotion

A record can have one S4 field and many S1 fields. A court verdict on one claim does not promote every factual allegation in the complaint.
A settlement amount does not promote an admission. A decertification order does not automatically validate every prior news account.

## Conflict handling

Conflicts are data. If sources disagree on date, officer spelling, injury description, amount, or outcome, record the conflict rather than smoothing it away.
