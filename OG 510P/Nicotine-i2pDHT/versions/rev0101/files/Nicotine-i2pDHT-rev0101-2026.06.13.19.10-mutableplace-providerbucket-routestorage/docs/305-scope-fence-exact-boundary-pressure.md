# Scope fence exact-boundary pressure

`ScopedClaim` is a small signed observation carrying:

- actor public key
- scope id
- object digest
- request id
- purpose
- source/path family hints
- sequence and validity window

`assess_scope_fence` rejects signature failure, expiry, scope mismatch, object mismatch, request mismatch, purpose mixing, source-family flood, and same-actor same-sequence forks.

The guess: exact matching feels boring, but boring exact matching is how we stop evidence from becoming a cross-protocol coupon.
