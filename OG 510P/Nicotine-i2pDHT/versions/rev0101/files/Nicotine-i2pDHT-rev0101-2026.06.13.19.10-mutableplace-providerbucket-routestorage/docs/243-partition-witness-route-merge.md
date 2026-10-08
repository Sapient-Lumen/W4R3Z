# Partition witness / route merge

`src/i2p_dht_lab/partitionwitness.py` wraps split-brain mutable epoch merge with route-gossip and witness-cache pressure.

`splitmerge.py` can say a candidate head is a valid linked advance. rev0026 adds a second local question:

```text
Did the route paths and witness cache give enough independent evidence to commit this merge now?
```

The module runs split-merge against a scratch copy of local memory first. It commits only after the route and witness gates pass. This avoids a bug class where a valid split-merge report mutates local memory before the rest of the evidence surface is checked.
