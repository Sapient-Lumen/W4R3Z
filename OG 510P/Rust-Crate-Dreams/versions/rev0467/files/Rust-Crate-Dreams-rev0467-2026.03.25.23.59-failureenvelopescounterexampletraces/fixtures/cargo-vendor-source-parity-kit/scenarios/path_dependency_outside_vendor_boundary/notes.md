# Scenario: path dependency outside vendor boundary

The workspace uses `cargo vendor`, but one dependency is still a path dependency outside the vendored tree.
The important artifact is a coverage report that says the vendored bundle is incomplete rather than silently implying full offline coverage.
