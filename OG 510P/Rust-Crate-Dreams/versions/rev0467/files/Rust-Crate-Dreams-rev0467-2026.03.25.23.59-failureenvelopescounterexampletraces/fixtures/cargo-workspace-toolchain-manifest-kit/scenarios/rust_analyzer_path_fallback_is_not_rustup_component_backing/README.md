# rust_analyzer_path_fallback_is_not_rustup_component_backing

A developer asks for `rust-analyzer` through a rustup-managed route, but the expected rustup-managed binary is absent for the active toolchain and rustup 1.29 falls back to a binary found on `PATH`.

The important distinction is that the command succeeded without proving rustup component backing for the active toolchain.
