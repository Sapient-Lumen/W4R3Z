# Scenario: Extism allowlists must survive as an explicit capability receipt

This scenario exists because Extism's manifest/config docs make capability posture concrete:

- `allowed_hosts` can whitelist outbound HTTP destinations,
- `allowed_paths` can map host paths into the guest,
- host configuration is read-only from the plugin side,
- and timeout/WASI posture are host-controlled runtime choices.

Those facts are useful, but they should not be flattened into one vague “sandboxed plugin” claim.

