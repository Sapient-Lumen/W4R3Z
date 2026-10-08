# Proof obligation — rev0033

Before a future live peer session can start, the cube now wants evidence for:

1. highest shared protocol version or an explicit downgrade exception;
2. required feature intersection;
3. namespace-policy digest agreement;
4. frame budget sufficiency;
5. preserved hard-negative local memory after migration;
6. no scope widening during migration;
7. no sequence rollback during migration;
8. accepted SAM-shadow trace;
9. joined safe-start report.

The proof obligation remains local. It is not global consensus and not a peer identity truth system.
