# Python surface rev0070

Active rev0070 implementation surfaces:

```text
src/i2p_dht_lab/exportreceipt.py
src/i2p_dht_lab/retentiongc.py
src/i2p_dht_lab/closurehandoff.py
src/i2p_dht_lab/exporthandofffold.py
tests/test_rev0070_exportreceipt_retentiongc_handoff.py
```

The modules are intentionally toy/no-network.  They pin the local decision algebra before any live public write, garden handoff, or operator export pathway exists.
