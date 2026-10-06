# BrowserRT changelog

## rev0005 — 2026-05-24

Summary highlight: testing observatory: affected selection, surface inventory, timing history, process policy.
Codename: Test Observatory Scaffold.

Rev0005 expands the testing facility into an explicit observatory for future
BrowserRT work. The purpose is to prevent browser, OPFS, SAB, WebGPU, mesh,
chaos, replay, and benchmark checks from entering as one giant expensive command.

Added:

- schema-2 `test/manifest.json` with areas, size, isolation, flakiness, risk,
  estimates, timeouts, and conservative input globs;
- `test/impact-map.json` for conservative affected-test selection;
- `test/surface-inventory.json` for current and future test surfaces;
- `test/quarantine.json` as an explicit flake/quarantine ledger;
- `tools/plan_tests.mjs` for dry planning and affected explanation;
- `tools/validate_test_surface.mjs` for manifest, impact, inventory, and
  quarantine validation;
- `tools/analyze_tests.mjs` for slowest-test and estimate-miss analysis;
- `--changed`, `--only-affected`, `--dry-run`, `--history`, and timing-summary
  support in `tools/run_tests.mjs`;
- `docs/05-research/testing-facility-research-pass-002.md`;
- docs for process-start policy, affected selection, browser harness planning,
  flake/chaos policy, stress policy, capability-gated testing, and artifact
  policy;
- validation artifacts for timing history, test analysis, surface report, turn
  bootstrap, turn smoke, release test run, and proof run.

Changed:

- `make lint` now validates cube surfaces, release tests, surface inventory,
  timing analysis, and cube surfaces again.
- `make test-affected CHANGED=<paths>` now gives a first affected-selection path.
- `tools/package_release.py` regenerates proof, test, surface, analysis, and
  turn-start artifacts before packaging.
- Reentry/status/validation/context surfaces now explain why cross-turn daemons
  are not canonical.

Non-claims:

- No real browser/CDP harness yet.
- No OPFS/SAB/WebGPU tests yet.
- No cross-turn daemon reliance.
- No remote cache.
- No cloudtainer timing as a public performance claim.

## rev0004 — 2026-05-24

Summary highlight: added a manifest-driven cloudtainer test facility with timing, sharding, and turn bootstrap.
Codename: Test Kernel Scaffold.

This revision treated testing cost as a first-class BrowserRT design constraint.
It added a researched testing-facility pass, a manifest-driven runner,
deterministic weighted sharding, parallel child-process execution with
serial-group guards, per-task timing reports, and a one-shot turn bootstrap
command.

## rev0003 — 2026-05-24

Summary highlight: added the first executable boot, trace, bounded-channel, worker-transfer, and supervisor-restart proof.
Codename: Phase Zero Agent Supervisor.

This revision paused research expansion and turned the rev0002 ambition into a
narrow running kernel slice. It proved, inside the cloudtainer and without
external dependencies, that BrowserRT could boot, emit trace evidence, bound a
channel, create a transferable object ref, send transferred bytes to a worker,
observe an intentional worker crash, spend a restart budget, and route a later
call through the replacement agent.

## rev0002 — 2026-05-24

Summary highlight: researched adjacent runtimes and folded a steal-bank into the BrowserRT kernel contract.
Codename: One Runtime Stealbank.

This revision researched adjacent systems and extracted ambitious design pressure
without adding dependencies or overclaiming implementation progress.

## rev0001 — 2026-05-24

Summary highlight: first BrowserRT baby cube: learned datacube discipline plus frozen runtime contracts.
Codename: Baby Kernel.

This first cube froze the baby archive shape and non-negotiable runtime contracts
before code growth.
