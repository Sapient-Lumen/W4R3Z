# rev0027 — branchmerge / persistlane / fuzzwire / refusalloop

rev0027 reconciles two useful rev0026 branchlets and then attacks three high-risk surfaces that were explicit debt:

1. persisted local evidence after crash/reload,
2. malformed parser/wire/shadow inputs before live I2P/SAM,
3. repeated useful-refusal laundering across garden windows.

The merged branchlets are:

- the spoken rev0026 `schedjoin` / `custodygc` / `partitionwitness` / `transportshadow` path,
- the unspoken rev0026 `lineagewindow` / `claimbundle` / `workmeter` path.

The branchlet merge is intentional. Losing either branch would erase hard pressure tests around mutable-head history and garden contribution accounting.

Core rule:

```text
Local memory is a protocol boundary after restart, not a cache.
```

Nonclaim: this is still a local deterministic design cube. It has no live I2P/SAM transport, no production DHT, no production persistence format, no production fuzz harness, no production garden scheduler, no mutable-head consensus, no private retrieval guarantee, no global reputation, no Sybil/anonymity guarantee, and no Nicotine+ patch.
