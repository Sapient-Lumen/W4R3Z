# Scenario — GDB versioned pretty-printer package drift is not plain asset failure

This scenario keeps one subtle GDB truth visible.
Current GDB guidance recommends versioned Python package names so multiple library versions can coexist and register pretty-printers against the correct objfile.

That means a release-to-release change in printer package naming or objfile-registration assumptions may be **comparison-basis drift** rather than “asset stopped working”.
This fixture shows how to classify that honestly.
