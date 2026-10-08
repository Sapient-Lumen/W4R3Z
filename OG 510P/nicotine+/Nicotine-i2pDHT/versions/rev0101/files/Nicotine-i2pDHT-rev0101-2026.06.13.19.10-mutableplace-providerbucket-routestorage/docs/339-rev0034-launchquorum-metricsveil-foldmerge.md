# rev0034 — launchquorum / metricsveil / foldmerge

rev0034 joins the restart, compatibility, and future-router boundaries before a node may treat itself as launched.  The design pressure is simple: a component report can be valid while the joined side effect is still unsafe.

New surfaces:

- `launchquorum.py` joins `safestart`, `persistjoin`, and `samprobe`.
- `metricsveil.py` treats diagnostics as a metadata side channel and redacts/budgets labels.
- `foldmerge.py` audits the current path while folding the parallel rev0033 `persistjoin` / `samprobe` / `foldreduce` branchlet into visible history.

Core sentence:

```text
A node is not launched because its parts passed; it is launched only when restart memory, negotiated compatibility, and router assumptions bind to one intent.
```

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production telemetry, no private retrieval guarantee, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
