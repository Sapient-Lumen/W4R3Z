# Indigenous Data Governance Fields current

Conceptual field schema for Indigenous data-governance review fields. This is not a claim of OCAP® compliance or community authorization.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| family_chosen_public_name_status | true | not_recorded/limited_named_profile_in_working_cube_only/family_chosen_public_name_allowed_for_specific_scope/blocked/unknown | Names are not copied merely because a source names them. |
| community_review_status | true | not_recorded_in_cube/requested/completed_for_scope/declined/not_applicable | Do not imply community authorization without record. |
| review_authority | true | none_recorded/family_named_representative/community_governance_body/Indigenous_data_project_authority/cube_editor_caution_only | Cube-editor caution is not Indigenous authority. |
| review_scope | true | boundary_only/name_use/image_use/testimony_use/public_link/public_prose/case_detail | Authorization is scope-limited. |
| consent_basis | true | not_recorded/public_source_visibility_only/family_chosen_public_profile_for_limited_scope/explicit_recorded_permission/official_policy_context_only | Public-source visibility alone is insufficient for expansion. |
| consent_limitations | true | free_text | Record blocked reuse surfaces. |
| harm_proximity | true | see SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv | Near-harm material needs stronger limits. |
| public_reuse_allowed | true | false/safe_aggregate_boundary_shape_only_after_review/specific_scope_only/true_with_recorded_authorization | Default false. |
| public_link_allowed | true | false/boundary_note_required/specific_scope_only/true_for_far_policy_context | A URL can be a release surface. |
| image_use_allowed | true | false_without_explicit_family_or_community_authorized_release/specific_scope_only/true_with_recorded_authorization | Default false. |
| takedown_contact_internal_only | true | true/false | Do not publish family/community contact paths. |
| do_not_extract_case_details | true | true/false | Default true for MMIWG2S+ and family-search material. |
