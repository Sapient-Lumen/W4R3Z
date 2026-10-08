# Proof obligation — rev0061

The proof obligation is local and modest:

```text
settlement requires accepted delivery witness and send fence
archive requires accepted terminal settlement
prune requires accepted settlement and archive
all joins bind action/profile/service/scope/request/payload/idempotency
all joins preserve hard-negative pressure
all joins refuse replay/fork/rollback/previous-link drift
```

The cube does not prove global delivery or consensus.  It proves only that the baby local algebra refuses obvious laundering paths.
