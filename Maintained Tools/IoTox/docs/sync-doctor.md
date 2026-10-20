# Synchronization doctor

Status: pre-creation and configured live-headroom paths implemented. Updated 2026-09-03.

`sync-doctor` answers a deliberately narrow question before any namespace, authority grant, network
session, or managed store is created: *can this source be represented by the selected IoTox sync
policy under its default bounds, and roughly how much durable space will that first revision need?*

```text
iotox sync-doctor /absolute/file
iotox sync-doctor /absolute/directory one-writer [INTERVAL_SECONDS]
iotox sync-doctor /absolute/directory read-write [INTERVAL_SECONDS \
  [executable-v1|owner-mode-v2 [include=PATH|exclude=PATH...]]]
```

A regular one-writer source uses content-v2. A directory in one-writer mode uses treepack-v1. A
read-write directory uses tree-v2, including the exact production selection, ownership, mode,
hard-link/special-file, path, hashing, manifest, and quota rules. The command hashes every selected
regular file and uses the normal race-detecting file hasher; a concurrent edit therefore refuses the
inspection instead of producing a plausible stale plan.

ADR 0318 wraps that source scan in a bounded read-only filesystem-contract walk before and after the
production inventory. It refuses foreign or group/world-writable entries, symlinks, hard links,
special files, any ACL/xattr state, sparse allocation, and ASCII case-fold collisions. The output
states that byte-exact case-sensitive paths are required, ownership is local, directory modes are
normalized, and timestamps are not preserved. A case-insensitive or Unicode-normalizing destination
is not inferred safe merely because the local walk passes.

Successful output is a line-oriented `iotox-sync-doctor-v3` record. ADR 0318 advances the strict
pre-creation grammar rather than adding fields to historical v1. Paths are hex encoded. It names
the selected engine and transformations, selected directory/file/entry population, content and
manifest sizes, estimated immutable object count, conservative first-revision store/staging minima,
the default namespace bounds, and free bytes on the *source filesystem*. The treepack staging minimum
also includes the same worst-case canonical path-sort memory charged to its staging quota. It also says:

```text
managed-storage-headroom=not-probed
backup=not-assessed
```

Every successful v3 or v4 record also carries:

```text
filesystem-contract=ready
path-model=byte-exact-case-sensitive-required
ascii-case-collisions=refused
ownership=agent-owner-required-local-owner-projected
hard-links=refused
symlinks=refused
special-files=refused
acl-xattrs=refused
sparse-layout=refused
timestamps=not-preserved
```

The old v1 pre-creation and v2 configured grammars remain unchanged historical records; current
commands emit v3 and v4. `ready` means the observed source fits IoTox's narrow filesystem model at
both walks. It does not mean those excluded features were implemented or that a source cannot change
immediately afterward.

Those lines are part of the contract, not TODO noise. No managed namespace exists yet, and the CLI
does not know where a later Agent configuration will place its store. Source-filesystem free space is
not evidence about that store. Likewise, inventorying synchronized bytes cannot prove an independent
versioned backup or restore drill.

The command is read-only: it does not contact a peer, open the control socket, create a namespace,
grant authority, create an identity, write a manifest/CAS object, stage a projection, or mutate the
source. Exit 0 means the bounded source inspection succeeded; exit 2 is command syntax; exit 4 is a
source, filesystem, hashing, policy, or quota refusal; exit 3 is an output failure.

## Configured namespace headroom

Once a namespace and its local automation exist, run the second read-only entrance against the exact
file-backed Agent configuration:

```text
iotox sync-doctor-configured --config /etc/iotox/agent.conf NAMESPACE
```

The selected namespace must already be initialized and have a stable-device-signed `publish`,
`writable`, or `bidirectional` automation record with a local source. The command reuses that exact
source, engine, projection, interval, and nondefault quota policy. While holding the namespace's
existing transaction it authenticates and inventories the immutable object store, including both
reachable and candidate tree-v2 objects, then inventories the private incoming staging tree.

A ready configured report is the line-oriented `iotox-sync-doctor-v4` grammar. ADR 0318 advances
the strict configured grammar rather than adding fields to historical v2. It adds:

```text
iotox-sync-doctor-v4
configured-namespace=NAMESPACE
automation-generation=GENERATION
automation-interval-ms=INTERVAL
managed-store-objects=OBJECTS
managed-store-bytes=BYTES
managed-staging-bytes=BYTES
managed-store-headroom-bytes=BYTES
managed-staging-headroom-bytes=BYTES
managed-filesystem-available-bytes=BYTES
managed-filesystem-capacity-bytes=BYTES
managed-filesystem-required-bytes=BYTES
source-filesystem-required-bytes=BYTES
managed-storage-headroom=ready
backup=not-assessed
```

It refuses if current occupancy plus the conservative next-revision estimate crosses the configured
store, staging, or object quota. It also refuses when current filesystem availability is below the
estimated additional store and staging requirement. For writable tree-v2 on one shared filesystem,
the requirement includes one complete selected-content reserve for projection work. Policy and
automation stores are reread before success so concurrent management changes cannot splice two
generations into one answer.

The check creates no missing namespace or transaction state, starts no Agent, contacts no peer, and
reserves no bytes. It is a point-in-time observation: source data and free space can change as soon
as it returns, and it assumes the owner-exclusive namespace rules are obeyed. It does not replace
signed namespace health, convergence/repair inspection, capacity testing, abrupt-storage tests, or
versioned recovery custody and a restore drill. ADR 0315 closes the bounded managed-headroom mechanism and
ADR 0318 closes the point-in-time filesystem-contract mechanism; the remaining trust gates are
maintained in `sync-trust-graduation.md`.
