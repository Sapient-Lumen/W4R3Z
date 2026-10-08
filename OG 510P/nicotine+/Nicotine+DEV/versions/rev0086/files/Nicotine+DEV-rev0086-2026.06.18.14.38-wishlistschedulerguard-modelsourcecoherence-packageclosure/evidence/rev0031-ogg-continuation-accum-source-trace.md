# rev0031 source trace — OGG-CONTINUATION-ACCUM-01 / U-124

Source bundle: `Nicotine-source.zip` / `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z`.

## Summary

The archived source lanes all route shared `.ogg`/`.oga`/`.opus`/`.spx` files through the vendored TinyTag Ogg parser during share metadata scanning when the file is larger than 128 bytes.

The relevant parser invariant is Ogg packet continuation assembly. Ogg pages can contain 255 lacing entries. A lacing value of `255` means the packet continues, and a value below `255` terminates the packet. The current TinyTag parser accumulates continued packet bytes into one in-memory packet object until a terminating lacing value appears. No local byte, page, or metadata-packet budget is enforced before concatenation/materialization.

## github-tag-3.3.10

```text
commit: caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
tinytag.py sha256: f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1
shares.py sha256:   62aff8095c6e28abefd41e25c566c1499b8a8f6cdd487ab44ef0641f04405f0e
```

Share-scanner route:

```text
pynicotine/shares.py:597-607
  get_audio_tag(encoded_file_path, size)
  parser_class = TinyTag._get_parser_for_filename(encoded_file_path)
  tag = parser_class(file_handle, size)
  tag.load(tags=False, duration=True, image=False)

pynicotine/shares.py:619-623
  if size > 128:
      tag = self.get_audio_tag(encoded_file_path, size)
```

Ogg parser route:

```text
pynicotine/external/tinytag.py:136-145
  extension mapping maps .oga/.ogg/.opus/.spx to Ogg

pynicotine/external/tinytag.py:1037-1062
  previous_page = b''
  for segsize in segsizes:
      total += segsize
      if total < 255:
          yield previous_page + fh.read(total)
          previous_page = b''
          total = 0
  if total != 0:
      if total % 255 == 0:
          previous_page += fh.read(total)
      else:
          yield previous_page + fh.read(total)
```

Current behavior: every full-lacing page (`255 * 255 == 65025` bytes of packet body) is appended to `previous_page` until a later segment below 255 terminates the packet.

## github-branch-3.3.x

```text
commit: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
tinytag.py sha256: f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1
shares.py sha256:   800fb26aaeab87d1aa6d20aba2a3ac185cd18a902d7bffadf87be0e8b4fd1bc9
```

Share-scanner route:

```text
pynicotine/shares.py:604-613
  get_audio_tag(encoded_file_path, size)
  parser_class = TinyTag._get_parser_for_filename(encoded_file_path)
  tag = parser_class(file_handle, size)
  tag.load(tags=False, duration=True, image=False)

pynicotine/shares.py:626-629
  if size > 128:
      tag = self.get_audio_tag(encoded_file_path, size)
```

Ogg parser route is the same as tag 3.3.10:

```text
pynicotine/external/tinytag.py:1037-1062
  previous_page = b''
  ...
  if total % 255 == 0:
      previous_page += fh.read(total)
```

Current behavior: same continuation accumulation as the stable tag.

## github-branch-master

```text
commit: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
tinytag.py sha256: aba37daaa69165ffa43298ddca6d6ba7515b76d0358286ad946fb37c102c393f
shares.py sha256:   e6580c5b8b240b9c0fadf2c15be6171b55c0e8ad903cae09cdfb5d1a3b2fd419
```

Share-scanner route:

```text
pynicotine/shares.py:660-671
  get_audio_tag(file_path, size)
  parser_class = TinyTag._get_parser_for_filename(file_path)
  tag = parser_class()
  tag._filehandler = file_handle
  tag.filesize = size
  tag._load(tags=False, duration=True, image=False)

pynicotine/shares.py:683-686
  if size > 128:
      tag = self.get_audio_tag(file_path, size)
```

Ogg parser route:

```text
pynicotine/external/tinytag.py:1469-1519
  packet_data = bytearray()
  ...
  for seg_size in seg_sizes:
      read_size += seg_size
      if seg_size < 255 and serial_match and not self._tags_parsed:
          packet_data += fh.read(read_size)
          yield packet_data
          packet_data.clear()
          read_size = 0
  if read_size:
      if not serial_match or self._tags_parsed:
          fh.seek(read_size, SEEK_CUR)
      else:
          packet_data += fh.read(read_size)
```

Current behavior: full-lacing pages for the active serial are appended to a `bytearray` until a terminating lacing value appears. The newer parser can skip packet bodies after tags are parsed, but the initial metadata/header packet is still assembled without a local packet-size/page-count cap.

## Maintainer witness result

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The compact witness uses four full-lacing continuation pages plus a one-byte terminator, causing the parser to assemble a single `260101` byte packet before the first yield. The scaling test verifies the accumulated packet grows by `65025` bytes for each additional unterminated full-lacing page.
