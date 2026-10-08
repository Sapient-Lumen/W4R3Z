# Cross-case memo — attribution traps and hidden software state

The rev0011 records share a question, not an identity.

In Therac-25, internal machine state and software interlock behavior could not be safely inferred from operator-facing signals. In Horizon, branch-accounting outputs and alleged shortfalls became evidence against people who did not have equal access to the system’s internal state, audit trail, or defect knowledge. In Dieselgate, official test behavior looked compliant because the software detected the test and altered behavior.

This creates the candidate pattern: software opacity can create attribution traps. The false witness is not necessarily intentional; in Dieselgate it was deliberate, in Horizon it became institutional/legal, and in Therac it emerged through safety design and feedback failure.

The pattern is not mature. It needs successful-control records: systems with strong audit trails, independent interlocks, adversarial regulator tests, or user-accessible state that prevented wrongful attribution.
