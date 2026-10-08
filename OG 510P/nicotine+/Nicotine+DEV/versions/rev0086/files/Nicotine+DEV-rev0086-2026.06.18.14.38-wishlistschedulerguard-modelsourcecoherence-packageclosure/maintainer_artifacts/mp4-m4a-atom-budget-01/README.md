# MP4-M4A-ATOM-BUDGET-01 maintainer artifact

Current-behavior witness for **U-125**.

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_mp4_m4a_atom_budget_reproducer.py
```

The test builds compact MP4/M4A-like streams with a valid `mvhd` duration prefix and controllable trailing padding inside the same atom. The assertions intentionally pass on the archived source lanes: the MP4 duration traversal reads the entire advertised `mvhd` atom payload into one `bytes` object before the fixed-prefix duration parser runs.

A hardened share-scanner metadata parser should apply a local MP4 atom payload budget or parse fixed-prefix leaves incrementally before materializing arbitrary atom payloads.
