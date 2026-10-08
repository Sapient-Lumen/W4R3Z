## Resilio evaluation — name planes, alias drift, and label-authority fragmentation

Current official Resilio docs are candid that `name` is not one truth class.
They still separate:

- the **identity name** that participates in certificate creation and peer recognition
- the **device name** shown alongside username and fingerprint in mobile identity views
- the **share path name** that comes from the filesystem object on disk
- the **local share alias** that can diverge from disk name in desktop UI only
- the **link-inserted label** that can differ per generated link or QR without changing the local share alias
- the **derived backup-folder default name** that can depend on mobile device class or device name

That candor is useful.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `what exactly did I rename, where will that new label show up, and did I change authority or only presentation?` still depends on stitching together custom-share-name tips, identity docs, mobile-interface pages, camera-backup naming notes, and filesystem rename guidance.

So this tranche freezes a stronger replacement line:
**identity handle, device handle, filesystem subject name, local UI alias, invitation label, and derived default folder name become separate modeled truths.**

That is why this revision adds five more first-class pages: **Name-plane contract sheet**, **Local-vs-remote alias review**, **Name-authority proof**, **Label-drift timeline**, and **Name-plane lineage receipt**.
