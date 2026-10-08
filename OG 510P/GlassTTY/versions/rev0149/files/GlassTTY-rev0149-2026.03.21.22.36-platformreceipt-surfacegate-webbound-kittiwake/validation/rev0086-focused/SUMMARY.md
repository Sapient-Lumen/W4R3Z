# rev0086 focused validation summary

## Scope

Validate that GlassTTY's native host no longer crashes when an outbound message exceeds Chrome's 1 MB host→extension limit.

## Results

- `pytest -q tests/test_native_host.py` → **6 passed**
- `python -m py_compile daemon/src/glassttyd/native_host.py daemon/src/glassttyd/protocol.py` → **passed**
- `cd extension && npm run typecheck` → **passed**
- `cd extension && npm run build` → **passed**
- `python scripts/verify-package.py /mnt/data/GlassTTY-rev0086-2026.03.17.10.03-nativeoverflow-spoolguard-budgetsafety-bobolink.zip --pretty` → **passed**
- `python scripts/archive-audit.py <extracted rev0086 root> --pretty` → **passed**
- Direct runtime overflow proof saved under `validation/rev0086-focused/runtime-overflow-proof/` → **passed**

## Direct runtime proof

The saved proof shows all of the intended runtime behaviors from a real `NativeBridge.emit_to_extension(...)` call in this container:

- the original oversized `bridge.offscreen_fixture` payload was too large for native messaging
- the full payload was saved to `state/fixtures/oversized-host-outbound-*.json`
- `state/latest/oversized-host-outbound.json` mirrored the measured overflow summary
- the outbound wire message became a compact `error.report`
- `bridge.status` surfaced `last_oversized_host_message`

## Honest limits

- This focused bundle does **not** prove a fresh live Chromium/native-host/browser round-trip.
- This focused bundle does **not** prove a fresh Playwright persistent-extension launch here.
