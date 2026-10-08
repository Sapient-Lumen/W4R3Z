# WMA-ASF-TINYSTEP-01 — rev0030

Canonical packet: **U-273**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ share scanning asks TinyTag to load metadata for audio files. In the archived lanes, `.wma` files route into the vendored TinyTag WMA/ASF parser when the scanned file is larger than 128 bytes.

The WMA/ASF object loop has this relevant shape:

```text
read ASF object id/header
read object_size
if object_size == 0 or object_size > filesize:
    break
...
for an unknown object id:
    seek(object_size - header_len, SEEK_CUR)
```

The ASF object header length is 24 bytes. The current parser rejects exactly zero and larger-than-file object sizes, but it does not reject nonzero object sizes below the 24-byte header length before the relative seek. For unknown object ids, `object_size=8` means the parser consumes a 24-byte header and then seeks back 16 bytes. The next object-header read starts only eight bytes after the previous one.

This is a parser progress/budget hardening item in local/share-scanner media metadata parsing. It is not a peer-message parser packet, not code execution, and not a standalone remote compromise claim.

## Source status

The source trace covers all archived lanes from the rev0003 upstream source bundle:

```text
github-tag-3.3.10:
  commit caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
  pynicotine/external/tinytag.py rejects object_size == 0 or > filesize;
  unknown object path seeks object_size - 24.

github-branch-3.3.x:
  commit 98089ac233aa57786e8dbdc48123f6ac1c4767d8
  same vendored tinytag.py hash and same WMA/ASF object-size behavior.

github-branch-master:
  commit f4e17d59783dbc48ea31d2e899a681e2dd1ed500
  tinytag.py sets header_len = 24, rejects object_size == 0 or > filesize,
  then unknown object path seeks object_size - header_len.
```

The share scanner source trace also records the `.wma` metadata path through `TinyTag._get_parser_for_filename(...)` and `tag.load(...)` / `tag._load(...)` when file size is greater than 128 bytes.

## Maintainer-style witness

Current-behavior test:

```text
maintainer_artifacts/wma-asf-tinystep-01/test_wma_asf_tinystep_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness constructs a compact ASF/WMA-like byte stream with repeated unknown ASF object headers. The malformed case uses `object_size=8`; the baseline uses the valid minimum unknown-object size, `object_size=24`.

Observed current behavior:

```text
object_size=8:
  object-header starts: 30, 38, 46, 54, 62, 70, ...
  object-loop reads over 1024-byte payload: 127
  backwards relative seeks: yes, 8 - 24 = -16

object_size=24:
  object-header starts: 30, 54, 78, 102, 126, 150, ...
  object-loop reads over 1024-byte payload: 43
  backwards relative seeks: no
```

The tests intentionally pass on current behavior. A hardened parser should make the under-header nonzero case fail, either by rejecting the malformed object or stopping before any backwards/overlapping seek.

## Impact framing

The conservative impact is:

```text
A local or downloaded WMA/ASF-like file in a scanned/share-indexed path can make
Nicotine+'s metadata parser spend extra parser iterations by advertising nonzero
ASF object sizes smaller than the object header. The parser progresses by the
attacker-chosen under-header size instead of the 24-byte object-header minimum.
```

Why this remains lower severity:

```text
- It is local/share-scanner media metadata parsing, not inbound peer protocol
  message handling.
- The witness demonstrates parser-step amplification, not memory corruption.
- Work remains proportional to file size and the parser eventually reaches EOF.
- The issue is class-adjacent to public ASF parser loop hardening in another
  package, so novelty language should stay conservative.
- It does not outrank U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.
```

## Fix-shape notes

A coherent fix should be small and testable:

```text
- Define the ASF object header length as a parser invariant.
- Reject, stop, or raise a parse error on 0 < object_size < header_len before
  object-specific reads or any relative seek.
- Preserve the existing guard for object_size == 0 and object_size > filesize.
- Add fixed-behavior tests for exactly zero, nonzero under-header values,
  exact-minimum size 24, oversized values, truncated object headers, and unknown
  object ids.
- Keep this fix in the WMA/ASF parser; do not merge it with Ogg, MP4, FLAC,
  ID3v2, share-cache, or network-message-budget packets.
```

## Evidence files

```text
evidence/rev0030-wma-asf-tinystep-pytest-run.txt
evidence/rev0030-wma-asf-tinystep-source-trace.md
evidence/rev0030-wma-asf-tinystep-source-trace.json
evidence/rev0030-web-public-overlap-wma-asf-tinystep.md
```
