# Scenario — workspace-private pack requires redaction before public export

This scenario captures a pack that is already good enough to help maintainers inside one workspace or organization, but still cannot be honestly frozen as a public downstream contract because it carries local paths, internal package aliases, and working notes.

It proves that:
- pack maturity and public export posture are not the same truth,
- audience/exposure scope should stay exact instead of collapsing to vague “shareable” language,
- and redaction debt should block public export explicitly rather than hiding inside notes.
