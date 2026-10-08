# Scenario: diagnostic message shift requires normalization receipt

This scenario keeps “diagnostic-only” verdicts honest.

The new solver’s proof-tree and canonicalization model can change message shape, note ordering, and spans even when the semantic verdict is unchanged.
A bundle should not call this case diagnostic-only without recording the normalization policy first.
