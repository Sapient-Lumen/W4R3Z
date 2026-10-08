# TRANSFER-SIZE-PROVENANCE-01 maintainer artifact

Current-behavior pytest witness for U-69, U-107, and U-198.

Run from a Nicotine+ checkout or set `NICOTINE_SOURCE`:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_transfer_size_and_file_provenance_reproducer.py
```

The tests are reproducer tests, not final patch tests. After a fix, invert the current-behavior assertions into fixed-behavior assertions:

- download size changes should be bounded/confirmed/bound to request generation;
- upload reads should be clamped to remaining advertised bytes;
- upload file identity/size should be revalidated at F-init/open time or kept as a stable opened handle.
