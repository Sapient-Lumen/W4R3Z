# Scenario: hidden shim uses allowlist and still needs provenance

A crate exposes a doc-hidden compatibility shim and suppresses `exported_private_dependencies`.
The bundle must keep the allowlisted exception visible and record whether the verdict came from rustc/Cargo or rustdoc-based inference.
