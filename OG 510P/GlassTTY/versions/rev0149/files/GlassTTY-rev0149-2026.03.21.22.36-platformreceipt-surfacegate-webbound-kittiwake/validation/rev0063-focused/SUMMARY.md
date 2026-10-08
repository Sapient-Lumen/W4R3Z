# rev0063 focused validation

- overall_ok: true
- gate: direct focused commands plus package verification
- wrapper_note: `scripts/validate-release.py` again preserved only early-step artifacts in this container; those partial artifacts remain under `validation/rev0063-focused/steps/` for honesty

## Saved artifacts

- `extension-typecheck.txt`
- `extension-build.txt`
- `receiver-inventory-check.json`
- `receiver-priming-check.json`
- `content-script-experiment-check.json`
- `compare-coverage-experiments.json`
- `doctor-pretty.json`
- `native-message-budget.json`
- `pytest-focused.txt`
- `package-verify.json`
- partial wrapper evidence under `steps/`

## Honest gap

This bundle still does not contain one live Chromium/native-messaging/browser proof where a real supported tab is reloaded after `set-content-script-experiment ...` and then compared via the new coverage-experiment comparator.
