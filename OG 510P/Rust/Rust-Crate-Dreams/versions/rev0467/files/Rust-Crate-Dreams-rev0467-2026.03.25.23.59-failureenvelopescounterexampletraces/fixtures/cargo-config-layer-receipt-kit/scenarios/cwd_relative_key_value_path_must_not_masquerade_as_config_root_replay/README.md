# Scenario: cwd-relative key-value path must not masquerade as config-root replay

A run passed `cargo --config build.target-dir="../shared-target" test` from a nested working directory while the project also used an included config file.
Because Cargo interprets `--config KEY=VALUE` paths relative to the current working directory, a replay recipe must not silently treat the winning path like a config-file-relative setting.
