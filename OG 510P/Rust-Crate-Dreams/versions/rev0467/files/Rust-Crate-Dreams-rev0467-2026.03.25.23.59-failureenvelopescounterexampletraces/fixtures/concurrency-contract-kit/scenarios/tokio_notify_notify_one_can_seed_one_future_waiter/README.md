# Scenario: Tokio `Notify::notify_one` can seed one future waiter

This scenario exists to prove that join-start semantics apply even to wake primitives.

Current docs say that if no task is waiting, one permit is stored and the next call to `notified().await` completes immediately consuming that permit.

The fixture should fail any classifier that turns this into queued wake history, current-waiters-only behavior, or unlimited future wake memory.
