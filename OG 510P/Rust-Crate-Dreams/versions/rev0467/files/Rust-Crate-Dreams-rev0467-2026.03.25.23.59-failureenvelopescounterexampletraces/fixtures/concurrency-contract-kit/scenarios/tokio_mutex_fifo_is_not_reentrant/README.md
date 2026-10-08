# Tokio `Mutex`: FIFO ordering is not a reentrancy claim

This scenario freezes a common confusion:
Tokio `Mutex` documents fair queueing, but that is not the same thing as recursive re-entry support.

The scenario keeps three claims separate:
- reentrancy scope,
- progress/fairness class,
- execution-context legality.
