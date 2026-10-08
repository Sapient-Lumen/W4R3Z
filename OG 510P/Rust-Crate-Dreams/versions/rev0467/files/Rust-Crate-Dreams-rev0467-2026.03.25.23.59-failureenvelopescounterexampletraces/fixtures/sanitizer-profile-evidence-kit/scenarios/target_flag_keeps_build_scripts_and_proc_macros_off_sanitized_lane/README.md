# `--target` keeps build scripts and procedural macros off the sanitized lane

This scenario records a practical Cargo truth from the sanitizer docs:
`--target` is used so `RUSTFLAGS` do not instrument host-built build scripts and procedural macros.

The receipt should not pretend those host helpers were covered by the sanitizer run.
