# Scenario — Subsecond rewind retires one hot call path, not the whole process

Subsecond documents that an actively called hot function can rewind the stack to the “cleanest” hot entrypoint and retry there.
That is a meaningful retirement boundary, but it is still **anchor-scoped** rather than a proof that every route in the process retired the older generation.
