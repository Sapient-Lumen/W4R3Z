# Risk register — rev0061

Risks tested in this revision:

```text
delivery witness accepted but settlement marker drifts
settlement marker replays or forks
ack digest conflict
archive restart memory rebinds idempotency to another payload
archive previous-link mismatch
prune allowed before archive
hard-negative evidence pruned after delivery
low family/path diversity treated as final
```

Risks not solved:

```text
real network acknowledgement authenticity
private retrieval
Sybil resistance
mutable-head consensus
production persistence
live SAM/I2P send behavior
```
