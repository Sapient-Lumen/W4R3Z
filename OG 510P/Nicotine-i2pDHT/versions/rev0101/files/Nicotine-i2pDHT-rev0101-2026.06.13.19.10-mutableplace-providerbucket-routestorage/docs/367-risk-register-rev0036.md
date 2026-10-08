# Risk register — rev0036

Still risky:

- Service descriptors are toy semantics; real garden services need wire/API definitions.
- Family labels remain lab hints, not solved independence or Sybil resistance.
- Load shedding is local and deterministic, not a production scheduler.
- Profile GC uses toy memory items, not a real database/journal migration.
- Foldregistry is only a first consolidation step.

New mitigations:

- Signed service catalogs bind giving claims to accepted start/router surfaces.
- Load sheath prevents protected work starvation in toy windows.
- Profile GC refuses to delete hard-negative evidence.
- servicefold keeps rev0036 discoverable and preserves rev0035 predecessor history.
