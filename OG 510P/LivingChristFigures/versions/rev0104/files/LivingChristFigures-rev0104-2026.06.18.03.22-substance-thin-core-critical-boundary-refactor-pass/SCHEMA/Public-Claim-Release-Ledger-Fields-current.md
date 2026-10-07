# Public Claim Release Ledger Fields current

Dedicated field schema for `META/Public-Claim-Release-Ledger-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| release_id | true | non-empty stable identifier | `release_id` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| date_reviewed | true | YYYY-MM-DD or documented date string | `date_reviewed` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| released_from_quarantine_id | true | non-empty stable identifier | `released_from_quarantine_id` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| claim_id | true | non-empty stable identifier | Stable claim identifier joining claim lifecycle, quarantine, release, and audit tables. |
| candidate_id | true | non-empty stable identifier | Stable candidate identifier joining candidate/frontmatter/governance/public tables. |
| candidate_name | true | YYYY-MM-DD or documented date string | Human-readable candidate label; not by itself public-release permission. |
| release_scope | true | string; non-empty when semantically required | `release_scope` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| source_registry_ids | true | string; non-empty when semantically required | `source_registry_ids` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| source_promotion_decision_ids | true | string; non-empty when semantically required | `source_promotion_decision_ids` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| what_is_now_allowed | true | true/false or controlled release-status string | `what_is_now_allowed` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| what_remains_blocked | true | string; non-empty when semantically required | `what_remains_blocked` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| required_future_preconditions | true | string; non-empty when semantically required | `required_future_preconditions` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| qa_gate | true | string; non-empty when semantically required | `qa_gate` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| notes | true | string; non-empty when semantically required | `notes` column from `META/Public-Claim-Release-Ledger-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
