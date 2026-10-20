# Design ledger: hsynz reference to toxsync

The cube carries an upstream hsynz v1.3.0 reference lock and original license. `toxsync` is a separately named, separately versioned C++20 repository. Its source was written against documented behavior and architectural ideas, not made by renaming hsynz files.

## Adopted concepts

- Publish one target summary/release rather than precomputing a patch for every old version.
- Perform similarity discovery at the receiver.
- Reuse blocks found at arbitrary offsets in an old local artifact.
- Download only required target ranges through a replaceable communication method.
- Support interrupted reconstruction and bounded resource policy.
- Treat a canonical directory representation as a byte artifact.

## Deliberately different in v1

- A small fixed `.txi` format instead of `.hsyni`/`.hsynz` compatibility.
- No compression layer in the core; compression can be an artifact transform or a later engine.
- No bundled HTTP/TLS implementation.
- No imported HDiffPatch, zlib, zstd, libdeflate, xxHash, or minihttp dependency.
- One whole-artifact SHA-256 acceptance rule.
- A narrow C++ `RangeSource` interface rather than demo-specific callbacks.
- Fresh-stage deterministic treepack instead of in-place directory patching.
- No hidden threading; IoT devices control concurrency above the library.

## Deferred

- Variable-size/content-defined chunks.
- Hash-addressed chunk stores and garbage collection.
- Multi-peer chunk scheduling and availability summaries.
- Compression dictionaries.
- Sparse files, hard links, ACLs, xattrs, timestamps, and full modes.
- Cryptographic signatures and namespace policy, which belong to IoTox.

## rev0005 independent implementation choices

The performance pass remains independent code. It does not import hsynz source or formats. The aligned probe, early-impossibility test, fixed-buffer rolling scanner, weak lookup, run coalescer, streaming SHA wrapper, and benchmark harness are toxsync designs implemented against the existing v1 contract.

The original hsynz reference remains a provenance/idea ledger and a future comparison target. The production toxsync build graph has no source or link dependency on it.
