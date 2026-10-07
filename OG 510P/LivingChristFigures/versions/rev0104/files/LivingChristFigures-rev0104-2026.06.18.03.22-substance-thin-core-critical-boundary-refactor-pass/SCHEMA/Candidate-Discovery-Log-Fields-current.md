# Candidate Discovery Log Fields — current

Field schema for rev0070 candidate-discovery/intake governance surface.

Rows: 17

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| discovery_id | yes | discovery_[0-9]{4} | stable discovery-log row id |
| revision | yes | rev[0-9]{4} | revision in which the discovery decision was recorded |
| date | yes | YYYY-MM-DD | research/decision date |
| candidate_name | yes | text | human candidate/scout label |
| proposed_candidate_id | yes | cand_[a-z0-9_]+ or proposed placeholder | candidate id if promoted or proposed id if parked |
| discovery_status | yes | promoted_to_candidate/parked_related_candidate/not_promoted_context_source/rejected_duplicate/rejected_boundary_risk | intake disposition |
| decision | yes | controlled/free-text decision token | decision made in this pass |
| decision_rationale | yes | text | why the decision was made |
| source_ids | no | pipe-delimited source ids | source ids used for promoted/context rows |
| source_urls | no | pipe-delimited URLs | research trail URLs; internal only |
| office_ids | no | pipe-delimited office ids | candidate office ids or proposed office |
| boundary_flags | yes | pipe-delimited tokens | public safety boundaries identified during discovery |
| public_layer_action | yes | no_public_expansion/no_public_expansion_boundary_index_only/boundary_index_shape_only | public-layer action for the row |
| research_mode | yes | text token | how research was conducted/safened |
| next_action | yes | text | next research/audit action |
| status | yes | pass/fail | row status |
| last_reviewed | yes | YYYY-MM-DD | last review date |
