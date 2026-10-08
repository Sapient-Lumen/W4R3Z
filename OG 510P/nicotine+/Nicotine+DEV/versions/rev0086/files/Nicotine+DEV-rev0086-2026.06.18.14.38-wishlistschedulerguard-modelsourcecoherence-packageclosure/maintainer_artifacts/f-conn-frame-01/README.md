# F-CONN-FRAME-01 maintainer artifact

This directory contains current-behavior pytest reproducers for U-164 fixed-width F-connection frame fragmentation.

Preferred rev0015 witness:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q   maintainer_artifacts/f-conn-frame-01/test_f_connection_fixed_frame_fragment_reproducer.py
```

rev0015 ran it against the archived external source lanes from the rev0003 source bundle:

```text
github-tag-3.3.10: 22 passed
github-branch-3.3.x: 22 passed
github-branch-master: 22 passed
```

The tests assert current behavior, not fixed behavior.
