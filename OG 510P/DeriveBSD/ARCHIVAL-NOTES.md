# Archival notes

## What is preserved

The eight original ZIPs retain their exact filenames and bytes. The companion `contents/` trees retain every original file-member path, including wrapper directories, generated files, validation logs and carried bytecode where present. Later editorial README files sit outside those trees. The archive's stale metadata and filename/internal-cut differences are not silently repaired.

ZIP member timestamps are preserved metadata, not authenticated chronology. The selection has gaps and must not be described as a complete release or development history.

## What was checked

The source archives and extracted files were checked against recorded SHA-256 values. The curation then read the relevant README/changelog entries and focused design/runtime documents. It examined source material statically and did not execute uploaded programs, checkers, bytecode, shell scripts or historical work orders.

Historical validation reports are attributed to the carried source. A reported pass, a fixture named `proof`, or an accepted ADR does not by itself establish a real deployment or an independently repeated test.

## Privacy and safety scope

A finite intake credential-pattern scan reported no high-confidence hits. Additional static review found example-domain identities, explicit fixture material and historical build-path residue; it did not identify a confirmed live credential in the reviewed material. These are bounded findings, not certification that every file is free of secrets, private material, unsafe code or third-party restrictions.

Some snapshots contain compiled Python bytecode, and the latest includes historical session reviews, logs and validation fixtures. These are preserved as received; their presence should not be read as an execution recommendation. The `.pkg` payloads inspected in the latest runtime are JSON fixtures that explicitly say they are not real FreeBSD packages. The tiny `invoice.pdf` in the removable-media fixtures identifies itself as harness material.

## Licensing

No filename beginning with `LICENSE`, `COPYING` or `NOTICE` was found, and a bounded scan of UTF-8 text did not identify a standard explicit license-grant phrase. That observation is not an exhaustive determination of rights. Architectural discussions of licenses, external references and carried author labels do not establish a repository-wide grant.

No new blanket license is added by this curation. Preserve any existing attribution and notices; consult the relevant rights holder before relying on reuse permissions that are not expressly documented.

See [the source map](ARCHIVAL-EVIDENCE.md) and [archive manifest](ARCHIVE-MANIFEST.json).
