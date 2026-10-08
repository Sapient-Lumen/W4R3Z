# Scenario: prototype tools lane is wide but control core stays restricted

This fixture keeps one common mixed-criticality reality visible:

- wide third-party dependency use is acceptable in tooling and diagnostics,
- but the control core still has a narrow external-dependency budget,
- so the crate must publish both a lane snapshot and a criticality-boundary report.
