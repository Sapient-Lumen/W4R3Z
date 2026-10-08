# Moderation quarantine as allegation

`moderationquarantine.py` models signed scoped reports for bridge abuse, false service, flooding, key compromise, policy violation, and retraction.

The key rule is deliberately uncomfortable: a locally accepted report can become local quarantine pressure, but it cannot invalidate a key globally or decide DHT truth. The report must pass signature, scope, service, target, policy, replay, sequence, previous-link, reporter-key, family, and path pressure before it becomes usable evidence.

This lane exists because public entrances are an abuse surface. It also exists because abuse tooling can become a capture surface. The cube keeps those facts together.
