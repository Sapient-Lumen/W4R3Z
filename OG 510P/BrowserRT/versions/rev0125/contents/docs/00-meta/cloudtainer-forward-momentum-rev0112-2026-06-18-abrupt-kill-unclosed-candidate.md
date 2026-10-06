# rev0112 forward momentum — abrupt-kill unclosed-candidate boundary

The highest-risk gap left after rev0111 was not another registry entry; it was the lifecycle boundary around browser death. rev0111 proved an acknowledged OPFS block survived a managed Chromium SIGKILL and same-profile relaunch, but it still left the in-flight/unclosed candidate path as a non-claim.

rev0112 keeps the same package-installed abrupt-kill proof and makes it stricter. The first launch now writes and verifies an acknowledged block through the package-root public API and namespaced guarded OPFS storage path, then creates an intentionally unclosed, partial content-addressed OPFS candidate before the harness SIGKILLs Chromium. The second launch reuses the same origin/profile, reads and verifies the acknowledged block, then inspects the unclosed candidate through the guarded store. Passing evidence requires the candidate to be absent or checksum/read rejected; it must not be silently accepted as a valid block.

This is still a boundary proof, not a durability guarantee. It does not prove fsync, power-loss safety, arbitrary renderer crash recovery, quota eviction survival, or cross-browser behavior. It does, however, close a concrete false-positive risk: partial OPFS content at a content-addressed path should not become trusted product data after process death.

The audit/refactor part is intentionally small: the reopen/abrupt-kill product example now uses `rt.storage` and `rt.coordination` namespaces, and the public API contract audit derives revisioned package-evidence output paths from `REVISION` instead of hard-coded `REV0111` literals.
