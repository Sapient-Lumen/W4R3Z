# FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127

Current-behavior witness for the TinyTag FLAC STREAMINFO fixed-length validation path used by Nicotine+ share scanning.

Run against one source lane:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_flac_streaminfo_block_budget_reproducer.py
```

The tests intentionally describe current behavior. A hardened metadata scanner should validate or bound the FLAC STREAMINFO block length before materializing an arbitrary advertised payload when the duration fields live in the fixed 34-byte STREAMINFO record.
