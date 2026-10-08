# rev0034 source trace — FLAC leading ID3v2 duration-only prelude

Canonical packet: **U-139 / FLAC-LEADING-ID3V2-DURATION-PRELUDE-01**.

## github-tag-3.3.10

Commit: `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026`

`pynicotine/shares.py` SHA256 `62aff8095c6e28abefd41e25c566c1499b8a8f6cdd487ab44ef0641f04405f0e`

`pynicotine/external/tinytag.py` SHA256 `f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1`

Relevant source landmarks:

- share scanner parser selection/load/size gate: lines 599 / 606 / 620
- FLAC class and leading ID3 handling: `Flac`, load/path line 1152, ID3 check line 1157, ID3 parse line 1159
- ID3 frame parser: ID3v2 loop line 762, frame-header read line 809, frame-content read line 823
- tags=False guard: none in leading-FLAC ID3 helper; ID3 instance defaults _parse_tags=True
- duration path: 1165-1205

Interpretation: Duration-only FLAC load always parses a leading ID3v2 tag; mapped text frames are read/decoded/applied before STREAMINFO duration extraction.

## github-branch-3.3.x

Commit: `98089ac233aa57786e8dbdc48123f6ac1c4767d8`

`pynicotine/shares.py` SHA256 `800fb26aaeab87d1aa6d20aba2a3ac185cd18a902d7bffadf87be0e8b4fd1bc9`

`pynicotine/external/tinytag.py` SHA256 `f4ad28eabd63321af276460c4693b6f874b96683679eb5ad448671d86a5802c1`

Relevant source landmarks:

- share scanner parser selection/load/size gate: lines 606 / 613 / 627
- FLAC class and leading ID3 handling: `Flac`, load/path line 1152, ID3 check line 1157, ID3 parse line 1159
- ID3 frame parser: ID3v2 loop line 762, frame-header read line 809, frame-content read line 823
- tags=False guard: none in leading-FLAC ID3 helper; ID3 instance defaults _parse_tags=True
- duration path: 1165-1205

Interpretation: Same vendored TinyTag behavior as 3.3.10; duration-only share scan can still materialize/apply leading ID3v2 text tags.

## github-branch-master

Commit: `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`

`pynicotine/shares.py` SHA256 `e6580c5b8b240b9c0fadf2c15be6171b55c0e8ad903cae09cdfb5d1a3b2fd419`

`pynicotine/external/tinytag.py` SHA256 `aba37daaa69165ffa43298ddca6d6ba7515b76d0358286ad946fb37c102c393f`

Relevant source landmarks:

- share scanner parser selection/load/size gate: lines 662 / 671 / 684
- FLAC class and leading ID3 handling: `_Flac`, load/path line _load inherited at 258-269, _Flac._parse_tag at 1633, ID3 check line 1636, ID3 parse line 1642
- ID3 frame parser: ID3v2 loop line 1040, frame-header read line 1135, frame-content read line 1158 only when _parse_tags is true for mapped frames
- tags=False guard: 1153-1155 returns frame_size for mapped ID3 fields when _parse_tags is false; no title is applied
- duration path: 1654-1683

Interpretation: Master propagates tags=False into the leading-ID3 parser and avoids mapped text-frame materialization/application; it still traverses the ID3v2 prelude before native FLAC duration parsing.
