# Governance Decision Fields — current

Field contract for `GOVERNANCE/Governance-Decision-Ledger-current.*`.

Rows: 10

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| decision_id | true | ^govdec_[0-9]{4}$ | Governance decision id. |
| date | true | YYYY-MM-DD | Date the decision was recorded. |
| decision_class | true | policy_gate_added/public_release_blocked/boundary_shape_allowed/source_link_restricted/manual_review_required | Decision class. |
| scope | true | non-empty string | Package area, candidate, or public surface governed. |
| decision | true | non-empty string | Decision made. |
| what_changed | true | non-empty string | Concrete package behavior changed by the decision. |
| what_remains_blocked | true | non-empty string | Surfaces still blocked. |
| review_required_before_change | true | non-empty string | Review needed before loosening or changing decision. |
| related_files | true | pipe-separated paths | Files carrying the decision. |
| status | true | active/superseded/closed | Current decision status. |
