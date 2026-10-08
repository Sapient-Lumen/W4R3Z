# Proof obligations — rev0086

The cube must demonstrate:

```text
native selection accepts only when reports bind at the exact boundary
fallback selection requires restart journal memory
fallback journal rejects replay/fork/previous-link drift
a promotion back to native preserves old negative memory
foldmap/foldregistry/surfaceledger expose rev0086
rev0085 nativeprovenancefold remains a passing predecessor
```

The tests are intentionally local and deterministic; they are not production proofs.
