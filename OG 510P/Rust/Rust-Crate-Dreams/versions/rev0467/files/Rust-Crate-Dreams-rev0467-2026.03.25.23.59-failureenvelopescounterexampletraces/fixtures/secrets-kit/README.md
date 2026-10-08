# secrets-kit fixtures

This fixture pack exists so future archive passes do not flatten secret handling into one fake “uses secrets safely” story.

## Core review objects

- `revelation-path.receipt.json`
- `persistence-posture.receipt.json`
- `memory-posture.receipt.json`
- `export-posture.report.json`

## Scenario families

### `env_string_then_wrapped_secret_must_not_masquerade_as_protected_source_path`
Shows that loading from an env `String` and only then wrapping in `secrecy::SecretBox<T>` is still a revelation path with plaintext intermediates and only zeroize-style memory posture.

### `keyring_mock_backend_must_not_masquerade_as_persistent_store_support`
Shows that a mock credential store may preserve test ergonomics while providing no persistence and therefore must not inherit the contract of a native store.

### `serializable_secret_opt_in_must_not_masquerade_as_default_export_safety`
Shows that explicitly opting secrets back into `serde` serialization widens export posture even if debug output remains redacted.

### `protected_memory_backend_must_not_masquerade_as_zeroize_only`
Shows that `mprotect` / `mlock`-class protected memory is stronger than ordinary zeroize-on-drop posture and should be reported separately.
