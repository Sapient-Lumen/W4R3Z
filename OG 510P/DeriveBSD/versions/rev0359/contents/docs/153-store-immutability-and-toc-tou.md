# Store immutability invariants (prevent post-build mutation / TOCTOU)

DeriveBSD’s security model assumes:
- store objects are **content-addressed**
- once published/consumed, they are **immutable facts**

If an attacker can mutate a store path after verification (or while a privileged component assumes immutability), the entire “hash = truth” model collapses.

## Why DeriveBSD should care

Real-world systems have shown that “the store is immutable” can be an *assumption*, not an enforcement.
Researchers have described scenarios where cooperating processes retain write access and mutate store paths after a build, creating time-of-check/time-of-use hazards for privileged tooling.

## DeriveBSD direction

### 1) Store objects live on read-only substrates

Treat immutability as an OS primitive:
- store lives on a **read-only ZFS dataset** (or read-only snapshots) by default
- writes happen only in a staging dataset, then **promote by snapshot/clone**
- activation consumes only snapshots (generation-bound)

### 2) No in-place mutation paths

- the only way to “change” an object is to create a **new** content-addressed object
- any imperative mutation is modeled as:
  - a new Plan
  - a new Artifact
  - a new generation

### 3) Verify at the edges (and keep verifying)

- verify digests at import (builder → store) and at consume (store → activation/launch)
- optionally run periodic “store scrubs” that sample objects and re-hash
- never trust writable mounts for store paths inside privileged daemons

### 4) Evidence hooks

Emit small evidence objects (policy-controlled):
- `store.integrity.report` (dataset mode, snapshot ids, spot-check results)
- `store.mount.report` (store mounted read-only; no writable alias)

## Notes

- This pairs naturally with `docs/152-store-view-minimization.md`: builders should not *see* or *write* beyond declared inputs/outputs.
- If policy allows delta/patch lanes, they still result in new objects or new overlay artifacts, never silent mutation.

References:
- Snyk research write-up on a `/nix/store` immutability assumption being exploitable via cooperating components (TOCTOU risk framing): https://labs.snyk.io/resources/nixos-deep-dive/
