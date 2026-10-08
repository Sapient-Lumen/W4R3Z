# Scenario: pymodule gil_used=true requires runtime opt-out note

This scenario models a PyO3 module that explicitly opts out of free-threaded support with `#[pymodule(gil_used = true)]`.

It exists to resist a common false conclusion:

> “The wheel loads on a free-threaded interpreter, therefore the project supports free-threaded execution.”

The expected outcome is a thread-support report that keeps the opt-out and manual-review boundary explicit.
