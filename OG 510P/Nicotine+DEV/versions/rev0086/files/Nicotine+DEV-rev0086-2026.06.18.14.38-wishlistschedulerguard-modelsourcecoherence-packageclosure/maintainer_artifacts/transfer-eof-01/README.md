# TRANSFER-EOF-01 / U-251 maintainer artifact

This directory contains a current-behavior pytest witness for upload send-loop behavior when the opened file cannot provide exactly the advertised transfer size.

Run against a source tree with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
  maintainer_artifacts/transfer-eof-01/test_upload_eof_before_advertised_size_reproducer.py
```

Expected current behavior in rev0019's archived lanes:

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The tests are current-behavior witnesses, not desired fixed-behavior tests. A future patch should invert or replace the expectations as appropriate.
