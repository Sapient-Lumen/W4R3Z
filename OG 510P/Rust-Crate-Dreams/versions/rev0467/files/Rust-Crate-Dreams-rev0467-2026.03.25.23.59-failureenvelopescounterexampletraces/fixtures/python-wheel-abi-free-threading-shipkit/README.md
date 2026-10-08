# python-wheel-abi-free-threading-shipkit

Fixture pack for **P-0466 Python Wheel ABI & Free-Threading ShipKit**.

The first implementation should revolve around a compact `pywheelbundle.zip` and a few reviewable reports rather than a giant new Python packaging stack.

## Core review objects

- **ABI target class** — which compatibility class the release is actually claiming.
- **Thread-support declaration** — whether the extension declares free-threaded safety, opts out, or still needs manual review.
- **Variant horizon** — whether accepted future surfaces like `abi3t` and wheel variants are intentionally out-of-scope, planned, or blocked on tooling.

## Core schemas in this fixture pack

- `abi-target.report.schema.json`
- `thread-support.report.schema.json`
- `variant-horizon.report.schema.json`

## Scenario families

- `scenarios/abi3_nonfree_plus_cp314t_split/`
- `scenarios/pymodule_gil_used_true_requires_runtime_optout_note/`
- `scenarios/abi3t_future_policy_waits_for_tooling/`

Future passes should keep this fixture pack scoped to **release-contract truth above PyO3 / maturin / wheel tooling** and avoid turning it into a full Python build backend.
