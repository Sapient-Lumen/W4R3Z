# Audit — rev0969

Rev0969 makes the shipping historical restore a path-local compare-and-restore operation. The owner must name both the retained historical operation and the exact sole current operation shown by inspection. A stale request fails as typed `source_changed` stage `restore_current_operation` before catalog, rooted destination, or targeted payload-store authority, while the later visible-state and publication fences remain mandatory.

The shared `SyncReplicaHistoricalVersionRestoreRequest` is now the request identity across CLI parsing, the owner-only socket, generation coalescing, stable and transient status, and folder-owner execution. Status advances to `anonsync.peer-service.status.v14`; the exact local response advances to v2. The rev0966 raw frame remains an explicitly unbound compatibility path, but the shipping CLI cannot emit it.

The adjacent audit corrected a false process oracle. Atomic publication can legitimately remove an exact internal `.anonsync-publish-v1-...tmp` name between enumeration and read. Both affected tree comparators now ignore only the product's exact lowercase-hex temporary grammar; broad dotfile suppression was rejected. The sync-once comparator also hashes files in bounded 1 MiB blocks instead of materializing whole files.

Mechanical evidence binds an 18-file binary-aware patch reconstructed 18/18 against sealed rev0968, the 568-file active projection, 247/247 structural checks, all 258 GCC tests, the independent 39-test GCC product set, the 238-edge Clang ASan/UBSan graph, and all 39 sanitizer product tests without a retained diagnostic.

The boundary remains narrow. Exact-current intent is not a durable transaction from browse through restore. It does not pin versions, define chronology, select conflicts, restore directories or batches, impose retention quotas, or make garbage collection safe.
