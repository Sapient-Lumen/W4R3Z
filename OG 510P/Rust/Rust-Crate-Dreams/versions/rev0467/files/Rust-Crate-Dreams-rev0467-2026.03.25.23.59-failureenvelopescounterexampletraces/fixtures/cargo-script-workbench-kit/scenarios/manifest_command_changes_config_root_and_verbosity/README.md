# Manifest-command changes config root and verbosity

Cargo documents `cargo <path>` as a manifest-command lane with a different config-root and a lower default verbosity than `cargo run --manifest-path <path>`.
The bundle should record the interpretation explicitly.
