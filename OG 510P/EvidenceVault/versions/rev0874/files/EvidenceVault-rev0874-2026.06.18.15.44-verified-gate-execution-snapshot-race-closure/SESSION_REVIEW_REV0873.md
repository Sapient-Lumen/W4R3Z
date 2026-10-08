# Session review — rev0873

## What materially changed

The exact rev0872 ZIP validator was proven able to validate one archive and then report the SHA-256 of a different pathname object. The replacement fixture was not a ZIP, yet the parent returned `zip_container_valid` because its final digest reopened the path after all structural handles were closed.

rev0873 now opens one source descriptor, snapshots and hashes exactly those bytes once, performs every ZIP and embedded-inventory check on that immutable snapshot, and refuses success unless the retained source descriptor still has the same bytes and the path still names the same identity. The deterministic builder automatically inherits this correction.

The regression suite reproduces the parent false success by exact script digest, rejects pathname replacement and same-inode mutation in the current validator, verifies the stable path, and reruns the complete rev0872 root/path boundary.

## Recovery discipline

Canonical README patch states and the 64-file OCF v244 low-entropy output family were investigated. Neither yielded a path, size, and full SHA-256 match. No guessed bytes were added. Coverage remains 109 exact current-path files and 125 rehydratable files.

## Still at risk

Root/component rights closure, the 17 selected StreamFold payloads, canonical `README.md`, and 4,461 unavailable canonical files remain unresolved.
