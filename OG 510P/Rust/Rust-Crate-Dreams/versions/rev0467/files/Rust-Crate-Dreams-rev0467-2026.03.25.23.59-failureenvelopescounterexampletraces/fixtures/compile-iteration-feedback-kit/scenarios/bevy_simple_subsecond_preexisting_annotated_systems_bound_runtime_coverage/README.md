# Scenario — Bevy simple subsecond coverage is bounded by annotations, launch-time existence, and project shape

This scenario freezes the fact that `bevy_simple_subsecond_system` only hotpatches annotated systems/observers, only considers functions that existed at launch, and documents unsupported workspace / `lib.rs` shapes.
A demo system patch should not masquerade as coverage for arbitrary runtime-discovered or newly introduced routes.
