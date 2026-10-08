# Resilio subject scope, ignore divergence, namespace role, and unsupported-name fragmentation evaluation

## Why this pass exists

The archive already had doctrine for chronology, change witness, materialization, path liveness, placeholder state, and archive truth.
What the current revision chain still lacked was one tighter current Resilio pass about another ordinary operator question:

> why is this pathname absent from sync, absent from size, hidden in the UI, present only as service residue, or blocked entirely — and is that because it is user data, an ignored subject, a hidden-but-real item, a critical service artifact, a transient transfer file, or an invalid name?

Current official Resilio docs are useful here precisely because they remain candid.
Today those docs still show that:

- `IgnoreList` rules exclude matching files from indexing and from the `Size` column, ship with default system/temp exclusions, are case-sensitive, and are advised — but not required — to match across peers;
- editing `IgnoreList` after a folder was already scanned does not retroactively unsend the folder structure, and later ignore changes can require rescans or restart to take full effect;
- the hidden `.sync` folder is critical service state rather than ordinary user content, and deleting or corrupting it suspends synchronization for that folder;
- files ending in `.!sync` are temporary transfer artifacts rather than finished user files;
- xattrs ride a separate `StreamsList` whitelist path, cannot be ignored via `IgnoreList`, and may fall back into stub files under `.sync/Streams` when a filesystem cannot store them directly;
- at least some current Sync UI surfaces still hide dot-prefixed hidden files by default;
- unsupported trailing-asterisk names can be interpreted as system data and disrupt syncing rather than behaving like ordinary user paths;
- `My files don't sync` still mixes unsupported names, encoding, path-length limits, permission failures, partial-transfer residue, time drift, and drive/filesystem faults into one troubleshooting lane.

That is strong operator candor.
It is also another strong reason not to clone the contract as-is.

## What current Resilio still gets right

### 1) It admits that presence in the filesystem is not the same as membership in sync scope

The current `IgnoreList` docs still say ignored subjects are not indexed and are not counted in `Size`.
That matters because it tells the truth that a file can exist on disk while not participating in the product's tracked subject set.

### 2) It admits that service artifacts and temporary residues are not ordinary user files

The current `.sync` article still says `.sync` is critical hidden service state, and the same article still says `.!sync` files are in-progress transfer artifacts.
That distinction is worth preserving.

### 3) It admits that metadata lanes and byte lanes do not share one exclusion authority

The current xattrs article still says `IgnoreList` cannot ignore xattrs and that `StreamsList` governs that lane instead.
That is unusually candid and worth keeping.

### 4) It admits that some invisibility is only a UI choice, not an exclusion truth

The current mobile settings docs still say hidden dot-files are not shown in the UI by default.
That matters because `not shown` and `not tracked` are different truths.

## Why AnonSync still should not clone it

### 1) Scope truth is still too scattered

The ordinary operator still has to reconstruct whether a pathname is:

- fully in sync scope,
- excluded by ignore rule,
- hidden only by the UI,
- critical service state,
- temporary transfer residue,
- xattr-sidecar state,
- or blocked because the name itself is unsupported.

AnonSync should not let one vague `ignored`, `hidden`, or `not syncing` label hide those distinctions.

### 2) Peer-local exclusion and shared namespace still sit too close together

Current `IgnoreList` docs still say matching lists across peers are advisable but not compulsory.
That means the same share can have peer-local scope differences while still looking like one common folder.
AnonSync should publish scope divergence as first-class state.

### 3) Retroactivity and structural propagation are still too easy to overclaim

Current `IgnoreList` docs still say later ignore edits do not retroactively unsend already-known folder structure.
That means `ignored now` is weaker than `never announced`, and much weaker than `purged everywhere`.
AnonSync should not blur those claims.

### 4) Namespace role and delete safety still require folklore

Current docs do tell the truth about `.sync`, `.!sync`, and xattr stub fallback.
But the operator still has to remember that from separate articles instead of seeing a stable product-owned `namespace role` classification before deleting something mysterious.
AnonSync should publish namespace role and delete safety directly.

## Hard decisions now locked for AnonSync

1. **Subject scope is a first-class per-peer contract object, not a side effect of file visibility and troubleshooting.**
2. **User file, peer-excluded file, UI-hidden file, service-critical artifact, temporary transfer residue, metadata-sidecar artifact, and invalid-name-blocked subject are separate namespace roles.**
3. **Visible in a path is weaker than indexed, indexed is weaker than counted, and counted is weaker than replicated.**
4. **`Ignored now` is weaker than `never announced`, and `never announced` is weaker than `purged from every peer view`.**
5. **Delete authority over service artifacts and transfer residues must be reviewed explicitly, not inferred from ordinary file affordances.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Subject-scope contract sheet**
- **Ignore-divergence review**
- **Namespace-role review**
- **Scope proof**
- **Subject-scope lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that ignored files, hidden files, service state, temp transfer residues, xattr sidecars, and invalid names are materially different truths. But it still makes one ordinary operator answer — `why is this pathname absent, invisible, uncounted, or unsafe to touch?` — depend on several articles instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.

