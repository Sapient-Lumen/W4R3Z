# Package coherence gate — rev0074

`tools/audit_rev0074_package.py` verifies the linked revision as a self-consistent research cube, not merely as a readable ZIP.

It checks:

- the rev0074 identity and required current landing pages;
- exact-current PB-01 summary status, 12/12 classified expectations, and three-state upstream-unit parity;
- the current packet ledger and deterministic packet-status audit;
- archived PB-01 source hashes;
- compilation of every current rev0074 Python helper and active PB-01 module;
- absence of embedded upstream source, Git metadata, caches, bytecode, and symlinks;
- a complete SHA-256 manifest covering every packaged file except the manifest itself;
- consistency of the rev0073→rev0074 delta inventory.

The full unit lane excludes `test_i18n.py` only when the external `msgfmt` executable is unavailable. That exclusion is recorded per source state; it is not reported as a test pass.
