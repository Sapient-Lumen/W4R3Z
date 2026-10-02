# ADR 0128: bind range manifests before publication and activation

Status: accepted, 2026-08-21.

## Decision

The first integrated synchronization engine is exactly `range-v1`. A local publication builds the
preserved toxsync canonical range index from one immutable regular file, under the namespace's
artifact and manifest quotas. IoTox must verify that the index names the exact artifact digest and
size before either object is committed and before the stable-device-signed HEAD advances.

The same semantic pair check is repeated by the subscriber after both SHA-256 objects have been
strictly committed and while holding the namespace transaction, immediately before accepted-HEAD
persistence. Manual activation repeats strict type, size, and digest checks for both objects and the
range-index/artifact semantic check under that same transaction before replacing the signed
activation pointer. A HEAD, two matching object digests, or transfer completion alone is never
activation evidence.

The same-user private control socket now admits two owner-local effects:

```text
sync-publish NAMESPACE ABSOLUTE_PATH
sync-activate NAMESPACE EXACT_HEAD_RECORD_HEX
```

Publication writes artifact and manifest objects before the HEAD and treats an exact retry as a
duplicate. Activation requires the exact accepted 32-byte record token exposed by `sync-status`; it
does not silently select a newer revision. These local commands do not consume or imply a remote
`sync.publish` or `sync.activate` grant. Remote publication/subscription still requires current
authority-ledger v3 proof and namespace membership at the corresponding network entrance.

## Consequences

- The preserved toxsync index is now part of the production binary as a bounded semantic manifest,
  not merely preserved component code or an opaque file.
- A malicious or accidentally mismatched artifact/index pair cannot acquire published, accepted, or
  newly activated root status through the Agent path.
- Whole artifact and manifest files still cross Tox in this slice. Range reconstruction from a
  related basis, deterministic treepack publication, cancellation, and multi-source scheduling remain
  qualification work.
- Namespace policy installation remains an owner-only out-of-band file operation until its frozen
  administration commands are implemented.
- The exact activation record is optimistic-concurrency input, not a friendly revision alias and not
  permission to move the accepted chain backward.

## Evidence

The owned registry contains direct build/verify, corrupt-index, publication-order, semantic-pair,
subscriber, activation-object/manifest, typed-control, malformed-CLI, and full Agent/provider checks.
The GCC warnings-as-errors build and all 26 CTest entries pass. Clang 21 ASan/UBSan passes all 504
owned checks in 16 shards and its complete 41-entry CTest surface. Five delegated-cgroup checks skip
on the non-delegated construction shell by design. Genuine two-IoTox Sandwurm convergence remains
the next external boundary.
