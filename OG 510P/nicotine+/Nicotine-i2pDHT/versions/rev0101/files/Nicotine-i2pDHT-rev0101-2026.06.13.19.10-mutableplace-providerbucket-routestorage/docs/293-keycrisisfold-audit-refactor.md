# keycrisisfold audit/refactor

`keycrisisfold.py` is the rev0030 navigation fold. It checks that the current revision is visible across:

- current modules
- current tests
- current docs
- `HEAD_REGISTRY.json`
- `PUBLIC_SURFACE.json`
- `docs/00-index.md`
- `README.md`
- `START_HERE.md`
- `surfaceledger.py`

It also runs the rev0029 `foldseal.py` predecessor check. The audit lane is intentionally part of the cube because the cube has many historical branchlets; a new useful surface that cannot be found later is a failed surface.
