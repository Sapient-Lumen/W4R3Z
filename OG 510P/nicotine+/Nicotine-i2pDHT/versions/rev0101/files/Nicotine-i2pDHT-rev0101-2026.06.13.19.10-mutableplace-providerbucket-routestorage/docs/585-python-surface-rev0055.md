# Python surface — rev0055

Primary code:

```text
src/i2p_dht_lab/restartchaos.py
src/i2p_dht_lab/effectseal.py
src/i2p_dht_lab/fuzzshrink.py
src/i2p_dht_lab/restartfold.py
```

Primary tests:

```text
tests/test_rev0055_restartchaos_effectseal_fuzzshrink.py
```

Design posture:

```text
restart chaos + effect seal + fuzz shrink
  -> no network
  -> local signed evidence
  -> exact-boundary joins
  -> audit-visible predecessor fold
```
