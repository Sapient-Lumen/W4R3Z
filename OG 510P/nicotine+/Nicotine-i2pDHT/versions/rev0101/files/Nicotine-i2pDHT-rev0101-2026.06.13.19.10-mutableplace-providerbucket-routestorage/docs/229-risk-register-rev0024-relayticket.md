# Risk register — rev0024 relayticket/gossipsieve/clockguard

Known risks intentionally left open:

- Clock guard is local policy, not clock consensus.
- Family labels remain hints, not independence proof.
- Relay tickets constrain capacity use but do not make relay use private.
- Gossip sieve admits hints for later work; it does not prove semantic truth.
- Replay memory is local and can be lost unless persisted.
- Branchlet fold audits a named set of surfaces, not every historical file.
- No live I2P/SAM behavior is measured in this cube.
- No anonymity or metadata-safety guarantee is made.

Riskiest next tests:

- queue scheduling where relay tickets, gossip hints, witness receipts, and provider probes compete for bounded garden capacity;
- cover-work planning where decoys do useful maintenance instead of random noise;
- replay memory persistence after restart;
- gossip capture under route-attestation and contact-lease collapse;
- relay ticket misuse by valid but compromised garden families.
