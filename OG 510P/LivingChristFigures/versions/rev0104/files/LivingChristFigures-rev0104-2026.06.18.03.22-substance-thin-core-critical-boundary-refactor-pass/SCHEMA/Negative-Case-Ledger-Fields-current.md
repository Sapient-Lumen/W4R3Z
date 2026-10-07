# Negative Case Ledger Fields current

Dedicated field schema for `META/Negative-Case-Ledger-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| negative_case_id | true | non-empty stable identifier | `negative_case_id` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| date_logged | true | YYYY-MM-DD or documented date string | `date_logged` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| case_label | true | string; non-empty when semantically required | `case_label` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| case_type | true | string; non-empty when semantically required | `case_type` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| related_candidate_ids | true | YYYY-MM-DD or documented date string | `related_candidate_ids` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| trigger | true | string; non-empty when semantically required | `trigger` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| decision | true | string; non-empty when semantically required | `decision` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| current_status | true | controlled status string | `current_status` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| source_or_trace | true | string; non-empty when semantically required | `source_or_trace` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| why_not_admitted_or_not_public | true | string; non-empty when semantically required | `why_not_admitted_or_not_public` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| behavior_change | true | string; non-empty when semantically required | `behavior_change` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| next_review_target | true | string; non-empty when semantically required | `next_review_target` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| public_export_safe | true | true/false or controlled release-status string | `public_export_safe` column from `META/Negative-Case-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
