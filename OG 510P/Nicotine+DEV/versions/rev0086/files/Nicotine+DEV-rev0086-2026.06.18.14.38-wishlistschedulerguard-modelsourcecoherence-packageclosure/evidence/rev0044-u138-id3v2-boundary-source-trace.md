# rev0044 U-138 source trace — ID3v2 frame materialization boundary

Revision: `Nicotine+DEV-rev0044-2026.06.15.13.05-u138id3boundary-tagparse-refactoraudit`

## Decision

The broad deferred row **U-138 / general ID3v2 advertised-frame materialization** is **not promoted** as a share-scanner strict/front packet.

The source trace and probe split the row into two paths:

1. **Nicotine+ MP3 share-scanner duration-only path**: calls TinyTag with `tags=False, duration=True`; it skips/probes the leading ID3v2 tag and seeks to audio without reading a mapped ID3v2 text frame body as one advertised allocation.
2. **Generic TinyTag tag-enabled ID3v2 path**: when `tags=True`, mapped text frames such as `TIT2` are read as `fh.read(frame_size)` and decoded. This is real parser materialization, but it is no longer the previously asserted Nicotine+ share-scanner duration-only packet.

## Source lanes traced

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

## Nicotine+ share-scanner call shape

### github-tag-3.3.10

`pynicotine/shares.py` lines 597-608:

```text
get_audio_tag(encoded_file_path, size)
  parser_class = TinyTag._get_parser_for_filename(encoded_file_path)
  with open(encoded_file_path, "rb") as file_handle:
      tag = parser_class(file_handle, size)
      tag.load(tags=False, duration=True, image=False)
```

### github-branch-3.3.x

Same call shape at `pynicotine/shares.py` lines 604-615:

```text
get_audio_tag(encoded_file_path, size)
  parser_class = TinyTag._get_parser_for_filename(encoded_file_path)
  tag.load(tags=False, duration=True, image=False)
```

### github-branch-master

`pynicotine/shares.py` lines 660-672:

```text
get_audio_tag(file_path, size)
  parser_class = TinyTag._get_parser_for_filename(file_path)
  tag = parser_class()
  tag._filehandler = file_handle
  tag.filesize = size
  tag._load(tags=False, duration=True, image=False)
```

## TinyTag load gate

### 3.3.10 / 3.3.x

`pynicotine/external/tinytag.py` lines 229-238:

```text
load(tags, duration, image=False)
  self._parse_tags = tags
  if tags:
      self._parse_tag(self._filehandler)
  if duration:
      if tags:
          self._filehandler.seek(0)
      self._determine_duration(self._filehandler)
```

With the share scanner's `tags=False`, `_parse_tag()` is not called before MP3 duration detection.

### master

`pynicotine/external/tinytag.py` lines 258-269 keeps the same gate as `_load()`:

```text
_load(tags, duration, image=False)
  self._parse_tags = tags
  if tags:
      self._parse_tag(self._filehandler)
  if duration:
      if tags:
          self._filehandler.seek(0)
      self._determine_duration(self._filehandler)
```

## ID3v2 header and duration skip/probe path

### 3.3.10 / 3.3.x

`ID3._determine_duration()` calls `_parse_id3v2_header()` only to discover the leading ID3v2 tag size when tag parsing was disabled, then seeks to `self._bytepos_after_id3v2` before scanning MPEG frames.

Relevant lines: `tinytag.py` 648-660.

```text
if self._bytepos_after_id3v2 is None:
    self._parse_id3v2_header(fh)
...
fh.seek(self._bytepos_after_id3v2)
```

`_parse_id3v2_header()` reads the 10-byte tag header and computes the tag payload size at lines 744-760. It does not parse individual frames.

### master

`ID3._determine_duration()` follows the same structure with `self._bytepos_after_id3v2 == -1`, reads the ID3v2 header, then seeks to the first audio position before MPEG frame scanning.

Relevant lines: `tinytag.py` 923-940.

## Tag-enabled materialization path

### 3.3.10 / 3.3.x

`ID3._parse_id3v2()` loops over frames and calls `_parse_frame()`; `_parse_frame()` reads parsable frame bodies in one call.

Relevant lines: `tinytag.py` 762-776 and 803-840.

```text
if frame_id not in ID3.PARSABLE_FRAME_IDS:
    fh.seek(frame_size, os.SEEK_CUR)
    return frame_size
content = fh.read(frame_size)
fieldname = ID3.FRAME_ID_TO_FIELD.get(frame_id)
if fieldname:
    self._set_field(fieldname, self._decode_string(content, language))
```

### master

`ID3._parse_frame()` returns early for mapped ID3 fields when `self._parse_tags` is false, but when `tags=True` it reads and decodes the mapped frame body.

Relevant lines: `tinytag.py` 1127-1159.

```text
if frame_id in self._ID3_MAPPING:
    if not self._parse_tags:
        return frame_size
    fieldname = self._ID3_MAPPING[frame_id]
    value = self._decode_string(fh.read(frame_size), language)
```

## Probe evidence summary

`maintainer_artifacts/u138-id3v2-frame-materialization-01/test_id3v2_frame_materialization_boundary_reproducer.py` contains five current-behavior assertions:

1. Share-scanner-style MP3 duration-only parse does **not** materialize a mapped `TIT2` body.
2. Generic tag-enabled ID3v2 parse does materialize the mapped text body.
3. The mapped text read scales with advertised frame size.
4. Unmapped/private frames are skipped rather than materialized.
5. Small `tags=True, duration=True` MP3 parsing still returns both title and duration.

Rerun matrix recorded in `evidence/rev0044-u138-id3v2-boundary-rerun-matrix.txt`:

```text
github-tag-3.3.10:    5 passed
github-branch-3.3.x:  5 passed
github-branch-master: 5 passed
```

## Final rev0044 classification

```text
old row: U-138 / general ID3v2 advertised-frame materialization
rev0044 action: demote/archive broad share-scanner form
remaining note: generic TinyTag tags=True mapped-frame materialization exists but is not a strict/front share-scanner packet without a Nicotine+ caller that enables tags on peer-controlled/adversarial inputs.
next queue: prefer external review/filing of the seven production-gated strict packets, or refresh source and discover a new row.
```
