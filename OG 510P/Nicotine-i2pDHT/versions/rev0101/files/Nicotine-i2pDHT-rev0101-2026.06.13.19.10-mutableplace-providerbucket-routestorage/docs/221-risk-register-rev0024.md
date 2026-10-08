# Risk register — rev0024

New risk surfaces tested:

```text
policy epoch rollback
policy epoch same-epoch fork
policy previous-link mismatch
policy digest mismatch
range Merkle bad proof
range Merkle same-sequence root fork
range tombstone-first repair
queue family flood
queue bulk starvation of head/witness/seed work
queue latency deadline miss
```

Persistent nonclaims:

```text
no live transport
no production DHT
no production Merkle/storage protocol
no global policy authority
no private retrieval guarantee
no Sybil/anonymity guarantee
```
