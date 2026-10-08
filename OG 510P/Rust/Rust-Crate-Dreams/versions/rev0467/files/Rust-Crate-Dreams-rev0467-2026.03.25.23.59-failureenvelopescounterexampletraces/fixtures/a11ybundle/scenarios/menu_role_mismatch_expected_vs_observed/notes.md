# Scenario: menu role mismatch expected vs observed

An app emits a menu-button pattern that should expose `menuitem` descendants.
The platform capture shows generic buttons instead.

This scenario exists to prove that the lab can:

- compare expected semantics against observed platform truth,
- classify the delta as portable/platform-specific/manual-review-required,
- and keep backend capability notes visible.
