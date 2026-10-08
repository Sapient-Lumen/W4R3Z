# Capability dispatch gate

`capgate.py` is a joined boundary. It does not let one green check imply the rest of the dispatch path is safe.

The order is deliberate:

```text
canonical wire frame
  -> validator wall
  -> namespace registry
  -> capability chain + revocation set
  -> admission budget
  -> handler dispatch
```

A signed frame with a valid namespace can still fail because the invoking actor does not match the frame sender or lacks a delegated capability. A valid capability can still fail because a revocation head has invalidated the grant. A valid capability can still be refused by admission pressure, and that refusal is a local signed receipt rather than a reputation fact.

The current toy mapping is intentionally simple:

- mutable heads require `write_head`,
- witness/useful-refusal records require `garden_watch`,
- repair/store/custody work requires `garden_reprovide`,
- provider claims currently map to `publish_seed` as a placeholder for a later provider-specific capability.

This is not final authorization design. It is the pressure surface that prevents namespace validation, capability validation, and garden capacity from being blurred together.


rev0025 also tests explicit actor mismatch: a capability granted to a different invoking key must not ride on a signed frame from another key.
