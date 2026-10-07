# Public Claim Quarantine Fields current

Dedicated field schema for `META/Public-Claim-Quarantine-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| quarantine_id | true | non-empty stable identifier | `quarantine_id` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| claim_id | true | non-empty stable identifier | Stable claim identifier joining claim lifecycle, quarantine, release, and audit tables. |
| candidate_id | true | non-empty stable identifier | Stable candidate identifier joining candidate/frontmatter/governance/public tables. |
| candidate_name | true | YYYY-MM-DD or documented date string | Human-readable candidate label; not by itself public-release permission. |
| claim_type | true | string; non-empty when semantically required | `claim_type` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| claim_status | true | string; non-empty when semantically required | `claim_status` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| evidence_strength | true | string; non-empty when semantically required | `evidence_strength` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| capacity_currentness_risk | true | string; non-empty when semantically required | `capacity_currentness_risk` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| quarantine_reason | true | string; non-empty when semantically required | `quarantine_reason` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| public_wording_status | true | string; non-empty when semantically required | `public_wording_status` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| allowed_public_use | true | string; non-empty when semantically required | `allowed_public_use` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| required_preconditions | true | string; non-empty when semantically required | `required_preconditions` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| related_negative_case_ids | true | string; non-empty when semantically required | `related_negative_case_ids` column from `META/Public-Claim-Quarantine-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
