# MP4-M4A-ATOM-BUDGET-01 — rev0032

Canonical packet: **U-125**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ share scanning asks TinyTag to load duration metadata for supported audio files larger than 128 bytes. In all archived source lanes, `.m4a`, `.m4b`, `.m4r`, `.m4v`, `.mp4`, `.aax`, and `.aaxc` route into the vendored TinyTag MP4 parser.

The MP4 duration traversal is tree-driven. When a traversed atom type maps to a parser callable, the traversal layer reads the complete advertised atom payload and passes that `bytes` object to the parser:

```text
sub_path(fh.read(atom_size))
```

For the `moov/mvhd` duration leaf, the parser needs only a small fixed prefix for version, timescale, and duration. Current behavior still materializes the entire advertised `mvhd` payload before parsing those fixed fields. The same traversal shape is also used for `stsd/mp4a` and `stsd/alac` leaves, so the coherent fix shape is an MP4 atom-leaf budget or bounded-prefix parsing at the traversal boundary.

This is local/share-scanner parser hardening. It is not an inbound peer protocol parser issue, not code execution, and not a claim that large MP4 atoms are globally invalid. The security boundary is a Nicotine+/TinyTag metadata-scanner budget for local indexing work.

## Source status

The source trace covers all archived lanes from the rev0003 upstream source bundle:

```text
github-tag-3.3.10:
  commit caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
  shares.py routes supported audio files larger than 128 bytes through TinyTag.
  tinytag.py maps .m4a/.mp4-family extensions to MP4.
  MP4.AUDIO_DATA_TREE maps b'mvhd' to Parser.parse_mvhd.
  MP4._traverse_atoms() calls the leaf parser on fh.read(atom_size).

github-branch-3.3.x:
  commit 98089ac233aa57786e8dbdc48123f6ac1c4767d8
  same vendored tinytag.py hash and same MP4 traversal/read behavior as 3.3.10.

github-branch-master:
  commit f4e17d59783dbc48ea31d2e899a681e2dd1ed500
  shares.py routes .m4a/.mp4-family files through TinyTag._get_parser_for_filename(...)
  and tag._load(...).
  _MP4._audio_data_tree maps b'mvhd' to _MP4._parse_mvhd.
  _MP4._traverse_atoms() calls the leaf parser on fh.read(atom_size).
```

The master lane modernizes TinyTag internals and supports more metadata fields, but the duration traversal still materializes the matching `mvhd` atom payload before the fixed-prefix duration parser runs.

## Maintainer-style witness

Current-behavior test:

```text
maintainer_artifacts/mp4-m4a-atom-budget-01/test_mp4_m4a_atom_budget_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness constructs compact MP4-like streams:

```text
ftyp
moov
  mvhd = valid version/timescale/duration prefix + controllable padding
```

Observed current behavior:

```text
1,048,699-byte mvhd payload:
  read once as one bytes object at the leaf-parser boundary.

2,097,169-byte mvhd payload:
  read once as one bytes object at the same boundary.

Minimal 20-byte mvhd duration prefix:
  read as 20 bytes.

20-byte prefix + 4,096 bytes padding:
  read as 4,116 bytes, even though the duration calculation needs only the
  fixed prefix.
```

The tests intentionally pass on current behavior. A fixed-behavior test should expect an over-budget atom leaf to raise, skip, or stop before materializing an arbitrary payload, while preserving normal MP4/M4A duration extraction.

## Impact framing

Conservative impact:

```text
A local or downloaded MP4/M4A-like file in a scanned/shared path can make the
share metadata parser allocate a bytes object matching an advertised MP4 atom
leaf payload before the duration parser consumes the small fixed fields it needs.
```

Why this remains lower severity:

```text
- It is local/share-scanner media metadata parsing, not inbound peer-message
  parsing.
- Work and memory are proportional to file size; the witness does not prove an
  infinite loop or memory corruption.
- Large MP4 atoms can exist for legitimate reasons, so the fix should be a local
  metadata-scanner budget or streaming prefix parser rather than blanket rejection.
- Public adjacency exists in TinyTag source/support and general MP4 parser
  hardening history, but the captured searches did not find a direct Nicotine+
  U-125-style public issue.
- It does not outrank U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.
```

## Fix-shape notes

A coherent fix should be small and testable:

```text
- Define a local maximum MP4 metadata atom-leaf byte budget for TinyTag/Nicotine+
  share scanning.
- Avoid `fh.read(atom_size)` for fixed-prefix leaves such as mvhd when only a
  small prefix is required.
- For `mvhd`, parse version 0/1 duration from bounded fixed-size reads and seek
  over the remainder.
- For `mp4a` and `alac`, parse only the required fixed fields or enforce a small
  sample-entry budget before materialization.
- Keep valid ordinary MP4/M4A files working.
- Add fixed-behavior tests for:
    * a normal small mvhd atom;
    * a version-1 mvhd atom;
    * an atom ending exactly at the configured budget;
    * an atom exceeding the budget by one byte;
    * nested stsd/mp4a and stsd/alac leaves;
    * unknown atoms that should continue to be skipped with seek rather than read.
- Keep this fix in the MP4 metadata parser/share-scanner path; do not merge it
  with Ogg continuation accumulation, WMA/ASF object-size progress, FLAC block
  validation, ID3v2 frame rows, share-cache provenance, or network-message caps.
```

## Evidence files

```text
evidence/rev0032-mp4-m4a-atom-budget-pytest-run.txt
evidence/rev0032-mp4-m4a-atom-budget-helper-rerun.txt
evidence/rev0032-mp4-m4a-atom-budget-source-trace.md
evidence/rev0032-mp4-m4a-atom-budget-source-trace.json
evidence/rev0032-web-public-overlap-mp4-m4a-atom-budget.md
```
