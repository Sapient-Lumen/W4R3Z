# Scenario: build script needs pkg-config path grants but proc macro stays deny-by-default

A package uses a `build.rs` that probes system headers and writes generated bindings into `OUT_DIR`.
The same package also depends on a derive proc macro that should not inherit those filesystem grants.

This scenario exists so the kit can prove that per-actor policy survived translation into an effective sandbox contract.
