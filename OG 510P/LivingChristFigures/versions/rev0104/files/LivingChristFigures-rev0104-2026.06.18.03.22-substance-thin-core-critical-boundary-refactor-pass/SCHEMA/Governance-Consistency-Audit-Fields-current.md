# Governance Consistency Audit Fields current

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| finding_id | true | ^gca_[0-9]{4}$ | Finding id emitted by governance_consistency_audit.py. |
| severity | true | info|medium|high | Finding severity; high blocks handoff. |
| check | true | non-empty string | Consistency check name. |
| scope | true | candidate|source|governance|package | Scope of the finding. |
| subject_id | true | candidate/source/package id | Specific subject of the finding. |
| detail | true | non-empty string | Finding detail or pass statement. |
| required_action | true | non-empty string | Action required to resolve or maintain the gate. |
