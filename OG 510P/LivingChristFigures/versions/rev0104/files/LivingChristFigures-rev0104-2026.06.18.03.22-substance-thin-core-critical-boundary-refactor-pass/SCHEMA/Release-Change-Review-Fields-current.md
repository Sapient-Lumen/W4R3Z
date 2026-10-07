# Release Change Review Fields — current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| review_id | yes | release_change_NNNN | Stable review row identifier. |
| subject_path | yes | package-relative path or . | Path or summary subject being reviewed. |
| review_check | yes | slug | Name of the delta/proof check. |
| change_type | yes | added|modified|removed|renamed|proof_check|summary | Raw delta class or synthetic proof/summary class. |
| review_area | yes | slug | Reviewer-risk/payload category. |
| expected_basis | yes | free text | Why this change is expected or why it blocks release. |
| observed_state | yes | free text | Observed delta or proof state. |
| review_required | yes | yes|no | Whether a human reviewer should glance at the row even when passing. |
| severity | yes | info|high | Release-blocking severity classification. |
| status | yes | pass|fail | Check outcome. |
| note | yes | free text | Interpretation or remediation note. |
