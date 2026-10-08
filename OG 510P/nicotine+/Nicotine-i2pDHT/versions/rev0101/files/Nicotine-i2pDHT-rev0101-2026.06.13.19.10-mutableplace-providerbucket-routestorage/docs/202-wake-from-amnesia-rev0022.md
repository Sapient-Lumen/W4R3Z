# Wake from amnesia — rev0022

Remember this sentence first:

```text
Signed bytes are not yet typed, fresh, scoped, or safe to parse.
```

rev0022 starts hardening the control-plane boundary before live I2P transport exists.

Start here:

1. `docs/196-rev0022-antientropy-validatorwall-parseguard.md`
2. `docs/197-parseguard-canonical-decode-pressure.md`
3. `docs/198-validator-wall-before-dispatch.md`
4. `docs/199-anti-entropy-summary-pressure.md`
5. `docs/200-surface-index-audit-refactor.md`
6. `tests/test_rev0022_antientropy_validatorwall_parseguard.py`

The DHT still does not claim production behavior.  The value is executable pressure around parser ambiguity, semantic dispatch confusion, anti-entropy rollback, tombstone repair, and current-surface navigation.
