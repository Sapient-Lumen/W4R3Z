# Scenario: Tokio `Notify::notify_waiters` reaches all current waiters without future subscription

This scenario exists to prove that **delivery audience** is not the same thing as stored memory or future subscription.

Current docs say `notify_waiters` notifies **all waiting tasks**, but unlike `notify_one`, it stores **no** permit for later calls to `notified().await`.

So the honest support story is:

- current already-registered waiters are in the audience,
- future waiters are not retroactively included,
- and this is not a payload-claim channel at all.

The fixture should fail any classifier that turns this into a queue, broadcast history, or “all future waiters also get it” claim.
