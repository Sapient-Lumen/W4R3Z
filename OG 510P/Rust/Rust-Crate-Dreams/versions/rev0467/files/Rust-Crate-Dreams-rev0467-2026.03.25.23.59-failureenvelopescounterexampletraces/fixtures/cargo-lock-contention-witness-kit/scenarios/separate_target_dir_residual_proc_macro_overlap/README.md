# Scenario — separate target dirs reduced one collision class but left residual proc-macro/build-script overlap

This scenario exists to force **P-0490** to keep “mitigation applied” separate from “contention solved”.

The Cargo 1.94 development-cycle update says `cargo check` and `cargo test` may still contend around proc-macros and build scripts even when other cache entries are unique enough not to contend.
A witness bundle should report that residual surface explicitly.
