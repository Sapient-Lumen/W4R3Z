# Public Negative Corpus Fields current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| test_id | true | neg_[0-9]{3} | Stable controlled-fixture test identifier. |
| fixture_name | true | nonempty string | Short name of the public-release lint fixture. |
| expected_risk_type | true | configured public_release_lint risk_type | Risk type the fixture must trigger. |
| expected_min_severity | true | medium|high | Minimum severity expected from the linter for this fixture. |
| observed_severities | false | pipe-separated severities | Severities observed for the expected risk type. |
| observed_risk_types | false | pipe-separated risk types | All configured risk types observed in the fixture output. |
| status | true | pass|fail | Pass when the fixture is caught at or above the expected severity. |
| note | false | free text | Human-readable fixture result note. |
