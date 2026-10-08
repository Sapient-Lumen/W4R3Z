# Scenario: portable bundle keeps delivery audience and claim semantics separate

This scenario exists to prove that a concurrency-support bundle should keep:

- who is in the audience,
- what one observer claiming the unit does to others,
- what memory exists,
- and what pressure happens under load

as separate artifacts.

The fixture should fail any bundle that collapses those into a single “channel behavior” bit.
