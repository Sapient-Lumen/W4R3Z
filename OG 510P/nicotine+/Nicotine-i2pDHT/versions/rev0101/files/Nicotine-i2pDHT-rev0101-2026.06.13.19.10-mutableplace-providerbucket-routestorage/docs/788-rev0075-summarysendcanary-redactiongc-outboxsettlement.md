# rev0075 — summarysendcanary-redactiongc-outboxsettlement

This revision folds the sibling rev0074 `summarysettlement-publicledger-redactiongc` branchlet into the active rev0074 `summaryoutbox-redactionarchive-publishfence` line.

The risky seam is now:

```text
summary outbox staged
+ redaction archive remembered
+ publish fence accepted
+ summary settlement/public ledger/redaction GC branch accepted
    ≠ safe summary send canary
```

The new local rule is:

```text
Two plausible public-summary branches do not authorize each other until their component digests, boundary, redaction memory, contradiction memory, and family/path diversity agree.
```

New active code:

```text
src/i2p_dht_lab/outboxsettlement.py
src/i2p_dht_lab/summarysendcanary.py
src/i2p_dht_lab/summarysettlement.py
src/i2p_dht_lab/publicledger.py
src/i2p_dht_lab/redactiongc.py
src/i2p_dht_lab/summarysendfold.py
```

`summarysendcanary.py` remains no-network. It does not send over SAM/I2P and does not publish anything. It only models the next exact-boundary permission before a future public-summary write could be attempted.
