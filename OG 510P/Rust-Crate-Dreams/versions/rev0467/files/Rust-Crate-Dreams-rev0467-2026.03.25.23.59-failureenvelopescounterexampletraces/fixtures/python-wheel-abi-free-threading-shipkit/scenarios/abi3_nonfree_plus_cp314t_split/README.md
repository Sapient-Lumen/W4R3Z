# Scenario: abi3 release plus cp314t split wheel family

This scenario models a project that uses `abi3` wheels for ordinary CPython releases but must still publish separate `t` wheels for the free-threaded build.

It exists to resist a common false conclusion:

> “We already ship `abi3`, therefore free-threaded Python is automatically covered.”

The expected outcome is an explicit `split_free_threaded` ABI target report rather than a fake single-ABI verdict.
