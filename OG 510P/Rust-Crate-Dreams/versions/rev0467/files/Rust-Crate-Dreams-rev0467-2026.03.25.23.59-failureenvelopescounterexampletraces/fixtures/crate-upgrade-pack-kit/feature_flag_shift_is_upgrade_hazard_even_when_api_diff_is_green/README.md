# Scenario — feature-flag/default-policy shift is an upgrade hazard even when API diff stays green

This scenario freezes the case where:

- public API diff tools stay green,
- but the crate changes default features or recommended backend/runtime policy,
- which still changes the real downstream upgrade surface.

Why it matters:

The July 2025 `hint-mostly-unused` post made the language around **feature flags as stable interface** unusually explicit.
That makes feature/default-policy drift a first-class upgrade hazard, not a side note.
