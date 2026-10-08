# Scenario — grouped optional dependencies hide internal switches from public surface

Focus: a public feature like `avif` groups optional dependencies with `dep:` so downstream users see one supported switch, not several accidental internal toggles.

Feature-surface reading: `avif` is part of the public contract; `ravif` and `rgb` are hidden optional dependencies and should not masquerade as separately supported public features.
