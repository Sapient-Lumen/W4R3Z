# Scenario — workspace patch override requires config-basis disclosure

This scenario freezes one remaining hidden-context bluff in upgrade support:

- the lane may look like an ordinary registry-backed upgrade review,
- but the actual evidence was produced under a checked-in `[patch]` override and repository config that change what Cargo resolved.

The pack should keep that override basis explicit so the result does not sound more portable or upstream-representative than it really is.
