# Current removable-media local fallback executable slice

The removable-media local fallback lane now has executable cloudtainer proof instead of only cross-linked JSON examples.

Three checks carry the substance:

```sh
python3 tools/check_removable_media_safe_capture.py
python3 tools/check_removable_media_local_fallback_harness_run.py
python3 tools/check_removable_media_local_fallback_prototype.py
```

`tools/removable_media_safe_capture.py` proves the capture primitive that the lane depends on: a pinned media-root fd, dirfd/openat traversal, no-follow opens, regular-file-only leaf admission, lstat/fstat object stability, source stability through copy, digest-addressed preservation, and rejection of traversal, absolute paths, directories, symlink leaves, and symlink ancestors.

`tools/removable_media_local_fallback_harness.py` drives fixture bytes from `fixtures/removable-media/local-fallback/exfat-card/invoice.pdf` through the modeled first lane: claimed filesystem-family admission, relative clean selected path, safe regular-file capture before later operations, digest-addressed preserved copy, detach gate, post-detach worker constraints, and a separate derivative summary. Its canonical output is `spec/examples/removable.media.local.fallback.harness.run.json`, with evidence files under `validation/removable-media-local-fallback-harness/expected/`.

`tools/run_removable_media_local_fallback_prototype.py` is the smaller no-root executable prototype. It creates a hostile fixture tree, rejects path traversal, absolute paths, directories, symlink leaves, and symlink ancestors, captures one regular file through the shared safe-capture helper, removes the source tree before worker launch, and starts the later worker with only preopened input/output file descriptors. The worker inventories fds without `/proc`, rejects unexpected inherited descriptors, and proves a parent media canary fd was not leaked. Its canonical receipt is `validation/removable-media-local-fallback-prototype-run.receipt.json`.

The vertical-slice check now joins the older modeled receipts to all executable surfaces. `tools/check_removable_media_local_fallback_vertical_slice.py` can no longer pass by schema coherence alone; it must also see safe-capture evidence, real-byte capture evidence, and fd-only post-detach worker delivery.

This is still not the final FreeBSD implementation. It does not perform a real block-device mount, enter Capsicum in the cloudtainer, or create a real jail/devfs ruleset. It does give the cube a replayable byte-level regression guard for the riskiest sequencing invariant: safely capture first, detach, then process only the preserved object.

Last updated: 2026-06-04r536
