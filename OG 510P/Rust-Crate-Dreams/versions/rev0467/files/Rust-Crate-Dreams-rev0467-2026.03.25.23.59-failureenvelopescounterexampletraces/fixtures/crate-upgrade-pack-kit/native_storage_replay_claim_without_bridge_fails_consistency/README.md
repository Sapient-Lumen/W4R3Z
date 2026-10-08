# Scenario — native-storage replay posture is claimed but no replay bridge exists

This scenario freezes a contradiction the pack should reject:

- capture context says imported evidence is replayable from native storage,
- but the bundle never records the actual replay route, attachment posture, or fidelity expectation.

The pack should fail consistency rather than let readers infer a replay path from a posture label alone.
