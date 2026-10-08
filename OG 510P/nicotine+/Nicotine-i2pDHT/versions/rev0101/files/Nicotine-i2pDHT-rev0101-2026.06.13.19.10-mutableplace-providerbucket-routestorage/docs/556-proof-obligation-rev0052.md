# Proof obligation — rev0052

Before a future live public-edge implementation, the cube should be able to show:

1. The live adapter plan binds exactly one profile, service, scope, request, payload, session, Destination, caller, and handler.
2. Backpressure joins inbound, outbound, router, reserve, metadata, refusal-loop, and hard-negative pressure.
3. Profile-edge capsules reject generation rollback and hard-negative pressure.
4. Fold/audit metadata points to the active code, tests, and docs.
5. No test treats a valid signature as sufficient when component scope or mode drifts.

rev0052 implements the first toy version of those obligations.
