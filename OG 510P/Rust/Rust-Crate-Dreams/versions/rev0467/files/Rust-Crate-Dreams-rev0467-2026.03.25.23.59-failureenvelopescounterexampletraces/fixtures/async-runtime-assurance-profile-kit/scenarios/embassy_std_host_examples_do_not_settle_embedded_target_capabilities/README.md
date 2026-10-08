# Scenario — Embassy std host examples do not settle embedded target capabilities

This scenario exists to stop one easy overread:

> “Embassy runs on the PC, therefore the runtime-support story is settled for the embedded target.”

The Embassy book says PC `std` examples exist, while Embassy executor docs still center static-task, no-`alloc`, embedded execution.
That means one family can span multiple deployment lanes without one uniform capability claim.

The receipt keeps:

- host/example lane,
- target/firmware lane,
- runtime family,
- and support level

separate.
