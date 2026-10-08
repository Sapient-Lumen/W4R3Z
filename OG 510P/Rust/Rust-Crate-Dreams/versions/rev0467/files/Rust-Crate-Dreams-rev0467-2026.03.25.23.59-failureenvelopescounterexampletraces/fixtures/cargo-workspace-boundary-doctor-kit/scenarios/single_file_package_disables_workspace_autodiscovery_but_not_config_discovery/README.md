# Scenario — single-file package disables workspace auto-discovery but not config discovery

This scenario exists because `.rs` single-file packages cannot be auto-discovered like `Cargo.toml` manifests.
That should not be collapsed into a fake claim that “no discovery happened.”
The bundle should preserve invocation mode and workspace-auto-discovery posture separately from config discovery.
