# Scenario: Tokio `Handle::block_on` on `current_thread` is not driver-complete

This scenario proves that having a handle capable of `block_on` is not the same thing as driving timers and I/O.

The important facts are:
- `Handle::block_on` can be called,
- but on `current_thread` it does not drive the I/O or timer drivers,
- so work that depends on those drivers still needs some thread calling `Runtime::block_on`.
