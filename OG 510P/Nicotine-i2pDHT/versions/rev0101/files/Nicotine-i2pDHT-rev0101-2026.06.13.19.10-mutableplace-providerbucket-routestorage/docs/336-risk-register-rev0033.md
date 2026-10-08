# Risk register — rev0033

Still risky:

- feature negotiation is a toy model;
- source/path family hints are lab labels, not measured independence;
- migration is an atom-level toy, not a database migration engine;
- soft-drop policy is underspecified;
- safe-start currently trusts report digests and cannot yet reconstruct every underlying scope boundary;
- no live I2P/SAM transport exists;
- no production DHT exists.

Newly pinned risks:

- downgrade attacks;
- namespace-policy mismatch;
- state migration dropping hard negatives;
- migration scope widening;
- migration sequence rollback;
- safe-start accidentally treating a component report as a joined permission.
