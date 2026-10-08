# rev0036 — servicecatalog / loadsheath / profilegc

rev0036 takes the rev0035 start profile seriously: if a node starts as a garden or bridge, it must not merely claim a mode. It needs a signed service catalog, per-service load-shedding sheath, and profile/config garbage-collection lane that preserve hard-negative memory.

The strongest sentence:

```text
A giving node is not safe because it launched; it is safe only when its advertised service surface, load-shedding behavior, and retained memory bind to the same start profile.
```

New surfaces:

- `servicecatalog.py` — signed garden/bridge service catalog capsules bound to start profile, start report, and router harness.
- `loadsheath.py` — per-service load budgets and useful-refusal pressure so bulk work cannot starve protected work.
- `profilegc.py` — profile/config-change GC that preserves tombstones, revocations, key-crisis notices, provider-false evidence, and witness-fork evidence.
- `foldregistry.py` — first declarative fold-registry surface to reduce one-off fold drift.
- `servicefold.py` — rev0036 audit/refactor fold preserving rev0035 `startfold` as predecessor history.

This remains a no-network design cube. No live SAM socket is opened.
