# Scenario: CLI override wins but bundle must stay invocation-scoped

A workspace inherits project and user config files, but the reviewed run added `cargo --config net.offline=true --config build.target-dir="/tmp/ci-target" check`.
The bundle may show those keys as winners, but it must not let the resulting effective config masquerade as the project’s ambient default configuration.
