# Resilio storage-accounting, occupancy budget, and hidden-growth fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `Folder Types and Management` and `Synchronization Modes` docs still say disconnected folders can remain visible while taking no local space and even no local folder path, which means visible subject and occupied disk are different truths
- those same current docs plus `What Is an RSLS File?` still say Selective Sync presents placeholders as 0-byte or minimal-space stand-ins, which means named file and materialized byte weight are different truths
- current `Ignoring files in Sync (Ignore List)` docs still say ignored subjects are not indexed and are not counted in the `Size` column, which means reported size and namespace reality are different truths
- current `Using Archive for file versioning and restoring deleted files` docs still say old or deleted copies are moved into hidden `.sync/Archive`, kept for a TTL that can be extended to forever, and operators should mind available disk storage space, which means hidden growth and visible working-tree size are different truths
- current `Power user preferences` docs still say low-space warnings are based on the drive with the default folder location, can stop syncing files, and separately list rotated logs and `profiler.dat` under the storage folder, which means sync-stopping budget gate and actual total footprint are different truths
- current `Sync Private Identity & Linking My Devices` docs still say a linked device in `Sync All` mode can show storage status remotely, which means free-space telemetry is its own class rather than just a side note on presence
- older-but-still-current changelog notes still reinforce that iOS gained `view and clear storage used`, which again treats occupancy control as a first-class operator concern rather than a hidden side effect

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct one practical answer to:

> what here is merely named, what actually consumes bytes, what is counted in the product's size claims, what hidden stores can keep growing, and what space budget gate will stop work first?

Current Resilio docs still scatter that answer across modes, placeholders, IgnoreList, Archive, power-user settings, identity storage-status surfaces, and mobile release notes.

That means several materially different questions remain merged unless the operator does their own synthesis:

1. **does this subject occupy namespace only, placeholder bytes, full working bytes, hidden archive bytes, or storage-folder service bytes?**
2. **is the reported `Size` number counting real durable bytes, only indexed sync subjects, or something narrower still?**
3. **what hidden reservoirs can continue growing even while the visible share looks small?**
4. **which low-space guard is actually armed, on which drive, and what work does it stop?**
5. **what evidence proves the current footprint rather than only the currently materialized working tree?**

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow six habits directly:

- **say openly when visible subject and occupied bytes are different truths**
- **say openly when reported size excludes ignored or otherwise unindexed subjects**
- **say openly when placeholders carry namespace without durable bytes**
- **say openly when hidden archive or service storage can grow independently of the visible tree**
- **say openly when free-space gates are tied to a specific budget basis rather than the whole product footprint**
- **say openly when remote storage telemetry is only a witness of one storage class rather than the full local footprint**

But AnonSync should reject six weaker habits:

- one flat `size` label that hides counted-scope rules
- one flat `uses space` sentence that hides placeholder, working-tree, archive, and service-storage classes
- silent hidden growth in Archive or storage folders
- low-space warnings that do not publish what budget basis and drive they actually watch
- remote storage status that implies full-footprint truth without saying what it excludes
- cleanup verbs that imply space was reclaimed everywhere when only one occupancy class changed

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1283` — Storage-accounting contract sheet
- `1284` — Footprint review
- `1285` — Space-stop proof
- `1286` — Occupancy drift timeline
- `1287` — Storage-accounting lineage receipt

These pages keep the Resilio candor and reject the scattered-storage-accounting contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that disconnected visibility, placeholder namespace, ignored-subject exclusion from `Size`, hidden Archive growth, storage-folder logs and profiler residue, remote storage telemetry, and default-location free-space stops are different truths; refuse any interface contract where `what is actually consuming bytes, what is counted, and what budget gate will stop sync first?` still makes the operator merge half a dozen help articles instead of one explicit storage-accounting object.
