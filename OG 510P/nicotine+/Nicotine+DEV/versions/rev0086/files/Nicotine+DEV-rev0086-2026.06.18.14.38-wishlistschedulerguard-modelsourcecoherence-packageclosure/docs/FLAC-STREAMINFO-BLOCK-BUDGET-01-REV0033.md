# FLAC-STREAMINFO-BLOCK-BUDGET-01 — rev0033

Canonical packet: **U-127**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ share scanning asks TinyTag to load duration metadata for supported audio files larger than 128 bytes. In all archived source lanes, `.flac` files route into the vendored TinyTag FLAC parser.

The FLAC duration parser reads the metadata block header after the `fLaC` marker. That header contains a 24-bit payload length. Current TinyTag behavior uses the advertised length directly for the STREAMINFO duration block:

```text
head = fh.read(size)
if len(head) < 34:
    ... invalid streaminfo ...
```

Older 3.3.x-era lanes use the same shape with `stream_info_header = fh.read(size)` followed by a `< 34` check and then an exact-34-byte `struct.unpack(...)`. Master changed the parser internals, but still reads `size` bytes before parsing fixed offsets out of the STREAMINFO prefix.

STREAMINFO is the fixed 34-byte FLAC record used for duration fields. The maintainer witness shows that a valid 34-byte prefix plus padding is materialized as one `bytes` object proportional to the advertised block length before the parser enforces or relies on the fixed-record shape.

This is local/share-scanner parser hardening. It is not an inbound peer protocol parser issue, not code execution, and not a claim that all large FLAC metadata blocks are invalid. The security boundary is a Nicotine+/TinyTag metadata-scanner budget for local indexing work and fixed-record validation of STREAMINFO specifically.

## Source status

The source trace covers all archived lanes from the rev0003 upstream source bundle:

```text
github-tag-3.3.10:
  commit caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
  shares.py routes supported audio files larger than 128 bytes through TinyTag.
  tinytag.py maps .flac to Flac.
  Flac._determine_duration() derives size from the metadata block header.
  For STREAMINFO, it calls fh.read(size) before checking len(...) < 34 and
  before exact-34-byte unpacking.

github-branch-3.3.x:
  commit 98089ac233aa57786e8dbdc48123f6ac1c4767d8
  same vendored tinytag.py hash and same FLAC STREAMINFO read behavior as 3.3.10.

github-branch-master:
  commit f4e17d59783dbc48ea31d2e899a681e2dd1ed500
  shares.py routes .flac files through TinyTag._get_parser_for_filename(...)
  and tag._load(...).
  _Flac._parse_tag() derives size from the metadata block header.
  For STREAMINFO, it calls fh.read(size) before the <34 check and before
  fixed-offset duration parsing.
```

The master lane modernizes TinyTag internals and no longer needs the legacy exact-buffer `struct.unpack()` for STREAMINFO, but the memory-budget invariant remains unchanged: the advertised block length is materialized before fixed-prefix parsing.

## Maintainer-style witness

Current-behavior test:

```text
maintainer_artifacts/flac-streaminfo-block-budget-01/test_flac_streaminfo_block_budget_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The witness constructs compact FLAC-like streams:

```text
fLaC
STREAMINFO metadata block header, type 0, advertised payload length N
  34-byte valid STREAMINFO duration record + controllable padding
```

Observed current behavior:

```text
Valid 34-byte STREAMINFO block:
  parses a five-second duration and reads exactly 34 bytes at offset 8.

1,048,677-byte STREAMINFO payload:
  read once as one bytes object at offset 8 before fixed-length validation or
  fixed-prefix parsing.

2,097,409-byte STREAMINFO payload:
  read once as one bytes object at the same boundary.

34-byte STREAMINFO prefix + 4,096 bytes padding:
  read as 4,130 bytes, even though the duration calculation needs the fixed
  34-byte record.
```

The tests intentionally pass on current behavior. A fixed-behavior test should expect an overlong STREAMINFO payload to raise, skip, or stop before materializing the full advertised block, while preserving normal FLAC duration extraction for the exact 34-byte record.

## Impact framing

Conservative impact:

```text
A local or downloaded FLAC-like file in a scanned/shared path can make the share
metadata parser allocate a bytes object matching an advertised STREAMINFO block
payload before the duration parser consumes the fixed 34-byte record it needs.
```

Why this remains lower severity:

```text
- It is local/share-scanner media metadata parsing, not inbound peer-message
  parsing.
- The FLAC metadata block length field is 24-bit, so the bounded worst case for
  one STREAMINFO payload is file-size/format bounded rather than unbounded
  process growth.
- The witness does not prove memory corruption or code execution.
- Other FLAC metadata blocks such as Vorbis comments and pictures are
  variable-length by design; the fix should target STREAMINFO fixed-record
  validation and local metadata-scanner budgets, not blanket rejection of every
  large FLAC metadata block.
- Public adjacency exists in FLAC format docs, TinyTag/Nicotine+ source context,
  and broad parser-hardening history, but the captured searches did not find a
  direct Nicotine+ U-127-style public issue.
- It does not outrank U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.
```

## Fix-shape notes

A coherent fix should be small and testable:

```text
- Validate STREAMINFO block length before reading payload bytes; for native FLAC,
  require the STREAMINFO block's advertised length to be exactly 34 bytes, or
  reject/stop duration parsing before allocation.
- Alternatively, read exactly 34 bytes for STREAMINFO, parse duration fields from
  that record, then reject or seek over any extra bytes only if the project wants
  to tolerate malformed files. Exact-34 rejection is simpler and aligns with the
  fixed-record invariant.
- Keep variable-length FLAC blocks separate: Vorbis comments, pictures, cuesheets,
  seektables, and padding need their own budgets/streaming rules.
- Preserve ordinary FLAC duration extraction for exact-34 STREAMINFO blocks.
- Add fixed-behavior tests for:
    * exact 34-byte STREAMINFO duration parsing;
    * advertised STREAMINFO length 33;
    * advertised STREAMINFO length 35;
    * large advertised STREAMINFO length;
    * truncated payload;
    * non-STREAMINFO variable-length metadata blocks that should remain seekable
      or separately budgeted.
- Keep this fix in the FLAC metadata parser/share-scanner path; do not merge it
  with MP4 atom-leaf materialization, Ogg continuation accumulation, WMA/ASF
  object-size progress, ID3v2 frame-size rows, share-cache provenance, or
  network-message caps.
```

## Evidence files

```text
evidence/rev0033-flac-streaminfo-block-budget-pytest-run.txt
evidence/rev0033-flac-streaminfo-block-budget-helper-rerun.txt
evidence/rev0033-flac-streaminfo-block-budget-source-trace.md
evidence/rev0033-flac-streaminfo-block-budget-source-trace.json
evidence/rev0033-flac-streaminfo-block-budget-behavior.json
evidence/rev0033-web-public-overlap-flac-streaminfo-block-budget.md
data/rev0033_flac_streaminfo_block_budget_source_trace.csv/json
```
