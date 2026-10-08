# OGG-CONTINUATION-ACCUM-01 — rev0031

Canonical packet: **U-124**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ share scanning asks TinyTag to load duration metadata for supported audio files larger than 128 bytes. In all archived source lanes, `.ogg` and related Ogg-family extensions route into the vendored TinyTag Ogg parser.

The parser assembles Ogg packets from page lacing values. The important current behavior is:

```text
A lacing value of 255 means the packet continues.
A lacing value below 255 terminates the packet.
The parser appends every continued page body into one packet buffer until a
terminator appears.
No local byte/page/metadata-packet budget is enforced before that materialization.
```

In the 3.3.10 and 3.3.x lanes, the accumulator is `previous_page`. In master, the accumulator is `packet_data = bytearray()`. Both forms assemble a potentially very large first metadata/header packet before the caller can classify or reject it.

This is local/share-scanner parser hardening. It is not a peer protocol parser packet, not code execution, and not a claim that Ogg continuation packets are invalid. Ogg allows packets to span pages; the proposed security boundary is a Nicotine+/TinyTag metadata-scanner budget for local indexing work.

## Source status

The source trace covers all archived lanes from the rev0003 upstream source bundle:

```text
github-tag-3.3.10:
  commit caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
  shares.py routes .ogg metadata through TinyTag when file size > 128 bytes.
  tinytag.py maps .oga/.ogg/.opus/.spx to Ogg.
  Ogg._parse_pages() appends continuation data to previous_page until a packet
  terminator appears.

github-branch-3.3.x:
  commit 98089ac233aa57786e8dbdc48123f6ac1c4767d8
  same vendored tinytag.py hash and same Ogg continuation accumulation behavior.

github-branch-master:
  commit f4e17d59783dbc48ea31d2e899a681e2dd1ed500
  shares.py routes .ogg metadata through TinyTag._get_parser_for_filename(...)
  and tag._load(...).
  _Ogg._parse_pages() appends continued packet data to a bytearray until a
  seg_size < 255 terminates the packet.
```

The newer master parser includes useful duration-path improvements after tags are parsed, but the initial metadata/header packet is still assembled before a local packet budget is applied.

## Maintainer-style witness

Current-behavior test:

```text
maintainer_artifacts/ogg-continuation-accum-01/test_ogg_continuation_accumulation_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness constructs compact Ogg streams where one packet spans multiple pages. Each continuation page uses the maximum lacing table shape:

```text
255 lacing entries * 255 bytes each = 65,025 packet-body bytes per page
```

Observed current behavior:

```text
4 full-lacing continuation pages + 1-byte terminator:
  first yielded packet length: 260,101 bytes

1 full-lacing continuation page + 1-byte terminator:
  first yielded packet length: 65,026 bytes

Scaling delta:
  each additional unterminated full-lacing page adds 65,025 bytes to the single
  accumulated packet before the first yield.
```

The third test exercises the public TinyTag/Nicotine+ metadata-scanner entry shape with `TinyTag.get(filename="witness.ogg", file_obj=..., tags=False, duration=True)`. It records four 65,025-byte continuation page-body reads before returning.

The tests intentionally pass on current behavior. A fixed-behavior test should expect the over-budget chain to raise, stop, or skip before assembling a packet beyond a maintainers-chosen metadata budget.

## Impact framing

Conservative impact:

```text
A local or downloaded Ogg-like file in a scanned/shared path can make the share
metadata parser allocate and copy a continued Ogg packet whose size grows with
each unterminated full-lacing page before the first packet boundary.
```

Why this remains lower severity:

```text
- It is local/share-scanner media metadata parsing, not inbound peer-message
  parsing.
- Work is proportional to file size; the witness does not prove an infinite loop.
- Ogg's format intentionally allows packets to span pages, so the fix should be
  a local metadata-scanner budget rather than a global Ogg validity claim.
- Public adjacency exists in TinyTag source, TinyTag parser-DoS advisories, Ogg
  format documentation, and broad Nicotine+ rescan performance reports.
- It does not outrank U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.
```

## Fix-shape notes

A coherent fix should be small and testable:

```text
- Define a local maximum Ogg metadata packet byte budget for TinyTag/Nicotine+
  share scanning.
- Count accumulated continuation bytes before appending to previous_page or
  packet_data.
- Stop, skip, or raise a parse error once the local metadata packet budget is
  exceeded.
- Preserve normal Ogg files with ordinary Vorbis/Opus/Speex/FLAC headers and
  comments.
- Add fixed-behavior tests for:
    * a normal small Vorbis identification packet;
    * a normal comment packet;
    * a packet ending exactly at the budget;
    * a packet exceeding the budget by one lacing segment;
    * multi-page continuation chains;
    * unrelated serials and post-tags duration skipping.
- Keep this fix in the Ogg metadata parser/share-scanner path; do not merge it
  with WMA/ASF object-size progress, MP4 atom memory, FLAC block validation,
  ID3v2 frames, share-cache provenance, or network-message budgets.
```

## Evidence files

```text
evidence/rev0031-ogg-continuation-accum-pytest-run.txt
evidence/rev0031-ogg-continuation-accum-helper-rerun.txt
evidence/rev0031-ogg-continuation-accum-source-trace.md
evidence/rev0031-ogg-continuation-accum-source-trace.json
evidence/rev0031-web-public-overlap-ogg-continuation-accum.md
```
