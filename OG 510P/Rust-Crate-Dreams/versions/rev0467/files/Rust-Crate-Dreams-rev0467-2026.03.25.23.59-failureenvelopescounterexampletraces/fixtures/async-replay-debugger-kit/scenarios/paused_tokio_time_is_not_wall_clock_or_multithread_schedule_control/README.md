# paused Tokio time is not wall-clock or multi-thread schedule control

This scenario captures a test harness running on Tokio's paused `current_thread` time.
The important truth is that frozen/auto-advanced test time is useful and real, but narrower than generic incident replay.

What the receipts should prove:

- that the clock class is `tokio_paused_time`,
- that auto-advance rules are explicit,
- and that this does not over-claim multi-thread schedule control or wall-clock fidelity.
