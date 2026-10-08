# FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 — rev0034

Canonical packet: **U-139**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ share scanning asks TinyTag for duration metadata only:

```text
tag.load(tags=False, duration=True, image=False)
```

For `.flac` files, the parser enters the FLAC path. FLAC files can appear with a leading ID3v2 envelope before the native `fLaC` marker. Rev0034 verifies that this leading prelude is handled differently across the archived source lanes.

In the 3.3.10 and 3.3.x lanes, `Flac.load()` checks for a leading `ID3` header and constructs a fresh `ID3` parser. That parser's `_parse_tags` flag defaults to `True`, so mapped text frames such as `TIT2` are read, decoded, and applied to the resulting FLAC tag even though the share-scanner caller requested `tags=False` and only needs duration fields.

In the master lane, `_Flac._parse_tag()` propagates `tags=False` into the leading `_ID3` parser. The master witness therefore leaves `tag.title` unset and avoids reading the large mapped text-frame body as one field. Master still traverses the leading ID3v2 envelope before reaching `fLaC` and the native STREAMINFO duration record.

This is local/share-scanner metadata-parser hardening. It is not an inbound peer-message parser issue, not code execution, and not an all-lane full-frame materialization claim.

## Source status

The source trace covers all archived lanes from the rev0003 upstream source bundle:

```text
github-tag-3.3.10:
  shares.py selects TinyTag by extension and calls tag.load(tags=False,
  duration=True, image=False). Flac.load() checks header[:3] == b'ID3', creates
  ID3(self._filehandler, 0), calls id3._parse_id3v2(), then self.update(id3).
  The ID3 parser reads mapped frame content with fh.read(frame_size) and sets
  fields; no tags=False guard is propagated into that helper.

github-branch-3.3.x:
  Same vendored tinytag.py hash and same leading-ID3 behavior as 3.3.10.

github-branch-master:
  shares.py calls tag._load(tags=False, duration=True, image=False). _Flac reads
  a leading ID3 header, seeks back, constructs _ID3(), propagates _parse_tags and
  _load_image, and calls id3._parse_id3v2(). For mapped ID3 fields, _ID3 returns
  early when _parse_tags is false, so the mapped text frame is not applied. The
  ID3 envelope is still traversed/probed before native FLAC duration parsing.
```

## Maintainer-style witness

Current-behavior test:

```text
maintainer_artifacts/flac-leading-id3v2-duration-prelude-01/test_flac_leading_id3v2_duration_prelude_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The witness constructs compact FLAC-like streams:

```text
ID3v2.3 header
  TIT2 text frame with controllable advertised frame content length
fLaC
  exact 34-byte STREAMINFO block with a seven-second duration
```

Observed current behavior:

```text
3.3.10 / 3.3.x:
  - duration still parses as seven seconds;
  - the 64-byte TIT2 body is read and applied to tag.title despite tags=False;
  - a 1,048,649-byte TIT2 body is read as one frame body and decoded/applied;
  - the legacy ID3v2 loop also probes the native fLaC boundary as if another
    ID3 frame header remained, then seeks back to the declared ID3 end.

master:
  - duration still parses as seven seconds;
  - tag.title remains None;
  - the large mapped TIT2 body is not read as one text frame when tags=False;
  - the parser still reads/probes inside the leading ID3v2 envelope and then
    seeks to the native fLaC marker before STREAMINFO parsing.
```

## Impact framing

Conservative impact:

```text
A local or downloaded FLAC-like file in a scanned/shared path can make stable
and 3.3.x share scanning parse and materialize leading ID3v2 mapped text frames
before FLAC duration extraction even though the caller requested duration-only
metadata.
```

Why this remains lower severity:

```text
- It is local/share-scanner media metadata parsing, not inbound peer-message
  parsing.
- Master already carries a partial fix for the mapped-frame/application shape.
- Public TinyTag history and general audio-tooling history make this parser class
  known/upstream-adjacent.
- The witness does not prove memory corruption, code execution, or remote
  unauthenticated triggering by itself.
- It does not outrank U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.
```

## Fix-shape notes

A coherent stable/3.3.x hardening shape should be small:

```text
- When Flac.load(tags=False, duration=True, image=False) sees a leading ID3v2
  envelope, skip/seek over that envelope or create the ID3 helper with
  _parse_tags=False before parsing the prelude.
- Preserve duration extraction for FLAC files that genuinely carry a leading
  ID3v2 envelope followed by a native fLaC marker.
- Do not apply mapped ID3 fields to the FLAC tag when the caller disabled tag
  parsing.
- Avoid decoding large mapped text frames in duration-only share scans.
- Add tests for:
    * leading ID3v2 + exact STREAMINFO duration parses;
    * tags=False does not set title/artist/album from leading ID3v2;
    * large mapped text frame is skipped rather than materialized;
    * tags=True still preserves intended FLAC/ID3 metadata behavior;
    * malformed ID3v2 envelope before fLaC fails closed without wild seeks.
```

## Evidence files

```text
evidence/rev0034-flac-leading-id3v2-duration-prelude-pytest-run.txt
evidence/rev0034-flac-leading-id3v2-duration-prelude-helper-rerun.txt
evidence/rev0034-flac-leading-id3v2-duration-prelude-source-trace.md
evidence/rev0034-flac-leading-id3v2-duration-prelude-source-trace.json
evidence/rev0034-flac-leading-id3v2-duration-prelude-behavior.json
evidence/rev0034-web-public-overlap-flac-leading-id3v2-prelude.md
data/rev0034_flac_leading_id3v2_prelude_source_trace.csv/json
```
