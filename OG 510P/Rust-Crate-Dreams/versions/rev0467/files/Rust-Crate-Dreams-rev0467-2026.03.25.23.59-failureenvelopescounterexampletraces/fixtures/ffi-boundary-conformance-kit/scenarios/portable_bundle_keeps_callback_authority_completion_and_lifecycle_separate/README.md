# Scenario — portable bundle keeps callback authority, completion, and lifecycle separate

This scenario shows the intended callback review handoff.

A downstream reviewer should be able to see:
- what defines the callback,
- how it executes,
- how it is registered/teardown-managed,
- and what completion/failure obligations remain,
without re-reading generator docs.
