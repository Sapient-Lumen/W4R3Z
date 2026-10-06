# DeriveBSD rev0535 session review — host probes collector releasegreen gull

## Result

This cut turns the remaining FreeBSD host-smoke proof seam into a stricter collection path instead of another checklist. The cube still does not contain a real non-simulated FreeBSD receipt, but the operator path for producing one is now executable and default-strict.

## Material changes

- Added `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh`, an executable wrapper that runs the real host smoke, validates the receipt without `--allow-*` non-proof flags, and prints the receipt path plus SHA-256.
- Extended `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` so it records seven host probes after fixture/worker-source admission and before compile, `makefs`, `mdconfig`, or mount authority: `uname -s`, `uname -r`, `uname -m`, `id -u`, `sysctl kern.osreldate`, `sysctl kern.features.security_capability_mode`, and `sysctl kern.features.security_capabilities`.
- Extended `tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py`, `spec/removable.media.local.freebsd.host.smoke.receipt.schema.json`, and the checked-in refusal example so default real-proof mode requires those host-probe fields.
- Refactored `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` so checker simulations generate probe rows, environment sanitization covers host probes and media commands, and the old duplicate worker-launch evidence block is gone.
- Refreshed generated hygiene/schema examples and generated docs for `2026-06-12r566`.

## Validation

- Release-critical hygiene: 36/36 passed.
- Schema-cube-audit hygiene: 3/3 passed.
- Targeted host-smoke runner, spec example validation, generated docs, executable-bit, bytecode, and front-door budget checks passed.
- Front-door budget stayed green by keeping `docs/00-index.md` at its ratcheted line limit.

## Still open

- A real non-simulated FreeBSD host receipt is still absent; rev0535 makes it harder to confuse checker simulations with proof and easier to collect the real evidence.
- `docs/00-index.md` and `docs/99-llm-runbook.md` still carry byte-growth warnings even though the line budget passes.
- The schema audit still has 7 open const-heavy refactor items; the current top open item is `spec/removable.media.capsicum.worker.bridge.schema.json`.
