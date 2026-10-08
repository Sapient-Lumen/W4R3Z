# Scenario — Chaud coverage depends on enabled hot-reload mode and `#[chaud::hot]` routes

This scenario freezes the fact that Chaud updates `#[chaud::hot]` functions and that its macros are effectively no-ops unless the relevant feature is enabled.
Seeing the macros in source is not enough to claim active live-update coverage.
