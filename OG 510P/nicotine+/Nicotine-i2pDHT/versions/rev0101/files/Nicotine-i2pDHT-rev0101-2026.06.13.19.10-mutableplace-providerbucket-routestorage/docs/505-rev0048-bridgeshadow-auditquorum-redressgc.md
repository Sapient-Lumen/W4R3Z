# rev0048 — bridgeshadow-auditquorum-redressgc

This revision stays no-network and risk-first.  The active seam is the moment after a public bridge publication guard/ledger/quench path appears locally acceptable, but before a future node would perform an externally visible publication, withdrawal, repair, mutable-head write, or garden mirror request.

The new rule is:

```text
A public bridge side effect is not safe because its parts passed; it is safe only when the dry-run plan, audit evidence, and retained redress memory bind to the same exact boundary.
```

## New surfaces

- `bridgeshadow.py` signs a no-network public bridge shadow plan and joins publication guard, publication ledger, and bridge quench reports before a later side effect can be considered locally eligible.
- `auditquorum.py` models scoped audit statements as local evidence.  It rejects replay, contradiction, missing required statement kinds, low family/path diversity, drift, and hard-negative scans.
- `redressgc.py` models redress/evidence cleanup without letting soft cleanup erase hard negatives.
- `bridgeshadowfold.py` pins rev0048 through source, tests, docs, public pointers, fold map, fold registry, surface ledger, and the rev0047 `publicationfold` predecessor.

## What changed in tests

The active test file is `tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py`.  It pins:

- bridge-shadow acceptance from diverse, component-bound dry-run plans;
- watch/quench holds before shadow acceptance;
- replay, scope drift, and same-sequence fork detection;
- audit-quorum acceptance with required statement kinds and diversity;
- audit replay, contradiction, and low-diversity holds;
- redress GC dropping expired soft evidence while retaining hard negatives;
- hard-negative byte-budget refusal and live watch-debt holds;
- current-revision fold/audit visibility.

## Nonclaims

No live I2P/SAM transport, no production DHT, no production audit quorum, no production public bridge publication protocol, no production redress database, no global ban list, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.

rev0048 bridgegovernancefold canonical audit anchor: bridgegovernancefold joins bridgeshadow, auditquorum, and redressgc while preserving shadowauditfold branchlet history.
