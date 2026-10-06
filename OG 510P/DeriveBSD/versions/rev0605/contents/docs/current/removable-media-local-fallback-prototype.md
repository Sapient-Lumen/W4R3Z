# Current removable-media local fallback prototype

The removable-media local fallback has a replayable userland prototype in addition to schema and receipt fixtures.

Run:

```sh
python3 tools/check_removable_media_local_fallback_prototype.py
```

The checker regenerates the deterministic prototype in a temporary workspace and compares it with `validation/removable-media-local-fallback-prototype-run.receipt.json`.

What the prototype actually exercises:

- a fixture media tree with a selected regular file and hostile members;
- path traversal, absolute path, directory-subject, symlink-subject, and symlink-ancestor rejection;
- dirfd/openat capture from a pinned media-root fd rather than friendly path resolution;
- no-follow opens for ancestors and the selected leaf;
- lstat/fstat object-stability checks around the opened member and source-stability evidence through copy;
- capture into a digest-addressed preserved copy;
- verification of the preserved copy after capture;
- simulated detach by removing the source media tree before the later worker starts;
- worker delivery by preopened input/output file descriptors rather than the live media path;
- worker-side fd inventory proving there are no unexpected inherited descriptors;
- a parent-held media canary fd that is deliberately not passed and is proven absent in the worker;
- derivative output that binds the preserved capture digest and remains separate from the preserved subject.

What it deliberately does not claim in this cloudtainer:

- no real FreeBSD mount is performed;
- Capsicum, jail, devfs, and pf enforcement are not exercised here;
- the prototype is an ordering, capture, and dataflow proof, not the production backend.

The modeled vertical-slice guard, `tools/check_removable_media_local_fallback_vertical_slice.py`, now requires this prototype receipt plus `validation/removable-media-safe-capture.receipt.json` as evidence. That keeps the modeled attach→capture→detach→post-detach-reader story connected to a real byte-moving path and to a concrete no-symlink path-walk guard.

Last updated: 2026-06-04r536
