# Scenario: focus order regression

A toolbar rerender introduces a non-deterministic node order.
Keyboard traversal still reaches all controls, but the order changes from the blessed baseline.

This scenario exists to prove that the kit can:

- emit a semantic diff for traversal order,
- preserve this as a warning or fail depending on policy,
- and keep the output small enough for CI or issue reports.
