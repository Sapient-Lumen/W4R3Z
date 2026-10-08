# Strict regression fixture contract gate — rev0067

Use this as the reviewer-facing index for the clean-room fixture hygiene layer.

## Command

```bash
python tools/probe_rev0067_regression_fixture_contract.py --source-zip /path/to/Nicotine-source.zip
```

## What it proves

The gate proves the clean-room regression fixtures exported in `handoff/rev0062/cleanroom-kit/tests/` are byte-for-byte copies of the intended maintainer regression artifacts, are free of cube-private path/helper dependencies, and are backed by inherited clean-room runtime evidence.

It also proves the clean-room patch copies exported in the same kit are byte-for-byte copies of the rev0059 split bundle patches.

## What it does not prove

It does not prove live-current upstream filing readiness. That remains blocked on a fresh current checkout/tarball and current-source seven-gate rerun.
