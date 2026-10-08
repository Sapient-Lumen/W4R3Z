# rev0038 — servicecontinuity / branchfold

rev0038 folds the split rev0037 garden-service branchlets into one continuity boundary. The cube now treats catalog wire frames, service probes, withdrawals, relays, use gates, handoff, veiled receipts, service announcements, ingress, tickets, and service receipts as separate local observations that must agree before a future garden-service side effect advances sticky state.

Strong sentence:

```text
A service branch can pass locally while the combined service side effect is still unsafe.
```

New active code:

```text
src/i2p_dht_lab/catalogwire.py
src/i2p_dht_lab/serviceprobe.py
src/i2p_dht_lab/profilegcjoin.py
src/i2p_dht_lab/catalogsuccession.py
src/i2p_dht_lab/servicewithdrawal.py
src/i2p_dht_lab/servicerelay.py
src/i2p_dht_lab/serviceusegate.py
src/i2p_dht_lab/handofflane.py
src/i2p_dht_lab/receiptveil.py
src/i2p_dht_lab/servicecontinuity.py
src/i2p_dht_lab/servicecontinuityfold.py
```

The first nine modules are folded branchlet surfaces recovered from alternate rev0037 lines. `servicecontinuity.py` is the new joined boundary. `servicecontinuityfold.py` is the audit/refactor spine for the fold.

Current nonclaims remain firm: no live I2P/SAM transport, no production DHT, no production garden-service protocol, no production authorization/settlement/reputation protocol, no private retrieval guarantee, no mutable-head consensus, no global reputation, no Sybil/anonymity guarantee, and no Nicotine+ patch.
