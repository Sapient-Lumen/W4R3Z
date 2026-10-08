# rev0033 source trace — FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127

Source bundle: `Nicotine-source.zip` / `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z`.

## Summary

All archived source lanes route shared `.flac` files through the vendored TinyTag FLAC parser during share metadata scanning when file size is greater than 128 bytes. The FLAC STREAMINFO metadata block is a fixed 34-byte duration record, but current parser lanes derive `size` from the 24-bit metadata block header and call `fh.read(size)` before rejecting short payloads or consuming fixed-offset duration fields. Oversized STREAMINFO payloads are therefore materialized first.

## github-tag-3.3.10

```text

commit: caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026

shares.py sha256:   62aff8095c6e28abefd41e25c566c1499b8a8f6cdd487ab44ef0641f04405f0e

tinytag.py sha256: f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1

```

### Share-scanner route

`pynicotine/shares.py:597-608`


```text
  597:     def get_audio_tag(self, encoded_file_path, size):
  598: 
  599:         parser_class = TinyTag._get_parser_for_filename(encoded_file_path)  # pylint: disable=protected-access
  600: 
  601:         if parser_class is None:
  602:             return None
  603: 
  604:         with open(encoded_file_path, "rb") as file_handle:
  605:             tag = parser_class(file_handle, size)
  606:             tag.load(tags=False, duration=True, image=False)
  607: 
  608:         return tag
```

`pynicotine/shares.py:619-623`


```text
  619:         # We skip metadata scanning of files without meaningful content
  620:         if size > 128:
  621:             try:
  622:                 tag = self.get_audio_tag(encoded_file_path, size)
  623: 
```

### TinyTag FLAC route

`pynicotine/external/tinytag.py:136-145`


```text
  136:     def _get_parser_for_filename(cls, filename):
  137:         if cls._file_extension_mapping is None:
  138:             cls._file_extension_mapping = {
  139:                 (b'.mp1', b'.mp2', b'.mp3'): ID3,
  140:                 (b'.oga', b'.ogg', b'.opus', b'.spx'): Ogg,
  141:                 (b'.wav',): Wave,
  142:                 (b'.flac',): Flac,
  143:                 (b'.wma',): Wma,
  144:                 (b'.m4b', b'.m4a', b'.m4r', b'.m4v', b'.mp4', b'.aax', b'.aaxc'): MP4,
  145:                 (b'.aiff', b'.aifc', b'.aif', b'.afc'): Aiff,
```

`pynicotine/external/tinytag.py:1152-1165`


```text
 1152:     def load(self, tags, duration, image=False):
 1153:         self._parse_tags = tags
 1154:         self._parse_duration = duration
 1155:         self._load_image = image
 1156:         header = self._filehandler.peek(4)
 1157:         if header[:3] == b'ID3':  # parse ID3 header if it exists
 1158:             id3 = ID3(self._filehandler, 0)
 1159:             id3._parse_id3v2(self._filehandler)
 1160:             self.update(id3)
 1161:             header = self._filehandler.peek(4)  # after ID3 should be fLaC
 1162:         if header[:4] != b'fLaC':
 1163:             raise TinyTagException('Invalid flac header')
 1164:         self._filehandler.seek(4, os.SEEK_CUR)
 1165:         self._determine_duration(self._filehandler)
```

`pynicotine/external/tinytag.py:1167-1180`


```text
 1167:     def _determine_duration(self, fh):
 1168:         # for spec, see https://xiph.org/flac/ogg_mapping.html
 1169:         header_data = fh.read(4)
 1170:         while len(header_data) == 4:
 1171:             meta_header = struct.unpack('B3B', header_data)
 1172:             block_type = meta_header[0] & 0x7f
 1173:             is_last_block = meta_header[0] & 0x80
 1174:             size = _bytes_to_int(meta_header[1:4])
 1175:             # http://xiph.org/flac/format.html#metadata_block_streaminfo
 1176:             if block_type == Flac.METADATA_STREAMINFO and self._parse_duration:
 1177:                 stream_info_header = fh.read(size)
 1178:                 if len(stream_info_header) < 34:  # invalid streaminfo
 1179:                     return
 1180:                 header = struct.unpack('HH3s3s8B16s', stream_info_header)
```

`pynicotine/external/tinytag.py:1200-1208`


```text
 1200:                 self.samplerate = _bytes_to_int(header[4:7]) >> 4
 1201:                 self.channels = ((header[6] >> 1) & 0x07) + 1
 1202:                 self.bitdepth = (((header[6] & 1) << 4) + ((header[7] & 0xF0) >> 4) + 1)
 1203:                 total_sample_bytes = [(header[7] & 0x0F)] + list(header[8:12])
 1204:                 total_samples = _bytes_to_int(total_sample_bytes)
 1205:                 self.duration = total_samples / self.samplerate
 1206:                 if self.duration > 0:
 1207:                     self.bitrate = self.filesize / self.duration * 8 / 1000
 1208:             elif block_type == Flac.METADATA_VORBIS_COMMENT and self._parse_tags:
```

