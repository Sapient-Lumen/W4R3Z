# rev0032 source trace — MP4-M4A-ATOM-BUDGET-01 / U-125

Source bundle: `Nicotine-source.zip` / `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z`.

## Summary

The archived source lanes all route shared MP4/M4A-family files through the vendored TinyTag MP4 parser during share metadata scanning when the file is larger than 128 bytes.

The relevant parser invariant is MP4 atom-leaf materialization. The duration parser traverses an atom tree; when an atom type maps to a callable, `_traverse_atoms()` invokes that callable on `fh.read(atom_size)`. For the `mvhd` leaf, the duration parser reads fixed header fields from the start of the atom payload, yet the traversal layer has already materialized the full advertised payload into memory.

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

MP4 parser route:

```text
pynicotine/external/tinytag.py:136-145
  extension mapping maps .m4a/.mp4-family extensions to MP4

pynicotine/external/tinytag.py:410-425
  Parser.parse_mvhd(data) reads version/timescale/duration from a BytesIO over data

pynicotine/external/tinytag.py:459-465
  AUDIO_DATA_TREE maps b'mvhd' to Parser.parse_mvhd

pynicotine/external/tinytag.py:485-523
  _traverse_atoms() calls leaf parsers as sub_path(fh.read(atom_size))
```

Current behavior: a matching `mvhd` atom payload is read in full before the parser consumes the fixed duration fields.

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

MP4 parser route is the same as tag 3.3.10:

```text
pynicotine/external/tinytag.py:410-425
pynicotine/external/tinytag.py:459-465
pynicotine/external/tinytag.py:485-523
```

Current behavior: same `fh.read(atom_size)` leaf materialization as the stable tag.

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

MP4 parser route:

```text
pynicotine/external/tinytag.py:191-200
  extension mapping maps .m4a/.mp4-family extensions to _MP4

pynicotine/external/tinytag.py:494-506
  _audio_data_tree maps b'mvhd' to _MP4._parse_mvhd

pynicotine/external/tinytag.py:544-603
  _traverse_atoms() calls leaf parsers as sub_path(fh.read(atom_size))

pynicotine/external/tinytag.py:724-732
  _parse_mvhd(data) reads version/timescale/duration from the start of data
```

Current behavior: a matching `mvhd` atom payload is read in full before the parser consumes the fixed duration fields.

## Maintainer witness result

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The compact witness uses a valid `mvhd` duration prefix and padding inside the same atom. A 1,048,699-byte `mvhd` payload and a 2,097,169-byte `mvhd` payload are each read as one `bytes` object at the leaf boundary. A 20-byte minimal duration prefix reads as 20 bytes, while the same prefix plus 4,096 padding bytes reads as 4,116 bytes, confirming that current reads scale with the advertised atom payload rather than the fixed fields needed for duration extraction.
