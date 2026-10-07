# Audit Selftest Fields — current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| selftest_id | true | nonempty string | stable self-test case identifier |
| target_tool | true | nonempty string | tool expected to detect the controlled mutation |
| mutation | true | nonempty string | temporary mutation injected into a copied package |
| expected_failure_signal | true | nonempty string | finding/exit signal that should appear if the auditor works |
| observed_failure_signal | true | nonempty string | actual return code or finding count observed during the self-test |
| status | true | pass|fail | pass if expected failure signal appeared; fail if the auditor did not catch the mutation |
| detail | false | string | human-readable purpose of the self-test |