Observation: 3.3.x-style lanes read `fh.read(size)` first and then the exact-buffer `struct.unpack(...)` raises for oversized payloads after materialization.

## github-branch-3.3.x

```text

commit: 98089ac233aa57786e8dbdc48123f6ac1c4767d8

shares.py sha256:   800fb26aaeab87d1aa6d20aba2a3ac185cd18a902d7bffadf87be0e8b4fd1bc9

tinytag.py sha256: f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1

```

### Share-scanner route

`pynicotine/shares.py:604-615`


```text
  604:     def get_audio_tag(self, encoded_file_path, size):
  605: 
  606:         parser_class = TinyTag._get_parser_for_filename(encoded_file_path)  # pylint: disable=protected-access
  607: 
  608:         if parser_class is None:
  609:             return None
  610: 
  611:         with open(encoded_file_path, "rb") as file_handle:
  612:             tag = parser_class(file_handle, size)
  613:             tag.load(tags=False, duration=True, image=False)
  614: 
  615:         return tag
```

`pynicotine/shares.py:626-629`


```text
  626:         # We skip metadata scanning of files without meaningful content
  627:         if size > 128:
  628:             try:
  629:                 tag = self.get_audio_tag(encoded_file_path, size)
```

### TinyTag FLAC route

`pynicotine/external/tinytag.py:136-145`


```text
  136:     def _get_parser_for_filename(cls, filename):
  137:         if cls._file_extension_mapping is None:
  138:             cls._file_extension_mapping = {
  139:                 (b'.mp1', b'.mp2', b'.mp3'): ID3,
  140:                 (b'.oga', b'.ogg', b'.opus', b'.spx'): Ogg,
  141:                 (b'.wav',): Wave,
  142:                 (b'.flac',): Flac,
  143:                 (b'.wma',): Wma,
  144:                 (b'.m4b', b'.m4a', b'.m4r', b'.m4v', b'.mp4', b'.aax', b'.aaxc'): MP4,
  145:                 (b'.aiff', b'.aifc', b'.aif', b'.afc'): Aiff,
```

`pynicotine/external/tinytag.py:1152-1165`


```text
 1152:     def load(self, tags, duration, image=False):
 1153:         self._parse_tags = tags
 1154:         self._parse_duration = duration
 1155:         self._load_image = image
 1156:         header = self._filehandler.peek(4)
 1157:         if header[:3] == b'ID3':  # parse ID3 header if it exists
 1158:             id3 = ID3(self._filehandler, 0)
 1159:             id3._parse_id3v2(self._filehandler)
 1160:             self.update(id3)
 1161:             header = self._filehandler.peek(4)  # after ID3 should be fLaC
 1162:         if header[:4] != b'fLaC':
 1163:             raise TinyTagException('Invalid flac header')
 1164:         self._filehandler.seek(4, os.SEEK_CUR)
 1165:         self._determine_duration(self._filehandler)
```

`pynicotine/external/tinytag.py:1167-1180`


```text
 1167:     def _determine_duration(self, fh):
 1168:         # for spec, see https://xiph.org/flac/ogg_mapping.html
 1169:         header_data = fh.read(4)
 1170:         while len(header_data) == 4:
 1171:             meta_header = struct.unpack('B3B', header_data)
 1172:             block_type = meta_header[0] & 0x7f
 1173:             is_last_block = meta_header[0] & 0x80
 1174:             size = _bytes_to_int(meta_header[1:4])
 1175:             # http://xiph.org/flac/format.html#metadata_block_streaminfo
 1176:             if block_type == Flac.METADATA_STREAMINFO and self._parse_duration:
 1177:                 stream_info_header = fh.read(size)
 1178:                 if len(stream_info_header) < 34:  # invalid streaminfo
 1179:                     return
 1180:                 header = struct.unpack('HH3s3s8B16s', stream_info_header)
```

`pynicotine/external/tinytag.py:1200-1208`


```text
 1200:                 self.samplerate = _bytes_to_int(header[4:7]) >> 4
 1201:                 self.channels = ((header[6] >> 1) & 0x07) + 1
 1202:                 self.bitdepth = (((header[6] & 1) << 4) + ((header[7] & 0xF0) >> 4) + 1)
 1203:                 total_sample_bytes = [(header[7] & 0x0F)] + list(header[8:12])
 1204:                 total_samples = _bytes_to_int(total_sample_bytes)
 1205:                 self.duration = total_samples / self.samplerate
 1206:                 if self.duration > 0:
 1207:                     self.bitrate = self.filesize / self.duration * 8 / 1000
 1208:             elif block_type == Flac.METADATA_VORBIS_COMMENT and self._parse_tags:
```

Observation: 3.3.x-style lanes read `fh.read(size)` first and then the exact-buffer `struct.unpack(...)` raises for oversized payloads after materialization.

## github-branch-master

```text

commit: f4e17d59783dbc48ea31d2e899a681e2dd1ed500

shares.py sha256:   e6580c5b8b240b9c0fadf2c15be6171b55c0e8ad903cae09cdfb5d1a3b2fd419

tinytag.py sha256: aba37daaa69165ffa43298ddca6d6ba7515b76d0358286ad946fb37c102c393f

```

