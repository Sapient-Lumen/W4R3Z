# redteamfold audit/refactor

`redteamfold.py` is the rev0051 fold audit. It does not introduce protocol truth; it keeps the cube navigable while the speculative surface grows.

It checks that the current rev0051 paths exist:

```text
src/i2p_dht_lab/routercanary.py
src/i2p_dht_lab/ingressdrain.py
src/i2p_dht_lab/redteamfold.py
tests/test_rev0051_ingressdrain_routercanary_redteamfold.py
docs/534-rev0051-ingressdrain-routercanary-redteamfold.md
docs/535-router-canary-public-edge.md
docs/536-ingress-drain-public-bridge.md
docs/537-redteamfold-audit-refactor.md
```

It also checks public-surface needles, fold map, fold registry, surface ledger, and the rev0050 `drainfold` predecessor. The important refactor is not deletion; it is making the active path visible while keeping historical wake-from-amnesia surfaces available.
