# Descriptor-bound ZIP validation — rev0873

## Priority result

The exact rev0872 `scripts/validate_zip_container.py` was vulnerable to a source-container identity split. It parsed and decompressed one ZIP, closed those handles, then reopened the pathname to compute the reported SHA-256. A deterministic regression swaps the pathname at that final reopen. The parent still reports `zip_container_valid`, retains the original ZIP size, and reports the digest of a replacement file that is not a ZIP.

This is a demonstrated correctness failure at the delivery boundary. It does **not** imply that an outside party modified a prior EvidenceVault bundle.

## Correction

rev0873 opens the archive once without following a final-component symlink and captures device, inode, mode, link count, size, `mtime`, and `ctime`. It copies exactly those descriptor bytes into an anonymous temporary snapshot while hashing them once. `zipfile`, EOCD/local-header parsing, decompression, and embedded-manifest checks all read independent `os.pread` cursors over that immutable snapshot.

Before success, the validator rehashes the retained source descriptor, requires equality with the snapshot digest, and requires the original pathname still to name the opened identity with unchanged metadata. `sha256_file()` now uses the same no-reopen policy. Because the deterministic ZIP builder imports this validator, temporary archive approval is now byte-bound to the inode that the builder later publishes and rechecks.

## Regression results

- Exact parent validator SHA-256: `bd06e3ecabc4a8a5eefed3960e53af2a29990e0cb405d4a705d1d1135901a0f5`.
- Parent false success: reproduced; validated original digest `4775…ad20`, reported replacement digest `c4f8…9082`, final path not a ZIP.
- rev0873 pathname replacement: rejected.
- rev0873 same-inode mutation after snapshot capture: rejected.
- Stable happy path: all four descriptor/snapshot return checks verified.
- Inherited rev0872 root anchoring, strict path spelling, exact-byte boundaries, and non-mutating entrypoints: retained and passed.

## Recovery work, without guessed bytes

The canonical root README was tested against cumulative and reverse incremental patch states and current byte ranges; none matched its indexed 10,499-byte identity and complete SHA-256. The indexed 64-file OCF v244 batch-output family and adjacent generator/family evidence were also tested as bounded hash-oracle candidates; no path-specific size plus full-digest match was found. No bytes were admitted.

Coverage therefore remains **109 / 4,586 exact current-path files**, **125 files / 4,973,641 bytes rehydratable**, and **4,461 files / 101,448,349 bytes unavailable**.

## Remaining priority blockers

The owner-approved root/component rights decision is absent; all 17 selected StreamFold payloads are absent; and canonical `README.md` remains the sole unresolved present-path mismatch.

The snapshot boundary uses POSIX descriptor operations available in this cloudtainer. It is a local transport-integrity control, not a signature, external attestation, or claim of platform-independent source authenticity.
