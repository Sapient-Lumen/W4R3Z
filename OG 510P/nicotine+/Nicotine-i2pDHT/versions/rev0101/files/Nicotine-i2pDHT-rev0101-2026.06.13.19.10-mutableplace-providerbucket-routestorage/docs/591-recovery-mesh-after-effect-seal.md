# Recovery mesh after effect seal

`recoverymesh.py` joins the accepted effect seal with restart-chaos evidence, seal-replay observations, and corpus-witness receipts. This prevents a component-local success from advancing sticky post-restart state alone.

The mesh can accept committed recovery, accept aborted recovery, accept with watch, hold repair, or quarantine drift. The important rule is that profile, service, scope, request, payload, idempotency, phase, component digest, and hard-negative pressure remain typed until the exact boundary agrees.

`sealreplay.py` is part of this lane: it records restart-generation observations so a committed effect is not later treated as an aborted effect or vice versa without local evidence of a fork/rollback.
