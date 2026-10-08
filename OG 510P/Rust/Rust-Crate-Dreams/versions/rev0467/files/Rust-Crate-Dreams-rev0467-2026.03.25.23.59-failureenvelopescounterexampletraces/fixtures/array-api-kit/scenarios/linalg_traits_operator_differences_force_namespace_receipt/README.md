# Scenario — `linalg-traits` proves generic matrix support still needs namespace coverage

`linalg-traits` is excellent prior art, but its docs explicitly say `ndarray` overloads `*` for elementwise multiplication while `nalgebra` overloads `*` for matrix multiplication.
That means a generic “matrix support” claim is too vague.
The right move is to publish a `namespace-coverage.receipt` that says which operation namespaces are exact, partial, or extension-only.
