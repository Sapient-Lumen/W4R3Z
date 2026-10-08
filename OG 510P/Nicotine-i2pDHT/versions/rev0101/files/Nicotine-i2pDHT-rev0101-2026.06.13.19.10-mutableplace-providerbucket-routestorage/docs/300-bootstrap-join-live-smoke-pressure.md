# Bootstrap join and live-smoke pressure — rev0030

`bootstrapjoin.py` joins entrance evidence before a local bootstrap window can advance.  A peerbook view, live-probe report, negative-space/absence report, and egress-budget report are separate observations until they agree at the same local boundary.

The join is deliberately conservative:

- a diverse peerbook is not enough if live probes are absent;
- a live probe is not enough if the egress meter says the probe window was too revealing;
- a soft negative-space absence report delays bootstrap rather than proving non-existence;
- a clean SAM-shadow script must be bound to the same contact lease destination.

`livesmoke.py` remains a no-router smoke surface. It tests HELLO/session/send/reconnect assumptions without opening a SAM socket. The point is to pin destination binding and transcript mismatch behavior before a real i2pd or Java I2P router makes failures noisy.

Nonclaim: this is not a SAM client, not an I2P reachability proof, and not a production bootstrap protocol.
