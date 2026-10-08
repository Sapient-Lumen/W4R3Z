# Scenario: Tokio `watch` receivers track seen state independently

This scenario exists to prove that **independent latest-state observation** is not the same as queue delivery or clone fanout of every send.

Current docs say each receiver independently tracks the last value seen by its caller.

The fixture should fail any classifier that turns this into exclusive message claim, full per-send broadcast history, or generic shared-state equivalence with no receiver-local seen state.
