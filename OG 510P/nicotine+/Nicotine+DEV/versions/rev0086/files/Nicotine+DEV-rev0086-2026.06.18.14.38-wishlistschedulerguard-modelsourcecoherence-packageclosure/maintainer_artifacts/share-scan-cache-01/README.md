# SHARE-SCAN-CACHE-01 / U-248 maintainer artifact

Current-behavior pytest witness for share-rescan cache provenance.

Run from a Nicotine+ source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_share_rescan_mtime_cache_reproducer.py
```

The tests intentionally document current behavior: if the path exists in the old share database and `st_mtime` matches, scanner metadata is reused without checking `st_size`, inode/device, ctime, or a cache-generation marker. Baseline tests show that `rebuild=True` or a changed mtime recomputes file size.
