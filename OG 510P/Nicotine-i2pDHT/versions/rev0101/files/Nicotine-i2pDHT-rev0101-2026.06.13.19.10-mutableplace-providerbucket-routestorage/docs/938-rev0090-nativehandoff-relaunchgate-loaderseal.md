# rev0090 — nativehandoff-relaunchgate-loaderseal

rev0090 continues the native/GCC branch without expanding native authority. The seam after rev0089 is not loading; it is **relaunch candidacy**.

```
native cold-start accepted
+ probe corpus refreshed
+ loader-GC preserved tombstones
    ≠ safe load
    ≠ safe dispatch
    ≠ safe relaunch memory
```

The revision adds three no-network gates:

- `nativehandoff.py`: converts cold-start/probe/loader-GC evidence into a fallback-active relaunch candidate while forbidding load and dispatch.
- `relaunchgate.py`: requires prior native lanes to revalidate before a relaunch plan exists.
- `loaderseal.py`: writes restart-sticky seal evidence for relaunch candidates while preserving tombstone/fallback/quarantine/crash memory.

It also adds `nativefoldspine.py`, a small declarative audit spine for the native branch from rev0081 through rev0090. This is the audit/refactor lane for this turn: fewer one-off fold surfaces, more visible branch continuity.

Strong sentence:

> A restart-discovered native artifact may become a no-network relaunch candidate only after cold-start, probe corpus, loader-GC, prior-lane revalidation, and loader-seal memory agree while load and dispatch remain forbidden.

Current nonclaims remain: no live I2P/SAM transport, no production DHT, no production native loader/ABI/sandbox, no native parser/crypto, no production supply-chain security, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
