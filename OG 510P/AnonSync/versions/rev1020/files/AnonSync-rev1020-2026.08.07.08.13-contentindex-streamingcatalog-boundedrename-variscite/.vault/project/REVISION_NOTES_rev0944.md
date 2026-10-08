# AnonSync rev0944

Mission: replace Resilio Sync with a practical C++ folder-sync product whose
shipping peer service supports direct, Tor, and I2P routes.

## Product-performance correction

- One shipping folder traversal now lazily retains a move-only payload-store
  mutation batch across sequential local publications.
- Batch construction acquires one exclusive cooperative lease, validates the
  identity marker, performs one complete bounded namespace scan, cleans exact
  stale publication residue, and freezes one exact capacity/index view.
- Successful puts update that live index after durable create-new publication
  and exact reopen; ordinary success no longer rescans all older payloads.
- The folder owner releases the batch before remote payload snapshots/apply,
  network work, and post-traversal absence handling.
- One-put APIs delegate to one-element batches, retaining one mutation engine.
- Retained scans may reuse a prior complete SHA-256 result only for an exact
  unchanged digest-name/device/inode/mode/link/owner/size/mtime/ctime observation
  under the exact identity-marker lease anchor.
- New, replaced, changed, restart-cold, and forensic observations still receive
  complete byte verification.

## Audit and refactor

- Combining the batch and warm-cache branches exposed an old-signature call in
  exceptional batch recovery. Recovery is now explicitly cold and receives no
  verification cache.
- Runtime tests distinguish same-inode overwrite from guaranteed atomic inode
  replacement, and prove wrong bytes fail in both cases.
- Batch tests prove one construction scan across many puts, move-only lifetime,
  shared/mutation busy classification, exact release, and a 32-file shipping
  folder pass.
- The release verifier now understands the actual BOOTSTRAP wrapper: one visible
  `BOOTSTRAPROSE.md`, hidden source under `.vault/project`, and retained hidden
  `.vault/parent`, `.vault/source-objects`, `.vault/witnesses`, plus `.h0p3`.
  Unknown visible roots and unknown `.vault` namespaces still fail closed.

## Measured effect and explicit limits

Directional measurements from this exact source put 256 distinct 4 KiB payloads
through one retained batch in about 1.14 seconds versus about 3.23 seconds through
one-element batches. A 64 MiB-plus-4 KiB snapshot took about 0.243 seconds cold
and 0.0022 seconds warm, with zero warm payload bytes hashed.

These are not broad scale qualification. Every new batch or snapshot still walks,
opens, and stats the complete private namespace. A large local segment retains
the exclusive cooperative lease. Batch-created payloads are conservatively
hashed once by the next retained scan before entering its warm cache. The cache
is process-local; there is no persistent exact metadata index or rotating scrub.
New local bytes are still read twice, one-byte edits still retransmit complete
content, and payload/partial reclamation, rename/directories, live public-overlay
qualification, and the first named Resilio-uninstall workflow remain open.

Archive: `AnonSync-rev0944-2026.07.29.13.16-batchedadmission-warmverification-wrappertruth-rosebatch.zip`
