## Resilio seam evaluation — salvage readiness, continuity escrow, and late decrypt authority

Current official Resilio Sync docs still expose another strong non-clone seam around **salvage readiness truth**.
The important current facts are not subtle:

- `Encrypted folders` still says an encrypted backup peer can only become a later rescue source if two preconditions were preserved ahead of failure: you saved the RW and RO keys somewhere and you did **not** remove the encrypted folder from Sync so the database remains the same as initially created.
- That same current `Encrypted folders` article still says the encrypted node itself cannot decrypt files, so later recovery depends on either reconnecting with the RW key from a safe workstation or running a local CLI decrypt path.
- That same current article still says the local CLI recovery path needs **both** the RW secret and the specific database path, and suggests learning the database name from debug logs by finding the shareID in `sync.log`.
- `Sync Storage folder` still says the storage directory is where Sync keeps its shares' databases and that the path varies materially by desktop OS, Linux package posture, and service account.
- `Disconnecting and Removing Folders` still says disconnect / remove changes what stays in Sync UI while folders remain in the filesystem, which is exactly why `folder still exists on disk` is weaker than `recovery continuity still survives`.
- `Using Archive for file versioning and restoring deleted files` and `Encrypted folders` together still show that ordinary Archive recovery and encrypted-node salvage are different ladders, with the encrypted node unable to republish deleted files back from Archive because it is both read-only and auto-healed to the source delete state.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `if the source dies later, is this encrypted backup actually salvageable, by which lane, and what present-day action would silently destroy that future option?` still depends on combining encrypted-folder guidance, storage-folder guidance, remove/disconnect docs, and archive behavior docs.

So this tranche freezes a stronger replacement line: **salvage readiness, secret escrow, database continuity, and late-decrypt lane become separate modeled truths.**

That is why this revision adds five more first-class pages: **Salvage-readiness contract sheet**, **Continuity-escrow review**, **Recovery-precondition proof**, **Salvage-viability timeline**, and **Salvage-readiness lineage receipt**.
