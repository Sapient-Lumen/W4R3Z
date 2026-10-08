# Resilio remedy hardening attestation catastrophe recovery, reconstitution legitimacy, and anchor fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the state survives named regime shifts`, `we can recover from loss or corruption`, and `the recovered world is legitimately continuous with the prior governed world` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Cloning Sync` docs still say cloning any Sync instance by plain copy, disk cloner, or backup-image means is unsupported and may create two or more instances that do not transfer data to one another
- current `Sync Storage folder` docs still say the storage folder keeps current configuration, auxiliary settings files, shares databases, dumps, and logs
- current `Encrypted folders` docs still say recovery from an encrypted backup peer is possible only if RW and RO keys were saved and the encrypted folder was not removed from Sync so the database remains the same as initially created
- the same current `Encrypted folders` docs still say local decryption requires the RW secret plus the path to the database file, which may have to be learned from debug logs
- current `Service files missing / Cannot identify destination folder` docs still say deleting or corrupting `.sync` suspends synchronization, and the operator fix is to remove the share, delete `.sync`, and add it back, which creates a new synchronization instance
- current `If your device is stolen` docs still say a serious recovery path requires backing up data, removing shares, unlinking the old identity if linked, deleting synced data from the storage folder, reinstalling Sync with settings removed, regenerating identity, relinking devices, and resharing folders
- current `Updating installation to Resilio Sync v3` docs still say preserving configuration across update depends on keeping the same command-line parameters, user, and storage path, which reinforces how much recovery truth depends on retained anchors
- older but still current `Resilio Sync change log` materials still record corrupt-database and lost-certificate fixes, reminding us that crash or corruption recovery is not a merely hypothetical seam

## Where the current contract still fragments

The problem is not that Resilio lacks disaster-recovery clues.
The problem is that it still does not produce one first-class, case-scoped **catastrophe-recovery legitimacy** object.

Today an operator can often infer only weaker truths such as:

- the bytes were recovered, but the same governing identity, share instance, or database lineage may not have been preserved
- the storage folder survived, but the operator still has to know which files are authoritative anchors and which merely happened to remain on disk
- encrypted recovery is possible, but only under exact saved-key and unchanged-database preconditions
- `.sync` corruption can be repaired, but the repair itself may create a new synchronization instance rather than reconstitute the prior one
- theft response can sever the old world and establish a safer new one, but that is re-foundation, not same-world recovery
- a copied image may look like a fast restore path, but the vendor explicitly says cloning is unsupported and may create twin runtimes with strange behavior

Those are useful clues.
They are not the same as an explicit answer to `after loss, corruption, theft, or catastrophic world damage, what exactly was preserved, what was regenerated, what continuity sentence is still honest, and which stronger same-world recovery sentence must remain blocked?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the state survived upgrades and normal world transitions`.
It needs to support claims such as:

- the prior governed world is lost, but a safe re-founded successor world has been established
- recovery is possible only if named anchors survive, such as keys, database lineage, storage continuity, or explicit receipts
- user-visible bytes were recovered, but governing continuity is blocked because the share instance or identity had to be regenerated
- the named catastrophe class was recovered for the governed slice, but broader same-world reconstitution remains blocked

So AnonSync should not clone Resilio's present contract at this seam.
It should borrow the candor about unsupported cloning, storage-folder anchor dependence, encrypted-node recovery conditions, `.sync`-loss repair branching, and stolen-device reset flows, while replacing the fragmented operator story with one first-class family for **catastrophe recovery, reconstitution legitimacy, and anchor-bounded continuity truth**.
