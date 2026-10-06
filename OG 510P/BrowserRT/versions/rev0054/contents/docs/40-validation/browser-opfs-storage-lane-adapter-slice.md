# Browser slice — OPFS storage-lane adapter

Current revision: rev0054

Manifest task:

```txt
browser:opfs-storage-lane-adapter-proof
```

This is an explicit `browser/full` slice. It is not part of broad release because broad release must remain browser-light inside cloudtainer windows.

The proof uses the managed Chromium/CDP fixture and verifies:

- local browser page is cross-origin isolated;
- `OpfsBlockStoreStorageLaneAdapter` is created;
- async OPFS provider is available;
- put operations are scheduled through `StorageLaneExecutor`;
- has/verify/estimate run through the same lane;
- page reload readback works in the same temporary Chromium profile;
- get/delete/cleanup run through the adapter after reload;
- scheduler snapshots validate with zero in-flight tasks;
- OPFS, storage-lane, and adapter trace events are present;
- managed Chromium policy is restored during teardown.

The slice is deliberately not a durability claim, not a performance claim, not an OPFS sync access handle proof, and not a browser Worker storage-lane proof.
