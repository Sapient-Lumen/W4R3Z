# Python surface rev0093

Python remains the protocol authority.

rev0093 adds Python-only semantic surfaces for native loopback, call canary, and dispatch fence. The C/GCC side remains constrained to tiny deterministic leaf kernels already guarded by the previous native boundary lanes.

Python owns:

```text
parsing
crypto and signatures
transport
persistence finality
policy and redress
mutable heads
DHT truth
all exact-boundary joins
```
