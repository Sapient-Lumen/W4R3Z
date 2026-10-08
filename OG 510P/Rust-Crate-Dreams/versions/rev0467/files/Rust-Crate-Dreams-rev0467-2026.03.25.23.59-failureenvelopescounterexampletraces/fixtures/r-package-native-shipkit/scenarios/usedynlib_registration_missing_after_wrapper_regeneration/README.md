# Scenario: `useDynLib` registration missing after wrapper regeneration

A package regenerated wrappers after changing the Rust export surface, but the final namespace/load contract never got refreshed into an explicit registration-aligned posture.
The shipkit should classify this as a registration-review problem, not as “good enough because wrappers exist.”
