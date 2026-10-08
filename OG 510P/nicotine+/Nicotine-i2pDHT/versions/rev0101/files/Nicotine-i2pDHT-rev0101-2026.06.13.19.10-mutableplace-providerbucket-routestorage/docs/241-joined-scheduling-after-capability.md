# Joined scheduling after capability

`src/i2p_dht_lab/schedjoin.py` joins `capgate.py` and `queueforge.py`.

The risky mistake it tests is treating a successful capability/admission result as permission to immediately spend scarce garden capacity. rev0026 models a second boundary:

```text
namespace + capability + admission accepted
  -> queue admission still required
  -> protected control-plane work must survive bulk work
  -> useful refusals are evidence, not work success
```

The test surface checks that protected head/witness work starts before bulk provider work, revoked work never reaches the queue, and repeated useful-refusal observations from one family can become refusal-laundering pressure.
