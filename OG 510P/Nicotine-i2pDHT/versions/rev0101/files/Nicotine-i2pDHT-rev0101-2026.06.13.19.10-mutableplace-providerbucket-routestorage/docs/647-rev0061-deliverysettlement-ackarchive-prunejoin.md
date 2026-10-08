# rev0061 — deliverysettlement-ackarchive-prunejoin

rev0061 moves one seam after rev0060's live-send gate, delivery witness, and send fence.

The new risk-first boundary is:

```text
live-send gate accepted
+ delivery witness accepted
+ send fence accepted
    != settled delivery
    != archived restart memory
    != safe evidence pruning
```

New active surfaces:

```text
src/i2p_dht_lab/deliverysettlement.py
src/i2p_dht_lab/ackarchive.py
src/i2p_dht_lab/ackprunejoin.py
src/i2p_dht_lab/ackfold.py
tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py
```

Strong sentence:

```text
Delivered-looking public-edge evidence is not settled, archived, or prunable until each step binds to the same exact boundary.
```

The cube remains no-network.  No live SAM/I2P transport is attempted.
