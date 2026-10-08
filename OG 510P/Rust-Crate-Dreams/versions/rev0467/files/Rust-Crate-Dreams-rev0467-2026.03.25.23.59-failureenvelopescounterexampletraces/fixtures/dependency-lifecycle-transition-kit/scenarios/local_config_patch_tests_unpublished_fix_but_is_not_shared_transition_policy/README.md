# Scenario: local config patch tests an unpublished fix but is not shared transition policy

This fixture keeps an important lifecycle distinction visible:

- testing an unpublished fix through `.cargo/config.toml` can be useful,
- but a local or CI-only config patch is not the same thing as checked-in shared transition posture,
- especially when Cargo itself recommends preferring `Cargo.toml` for shared builds.
