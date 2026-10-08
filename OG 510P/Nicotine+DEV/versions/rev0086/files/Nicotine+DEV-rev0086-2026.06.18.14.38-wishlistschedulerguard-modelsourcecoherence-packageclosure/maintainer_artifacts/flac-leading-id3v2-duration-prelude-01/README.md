# FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 maintainer artifact — rev0034

This directory contains a current-behavior pytest witness for **U-139**.

Run one lane manually:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus PYTHONPATH=/path/to/nicotine-plus PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider test_flac_leading_id3v2_duration_prelude_reproducer.py
```

Run all archived lanes from the cube root:

```bash
python tools/probe_rev0034_flac_leading_id3v2_duration_prelude.py /path/to/source-trees
```

The witness intentionally preserves the lane split:

```text
3.3.10 / 3.3.x:
  leading ID3v2 TIT2 frame content is read, decoded, and applied to the FLAC tag
  even though the caller requested tags=False and duration=True.

master:
  mapped ID3v2 tag fields are no longer applied when tags=False, and the large
  frame body is not read as one text field. The parser still traverses the
  leading ID3v2 envelope before reaching native FLAC STREAMINFO.
```
