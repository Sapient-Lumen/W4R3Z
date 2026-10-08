# rev0056 focused validation summary

## Commands run

- `npm --prefix extension run typecheck`
- `npm --prefix extension run build`
- `node extension/scripts/receiver-inventory-check.mjs`
- `node extension/scripts/receiver-priming-check.mjs`
- `pytest -q tests/test_protocol.py tests/test_state.py tests/test_broker.py tests/test_cli.py tests/test_native_host.py tests/test_validate_release.py`
- `python -u scripts/validate-release.py` *(partial only in this container)*

## Result

- extension typecheck: passed
- extension build: passed
- deterministic receiver inventory check: passed
- deterministic receiver priming check: passed
- focused pytest slice: passed (`34 passed`)
- umbrella release validator: partial only; it did not produce a full clean pass in this container

## What this proves

rev0056 changes GlassTTY's daemon/CLI receiver-resolution layer. The focused proof covers the new outermost/lifecycle-aware CLI helpers directly, while the existing extension deterministic checks confirm that the receiver inventory and priming helpers still behave as expected after the archive refresh.

## Honest gap

This container still does not prove a live Chromium navigation-churn case where `glassttyd resolve-receiver --active-outermost` is exercised against real prerender/active documents end to end.
