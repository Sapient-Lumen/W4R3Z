# Python surface — rev0022

Active new modules:

```text
src/i2p_dht_lab/parseguard.py
src/i2p_dht_lab/validatorwall.py
src/i2p_dht_lab/antientropy.py
src/i2p_dht_lab/surfaceindex.py
```

Active new test:

```text
tests/test_rev0022_antientropy_validatorwall_parseguard.py
```

Risk-first behaviors tested:

- canonical bdecode rejection and bounded parsing,
- validator-wall role/kind/scope/body/flag checks,
- validator-window request-id conflict detection,
- anti-entropy source-family pressure,
- same-sequence fork detection,
- tombstone-first repair planning,
- expired/bad-signature summary rejection,
- current surface-index audit.
