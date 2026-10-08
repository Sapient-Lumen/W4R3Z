# Scenario: Tokio `Notify::notify_waiters` has no future-joiner memory

This scenario exists to prove that reaching all current waiters is not the same thing as admitting future joiners to a stored wake.

Current docs say `notify_waiters` notifies all waiting tasks and stores no permit for the next call to `notified().await`.

The fixture should fail any classifier that turns this into stored-permit memory for future waiters.
