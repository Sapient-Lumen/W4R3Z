# Rev0957 research record

Research date: 2026-07-31

## Scope

The online review looked for primary-source precedent relevant to reusing an
already completed integrity cutpoint, proving that a second lock acquisition is
truly excluded, exposing expensive verification work, and evaluating future
filesystem assistance. These sources informed design and tests; none is treated
as authority for AnonSync's implementation.

## Linux `flock(2)`

Source: <https://man7.org/linux/man-pages/man2/flock.2.html>

The Linux manual states that locks created by separate `open()` calls are
associated with independent open-file descriptions and may conflict even when
held by the same process. AnonSync's payload store uses an exclusive lease as a
mechanical regression oracle: after a complete snapshot is acquired, a separate
exclusive mutation lease remains live while convergence consumes the moved
snapshot. A fresh complete snapshot would require a conflicting shared lease and
must fail busy. Successful convergence therefore proves actual handoff use more
strongly than elapsed-time or counter-only assertions.

Caveat: advisory-lock behavior varies across platforms and network filesystems.
The shipping product remains Linux/headless pre-alpha and must qualify any future
port rather than generalize this oracle silently.

## Syncthing Block Exchange Protocol v1

Source: <https://docs.syncthing.net/specs/bep-v1.html>

Syncthing uses an index ID plus maximum sequence number to identify an index
point, then sends only changes after the peer's known point. The useful analogy
is not wire compatibility: a validated named cutpoint should be composed rather
than discarded and immediately reconstructed. Rev0957 reuses one exact
process-local payload snapshot across adjacent owner operations. It does not add
remote index sequences, persistence, or a new protocol.

The cutpoint-freshness regression adds a second lesson. A named inventory point
must not be consulted as a current absence oracle after the same pass has learned
about state beyond that point. Syncthing expresses advancement explicitly with
monotonic sequence values; rev0957 uses the much narrower local rule that any
payload mutation put invalidates the older complete inventory before remote
selection. This is an analogy, not a claim that the local store now has a durable
sequence index.

Speculation: AnonSync's next substantial scale improvement should likely retain
a durable monotonic payload/catalog change sequence and an independently
rebuildable complete descriptor-rooted oracle. The exact-owner handoff is a
small safe precursor: it establishes explicit cutpoint identity and accounting
without prematurely making metadata authoritative.

## OpenZFS `zpool scrub`

Source: <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-scrub.8.html>

OpenZFS describes scrub as verification of all data and reports that scrub is
I/O intensive while exposing progress. The relevant lesson is operational:
full-byte proof is real work and should be distinguishable from subsequent
repair/convergence work. Rev0957 reports supplied snapshots, newly observed
snapshots, and fallback mutation full scans separately so an optimization cannot
hide a different complete scan.

Speculation: future AnonSync status should add measured bytes and monotonic
elapsed time for recovery reproof, while avoiding ETA or maximum-detection-age
claims until scheduling and storage throughput are controlled.

## Linux fs-verity

Source: <https://docs.kernel.org/filesystems/fsverity.html>

The kernel documentation describes fs-verity as read-only file authenticity and
integrity protection backed by a Merkle tree; reads fail when verification fails.
This is potentially attractive for immutable digest-named payloads on supported
Linux filesystems.

It is not a drop-in replacement for the current store:

- shared-folder source files are mutable;
- AnonSync must remain portable beyond one Linux filesystem feature;
- store identity, namespace capacity, rooted pathname proof, restart witnesses,
  retention, and garbage collection remain userspace concerns; and
- enabling verity changes publication and lifecycle semantics and requires its
  own migration/recovery design.

A future experiment could enable fs-verity only after atomic publication of an
immutable payload, retain SHA-256 as the protocol identity, and compare cold
read/restart behavior. It should be feature-detected and never silently lower
verification on unsupported filesystems.

## Research boundary

These comparisons support three design choices: exact cutpoint reuse, a hard
lease oracle, and visible accounting for expensive verification. They do not
prove AnonSync's race, crash, lock, filesystem, cryptographic, or cross-platform
semantics. Compiler, sanitizer, runtime, process, structural, and package checks
remain the release evidence.
