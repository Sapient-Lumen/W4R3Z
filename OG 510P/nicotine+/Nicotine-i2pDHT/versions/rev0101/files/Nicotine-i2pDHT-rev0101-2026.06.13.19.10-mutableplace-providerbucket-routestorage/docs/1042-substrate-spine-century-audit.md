# Substrate spine and rev0100 audit

rev0100 adds `substratespine.py` so the post-native substrate line is visible as a chain rather than as isolated one-off modules.

Current substrate spine:

```text
rev0099 -> substratereentry / substratereturnfold
rev0100 -> recordingress / providersemantics / routinganchor / substratecenturyfold
```

`substratecenturyfold.py` audits the rev0100 path, the rev0099 predecessor, fold map, fold registry, surface ledger, and wake-from-amnesia anchors.

The audit/refactor intent is to start a new spine for generic I2P DHT substrate work now that the long GCC/native thread is closed as shadow-only.
