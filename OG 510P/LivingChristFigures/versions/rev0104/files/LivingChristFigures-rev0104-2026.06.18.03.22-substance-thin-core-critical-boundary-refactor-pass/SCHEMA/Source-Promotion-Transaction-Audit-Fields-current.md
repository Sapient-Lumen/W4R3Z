# Source Promotion Transaction Audit Fields current

Dedicated field schema for `META/Source-Promotion-Transaction-Audit-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| transaction_id | true | non-empty stable identifier | `transaction_id` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| date_reviewed | true | YYYY-MM-DD or documented date string | `date_reviewed` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| candidate_id | true | non-empty stable identifier | Stable candidate identifier joining candidate/frontmatter/governance/public tables. |
| candidate_name | true | YYYY-MM-DD or documented date string | Human-readable candidate label; not by itself public-release permission. |
| promoted_intake_ids | true | string; non-empty when semantically required | `promoted_intake_ids` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| promoted_source_ids | true | string; non-empty when semantically required | `promoted_source_ids` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| held_intake_ids | true | string; non-empty when semantically required | `held_intake_ids` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| claim_rows_changed | true | string; non-empty when semantically required | `claim_rows_changed` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| ledger_rows_changed | true | string; non-empty when semantically required | `ledger_rows_changed` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| public_claim_effect | true | string; non-empty when semantically required | `public_claim_effect` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| operator_dissent_effect | true | string; non-empty when semantically required | `operator_dissent_effect` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| release_scope | true | string; non-empty when semantically required | `release_scope` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| remaining_blocks | true | string; non-empty when semantically required | `remaining_blocks` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| next_action | true | string; non-empty when semantically required | `next_action` column from `META/Source-Promotion-Transaction-Audit-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
