# Source Manual Preservation Decision Fields — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| decision_id | yes | nonempty string | stable row id for the manual-sensitive preservation decision audit |
| source_id | yes | nonempty string | Source Registry source id |
| domain | yes | nonempty string | source domain |
| candidate_ids | yes | nonempty string unless explicitly blank | pipe-separated candidate ids linked to the source |
| harm_proximity | yes | nonempty string | harm-proximity classification from Source Registry |
| public_link_policy | yes | nonempty string | public-link policy from Source Registry |
| safe_to_recheck_automatically | yes | nonempty string | refresh/recheck posture from Source Registry |
| public_url_release_decision | yes | nonempty string | public source-link review decision |
| source_metadata_status | yes | nonempty string | metadata_and_freshness_recorded or metadata_or_freshness_unresolved |
| archived_copy_status | yes | nonempty string | Source Registry archived-copy or manual preservation decision status |
| archive_url_or_archive_id | yes | nonempty string unless explicitly blank | archive URL/id if any; blank for no-public-archive decisions |
| manual_preservation_tier | yes | nonempty string | triage tier for sensitive preservation decision work |
| severity | yes | nonempty string | info or high |
| status | yes | nonempty string | pass or fail |
| recommended_action | yes | nonempty string | action required or maintained posture |
| note | yes | nonempty string | human-readable rationale |
