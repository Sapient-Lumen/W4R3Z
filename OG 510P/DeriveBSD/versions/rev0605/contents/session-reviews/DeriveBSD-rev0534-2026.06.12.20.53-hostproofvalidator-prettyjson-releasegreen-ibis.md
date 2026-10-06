# rev0534 review — host proof validator and host-smoke receipt refactor

This cut prioritizes the riskiest still-open seam: the FreeBSD host-smoke proof path. rev0533 made the receipt schema-backed, but a real operator still needed a crisp answer to “does this JSON count as host proof?” rev0534 adds that answer as code.

## Material movement

- Added `tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py`.
- The validator exits 0 by default only for a real, non-simulated FreeBSD `passed` host-smoke receipt.
- Cloudtainer refusal evidence requires `--allow-refusal`.
- Receipt-shaped failure evidence requires `--allow-failed`.
- Checker-only success/failure simulations require `--allow-checker-simulation`.
- The release-critical host-smoke checker now proves that the success simulation is rejected in default real-proof mode and accepted only with the explicit checker-simulation flag.
- Successful host-smoke receipts now carry `host_smoke.worker_launched = true`, so worker execution after `umount` and `mdconfig -d` is directly visible instead of inferred only from the nested worker object.
- Host-smoke receipt writes now use `tools/cube_digest_lib.py` `write_pretty_json()`, and `command_shape_sha256` uses the shared restricted canonical JSON bytes.

## Validation

- `tools/hygiene.py --profile release-critical`: 36/36 passed.
- `tools/hygiene.py --profile schema-cube-audit`: 3/3 passed.
- Bytecode artifact check: passed after cleanup.

## Remaining risk

A real FreeBSD host-smoke receipt is still absent. This cut deliberately does not fake that. It makes the proof gate executable so the first real FreeBSD receipt can be judged without accepting checker simulations by accident.
