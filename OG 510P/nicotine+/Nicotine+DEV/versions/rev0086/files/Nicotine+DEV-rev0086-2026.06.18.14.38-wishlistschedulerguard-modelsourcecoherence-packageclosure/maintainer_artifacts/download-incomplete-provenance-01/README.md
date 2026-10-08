# DOWNLOAD-INCOMPLETE-PROVENANCE-01 maintainer witness

Current-behavior pytest witness for rev0023.

Run against a source lane with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_download_incomplete_provenance_reproducer.py
```

The tests intentionally describe current behavior, not a patch. They cover:

- stale exact-size incomplete file promoted to finished without receiving new bytes;
- stale partial incomplete file trusted as the resume offset;
- incomplete path symlink following / non-regular-file gate absence;
- advisory lock failure logged but transfer continuing;
- ambiguous `virtual_path + username` incomplete-file identity plus basename truncation collision;
- existing completed file same-size shortcut support case;
- completed-file move destination race support case.
