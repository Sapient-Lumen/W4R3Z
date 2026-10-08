# Router canary public-edge boundary

`routercanary.py` is a no-network pressure surface for the last router/session assumption before a future public bridge write. It is deliberately not a SAM probe and does not open sockets.

It tests whether the router-facing facts still bind to the same public-edge tuple:

```text
profile / service / action
scope / request / payload / frame
SAM canary report / router harness report / outbox drain report
session id / I2P Destination / SAM endpoint / router profile digest
persistent Destination state / transit enabled / no accidental proxy exposure
sequence / previous digest / family / path family
```

The risky guesses tested first are the easy-to-miss ones: a bundled router accidentally starts with ephemeral Destination state, a public bridge refresh silently disables transit, an HTTP/SOCKS proxy is exposed by a testing profile, or a stale observation from a previous session is replayed into a fresh publication boundary.

A valid router canary remains only local evidence. It does not prove that a router is healthy on the live I2P network.
