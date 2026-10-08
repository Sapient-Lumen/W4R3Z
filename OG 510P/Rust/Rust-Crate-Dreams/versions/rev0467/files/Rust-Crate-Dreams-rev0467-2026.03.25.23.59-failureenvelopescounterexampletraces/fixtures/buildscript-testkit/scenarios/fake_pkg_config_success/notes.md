# Scenario: fake pkg-config success

This scenario exists to prove that **P-0059** is useful even on the happy path.

The core value is not merely “did the script fail deterministically?” It is also “did the script emit the same linking and metadata contract as before?”

That is why the normalized directives artifact matters more than a raw golden log.
