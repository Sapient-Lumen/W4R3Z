# Parallel testing and metrics through rev0011

MTGSim's test strategy assumes the suite will become much larger than this cloud/container can run naively. The harness therefore decomposes work into small subprocess jobs and records enough timing data to improve scheduling over time.

## Current parallel units

- C++ test cases: discovered from `mtgsim_tests --list-json` and run case-by-case.
- Scenario files: discovered from `tests/scenarios/*.mtgscn` and run independently.
- Fuzz seeds: each seed/step pair is its own deterministic job.
- Priority-pass benchmark pairs: the microbenchmark reports both pass pairs and actual priority-pass calls; it is not labeled as representative full-game throughput.

## Sharding

C++ cases support round-robin, hash, and SQLite-duration-greedy sharding. Scenario and fuzz runners support deterministic shard index/count arguments. The goal is to make local runs and CI/multi-machine runs use the same mental model.

## Metrics

`tools/metrics_db.py` records harness runs, build runs, C++ cases, scenarios, fuzz seeds, rule-progress snapshots, and step timings into SQLite. rev0009 fuzz reports add trigger-stack action counts so future dashboards can detect whether new action surfaces are being exercised.

## Native CMake compatibility

CMake/CTest exists as a compatibility path for users and CI environments that expect native CMake workflows. CTest labels select broad groups such as C++ core, scenario/rules, or fuzz/invariants. Future resource-aware jobs can borrow CTest-style processor/resource concepts for long fuzz/benchmark tasks.

## rev0010 test-inventory manifest

`tools/plan_test_matrix.py` now emits schema `mtgsim.test_matrix_plan.v2`. In addition to rule/tag buckets, it writes a normalized `work_units` array covering C++ cases, scenario files, and fuzz seed jobs. It also writes `duration_greedy_bins`, which is a ready-to-schedule shard plan balanced by historical C++ durations plus conservative estimates for scenarios and fuzz seeds.

This does not replace the existing runners. It gives CI/cloud execution a stable planning layer: produce the matrix once, fan out workers by work-unit IDs or duration-greedy bins, and keep the low-level runners focused on executing small slices fast.

## rev0011 matrix growth

The counter slice increases the decomposable work inventory with six C++ cases and two scenario files. These remain small, independent work units, which is the shape we want for long-term high-parallel CI and cloudtainer-friendly optimization loops.

## rev0013 work-unit growth

The new keyword slice adds C++ cases and scenario files without changing the parallelization model. The stable unit remains the same: C++ case, scenario file, or fuzz seed. That means new rule slices increase coverage without requiring new harness topology.

## rev0036 bounded auto fan-out

The low-level runners already submit bounded waves instead of preloading the entire suite, but `--jobs auto` could still expand to the host-reported CPU count. In this cloudtainer that meant C++ case execution attempted extremely high fan-out and could waste budget before any semantic failure appeared. rev0036 adds default caps: `MTGSIM_BUILD_AUTO_JOBS=8`, `MTGSIM_AUTO_JOBS=8`, and `MTGSIM_SANITIZE_AUTO_JOBS=8`. Explicit `--jobs N` remains available when a caller has a known-capacity machine.

## rev0060 release clean-build guard

The harness previously capped auto fan-out, but a separate waste mode remained: release builds spent excessive time optimizing validation and executable driver translation units with `-O3`. In this cloudtainer, clean release builds could time out before any semantic tests ran. `tools/build.py` now applies `--release-fast-build-opt-level 1` by default to `src/validation.cpp` plus driver files under `tests/`, `apps/`, and `benchmarks/`, while keeping the reusable engine core on the normal release flags. CMake Release builds mirror that posture for validation and driver targets.

Use `--release-fast-build-opt-level 3` when a machine is specifically benchmarking driver/validation optimization. For ordinary artifact validation, spending compiler budget on glue is lower value than running C++ cases, scenarios, fuzz, rules coverage, and the audit.

## rev0067 sanitizer and budget correction

Release was no longer the only compile-time waste mode. `src/validation.cpp` under GCC `-O1 -g3` plus ASan/UBSan exceeded a five-minute outer budget even though clean release builds were fast. The sanitizer build now leaves instrumentation enabled but defaults that translation unit to `-O0 -g1`; the same unit compiled in roughly 6.2 seconds in the audit container with that posture.

`--time-budget-sec` is also a true subprocess deadline now. Each compile/link receives the remaining time, and timeout cleanup kills the complete compiler process group. This prevents the wrapper from reporting a timeout while orphaned compiler children continue spending cloud resources.
