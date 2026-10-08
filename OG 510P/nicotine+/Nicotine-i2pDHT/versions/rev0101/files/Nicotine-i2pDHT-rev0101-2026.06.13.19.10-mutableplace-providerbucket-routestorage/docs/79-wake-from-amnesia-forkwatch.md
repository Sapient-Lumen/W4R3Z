# Wake from amnesia — rev0009

You are inside `forkwatch-capgrant-chaosloom`.

## Scope

Still a Python-first DHT design cube over I2P.  No live I2P/SAM transport.  No production DHT.  No application integration.

## What changed

The cube stopped treating mutability as a dream ledger only.  It now tests the hardest mutable-name guesses first:

```text
history-aware heads
local monotonic memory
same-sequence fork evidence
rollback evidence
signed garden witness receipts
capability delegation
revocation heads
fake lookup chaos
```

## Key files

- `src/i2p_dht_lab/headlog.py`
- `src/i2p_dht_lab/capability.py`
- `src/i2p_dht_lab/chaos.py`
- `tests/test_headlog_capability_chaos.py`
- `docs/72-rev0009-risk-first-mutability.md`
- `docs/73-not-ipns-history-aware-heads.md`
- `docs/74-capability-grants-and-revocation-heads.md`
- `docs/75-fake-chaos-transport-and-forkwatch.md`
- `docs/76-garden-witness-receipts.md`

## Current strongest sentence

```text
A valid mutable head is only an observation; acceptance requires local history.
```

## Next turn guess

rev0010 should add seed/policy portfolio capture simulation, revocation-head rollback tests, garden witness poisoning tests, and path-isolated lookup pressure around mutable heads.
