# Risk register — rev0042

Implemented risk probes:

- shared-router stop while sibling services remain active;
- public bridge exposure left active during shared-router stop;
- emergency freeze bypass by a single fresh resume signal;
- operator-key rotation without successor cosign;
- operator-key recovery without witness-family diversity;
- hard-negative drop during operator-key recovery;
- stale public announcement after bridge disable;
- successor catalog rollback/fork during repair;
- current surface visibility drift.

Still open:

- real router/i2pd/SAM behavior;
- durable key-management and local-database formats;
- multi-service scheduling with real load;
- production bridge announcement propagation;
- production operator-key recovery UX;
- stronger fold-registry consolidation.
