# Candidate Governance Snapshot Fields — current

Field contract for `META/Candidate-Governance-Snapshot-current.*`.

Rows: 20

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| candidate_id | true | candidate id | Candidate Ledger id; coverage must match every candidate. |
| candidate_name | true | non-empty string | Candidate display name copied from Candidate Ledger. |
| public_export_tier | true | eligibility tier | Tier from Public Export Eligibility. |
| public_shape_template | true | template key | Safe public shape template. |
| required_review | true | non-empty string | Eligibility review gate. |
| governance_rows | true | integer-like | Count of consent/governance rows for candidate. |
| governance_quarantine | true | true/false | Whether governance/consent quarantine applies. |
| claim_count | true | integer-like | Claim rows for candidate. |
| claims_needing_human_review | true | integer-like | Lifecycle rows requiring human review. |
| highest_refresh_priority | true | refresh priority enum | Refresh queue result. |
| capacity_state | true | non-empty string | Candidate capacity state. |
| source_count | true | integer-like | Source Registry rows linked to candidate. |
| blocked_public_url_sources | true | integer-like | Source links blocked publicly. |
| manual_review_url_sources | true | integer-like | Source links blocked until review. |
| boundary_note_url_sources | true | integer-like | Source links requiring boundary note and review. |
| near_harm_profile | true | pipe-separated vocabulary | Joined harm-proximity values. |
| public_url_release | true | non-empty string | Eligibility URL release gate. |
| public_claim_release | true | non-empty string | Eligibility public-claim gate. |
| release_posture | true | controlled posture string | Derived release posture. |
| next_governance_action | true | non-empty string | Next manual action before expansion. |
