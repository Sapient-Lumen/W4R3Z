# rev0073 construction-stage tools

`probe_rev0073_u123_current_pre_disposition.py` is preserved as construction history. It is not an active entrypoint: it used a shared temporary parent, ran a superseded classification, and could overwrite the canonical `rev0073_u123_test_matrix.*` files with an incompatible schema.

Use these active tools instead:

```text
tools/probe_rev0073_u123_disposition.py
tools/probe_rev0073_u123_native_patch.py
```
