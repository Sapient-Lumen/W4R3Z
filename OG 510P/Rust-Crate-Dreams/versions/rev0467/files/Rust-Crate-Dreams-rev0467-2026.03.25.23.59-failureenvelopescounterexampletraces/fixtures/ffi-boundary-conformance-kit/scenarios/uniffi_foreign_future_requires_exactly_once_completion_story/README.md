# Scenario — UniFFI foreign future requires exactly-once completion and optional dropped-future cancellation

This scenario models UniFFI's async foreign-callback contract.

Why it exists:
- the callback surface is native to UniFFI's async FFI lane,
- completion is not “some callback eventually” but an **exactly-once** `complete_func` obligation,
- cancellation is optional and wired through a dropped-future callback,
- and the docs explicitly warn that the dropped callback may run after task completion.

The point is to keep authority, completion, and lifecycle separate instead of flattening them into “async callbacks supported”.
