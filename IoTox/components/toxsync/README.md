# toxsync

`toxsync` is a transport-neutral C++20 library for verified mutable-artifact
synchronization. Mutation is represented by a small signed HEAD; revision bytes remain
immutable and move through either the range-v1 engine or the content-addressed v2 fabric.

```text
signed mutable HEAD
        |
        +-- toxsync-range-v1
        |     stable .txi target index
        |     receiver-side basis reuse
        |     bounded aligned streaming for huge artifacts
        |     adaptive rolling reuse for shifted smaller artifacts
        |
        +-- toxsync-content-store-v2-paged-fabric
              content-defined SHA-256 chunks
              paged root + immutable page objects
              sparse and exact availability exchange
              bounded rarest-first multi-source scheduling
              pin ledger and conservative garbage collection
```

Directories are serialized into deterministic `treepack` artifacts. Toxsync does not own
peer identity, namespace authorization, transport, or live-directory activation. Those
policies belong to the embedding application.

## Status

This tree is **toxsync 0.7.0**. The v1 `.txi` format remains byte-compatible with 0.1.0
through 0.7.0. The original flat v2 manifest remains readable, and the paged v2 root/page/chunk
formats introduced in 0.5.0 are unchanged.

0.7.0 closes several lifecycle and large-tree boundaries without introducing another delta format:

- fixed 80-byte HEAD summary/query records and an 84-byte receipt record for bounded reconnect
  anti-entropy;
- deterministic publication transactions that treepack, content-chunk, commit immutable objects,
  build a paged root, link and sign the next HEAD, and publish that HEAD last;
- verified treepack activation into immutable revision directories with an idempotent receipt and an
  atomic relative `current` symlink switch;
- bounded external path sorting for treepack, including spill runs and bounded multi-pass merge, so
  publisher memory is capped independently of total entry count;
- cooperative cancellation checkpoints in content reconstruction and publication work;
- explicit lane backoff and verified-byte/time observation seams for embedding applications;
- retained elastic peer availability, global request budgets, paged manifests, exact inventories,
  content-addressed ingest, pin ledger, conservative garbage collection, and range-v1 compatibility.

The library remains transport-neutral. Durable peer obligations, namespace authorization, live
connection epochs, and the event-loop/worker split belong to the embedding application. IoToxsync
rev0010 was the historical embedding; current IoTox owns a deliberately forward-ported production
policy around a reviewed subset of these primitives.

## Build

```sh
cmake --preset gcc-release
cmake --build --preset gcc-release --parallel
ctest --preset gcc-release --output-on-failure
```

The standalone registry currently contains 125 native C++ checks. CTest also runs a version route
and a command-level transaction that reconstructs content and range artifacts in every lane and,
when OpenSSL is selected, covers key no-clobber/partial-pair rollback, HEAD-last directory
publication, exact retained-revision retry, signed verification, repeated activation, pins, and a
conservative GC dry run.

Dependency-minimum lane:

```sh
cmake --preset gcc-portable-release
cmake --build --preset gcc-portable-release --parallel
ctest --preset gcc-portable-release --output-on-failure
```

The portable lane uses the project-owned C++ SHA-256 and scalar rolling checksum. Mutable
HEAD signing is deliberately unavailable there until a project-owned Ed25519 implementation
is selected and audited.

The complete GCC/Clang/portable/ASan/UBSan/TSan/fuzzer matrix is available from the enclosing IoTox
repository:

```sh
nix develop ./components/toxsync --command ./tools/build-toxsync-matrix.sh
```

## CLI

### v1 bounded ranges

```sh
toxsync pack ./tree ./revision-0042.treepack
toxsync index ./revision-0042.treepack ./revision-0042.txi auto 64
toxsync sync ./revision-0037.treepack ./revision-0042.txi \
  ./revision-0042.treepack ./received-0042.treepack
toxsync verify ./revision-0042.txi ./received-0042.treepack
```

### v2 paged content fabric

```sh
toxsync content-build-paged \
  ./revision-0042.treepack ./store ./revision-0042.txp auto 64

toxsync content-inspect ./revision-0042.txp
toxsync content-scan ./revision-0042.txp ./store verify
toxsync content-apply ./revision-0042.txp ./store ./received-0042.treepack
```

### Publish and activate a directory revision

```sh
toxsync publish-tree \
  ./source-tree ./work ./content-store NAMESPACE_HEX 42 \
  ./writer.private ./head-0042.txh none snapshot retain

toxsync activate-tree \
  RETAINED_TREEPACK_FROM_PUBLISH_OUTPUT ./active ./head-0042.txh ./writer.public
```

Publication writes the signed HEAD only after the immutable root, pages, and chunks are readable.
With `retain`, it reports the exact immutable `retained-treepack` and `retained-root-manifest` paths;
use the former for activation rather than guessing a workspace filename. An exact retry validates
and resumes an already-landed retained revision instead of failing after a crash at that boundary.
Activation verifies the signed HEAD and artifact digest, unpacks into a private staging directory,
writes an activation receipt, and atomically switches `current`. It never overlays an unrelated
existing revision directory.

### Retention

```sh
toxsync pin-set ./pins.log NAMESPACE_SHA256 42 MANIFEST_SHA256 0 1
toxsync pin-list ./pins.log
toxsync content-gc ./store ./pins.log 1073741824 805306368 dry-run
```

Garbage collection is conservative: a false-positive reachability mark retains an object; it
does not delete a live object. Missing or corrupt pinned manifests fail closed.

### Signed HEADs

```sh
toxsync head-keygen ./writer.private ./writer.public
toxsync head-create NAMESPACE 42 content ARTIFACT_SHA SIZE MANIFEST_SHA MANIFEST_SIZE \
  PARENT_RECORD_SHA ./writer.private ./head-0042.txh
toxsync head-verify ./head-0042.txh ./writer.public
toxsync head-evaluate ./head-0042.txh ./head-0041.txh ./writer.public
```

## Memory model

The large-sync path never retains state proportional to the complete artifact. Paged
manifests let a worker load only one caller-bounded chunk window and the intersecting page
objects. A `MultiSourceScheduler` can borrow that same window, avoiding a second chunk array.
Peer availability is bounded by an inline word for at most 32 configured peers or a contiguous
dynamic bitset of `ceil(maximum_peers / 64)` words per active object. Thirty-two is an
implementation crossover, not a library policy. A fixed-size conservative sketch remains available
for broad discovery.

The store-ingest path verifies a completed private staging object once. On the same
filesystem it can publish by hard link and unlink without copying payload bytes. Across
filesystems it uses one reusable bounded buffer, verifies while copying, and publishes with
no replacement.

## Integration seam

IoTox compiles a deliberate source-compatible subset into `iotox_core`: hash/index/planner/apply,
treepack, content-store/paged-fabric, multisource, and range-source primitives. IoTox owns the
production HEAD signature, authority-ledger v3 trust, durable attempts, FileIds, epochs, quotas,
activation, retention witnesses, transport records, and route policy. The standalone HEAD key,
publication helper, wire records, pin journal, and CLI are retained laboratory/reference surfaces,
not a parallel production authority path.

See `docs/large-sync-v1.md`, `docs/paged-content-v2.md`, `docs/range-protocol-v1.md`,
`docs/security.md`, and `ROADMAP.md`.
