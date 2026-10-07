# Governance Review Queue Fields — current

Field contract for `META/Governance-Review-Queue-current.*`.

Rows: 8

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| queue_id | true | unique gq_ id | Review queue row id. |
| candidate_id | true | candidate id | Candidate to review. |
| candidate_name | true | non-empty string | Candidate display name. |
| priority | true | 0/1/2/3 | 0 is governance quarantine; 1 lifecycle; 2 source-link; 3 near-harm manual review. |
| queue_type | true | release posture string | Why the candidate is in the queue. |
| trigger | true | non-empty string | Machine-readable trigger summary. |
| next_action | true | non-empty string | Required next governance action. |
| blocking_files | true | pipe-separated paths | Files that define the block/review gate. |
