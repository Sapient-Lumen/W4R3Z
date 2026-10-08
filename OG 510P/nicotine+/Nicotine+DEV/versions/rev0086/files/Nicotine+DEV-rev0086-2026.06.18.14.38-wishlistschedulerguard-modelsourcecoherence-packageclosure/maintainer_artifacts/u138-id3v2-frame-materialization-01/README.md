# U-138 ID3v2 frame-materialization boundary witness

This maintainer artifact is a current-behavior boundary witness, not a strict/front promotion packet.

It verifies the split discovered in rev0044:

- Nicotine+'s MP3 share-scanner duration path uses TinyTag with `tags=False, duration=True`; across the archived lanes, that path skips the leading ID3v2 payload and does not materialize a mapped text frame body as one advertised read.
- Generic TinyTag ID3v2 tag parsing with `tags=True` still materializes mapped text-frame bodies according to the advertised frame size.
- Unmapped/private ID3v2 frames are skipped rather than materialized.

Run one lane directly:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python -m pytest -q -p no:cacheprovider \
  maintainer_artifacts/u138-id3v2-frame-materialization-01/test_id3v2_frame_materialization_boundary_reproducer.py
```

Run all archived lanes with:

```bash
python tools/probe_rev0044_u138_id3v2_boundary.py /path/to/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
```
