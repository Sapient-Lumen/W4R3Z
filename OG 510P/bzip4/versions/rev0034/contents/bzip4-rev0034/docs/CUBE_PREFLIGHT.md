# Datacube ZIP preflight — rev0031

`bzip4_cube_preflight` treats an archive as untrusted structure and never
extracts it. The final path is opened without following a symlink; all reads use
a retained descriptor and positional I/O; the descriptor fingerprint is checked
after inspection. A change adds a fatal `source_changed` issue.

## Bounded directory resolution

A terminal classic EOCD is found with exact comment coverage. The parser then
resolves either its ordinary directory values or an adjacent ZIP64
locator/ZIP64-EOCD chain. Single-disk metadata, record adjacency, versions,
legacy/ZIP64 agreement, checked 64-bit ranges, and the bounded extensible-data
sector are validated before central parsing begins.

Independent limits cover entry count, central-directory bytes, one name,
aggregate retained names, diagnostics, and the complete ZIP64 EOCD. The entry
count must also be feasible from the central-directory fixed-header byte budget
before metadata is reserved.

## Central-directory memory model

The declared central directory is never copied wholesale. Each record is read as
a fixed 46-byte header, a name, and one reusable extra-field buffer; comments
are skipped by checked offsets. Accepted names are appended to one contiguous
arena. Each retained entry stores numeric metadata and a name offset/length.
Duplicate detection sorts entry indexes over the same arena.

Central-extra scratch is destroyed before duplicate sorting; duplicate-order
scratch is destroyed before local-record reconciliation. Local name/extra
buffers are reused. Report schema `bzip4.zip-preflight.v7` exposes:

- actual central name bytes;
- peak individual central read;
- entry descriptor width;
- retained entry-vector capacity bytes;
- retained name-arena capacity bytes; and
- peak core retained bytes across explicitly tracked parser vectors.

The retained-memory telemetry excludes allocator bookkeeping, issue strings,
the method map, and the EOCD tail. It is intended for deterministic layout and
capacity comparisons, not as an RSS substitute.

## Optional duplicate-payload nomination

`--probe-payload-duplicates` enables a second, explicitly bounded pass after
the complete structural gate. It first nominates nonempty, unencrypted entries
with equal central CRC-32 and uncompressed size. Those values are a classifier
hint, not proof. Candidate entries with the same method and compressed size are
then SHA-256 grouped and compared byte for byte through descriptor-pinned
ranges. Only the final exact comparison contributes verified repeated-payload
counters.

The probe remains off by default. It has independent read, group-entry,
minimum-payload, and chunk-memory limits. A group is either admitted against a
conservative complete hash/compare budget or skipped whole. The existing
24-byte local span now carries a compact payload delta, so no second per-entry
offset vector is retained. Probe scratch telemetry is separate from parser
retention.

## Structural checks

- exact classic and ZIP64 terminal-record accounting;
- complete local and central extra-field TLV framing;
- sentinel-driven central ZIP64 resolution;
- the required two-size local ZIP64 pair whenever either legacy size is a
  placeholder;
- redundant ordinary/ZIP64 size agreement;
- local/central name, flags, method, CRC, and size reconciliation;
- signed/unsigned 32-bit and 64-bit data descriptors;
- path traversal, absolute, drive-qualified, backslash, NUL, empty, dot, and
  empty-interior-component rejection;
- duplicate names;
- encrypted-entry policy;
- POSIX/DOS/name member-type classification and mismatch policy;
- local data ranges, central overlap, and a maximum-end interval sweep that
  catches nested record overlaps; and
- bounded issue retention with fatal-suppression accounting.

Unknown extra identifiers are accepted only when their TLV framing is complete.
The parser supports bounded single-disk ZIP64 but deliberately rejects split or
spanned archives.

## Representative evidence

The 18 regular-datacube archives pass with 20,677 entries, 406,637,451 logical
bytes, 2,563 per-entry ZIP64 representations, and zero issues. The optional
probe exactly verifies 238 repeated-payload groups containing 678 entries. The
440 entries beyond one representative per group account for 1,718,627 gross
repeated compressed bytes and 4,935,579 gross repeated logical bytes. A
separately generated 65,536-entry archive exercises a real archive-level ZIP64
EOCD and passes both preflight and independent ZIP integrity checking.

## Nonclaims

Preflight does not decompress member data, recompute CRCs, authenticate
provenance, authorize extraction, or prove an extractor bug-free. The optional
probe classifies only conservative repetition candidates and exact compressed
payload identity. It does not detect differently compressed equal content or
claim net savings after reference metadata. The tool remains a bounded
admission and measurement boundary.
