# UPLOAD-QUEUE-POLICY-01 maintainer artifact — rev0020

This directory contains a current-behavior pytest witness for U-244:

```text
test_upload_queue_megabyte_limit_reproducer.py
```

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_upload_queue_megabyte_limit_reproducer.py
```

Run through the cube helper against all archived source lanes with:

```bash
NICOTINE_SOURCE_ROOT=/path/to/source-trees python tools/probe_rev0020_upload_queue_policy.py
```

Expected current behavior in rev0020:

```text
6 passed per lane
```

The tests are intentionally current-behavior witnesses, not a patch. A fixed-behavior version should invert the acceptance assertions for candidate-inclusive megabyte caps if maintainers choose that semantics.
