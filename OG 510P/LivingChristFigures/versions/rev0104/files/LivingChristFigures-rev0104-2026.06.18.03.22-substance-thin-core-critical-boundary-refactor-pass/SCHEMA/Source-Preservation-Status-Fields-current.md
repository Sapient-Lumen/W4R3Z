# Source Preservation Status Fields current — current

Field schema for `META/Source-Preservation-Status-current.csv`.

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| source_id | yes | nonempty string unless explicitly blank | source id |
| domain | yes | nonempty string unless explicitly blank | domain |
| source_type | yes | nonempty string unless explicitly blank | source type |
| candidate_ids | yes | nonempty string unless explicitly blank | candidate ids |
| harm_proximity | yes | nonempty string unless explicitly blank | harm proximity |
| public_link_policy | yes | nonempty string unless explicitly blank | public link policy |
| archived_copy_status | yes | nonempty string unless explicitly blank | archived copy status |
| archive_url_or_archive_id | yes | nonempty string unless explicitly blank | archive url or archive id |
| link_rot_risk | yes | nonempty string unless explicitly blank | link rot risk |
| archive_need | yes | manual_preservation_decision_needed/archive_recommended_for_context_link/archive_recorded_or_not_needed/policy_unclear_preservation_review | archive need |
| may_auto_archive | yes | no_manual_review_only/yes_context_only_after_review/manual_review_required | may auto archive |
| preservation_action | yes | nonempty string unless explicitly blank | preservation action |
| status | yes | pass/fail | status |
| note | yes | nonempty string unless explicitly blank | note |
