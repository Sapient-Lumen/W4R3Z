# Policy-Assertion-Matrix Fields — current

Rows: 8

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| assertion_id | true | assertion_[0-9]{3} | Stable policy assertion identifier. |
| policy_assertion | true | nonempty string | High-level release or governance claim being backed by executable evidence. |
| policy_surface | true | pipe-separated package paths | Policy/handoff surfaces where the assertion appears. |
| enforced_by_gates | true | pipe-separated gate IDs | Release gates that enforce or summarize the assertion. |
| enforced_by_tools | true | pipe-separated tool paths | Tools that produce the evidence reports. |
| evidence_reports | true | pipe-separated package paths | Reports that must exist and be pass/zero-high compatible. |
| status | true | pass/fail | Pass when surfaces/tools/reports exist and evidence reports are not failing/high. |
| note | false | free text | Human-readable evidence or failure note. |
