# Scenario: future user-wide build cache plugin is not the same surface as Cargo-home download cache

This scenario exists so **P-0480** stays honest as Cargo evolves.

The key claim is that a future plugin-backed user-wide build cache may recover entries through a different route, trust posture, and cost bearer than today’s Cargo-home download/source caches.
