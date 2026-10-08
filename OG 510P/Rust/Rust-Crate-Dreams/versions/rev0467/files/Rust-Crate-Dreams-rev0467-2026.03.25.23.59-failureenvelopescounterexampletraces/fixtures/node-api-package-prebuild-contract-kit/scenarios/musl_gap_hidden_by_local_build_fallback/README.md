# Scenario: musl gap hidden by local-build fallback

The package claims broad Linux support, but the published native payloads only cover `linux-x64-gnu`.
`linux-x64-musl` is allowed to fall back to a local native build, so the release should not be described as fully prebuilt.

This scenario exists to keep the shipkit from flattening:
- “works if a local Rust toolchain is present”
- and “a prebuilt native artifact shipped for that tuple”

into the same support claim.
