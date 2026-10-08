# Negative-space absence pressure

`negspace.py` models signed absence observations for risky DHT answers:

- no provider
- no mutable head
- no route
- no tombstone
- no custody

The core rule is that **absence is not proof**. A fast captured path can say "nothing exists" and cause the lookup to stop. The module therefore asks for typed target/request binding, responder-family diversity, path-family diversity, short TTLs, and positive-evidence contradiction checks.

A valid absence observation can still be rejected or quarantined for:

- bad signature
- expiry
- contradiction by positive evidence
- same-responder same-sequence fork
- responder-family flood
- low responder-family diversity
- low path-family diversity

This becomes especially important around provider lookups and mutable heads, where a stale or empty answer can be just as damaging as a false positive.
