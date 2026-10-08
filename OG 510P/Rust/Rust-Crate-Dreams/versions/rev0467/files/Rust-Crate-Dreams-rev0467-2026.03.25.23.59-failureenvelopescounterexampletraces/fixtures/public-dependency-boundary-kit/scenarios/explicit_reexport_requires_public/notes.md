# Scenario: `explicit_reexport_requires_public`

A facade crate reexports items from a dependency.
The bundle should classify the dependency as effectively public and recommend making manifest intent explicit.
