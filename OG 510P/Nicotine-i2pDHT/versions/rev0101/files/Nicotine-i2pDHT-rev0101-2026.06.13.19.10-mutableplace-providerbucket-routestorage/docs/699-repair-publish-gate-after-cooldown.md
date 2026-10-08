# Repair publish gate after cooldown

`repairpublishgate.py` models the first boundary after a repair outbox is staged.  It refuses to treat `repair_outbox.staged` as publication permission.

The gate checks:

- the repair outbox and conflict cooldown bind to the same profile, service, scope, request, payload, and idempotency key;
- the outbox is accepted and staged;
- the cooldown has not been benignly released;
- the cooldown explicitly allows repair;
- markers are previous-linked and sequence-monotonic;
- marker component digests match;
- family/path diversity exists;
- hard-negative pressure is absent.

This is a no-network surface.  It decides only whether repair publication is locally ready to be considered by a future outbox/SAM path.

Audit needle: repair publish gate.
