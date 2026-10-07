# Dependency-Cycle-Audit Fields — current

Field schema for rev0062 report family.

Rows: 6

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| cycle_id | yes | nonempty string | stable cycle row id |
| cycle_class | yes | no_generated_artifact_cycle/unapproved_generated_artifact_cycle | cycle classification |
| path_chain | no | artifact path chain | cycle path chain when applicable |
| severity | yes | info/medium/high | release severity |
| status | yes | pass/fail | audit row status |
| note | yes | free text | explanation |
