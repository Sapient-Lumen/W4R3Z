# Tokio `watch::Receiver::changed` true cancel safety keeps seen-state truth

This scenario exists to show that some waits have stronger cancellation guarantees than queue-based waiters.

`changed` documents that cancellation in a `select!` race does **not** mark a value seen.
The fixture protects against flattening true cancel safety into the same class as queue withdrawal.
