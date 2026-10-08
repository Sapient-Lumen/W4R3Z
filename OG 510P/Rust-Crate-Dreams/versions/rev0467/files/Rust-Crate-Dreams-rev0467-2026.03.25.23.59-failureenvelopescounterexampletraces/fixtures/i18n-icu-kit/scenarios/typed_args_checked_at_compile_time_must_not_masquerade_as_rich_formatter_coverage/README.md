# Scenario: typed args checked at compile time must not masquerade as rich formatter coverage

This scenario keeps two truths separate:

- the message contract may be compile-time checked for argument names and requiredness,
- while formatter coverage may still be only plain substitution with no ICU4X-backed date/list/relative-time support.

That distinction matters because many existing crates prove there is demand for typed messages, but the existence of typed args does not itself prove rich locale-aware formatting coverage.
