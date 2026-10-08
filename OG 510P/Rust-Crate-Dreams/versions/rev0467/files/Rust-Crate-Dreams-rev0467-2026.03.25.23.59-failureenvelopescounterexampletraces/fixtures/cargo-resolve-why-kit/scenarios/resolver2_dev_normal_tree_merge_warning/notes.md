# Scenario — resolver v2 dev + normal lanes look merged in `cargo tree`

This scenario keeps one sharp boundary visible:

- resolver v2 says normal and dev lanes should remain split unless the dev targets are being built,
- but `cargo tree` can still show a feature-unified investigative view,
- so the bundle must freeze that the displayed merge is **surface-level** and not automatically exact build truth.
