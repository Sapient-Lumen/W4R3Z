# Border Route Referral Boundary Audit Fields — current

Rows: 16

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| finding_id | true | ^brrba_[0-9]{4}$ | `finding_id` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| finding_type | true | claim_boundary/source_boundary/summary | `finding_type` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| candidate_id | true | string; may be blank when not applicable | `candidate_id` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| candidate_name | true | string; may be blank when not applicable | `candidate_name` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| claim_id | true | string; may be blank when not applicable | `claim_id` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| source_id | true | string; may be blank when not applicable | `source_id` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| domain | true | string; may be blank when not applicable | `domain` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| hazard_tokens | true | string; may be blank when not applicable | `hazard_tokens` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| claim_status | true | string; may be blank when not applicable | `claim_status` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| public_url_release_decision | true | string; may be blank when not applicable | `public_url_release_decision` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| public_link_policy | true | string; may be blank when not applicable | `public_link_policy` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| quarantine_status | true | string; may be blank when not applicable | `quarantine_status` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| severity | true | info/medium/high | `severity` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| status | true | pass/fail | `status` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| required_action | true | string; may be blank when not applicable | `required_action` column for Border-Route-Referral-Boundary-Audit-current.csv. |
| note | true | string; may be blank when not applicable | `note` column for Border-Route-Referral-Boundary-Audit-current.csv. |
