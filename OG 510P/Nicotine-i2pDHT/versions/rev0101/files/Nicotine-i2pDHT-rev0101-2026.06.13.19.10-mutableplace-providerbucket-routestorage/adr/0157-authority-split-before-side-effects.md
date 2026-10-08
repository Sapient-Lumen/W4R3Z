# ADR 0157 — Authority split before side effects

Decision: a passed key compartment is not enough for sensitive work. Component reports must join at the same profile/scope/object/request boundary.

Reason: local reports are individually valid observations, not cross-boundary permissions.
