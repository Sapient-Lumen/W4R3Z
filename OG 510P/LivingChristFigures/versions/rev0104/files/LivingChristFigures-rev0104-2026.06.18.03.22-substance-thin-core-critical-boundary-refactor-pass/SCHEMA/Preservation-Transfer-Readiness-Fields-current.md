# Preservation-Transfer-Readiness Field Schema — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| readiness_id | yes | ptr_NNNN | Stable row identifier. |
| area | yes | slug | Preservation/transfer area. |
| check | yes | slug | Specific readiness check. |
| expected | yes | free text | Expected condition. |
| observed | yes | free text | Observed condition. |
| severity | yes | high|info | Release-blocking severity classification. |
| status | yes | pass|fail | Check outcome. |
| next_action | yes | free text | Correction or next action if needed. |
