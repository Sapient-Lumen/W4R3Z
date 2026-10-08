# Harness design through rev0011

The harness exists because MTGSim will eventually have thousands of small rules fixtures and a time-limited cloud/container workflow. Every expensive operation should be decomposable, timed, reportable, and rerunnable in isolation.

## Main entry point

`tools/harness.py` owns high-level plans:

- `audit`: structural datacube audit only;
- `rules`: rule ledger validation plus progress estimate;
- `cards`: build and report the SQLite card catalog;
- `build`: GCC object-level build of all targets;
- `plan-tests`: build scenario/tests targets and emit a rule/tag/scenario matrix plan;
- `quick`: rule coverage, build tests, and run release C++ cases;
- `test`: rules, progress, manifest, card catalog, C++ cases, scenarios, and fuzz;
- `scenarios`: build the scenario executable and run scenario files only;
- `fuzz`: build the fuzz executable and run seed-parallel randomized invariant tests;
- `bench`: build and run the benchmark;
- `shards`: build tests and run a local multi-shard C++ aggregate;
- `all`: rules, progress, manifest, card catalog, build, audit, matrix plan, C++ cases, scenarios, fuzz, benchmark, and metrics summary;
- `matrix`: release and sanitizer C++, scenario, fuzz, and card-catalog passes.

Each step records status, duration, command, return code, output tails, and selected metrics. Reports are written as JSON, JSONL, JUnit XML, and SQLite records where appropriate.

## Build layer

`tools/build.py` is GCC-first. It supports target decomposition, object-level incremental builds, command hashes, depfiles, parallel compiles, sanitizer/profile modes, compile command generation, and hard wall-clock budgets. Targets include `tests`, `scenario`, `fuzz`, `cli`, and `bench`.

## Case, scenario, and fuzz layers

The C++ test binary owns test registration and case metadata. Python owns scheduling. This split keeps C++ tests tiny while the runner provides discovery, filters, repeat counts, shuffle seeds, subprocess isolation, timeouts, global budgets, sharding, JSON/JUnit reports, and SQLite ingestion.

`apps/mtgsim_scenario.cpp` reads line-oriented `.mtgscn` fixtures. Scenarios are the future low-friction way to add rule/card-template regressions without recompiling the test binary; rev0009 uses them for trigger examples.

`apps/mtgsim_fuzz.cpp` builds a deterministic mini-game, samples legal actions from a seeded PRNG, applies them, and validates invariants after each step. It is not coverage-guided fuzzing yet; it is cheap randomized invariant testing. rev0009 includes a trigger-action counter in fuzz reports so we can detect whether random walks are exercising the new action surface.

## Card catalog layer

`tools/card_db.py` builds a small SQLite catalog from local sample JSON. The harness runs it so card-data ingestion remains part of the normal validation loop rather than a forgotten side tool.

## Continuous optimization

The metrics spine records durations by step, C++ case, scenario, fuzz seed, and build target. Duration-greedy sharding can then use history to balance future parallel jobs. This keeps the project compatible with short cloud time limits while still allowing the suite to grow.

## rev0010 matrix planner integration

The `plan-tests` and `all` harness plans now pass fuzz seed/step counts and a target shard count to `tools/plan_test_matrix.py`. The resulting matrix report can decompose all native work into three categories: `cpp_case`, `scenario`, and `fuzz_seed`. This is the first step toward a resource-aware scheduler that can decide whether a cloudtainer should run many tiny C++ cases, a few scenario batches, or fuzz seeds with tighter timeouts.

## rev0011 harness refactor note

`--no-sqlite` now skips the final `metrics.summary` step instead of only disabling final harness-report ingestion. This makes large matrix runs easier to decompose when SQLite is not the thing under test and prevents the final metrics read from consuming cloudtainer budget after all build/test work has already passed. Regular `all` runs still execute the SQLite summary by default.

## rev0036 auto-parallelism cap

This cloudtainer reports a very high CPU count, which made `--jobs auto` fan out far more subprocesses than the actual time budget could justify. rev0036 caps automatic build, C++ case, scenario, and fuzz parallelism to 8 by default while preserving explicit `--jobs N` for intentional overrides. The default caps are controlled with `MTGSIM_BUILD_AUTO_JOBS` for compilation and `MTGSIM_AUTO_JOBS` for C++/scenario/fuzz subprocess runners; sanitizer still also honors `MTGSIM_SANITIZE_AUTO_JOBS` as a tighter ceiling.

The intent is not to make tests less parallel. It is to keep automatic runs bounded, budget-respecting, and predictable in containers where reported CPU count is not a good proxy for useful subprocess fan-out.

## rev0067 hard build deadline and sanitizer hotspot guard

The pre-rev0067 build budget was advisory once a compiler command had started: the helper checked elapsed time before an action but did not give `g++` a deadline. A sanitizer compile of the large validator could therefore run beyond the entire linked-revision budget. The build helper now passes the remaining deadline into every compile/link subprocess, starts each command in its own process group, and kills that group on expiry so `cc1plus` descendants cannot continue consuming the cloudtainer.

GCC sanitizer compilation of `src/validation.cpp` also defaults to `-O0 -g1` while retaining ASan/UBSan. The focused `tests/python/test_build_tool.py` check verifies both the source-specific flags and the hard timeout path. Override with `--sanitize-validation-opt-level` and `--sanitize-validation-debug-level` only when profiling compiler behavior on a larger machine.