### Share-scanner route

`pynicotine/shares.py:660-673`


```text
  660:     def get_audio_tag(self, file_path, size):
  661: 
  662:         parser_class = TinyTag._get_parser_for_filename(file_path)  # pylint: disable=protected-access
  663: 
  664:         if parser_class is None:
  665:             return None
  666: 
  667:         with open(encode_path(file_path), "rb") as file_handle:
  668:             tag = parser_class()
  669:             tag._filehandler = file_handle                          # pylint: disable=protected-access
  670:             tag.filesize = size
  671:             tag._load(tags=False, duration=True, image=False)       # pylint: disable=protected-access
  672: 
  673:         return tag
```

`pynicotine/shares.py:683-686`


```text
  683:         # We skip metadata scanning of files without meaningful content
  684:         if size > 128:
  685:             try:
  686:                 tag = self.get_audio_tag(file_path, size)
```

### TinyTag FLAC route

`pynicotine/external/tinytag.py:191-205`


```text
  191:     def _get_parser_for_filename(cls, filename: str) -> type[TinyTag] | None:
  192:         if cls._file_extension_mapping is None:
  193:             cls._file_extension_mapping = {
  194:                 ('.mp1', '.mp2', '.mp3'): _ID3,
  195:                 ('.oga', '.ogg', '.opus', '.spx'): _Ogg,
  196:                 ('.wav',): _Wave,
  197:                 ('.flac',): _Flac,
  198:                 ('.wma',): _Wma,
  199:                 ('.m4b', '.m4a', '.m4r', '.m4v', '.mp4',
  200:                  '.aax', '.aaxc'): _MP4,
  201:                 ('.aiff', '.aifc', '.aif', '.afc'): _Aiff,
  202:             }
  203:         filename = filename.lower()
  204:         for ext, tagclass in cls._file_extension_mapping.items():
  205:             if filename.endswith(ext):
```

`pynicotine/external/tinytag.py:1622-1656`


```text
 1622: class _Flac(TinyTag):
 1623:     """FLAC Parser."""
 1624: 
 1625:     _STREAMINFO = 0
 1626:     _VORBIS_COMMENT = 4
 1627:     _PICTURE = 6
 1628: 
 1629:     def _determine_duration(self, fh: BinaryIO) -> None:
 1630:         if not self._tags_parsed:
 1631:             self._parse_tag(fh)
 1632: 
 1633:     def _parse_tag(self, fh: BinaryIO) -> None:
 1634:         id3 = None
 1635:         header = fh.read(4)
 1636:         if header.startswith(b'ID3'):  # parse ID3 header if it exists
 1637:             fh.seek(-4, SEEK_CUR)
 1638:             # pylint: disable=protected-access
 1639:             id3 = _ID3()
 1640:             id3._parse_tags = self._parse_tags
 1641:             id3._load_image = self._load_image
 1642:             id3._parse_id3v2(fh)
 1643:             header = fh.read(4)  # after ID3 should be fLaC
 1644:         if header[:4] != b'fLaC':
 1645:             raise ParseError('Invalid FLAC header')
 1646:         # for spec, see https://xiph.org/flac/ogg_mapping.html
 1647:         header_len = 4
 1648:         block_header = fh.read(header_len)
 1649:         while len(block_header) == header_len:
 1650:             block_type = block_header[0] & 0x7f
 1651:             is_last_block = block_header[0] & 0x80
 1652:             size = unpack('>I', b'\x00' + block_header[1:])[0]
 1653:             # http://xiph.org/flac/format.html#metadata_block_streaminfo
 1654:             if block_type == self._STREAMINFO and self._parse_duration:
 1655:                 head = fh.read(size)
 1656:                 if len(head) < 34:  # invalid streaminfo
```

`pynicotine/external/tinytag.py:1674-1683`


```text
 1674:                 sr = unpack('>I', b'\x00' + head[10:13])[0] >> 4
 1675:                 self.channels = ((head[12] >> 1) & 0x07) + 1
 1676:                 self.bitdepth = (
 1677:                     ((head[12] & 1) << 4) + ((head[13] & 0xF0) >> 4) + 1)
 1678:                 tot_samples_b = bytes([head[13] & 0x0F]) + head[14:18]
 1679:                 tot_samples = unpack('>Q', b'\x00\x00\x00' + tot_samples_b)[0]
 1680:                 self.duration = duration = tot_samples / sr
 1681:                 self.samplerate = sr
 1682:                 if duration > 0:
 1683:                     self.bitrate = self.filesize * 8 / duration / 1000
```

Observation: master parses duration from fixed offsets inside the already-read payload, so oversized STREAMINFO is accepted after materialization.

## Maintainer witness result

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The compact witness uses a valid 34-byte STREAMINFO duration record and padding inside the same metadata block. A 1,048,677-byte STREAMINFO payload and a 2,097,409-byte payload are each read as one `bytes` object at offset 8. A valid 34-byte STREAMINFO block parses a five-second duration, while a 34-byte prefix plus 4,096 padding bytes reads as 4,130 bytes.
