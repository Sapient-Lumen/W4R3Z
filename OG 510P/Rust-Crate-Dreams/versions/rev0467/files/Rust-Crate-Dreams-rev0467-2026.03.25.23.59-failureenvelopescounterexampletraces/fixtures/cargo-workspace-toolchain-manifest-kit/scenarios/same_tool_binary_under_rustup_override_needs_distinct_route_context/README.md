# same_tool_binary_under_rustup_override_needs_distinct_route_context

The binary path can stay identical while the surrounding rustup/toolchain context changes because the user invoked `cargo +beta` or entered a directory with a different override.

This fixture keeps **tool route** separate from **toolchain context**.
