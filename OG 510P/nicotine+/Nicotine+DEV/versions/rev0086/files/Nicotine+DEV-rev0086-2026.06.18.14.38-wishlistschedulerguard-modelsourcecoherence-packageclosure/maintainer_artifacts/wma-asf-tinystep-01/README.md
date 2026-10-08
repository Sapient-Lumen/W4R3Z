# WMA-ASF-TINYSTEP-01 maintainer artifact

Current-behavior witness for **U-273**.

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_wma_asf_tinystep_reproducer.py
```

The test builds a compact ASF/WMA-like byte stream with repeated unknown ASF object headers. When `object_size` is `8`, the WMA parser consumes the 24-byte object header and then seeks back 16 bytes, so each next object-header read starts only eight bytes later.

The assertions intentionally pass on current archived lanes. A hardened parser should reject or stop on `0 < object_size < 24` before seeking relative to the current position.
