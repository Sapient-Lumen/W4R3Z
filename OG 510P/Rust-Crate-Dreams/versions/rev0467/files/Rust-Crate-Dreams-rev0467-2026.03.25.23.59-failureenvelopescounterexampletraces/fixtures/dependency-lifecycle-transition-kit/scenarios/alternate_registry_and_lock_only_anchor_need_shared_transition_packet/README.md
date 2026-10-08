# Scenario: alternate registry and lock-only anchor need a shared transition packet

A build that remains green because of an existing lockfile and an alternate registry route is not the same thing as a stable shared lifecycle policy.
The kit should emit one transition packet that distinguishes current success from future clean-resolve durability.
