# ADR 0278: Freeze selective tree-v2 projection and owner mode

Status: accepted, 2026-09-01

## Context

Tree-v2 previously scanned and materialized every ordinary path and represented regular-file
metadata as only an executable bit. That was sufficient for the first causal multiwriter gate, but
not for ordinary directory use: caches and machine-local subtrees need to remain outside authored
history, different replicas may choose different local subsets, and owner read/write bits must not
silently widen during convergence.

Selection cannot be a remotely supplied transfer filter. The namespace root, visible subset, and
metadata fidelity are recipient-local policy, just like activation. A hidden baseline entry also
cannot be converted into a tombstone merely because this device stopped projecting it.

## Decision

Add canonical namespace-policy format v2 and tree-manifest format v2 while retaining byte-exact v1
decoding and default v1 emission.

Namespace policy v2 carries:

- metadata mode `executable-v1` or `owner-mode-v2`;
- at most 64 sorted, unique include component-prefixes;
- at most 64 sorted, unique exclude component-prefixes; and
- no glob, symlink, absolute-path, `.`/`..`, control-byte, or `.iotox-conflicts` grammar.

An empty include set selects the complete ordinary tree. Otherwise a file is selected when an
include is its component-prefix, and directory ancestors of includes remain traversable. Exclude
always wins. An include wholly hidden beneath an exclude is rejected as contradictory policy.

Selection is local projection policy, not shared authority or shared branch policy. A scan ignores
new unselected local paths but retains every unselected entry already present in its signed baseline;
it never authors a tombstone from policy hiding. Atomic materialization skips unselected manifest
paths and copies existing unselected local files into the staged tree before exchange. Thus a remote
branch remains causally complete while each device can retain a different visible subset.

Manifest v2 stores exact regular-file owner `r/w/x` bits. Only readable private modes `0400`, `0500`,
`0600`, and `0700` are accepted; group/other permissions, special bits, directory modes, links, and
special files remain outside the contract. Manifest v1 executable entries canonically map to
`0600`/`0700`, so mixed retained history does not create false changes.

The ordinary command is:

```text
iotox sync-create NAMESPACE DIRECTORY read-write INTERVAL_SECONDS \
  executable-v1|owner-mode-v2 [include=PATH|exclude=PATH...]
```

Paths are relative to the owner-selected local directory. Runtime namespace listings expose only
metadata mode and rule counts, never selected path names.

## Consequences

Existing read-write commands retain their bytes and complete-tree behavior. Namespace and manifest
v2 are emitted only when the new local policy or metadata requires them. Peers still exchange the
complete authenticated graph and every required CAS object in this first version; selective
projection is not a bandwidth-on-demand placeholder or remote sparse-fetch protocol.

Owned tests cover canonical v1/v2 migration, malformed rules and modes, selection precedence,
baseline retention, excluded-local-file survival across atomic exchange, exact owner-mode round
trip, CLI bounds, and live Agent creation/persistence/rendering. Symlinks, case-fold translation,
timestamps, ownership identities, ACLs, xattrs, special files, sparse remote object fetching, and
incremental watching remain unsupported rather than being normalized implicitly.
