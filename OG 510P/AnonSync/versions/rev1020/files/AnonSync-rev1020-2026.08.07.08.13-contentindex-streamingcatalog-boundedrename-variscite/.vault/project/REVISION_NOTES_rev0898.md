# AnonSync rev0898 revision notes

## Mission increment

Rev0898 makes product bootstrap an explicit authority rather than a side effect
of ordinary work. The mission remains authority-preserving convergence: exact
history and live owned capabilities decide what may exist, move, retry, settle,
or become visible; observation and configuration must not manufacture durable
truth.

`anonsync_replica init` is now the sole product-spine command authorized to
create replica, payload, effect, membership, or anchor state. It prepares one
immutable deployment-manifest name, initializes the selected stores through
their existing owners, and publishes the manifest last. Every operational
command requires that manifest, derives the complete store set, folder, local
actor, and payload ceiling from it, and uses existing-only opens.

## Deployment manifest

The new `SyncReplicaDeploymentManifest` codec owns a bounded exact 22-field
schema with:

- absolute normalized store paths and local identity;
- selected-store profile and authority-resource count;
- required WAL and existing-only operational policies;
- manifest-only configuration policy;
- explicit commit-marker and non-atomicity declarations; and
- a domain-separated SHA-256 self-digest.

The operational reader performs a 16 KiB bounded regular-file read, refuses a
symbolic link in the final component, uses strict UTF-8 JSON with duplicate-key
rejection, requires exact field closure, binds the embedded manifest path to
the opened filename, validates profile/resource/policy consistency, re-encodes
the value, and requires byte-for-byte canonical equality.

The encoder now proves its own reader contract before bootstrap mutation. It
rejects output beyond the 16 KiB ceiling and reparses the exact bytes so a POSIX
path containing non-UTF-8 bytes cannot strand already initialized stores behind
an unreadable manifest.

The manifest is published only after every selected owner restores. It is a
committed operational cutpoint, not a cross-resource transaction. An interrupted
`init` may leave individually valid stores while the absent manifest truthfully
shows that the store set never committed for normal operation.

## Operational grammar and store acquisition

`status`, `clock-observe`, `clock-recover`, `enqueue-file`,
`membership-publish`, `send-one`, and `serve-one` now accept `--manifest` as
their only local store-set configuration source. Independently mixable
`--replica-db`, `--payload-root`, `--effect-db`, `--files-root`,
`--membership-db`, `--anchor-db`, `--folder`, `--local-device`,
`--local-epoch`, and `--max-payload-bytes` options are rejected on those paths.
Every result includes `deployment_manifest_digest`.

All operational SQLite opens are `ExistingOnly`. The durable payload store now
also requires an explicit, non-defaulted
`SyncReplicaFilePayloadStoreOpenDisposition`. `ExistingOnly` refuses an absent
folder identity marker before adoption or mutation; only `init` may use
`CreateIfMissing`. This closes the remaining authority leak where status,
enqueue, or send could mint a payload-store identity merely by observing an
empty directory.

## JSON parser refactor

The strict JSON parser was extracted from `json_codec_crypto.cpp` into the
small shared `anonsync_json_parser` leaf. The broad core codec and deployment
manifest now use one duplicate-key-, Unicode-, number-, trailing-content-, and
depth-validating parser without making the narrow manifest codec depend on the
runtime monolith.

The bounded-regular-file source audit was advanced to v3 so its exact consumer
inventory recognizes the manifest reader. This correction retains the
fail-closed audit instead of weakening it after the refactor.

## Proof

The registered process proof now covers:

- missing-manifest failure before database or payload authority;
- wrong-profile and overlapping bootstrap rejection before mutation;
- pre-existing manifest collision before fresh store creation;
- exact sender and receiver manifest bytes, mode, policy, and self-digest;
- copied-path and same-path tamper rejection;
- rejection of raw operational path mixing;
- detached replica and membership stores without recreation or later-store
  access;
- empty replacement payload roots without identity-marker creation;
- command/profile capability mismatches;
- anchored membership publication;
- enqueue, status, clock observation, quarantine, and generation-fenced
  recovery; and
- real mutual TLS, exact receiver publication, authenticated receipt, and
  terminal sender settlement through manifest-bound commands.

The final GCC 14 Debug build completed across the whole graph, and all 217
registered tests pass. The database-open policy audit passes 16/16, the new
bootstrap-authority audit passes 18/18, and the bounded-regular-file audit
passes 23/23.

## Audit findings and remaining gaps

The most important remaining correctness gap is store-internal composition.
The manifest binds paths and configuration, but every selected store does not
yet persist one shared immutable deployment identifier. Independently valid
stores with compatible folder/actor values can still be assembled under a new
canonical manifest. The next revision should mint a deployment ID, persist it
inside every SQLite owner and root marker, and require it on every restore.

Interrupted initialization also needs explicit `inspect`, `resume`, and
quarantine/abort semantics. Publishing the manifest last exposes noncommit but
does not explain or safely classify partial stores.

Path authority remains string-based between components. The manifest read
refuses the final symlink, but ancestor symlinks, bind mounts, and namespace
rebinding require a future descriptor-rooted design, with Linux `openat2`
policies evaluated separately from other platforms. Role-specific SQLite
`application_id` values would provide useful early wrong-file rejection but
would supplement, not replace, exact schema and deployment attestation.

`status` still uses write-capable WAL owners and is not a side-effect-free
read-only export. The product remains one-shot rather than a bounded durable
supervisor. SQLite WAL does not make separate attached databases one atomic
store-set transaction, so future cross-store transitions require an explicit
coordinator/recovery protocol or a schema redesign.

The full release closure remains expensive: a clean build scheduled 297 Ninja
actions and the registry contains 217 tests. A target-scoped development lane,
compiler cache integration, and carefully measured optional unity-build
experiments may reduce cloudtainer cost without weakening the complete release
gate.

Detailed findings, primary-source research, speculation, and the recommended
sequence are in
`EXPLICIT_STORE_SET_BOOTSTRAP_AND_MANIFEST_AUTHORITY_AUDIT_rev0898.md`.
