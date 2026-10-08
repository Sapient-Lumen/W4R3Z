# Rev0958 implementation and adjacent audit

## Mission checkpoint

The shipping spine remains one C++ product:

`anonsync_sync` → linked-peer service → folder process/scan owner → SQLite
catalog and replica owners → rooted payload store/shared-folder effects →
authenticated direct/Tor/I2P sessions.

No parallel daemon, scanner, catalog, or recovery engine was introduced. The
slice corrects how the retained payload owner composes durable restart
acceleration with bounded integrity scrubbing.

## Severe composition defect

A durable verification-index entry can authorize an exact unchanged POSIX
observation after restart. Rotating scrub can later discover metadata-hidden
content damage. Rev0957 installed a process-local fixed-width corruption witness
before allocation-bearing evidence, but the terminal durable
`IntegrityFailure` record remained best effort. If terminal publication was lost
and the process died, the fresh process lost the fixed-width witness, could reuse
the stale verification entry, and could have its optional immediate scrub
deferred by another process's shared lease. Authority could therefore return
without re-reading bytes already known by the dead process to be contradictory.

## Implemented authority fence

- Added canonical fixed-width disposition `Prepared = 4`.
- New work commits and exactly re-observes `Prepared` under the exclusive store
  lease before opening or reading the payload.
- A fresh owner observing `Prepared` or `Progress` forbids durable and process
  cache reuse for that digest during the ordinary complete scan.
- The exact live owner may reuse only its process cache after its own commit/
  re-observation or after a complete current-byte scan while the same state and
  state-file observation were frozen.
- Replacement, malformed publication, or uncertain re-observation causes an
  optional publication deferral with no payload read.
- Mismatch clears active acceleration and installs the fixed-width integrity
  witness before terminal allocation or best-effort failure publication.

## Hard regression

The process test constructs a valid stale verification checkpoint over
metadata-hidden corrupt bytes plus a valid `Prepared` record. A child process
holds the shared identity lease, which mechanically permits the complete shared
scan but prevents the optional exclusive scrub. The fresh owner nevertheless
hashes the active payload in the ordinary scan and throws the exact integrity
error with `failure_persisted=false`; the durable intent remains the restart
fence.

The one-payload cyclic test also distinguishes all reuse domains: same-owner
active work performs zero new hashes and one process reuse, fresh owners hash
once while `Progress` is active, and durable reuse returns only after `Idle`.
The codec accepts canonical zero-offset Prepared state—including an empty
payload—and rejects consumed-byte or terminal-digest variants.

## Adjacent refactor

Scrub publication now returns exact re-observed state-file metadata instead of a
Boolean. Normal publication and rename-cutpoint reconciliation share one parse,
identity, byte-equality, and POSIX-observation rule. One transition owner assigns
generations, publishes, records same-process evidence, and advances the expected
observation. This removes duplicated transition logic and makes the no-read-
after-uncertain-publication ordering locally reviewable.

## Audit result

The structural audit passed 135/135 checks on the frozen
active source. It now binds the Prepared grammar, intent-before-read ordering,
exact state-file observation, process-only acceleration, fresh-process blocked-
scrub regression, allocation-independent mismatch cutpoint, release verifier,
and documentation. This lexical audit is defense in depth, not semantic proof.

## Nonclaims

The v1 record width is retained, but downgrade compatibility is not claimed.
Neither terminal state nor intent is content authority. Power-loss behavior,
hostile same-UID mutation, filesystem-native checksums, quarantine, restore,
retention, reachability pinning, garbage collection, rename identity, directory
semantics, selective sync, many-share supervision, cross-platform qualification,
a named measured Resilio uninstall workload, and live public Tor/I2P privacy
qualification remain open.
