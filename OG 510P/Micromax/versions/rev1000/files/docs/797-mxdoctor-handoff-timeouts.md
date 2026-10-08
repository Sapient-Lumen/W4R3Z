# rev0838 — mxdoctor handoff manifest and timeout discipline

## Landing

Rev0838 closes a concrete handoff gap in the doctor/preflight lane, trims one small repeated-test waste found during audit, and fixes a budget-resume bug that could throw away later valid pass evidence.

## What changed

- `mxdoctor --chunked` now defaults to the archive-carried aggregate manifest `.artifacts/mxtest-all-64.json`, matching the Makefile handoff lane instead of creating or advancing the legacy `.artifacts/mxtest-all.json` side lane.
- The chunked doctor command now includes `--checkpoint-tests` so interrupted aggregate health checks preserve completed test prefixes through the same runway used by `make test-all-chunks`.
- Default doctor child commands now have process-level timeout handling: mxlint defaults to 120 seconds, default preflight pytest children default to 180 seconds, and both can be disabled or tuned with environment variables.
- Explicit long lanes remain opt-in: `MXDOCTOR_FULL_TIMEOUT_SECONDS` and `MXDOCTOR_CHUNKED_SUPERVISOR_TIMEOUT_SECONDS` can add outer bounds without changing their default semantics.
- `FAST_PYTEST_TARGETS` no longer repeats `tests/test_editor_readonly_option.py`, and tests now assert the fast lane has no duplicate selectors.
- A duplicate local declaration in `tools/mxtest.py` was removed while preserving the source-dependency behavior from rev0837.
- Budget-limited aggregate resumes now preserve later matching passed chunks instead of replacing them with `not_run` rows after an early max-new budget stop.

## Why this mattered

The riskiest unfinished item is still aggregate evidence. A doctor command that writes a different manifest from the handoff path makes that risk worse because future sessions can spend time advancing the wrong witness. The fix keeps the quick health command and the long evidence lane pointed at the same carried manifest.

The second risk was evidence regression during budget-limited resumes: an early max-new budget stop could erase later matching pass evidence from the manifest. Rev0838 now keeps that evidence when it is still source/environment/chunk compatible.

The third risk was unbounded default preflight children. `mxtest` had already gained child timeout, checkpoint, and runtime-budget behavior; doctor was still delegating to subprocesses without a timeout. Rev0838 gives the default lane a bounded failure mode without turning doctor into another registry-heavy system.

## Validation

- `python tools/mxlint.py`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxdoctor.py tests/test_mxtest.py`

## Remaining risk

The aggregate manifest is still partial. After docs/context are refreshed for rev0838, resume `.artifacts/mxtest-all-64.json` before packaging so the archive carries current-source, current-environment evidence.
