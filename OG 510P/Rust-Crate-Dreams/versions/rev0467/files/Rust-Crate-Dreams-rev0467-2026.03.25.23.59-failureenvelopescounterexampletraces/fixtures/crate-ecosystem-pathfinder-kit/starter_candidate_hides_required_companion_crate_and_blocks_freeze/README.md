
# Scenario — starter candidate hides required companion crate and blocks freeze

This scenario exists to show that a candidate can rank highly yet still be **not freeze-ready**.
If the pathfinder pack discovers that the advertised starter answer only works with an unstated companion crate, runtime, or support package, the freeze step should stop and emit a readiness report rather than silently lock the incomplete answer.
