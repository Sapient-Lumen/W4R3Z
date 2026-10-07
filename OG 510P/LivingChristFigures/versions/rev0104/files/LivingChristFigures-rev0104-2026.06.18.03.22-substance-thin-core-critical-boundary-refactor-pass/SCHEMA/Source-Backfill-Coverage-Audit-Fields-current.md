# Source-Backfill-Coverage-Audit Fields — current

Field schema for Source-Backfill-Coverage-Audit-current.*

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| coverage_id | yes | sbc_[0-9]{4} | Stable row identifier for one Source Registry source_id coverage check. |
| source_id | yes | source registry id | Source Registry source identifier. |
| domain | yes | string | Source domain from Source Registry. |
| candidate_ids | no | pipe-separated candidate ids | Candidate ids from Source Registry. |
| source_registry_row_present | yes | true/false | Whether the source exists in Source Registry. |
| backfill_action_count | yes | integer | Number of Source-Metadata-Backfill rows for this source_id. |
| latest_backfill_revision | no | revision id | Latest batch revision observed for this source_id. |
| latest_backfill_status | no | string | Latest backfill status observed for this source_id. |
| duplicate_action_count | yes | integer | Backfill action count beyond the first row. |
| coverage_status | yes | covered/missing_backfill_coverage | Coverage result for this source_id. |
| severity | yes | info/high | High if coverage is missing. |
| status | yes | pass/fail | Pass/fail state for release gate. |
| action_needed | yes | string | Recommended action if missing or duplicated. |
