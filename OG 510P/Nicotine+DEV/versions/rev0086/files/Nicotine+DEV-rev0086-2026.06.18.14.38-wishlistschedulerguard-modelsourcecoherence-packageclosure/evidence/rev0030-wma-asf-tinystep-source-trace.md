# WMA-ASF-TINYSTEP-01 source trace — rev0030

Packet: **U-273**.

Source bundle: `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z`.

## Source invariant

All three archived lanes route share-scanner audio metadata through the vendored TinyTag WMA parser. The WMA/ASF object loop rejects `object_size == 0` and `object_size > filesize`, but does not reject `0 < object_size < 24` before seeking by `object_size - header_len`.

For unknown ASF object ids, that permits a backwards relative seek after a 24-byte object header has already been consumed. A compact witness using `object_size = 8` therefore advances object parsing by eight bytes per loop instead of the 24-byte object-header minimum.

## github-tag-3.3.10

Commit: `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026`

### `pynicotine/external/tinytag.py`

sha256: `f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1`

```text
L1301:             object_size = _bytes_to_int_le(fh.read(8))
L1302:             if object_size == 0 or object_size > self.filesize:
L1390:                 fh.seek(object_size - 24, os.SEEK_CUR)  # read over onknown object ids
```

### `pynicotine/shares.py`

sha256: `62aff8095c6e28abefd41e25c566c1499b8a8f6cdd487ab44ef0641f04405f0e`

```text
L597:     def get_audio_tag(self, encoded_file_path, size):
L599:         parser_class = TinyTag._get_parser_for_filename(encoded_file_path)  # pylint: disable=protected-access
L606:             tag.load(tags=False, duration=True, image=False)
L620:         if size > 128:
```

## github-branch-3.3.x

Commit: `98089ac233aa57786e8dbdc48123f6ac1c4767d8`

### `pynicotine/external/tinytag.py`

sha256: `f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1`

```text
L1301:             object_size = _bytes_to_int_le(fh.read(8))
L1302:             if object_size == 0 or object_size > self.filesize:
L1390:                 fh.seek(object_size - 24, os.SEEK_CUR)  # read over onknown object ids
```

### `pynicotine/shares.py`

sha256: `800fb26aaeab87d1aa6d20aba2a3ac185cd18a902d7bffadf87be0e8b4fd1bc9`

```text
L604:     def get_audio_tag(self, encoded_file_path, size):
L606:         parser_class = TinyTag._get_parser_for_filename(encoded_file_path)  # pylint: disable=protected-access
L613:             tag.load(tags=False, duration=True, image=False)
L627:         if size > 128:
```

## github-branch-master

Commit: `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`

### `pynicotine/external/tinytag.py`

sha256: `aba37daaa69165ffa43298ddca6d6ba7515b76d0358286ad946fb37c102c393f`

```text
L1777:         header_len = 24
L1780:             object_size = unpack('<Q', object_header[16:])[0]
L1781:             if object_size == 0 or object_size > self.filesize:
L1851:                 fh.seek(object_size - header_len, SEEK_CUR)
```

### `pynicotine/shares.py`

sha256: `e6580c5b8b240b9c0fadf2c15be6171b55c0e8ad903cae09cdfb5d1a3b2fd419`

```text
L660:     def get_audio_tag(self, file_path, size):
L662:         parser_class = TinyTag._get_parser_for_filename(file_path)  # pylint: disable=protected-access
L671:             tag._load(tags=False, duration=True, image=False)       # pylint: disable=protected-access
L684:         if size > 128:
```

## Dynamic witness summary

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness records object-header read starts. With `object_size = 8`, starts begin at `30, 38, 46, 54, 62, 70`, and the loop performs 127 object-header reads over the compact 1024-byte payload. With a valid minimum unknown-object size of 24, starts begin at `30, 54, 78, 102, 126, 150`, and the loop performs 43 object-header reads over the same payload length.
