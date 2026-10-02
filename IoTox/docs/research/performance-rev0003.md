# rev0003 Small Circles performance record

**Revision:** rev0003  
**Codename:** Small Circles, One Home  
**Environment:** Linux x86-64 cloud container, GCC 14.2.0 release build  
**Purpose:** descriptive microbenchmark evidence, not a network or embedded claim

Command:

```sh
./build/gcc-release/iotox_bench \
  --nodes 30 --namespaces 200000 --rounds 5
```

Retained result:

```text
nodes=30
namespaces-per-round=200000
rounds=5
cube-build-ns-per-op=1374.27
cube-build-ops-per-second=727656.93
custodian-select-ns-per-op=1604.25
custodian-select-ops-per-second=623343.67
head-evaluate-ns-per-op=41.88
head-evaluate-ops-per-second=23875091.63
checksum=9326512983994446362
```

The benchmark includes deterministic Cube construction, fixed-capacity three-custodian
selection, and linked-head progression evaluation. It excludes toxcore, sockets,
cryptographic signatures, cryptographic hashing, encryption, storage, gossip queues,
file transfer, authorization, and power behavior.

The companion topology demo for thirty members reports:

```text
maximum degree:       4
small-circle edges:   60
full-mesh edges:      435
edge reduction:       86.21 percent
diameter:             8 hops
replication factor:   3
```

These results support only a narrow conclusion: the imported Small Circles planner is
cheap enough to keep exploring in C++ and substantially reduces *application topology*
relative to a full mesh. They do not prove availability under churn or reduce the
number of Tox relationships automatically; the future connection scheduler must reuse
the union of peer relationships across namespaces.
