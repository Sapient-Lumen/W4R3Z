# Technical preservation review

Prepared 2026-10-07. Local archival candidate only; no public commit or upload is established by this report.

## Independently checked

- All five original SHA-256 values match the intake record. Copies also compare byte-for-byte against the originals.
- All ZIP members passed CRC reads. There are 1,971 regular files and 14 explicit directory entries. No empty explicit directory, duplicate member path, symlink, special file, path traversal or case-fold collision was found.
- Every extracted regular file matches its ZIP member and the earlier independent intake SHA-256 inventory. The extracted file set has no extra files. File permission bits are preserved: two rev0048 tools carry 0755; all other regular files carry 0644. No uploaded script or binary was executed.
- No member path contains a repository-control .git/.github component, .gitmodules, .gitattributes, .gitconfig, .gitignore or AGENTS.md (case-insensitive). This is a path guard, not a content-security guarantee. The largest extracted file is 6,181,192 bytes.
- Original member paths include the ZIP's export-root directory, preserved below versions/REV/files/. Generated files are outside those original-member namespaces. Raw local-header filename bytes, ZIP flags, recorded modes, CRCs and SHA-256s are in each inventory.

[Provenance and version inventory](machine/provenance-and-versions.json) · [readback/checksum results](machine/readback-and-internal-checksums.json).

## Directory metadata and Git limits

Rev0015's following explicit directory entries record mode 0600 (no directory type bits or traversal permission). Literal extraction made child files inaccessible. The local browsing copies add owner traversal only, materializing them as 0700:

- versions/rev0015/files/LivingChristFigures-rev0015-2026.05.15-datacube/CANDIDATES/
- versions/rev0015/files/LivingChristFigures-rev0015-2026.05.15-datacube/OFFICE-CARDS/
- versions/rev0015/files/LivingChristFigures-rev0015-2026.05.15-datacube/archive/

No file mode was changed by this adjustment; no other principal gained access. The source ZIP bytes, source mode 0600 and materialized mode 0700 are retained in the [exact adjustment record](machine/directory-mode-adjustments.json) and member inventory. Other explicit source directories carry 0755. Parent directories implied by file paths are filesystem scaffolding, not additional ZIP directory records. Git retains regular-file executable status but not general directory permissions or empty directories; ZIPs and inventories therefore remain authoritative for those attributes. No empty-directory placeholder was inserted into source material.

## Internal checksum qualifications

- rev0002: no internal SHA256SUMS.txt.
- rev0015: 71 listed hashes match; the checksum file itself is unlisted.
- rev0021: 136 exact-path matches, one byte-identical encoding-alias match and eight referenced but absent historical ZIPs. The checksum file itself is unlisted.
- rev0048: 377 exact-path matches and one byte-identical encoding-alias match. SHA256SUMS.txt and QA-REPORT-rev0048.txt are unlisted.
- rev0104: all 1,355 listed hashes match; the checksum file itself is unlisted.

The two alias matches are the same filename-encoding defect: a UTF-8-spelled checksum path for Sonia-Bermúdez is represented by the ZIP-decoded member spelling Sonia-Berm├║dez. Exact spellings and matching hashes are in the readback report. No source member was renamed or repaired. Standard ZIP decoding and raw filename bytes are both recorded. The rev0015 outer filename's underscore date likewise remains distinct from its dotted-date internal root.

## Version and nested-history limits

Rev0015 preserves two nested ZIP members, labeled rev0013 and rev0014, with original member-byte hashes. They remain unopened payloads in this preparation. The earlier intake described recursively bundled history; this candidate does not claim a fresh recursive check or complete historical release sequence. No nested archives were extracted or added as new releases. Rev0002's archive/rev0001 text is preserved because it is already ordinary top-level ZIP-member content.

The absent rev0021 history is documented rather than reconstructed. Rev0104's historical predecessor metadata is not proof of possession or verification of that predecessor. Old gate reports, keys, signatures, unsigned statements and workflow files are archival evidence, not current attestations.

## Scope boundaries

Verification establishes byte preservation and the stated structural properties. It does not establish every claim's truth, every source's availability, exhaustive secret clearance, legal rights, consent, clinical or operational safety, mathematical validity, signature authenticity or historical gate reproducibility. No historical work order, service test, person search, new personal inference or current contact/referral index was undertaken. External factual context in the errata is attributed to the prior bounded source review rather than represented as a new live audit.
