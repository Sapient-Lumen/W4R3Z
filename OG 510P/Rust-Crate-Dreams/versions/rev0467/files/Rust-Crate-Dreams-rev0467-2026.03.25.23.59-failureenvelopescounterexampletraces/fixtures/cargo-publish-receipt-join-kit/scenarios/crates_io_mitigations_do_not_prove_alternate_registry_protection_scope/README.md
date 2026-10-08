# crates.io mitigations do not prove alternate-registry protection scope

This scenario freezes another overclaim:

> “Because crates.io blocked a vulnerable upload pattern and audited previously published crates, our alternate-registry release lane must have been protected too.”

The point is to keep **protection scope** separate from:

- the existence of a public advisory,
- crates.io-specific mitigation actions,
- and coarse trust in “Cargo publishing” as one uniform surface.
