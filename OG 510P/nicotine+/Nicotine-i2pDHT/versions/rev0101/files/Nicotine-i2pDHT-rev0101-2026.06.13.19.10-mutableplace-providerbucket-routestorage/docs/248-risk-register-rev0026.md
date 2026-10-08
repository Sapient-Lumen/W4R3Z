# Risk register — rev0026

| Risk | New pressure test | Remaining debt |
|---|---|---|
| Capability success bypasses scheduling | `schedjoin.py` queues only accepted dispatches and still protects control-plane work | Need production resource accounting and cross-window persistence |
| Useful refusals become fake contribution | Refusal laundering from one family is quarantined | Need multi-garden refusal replay simulation |
| Evidence GC drops hard negative context | `custodygc.py` synthesizes custody/tombstone/witness/revocation evidence before GC | Need durable storage and compaction format |
| Split merge commits too early | `partitionwitness.py` uses scratch memory until route/witness gates pass | Need larger partition/churn simulations |
| Wire framing drifts before transport | `transportshadow.py` signs canonical shadow report frames | Need real SAM transcript fixtures and parser fuzzing |
| Current surface becomes hard to find | `joinfold.py` audits code/test/docs/public/ledger visibility | Need periodic fold-module consolidation |
