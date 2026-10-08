# Scenario: lib name drift breaks DLL load alignment

The R package name remained stable, but the underlying Rust lib name changed.
The installed artifact name and load contract no longer line up cleanly with the wrapper/runtime story.
