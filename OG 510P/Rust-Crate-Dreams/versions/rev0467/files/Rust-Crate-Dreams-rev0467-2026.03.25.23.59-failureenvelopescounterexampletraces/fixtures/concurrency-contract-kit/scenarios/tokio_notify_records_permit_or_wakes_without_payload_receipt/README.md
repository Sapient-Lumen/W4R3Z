# Scenario: Tokio `Notify` records a permit or wakes waiters without payload receipt

This scenario exists to prove that wake-oriented acceptance is its own class.

Current docs say `Notify` carries no data, `notify_one()` makes a permit available, and `notify_waiters()` wakes current waiters without storing a future permit.

The fixture should fail any classifier that treats notify success as payload delivery or later observation proof.
