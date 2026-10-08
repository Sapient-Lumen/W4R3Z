# AnonSync rev0899 audit

## Heart of the mission

AnonSync is a durable, bounded causal-convergence system in which authority is
explicit, evidence-bound, recoverable, and never fabricated by observation.
Exact authorized history and live owned capabilities decide what may exist,
move, retry, settle, or become visible. Paths, clocks, handles, summaries,
indexes, process exits, and configuration documents remain subordinate evidence.

## Corrected common-birth gap

Rev0898 made one canonical deployment manifest the mandatory operational
capability, but independently valid stores could still be recomposed under a
new manifest. Rev0899 generates one checked 256-bit OpenSSL CSPRNG deployment ID
before mutation and persists that exact identity, manifest digest, manifest
path, role, database path, folder, actor, application ID, and framed binding
digest into every selected SQLite store and the product payload marker.

Every SQLite role now has a distinct `application_id` and one exact STRICT
singleton `anonsync_store_set_binding` table. Operational opens pass through one
shared bound-open frontier that proves the opened main filename, role header,
exact schema, singleton row, all expected fields, digest, and absence of
same-name temporary shadows before constructing the role owner. The payload
marker moved to v3 and binds the same deployment identity and manifest.

## Fresh-bootstrap boundary

Product `init` now refuses pre-existing SQLite main files and all three relevant
sidecar names (`-journal`, `-wal`, and `-shm`) before mutation. Payload and file
delivery roots must be empty. This prevents rev0899 from silently adopting an
older or foreign namespace and makes the lack of an in-place migration protocol
explicit rather than accidental.

The process proof independently recomputes canonical manifest and store-binding
digests. It rejects forged-but-self-consistent manifests, same-role and
cross-role database substitution, foreign payload-root substitution, orphan
sidecars, and preseeded roots, while retaining the real mutual-TLS transfer,
receipt, publication, and sender-settlement proof.

## Audit/refactor findings

The common deployment identity grammar is one dependency-light owner shared by
manifest, SQLite binding, and payload marker code. The binding schema was added
to the file-effect owner's exact schema inventory instead of being duplicated
across role implementations. Lexical source audits were updated to recognize
that single frontier without weakening their closed inventories.

A release-validation audit caught a separate cloudtainer failure mode: changing
compiler variables caused CMake to delete and regenerate its cache, silently
leaving `CMAKE_BUILD_TYPE` empty while earlier evidence still called the build
Debug. That result was rejected. Rev0899 was reconfigured from a clean build
directory with `/usr/bin/gcc-14`, `/usr/bin/g++-14`, and
`CMAKE_BUILD_TYPE=Debug`, rebuilt across 426 actions, and fully retested. The
intermediate cache observation is retained as evidence.

The broad clean build also demonstrates the current cost problem. Two command
ceilings interrupted the 426-action graph before the final continuation
completed. The ownership leaves remain valuable for review, so the corrective
direction is a measured compiler-cache launcher, a documented product fast
lane, dependency-fan-out reporting, and only target-scoped unity experiments.

## Remaining highest-risk gaps

1. Interrupted initialization is fail-closed but stranded. There is no durable
   inspect/resume/quarantine/abort state machine for partially created stores.
2. Whole-namespace freshness uses preflight checks and remains racy against a
   noncooperating local writer between check and creation.
3. WAL does not make the separate role databases atomic as a set. Cross-store
   transitions need an explicit coordinator/recovery protocol or redesign.
4. The unkeyed binding detects corruption and recomposition, not a hostile
   writer able to rewrite every deployment resource. That threat model needs a
   key or signature rooted outside the writable store set.
5. Product path authority is not yet rooted in one live ancestor descriptor;
   ancestor replacement and namespace rebinding remain platform-sensitive.
6. `status` still traverses write-capable WAL owners and is not a forensic,
   side-effect-free snapshot reader.
7. The product remains a bounded command spine rather than a supervised daemon
   with chunking/resume, causal filesystem semantics, indexing/GC, at-rest
   encryption, and a defensible anonymity/privacy threat model.

## Validation

- Clean GCC 14.2.0 Debug configuration with explicit C and C++ compiler pins.
- Bundled SQLite 3.53.3 CMake hash verification passed.
- Clean build completed across an initially scheduled 426 Ninja actions.
- Final dependency closure reported `ninja: no work to do.`
- Focused product/authority lane: 9/9 passed.
- Full registered suite: 219/219 passed with 8 workers in 18.30 seconds.
- Database-open policy audit: 16/16 passed.
- Bootstrap-authority audit: 19/19 passed.
- Deployment-binding audit: 20/20 passed.
- Payload-store source audit: 33/33 passed.
- Release path-policy selftest: 14/14 passed.
- Direct and registered executable process proofs passed.
- Changed-text whitespace/newline audit and Python bytecode compilation passed.
- `clang-format` was unavailable in the cloudtainer and is not claimed.

The source audits are lexical tripwires, not formal proofs of runtime race
freedom, crash safety, filesystem semantics, cross-store atomicity, or hostile
local-writer resistance.
