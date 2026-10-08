# Scenario: source replacement or vendor mirror is not fork progress by itself

This fixture keeps source-route semantics honest.

A vendored or mirrored source may be a real operational choice,
but Cargo's source-replacement model assumes the code is the same on both sides.
That does not by itself prove owned-fork readiness or architectural replacement progress.
