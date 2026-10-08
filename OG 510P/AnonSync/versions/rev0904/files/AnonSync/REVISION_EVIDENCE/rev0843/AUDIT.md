# AnonSync rev0843 deep audit

## Executive verdict

AnonSync's strongest implemented law remains sound:

> An observation may authorize a transition only after the exact object, bytes,
> identity, lifetime, relationships, generations, resource limits, and durability
> evidence are frozen in an owner whose outputs cannot independently reread broad
> mutable state.

Rev0843 applies that law one level lower than rev0842. The bounded reader had
already improved pathname safety, but its POSIX implementation still fused five
different authorities: path opening, descriptor lifetime, shared file offset,
byte collection, and pre/post object proof. The extracted descriptor snapshot now
owns only byte and metadata observation. The adapter alone owns open/close. This
is the correct seam for future `openat`/`openat2` namespace ownership and for
worker processes that receive sealed descriptors instead of hostile paths.

## What changed and why it matters

### Mutable shared offset is no longer part of the proof

`read(2)` consumes the open file description's shared offset. That is harmless for
the current adapter's freshly opened descriptor, but it is the wrong primitive
for a reusable borrowed-descriptor owner: duplicated descriptors and threads can
share the same open file description. `pread(2)` gives each read an explicit
offset and does not change the file offset. The new owner therefore freezes from
byte zero while preserving whatever position the caller maintains.

### Descriptor ownership is explicit

The snapshot never closes the descriptor. The adapter closes exactly the
descriptor it opened, including exception cleanup, and preserves primary-error
precedence. Direct tests prove that the descriptor remains valid after both a
successful snapshot and policy/size rejection. This is a capability boundary,
not merely a resource-management preference.

### Namespace topology is part of authority

An open file can survive removal of its final name. Its bytes remain readable,
but it no longer proves what the selected namespace currently names. The owner
rejects `st_nlink == 0`. It also exposes two deliberate policies: a general
observation may accept a stable multiply-linked regular file; mutable authority
such as a ledger or journal requires exactly one link. Pre/post link-count
stability is checked in addition to identity, size, mtime, and ctime.

### Limits are now shared and typed

The prior helper checked positivity and `size_t`. The shared policy also checks
`std::string::max_size()` and POSIX `off_t`, so reserve and positional-read
frontiers fail with the same labeled contract. The initial `st_size` remains only
a ceiling check and reserve hint. EOF is still proved by reading through a
one-byte over-limit sentinel.

## Independent refactor audit

The extraction reduces `src/sync_bounded_regular_file.cpp` from its parent shape
by 112 lines and moves the reusable POSIX state machine into a focused 158-line
translation unit with no project-library dependency. The source audit has 23
release-gate checks covering exact consumers, dependency topology, open flags,
borrowed lifetime, `fstat`/`pread` ordering, offset preservation, link policy,
metadata binding, live tests, syscall scripts, CTest registration, and package
inventory.

The audit deliberately distinguishes semantic proof from source spelling. The
new direct runtime and syscall oracles are the primary evidence; lexical checks
remain useful only for dependency and ownership regressions that C++ type rules
and CMake do not yet express.

## Open local correctness work

### Directory-descriptor namespace authority

Final-component `O_NOFOLLOW` is not all-component confinement. A later owner
should retain a trusted directory descriptor, resolve relative names under a
stated policy, and perform open/rename/unlink/fsync operations relative to that
same directory authority. On supporting Linux kernels, `openat2` resolution flags
can make `BENEATH`, no-symlink, no-magic-link, and mount-crossing policy explicit.
The current 4.4 host cannot execute an `openat2` lane.

### Borrowed-descriptor concurrency contract

`pread` prevents shared-offset interference, but no userspace wrapper can make an
integer descriptor safe if another thread concurrently closes it and the kernel
reuses the number. Callers must retain descriptor-lifetime authority for the
whole freeze. A future API could encode this more strongly with a scoped
borrow/capability type rather than a raw `int`.

### Cross-resource crash state machine

Rev0842's audit identified that file fsync does not by itself make a newly created
journal name durable, and journal unlink retirement also needs directory
durability. That replay-ledger protocol remains the next local correctness target.
The descriptor extraction is enabling infrastructure, not a substitute for that
crash oracle.

## Waste and change amplification

The active cube still carries major concentration points:

- `src/sync_domain.cpp`: 15,287 lines / 1,122,163 bytes;
- `src/sync_domain_selftests.cpp`: 9,348 lines / 805,483 bytes;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines / 266,224 bytes;
- `src/reporting_selftests.cpp`: 4,773 lines / 288,345 bytes;
- `CMakeLists.txt`: 2,362 lines / 120,637 bytes;
- `REVISION_EVIDENCE`: about 25 MiB and 2,845 files before rev0843 evidence;
- 40 `audit_*.py` tools, with many checks still tied to source spelling.

These are not automatically defects, but they make each invariant expensive to
change and encourage audits to prove textual choreography rather than behavior.
The corrective direction is small authority-owned libraries, generated CMake
registries, property/model tests, and content-addressed evidence that does not
recursively replicate every historical handoff.

## Product-level mission still missing

Local authenticity and recovery remain prerequisites, not convergence or
anonymity. AnonSync still needs an executable operation algebra for duplicate,
reordered, concurrent, partitioned, retried, and restarted histories; device and
key epochs; membership and revocation; payload encryption; forward secrecy;
post-compromise recovery; metadata-leakage policy; backup custody; and realistic
erasure limits.

A plausible destination remains a ciphertext/content-addressed data plane plus a
small authenticated causal control plane. The deterministic operation model
should be the protocol specification and generated-history oracle; local file and
SQLite mechanisms should implement that model rather than silently define it.
