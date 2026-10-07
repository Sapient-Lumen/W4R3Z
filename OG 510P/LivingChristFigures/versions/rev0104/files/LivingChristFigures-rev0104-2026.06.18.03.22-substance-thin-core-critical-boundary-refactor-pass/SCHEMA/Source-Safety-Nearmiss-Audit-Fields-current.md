# Source Safety Nearmiss Audit Fields — current

Generated as the field contract for `META/Source-Safety-Nearmiss-Audit-current.csv`.

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| finding_id | yes | ssnm_#### | near-miss finding id |
| source_id | yes | source id or blank for summary row | None |
| domain | yes | pass-through string | source domain |
| candidate_ids | yes | pipe-separated ids or blank | candidate ids linked to source |
| hazard_family | yes | controlled hazard family combination | source-safety trigger family |
| trigger_terms | yes | pipe-separated trigger terms or blank | matched terms from URL/metadata/governance notes |
| harm_proximity | yes | controlled harm-proximity value | current source harm-proximity classification |
| public_link_policy | yes | controlled public-link policy | current source public-link policy |
| safe_to_recheck_automatically | yes | controlled recheck posture | current recheck posture |
| public_url_release_decision | yes | controlled link-review decision | current public URL release decision |
| severity | yes | info/high | release severity |
| status | yes | pass/fail | audit status |
| recommended_action | yes | pass-through string | what to do if the row fails |
| note | yes | pass-through string | audit note |
