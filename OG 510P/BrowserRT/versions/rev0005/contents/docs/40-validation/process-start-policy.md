# Process-start policy

Revision: rev0005.

Question: should anything be started immediately each turn to save time?

Answer: by default, no daemon. Start `make turn-start`, not a persistent process.

## Rationale

A long-lived process might save cold-start time if it survives, but survival
across turns is not part of the cloudtainer contract. A hidden daemon also makes
failures harder to reproduce because its state is outside the zip.

## Allowed within-turn leases

The harness may create scoped resources inside one command:

- a local HTTP server;
- a Chromium/CDP session;
- a worker pool;
- an OPFS namespace;
- temporary files;
- trace capture.

The command owns cleanup and artifact capture. A later turn must be able to rerun
from the zip alone.

## Future optimization

The right optimization is not cross-turn daemons. It is better selection,
sharding, timing history, and local cache/replay artifacts.
