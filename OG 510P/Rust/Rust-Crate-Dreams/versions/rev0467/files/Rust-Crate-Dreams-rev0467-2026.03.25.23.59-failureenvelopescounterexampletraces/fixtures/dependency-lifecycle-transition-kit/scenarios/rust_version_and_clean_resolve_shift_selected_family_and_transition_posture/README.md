# Scenario: rust-version and clean resolve shift the selected family and transition posture

This fixture keeps a third lifecycle distinction visible:

- dependency selection can change when `rust-version` context changes,
- that means a clean resolve under a different supported toolchain floor can move the chosen dependency family,
- and the lifecycle bundle should surface that as transition risk rather than burying it in general MSRV prose.
