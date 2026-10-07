# Claim Source Boundary Matrix Fields — current

Generated as schema companion for `SCHEMA/Claim-Source-Boundary-Matrix-Fields-current.csv`.

Fields: 21

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| matrix_id | yes | claim_source_matrix_[0-9]{5} | stable row id for the claim-source matrix link |
| claim_id | yes | claim_[0-9]+ | claim identifier from Claim-Ledger-current.csv |
| candidate_id | yes | cand_[a-z0-9_]+ | candidate identifier for the claim |
| candidate_name | yes | text | candidate display label copied from claim ledger |
| claim_type | yes | controlled or ledger value | claim type from Claim-Ledger-current.csv |
| claim_status | yes | controlled or ledger value | claim status from Claim-Ledger-current.csv |
| overclaim_risk | yes | low/medium/high or ledger value | claim overclaim risk from Claim-Ledger-current.csv |
| source_id | yes | src_[a-z0-9_]+ | evidence source identifier referenced by the claim |
| source_defined | yes | true/false | whether source_id exists in Source-Registry-current.csv |
| source_type | no | source-type vocabulary | source_type from Source Registry |
| evidence_roles | no | pipe-delimited tokens | evidence roles from Source Registry |
| harm_proximity | no | harm-proximity vocabulary | source harm-proximity posture |
| public_link_policy | no | public-link policy vocabulary | source public link policy |
| safe_to_recheck_automatically | no | source freshness vocabulary | automatic recheck posture from Source Registry |
| source_owner_type | no | owner-type vocabulary | source owner type from Source Registry |
| source_candidate_reciprocity | yes | pass/no_candidate_scope_declared/fail_candidate_not_listed_on_source/fail_source_missing | whether Source Registry candidate_ids reciprocally covers the claim candidate |
| candidate_canonical_source_status | yes | pass/candidate_missing/fail_source_not_listed_in_candidate_canonical_source_ids | whether Candidate-Ledger source_ids includes the claim evidence source |
| public_use_posture | yes | internal_evidence_only_no_public_url/manual_review_required_before_public_use/boundary_note_required_before_public_link/unknown_policy_manual_review/policy_bound_manual_review/source_missing_no_public_use | derived public-use posture for this claim-source link |
| capacity_or_referral_risk | yes | derived token | derived risk flag for capacity/referral/contact language near the source policy |
| status | yes | pass/fail | row status; fail blocks handoff |
| note | no | text | short explanation of row status |
