# testcontainers_scope_cleanup_isolated_but_external_daemon_backing

This scenario keeps another ordinary testing-support shortcut honest:

- `testcontainers` documents self-contained isolated integration tests,
- running containers are removed when the handle goes out of scope,
- but the topology still depends on an external Docker daemon and host configuration.

A crate-authored test-support contract should therefore distinguish isolation class from cleanup mechanism and host-environment assumptions.
