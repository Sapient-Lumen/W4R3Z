# Meta-research audit fields

Revision: `rev0009`.

A `MET` record is a meta-research audit record. It is used when the object of study is not a single failed trial or incident, but the evidence system itself.

Required payload fields:

- `audit_class`
- `denominator_surface`
- `numerator_surface`
- `bias_mechanisms_encoded`
- `limits`

Recommended fields:

- `evidence_period`
- `scope`
- `subjects`
- `negative_controls_needed`
- `matching_problem_notes`

A `MET` record must never be promoted as a universal prevalence estimate unless it has a mature synthesis record and explicit field/time boundaries.
