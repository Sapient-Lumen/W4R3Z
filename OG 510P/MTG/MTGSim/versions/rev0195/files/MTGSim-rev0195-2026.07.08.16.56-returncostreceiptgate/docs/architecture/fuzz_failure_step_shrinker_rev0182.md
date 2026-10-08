# rev0182 — Fuzz Failure Step Shrinker

## Why this was the riskiest next seam

The cube already runs legal-action fuzzing, broad seeds, and risk-seam seeds. The weak point was what happened after a randomized failure: the report could tell us a seed and a large step budget, but it did not automatically prove that the failure reproduced or reduce the step tail to the first failing prefix. That is high risk because future fuzz failures would consume human time and could be mis-triaged as noisy or flaky.

## What changed

`tools/run_fuzz.py` now emits a replay command for every seed. When a seed fails, the runner replays the original failing seed and binary-searches the smallest `--steps` value that still fails, subject to the existing timeout/budget controls. Reports now carry:

- `repro_command` for the original failing seed and step budget.
- `minimal_failing_steps` when shrinking succeeds.
- `minimal_repro_command` for direct debugging.
- `shrink_status`, `shrink_attempts`, and `shrink_message` so timeout, budget, non-repro, disabled, and minimized outcomes are distinguishable.
- `summary.failed_repro_commands` and JUnit failure text with `minimal_repro=...` so CI logs are actionable without opening the full JSON.

`tools/harness.py` now runs `tests/python/test_fuzz_runner.py` as `python.fuzz_runner` in `test`, `all`, and `matrix` plans. `tools/audit_datacube.py` also probes the shrinker wiring so later refactors cannot silently drop it.

## Online grounding

The online check for this pass focused on current fuzzing practice rather than adding Magic-rules doctrine. LLVM libFuzzer documents crash artifacts, corpus minimization, `-minimize_crash`, and deterministic/fast targets; AFL/AFL++ document test-case minimizers such as `afl-tmin` that preserve failure behavior while reducing the artifact. MTGSim's harness is seed/step driven rather than byte-input driven, so rev0182 implements an equivalent local reducer over the failing transition prefix.

Sources observed online this session:

- https://llvm.org/docs/LibFuzzer.html
- https://afl-1.readthedocs.io/en/latest/fuzzing.html
- https://aflplusplus-aflplusplus.mintlify.app/commands/afl-tmin

## Deliberate limits

The shrinker currently minimizes the number of legal-action steps, not the full scenario/card-state input. It also skips timeout failures because shortening a timeout can hide scheduling noise. The next useful improvement would be semantic delta-debugging over the action trace once failure classes become richer.

Datacube: `MTGSim-rev0182-2026.07.08.05.55-fuzzshrinkaudit.zip`
