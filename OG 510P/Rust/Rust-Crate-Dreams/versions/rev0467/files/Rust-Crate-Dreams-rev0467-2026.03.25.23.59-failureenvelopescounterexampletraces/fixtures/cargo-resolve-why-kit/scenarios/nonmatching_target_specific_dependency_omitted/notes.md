# Scenario — non-matching target-specific dependency clause is out of scope

This scenario keeps another boundary visible:

- resolver v2 ignores features from target-specific dependencies that are not currently being built,
- `cargo metadata` without `--filter-platform` can still include those edges in the graph,
- so the bundle must freeze whether platform coverage came from an all-target graph or from a selected-target capture.
