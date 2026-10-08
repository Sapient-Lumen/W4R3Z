# Scenario: prototype tools can depend widely but control core must stay restricted

This scenario keeps the main P-0535 distinction explicit:
- a prototype or diagnostics tool may use many outside crates,
- a restricted control core may not.

The point is not “few dependencies good”.
The point is **lane-specific placement truth**.
