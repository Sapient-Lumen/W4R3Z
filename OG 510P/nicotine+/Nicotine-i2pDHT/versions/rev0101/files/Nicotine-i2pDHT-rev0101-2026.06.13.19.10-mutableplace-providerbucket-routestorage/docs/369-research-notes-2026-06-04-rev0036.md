# Research notes — 2026-06-04 — rev0036

Relevant external constraints carried into this revision:

- SAM remains the likely non-Java integration surface, and current I2P SAM docs recommend explicitly selecting modern signature types such as Ed25519 rather than inheriting old defaults.
- i2pd exposes a SAM bridge configuration surface, usually on localhost port 7656, so a bundle-first harness needs to keep SAM local and explicit.
- A future real router manager must preserve router data and destination identity; rev0036 still models this only as local capsules and reports.

No new production protocol is claimed from these notes.
