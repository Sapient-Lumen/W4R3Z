# nativeloadloopfold audit/refactor

`nativeloadloopfold.py` is the rev0093 audit/refactor surface.

It checks:

- `nativeloadloop.py`
- `nativecallcanary.py`
- `dispatchfence.py`
- `nativefoldspine.py`
- `tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py`
- rev0093 docs
- `README.md`
- `START_HERE.md`
- `PUBLIC_SURFACE.json`
- `HEAD_REGISTRY.json`
- predecessor `nativeloadreentryfold`
- fold map / fold registry / surface ledger

The refactor goal is to keep the native branch as an auditable spine rather than a pile of one-off hold states.
