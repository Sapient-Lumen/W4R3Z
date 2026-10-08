# Gap: Machine-readable test execution truth and reviewable run artifacts

## Summary
Rust has strong testing tools, but their outputs still do not compose cleanly.
The ecosystem now has:
- the default `cargo test` / libtest lane,
- an upstream push to finish machine-readable libtest JSON,
- `cargo-nextest` with JSON/JUnit/run-id surfaces,
- coverage tools that already emit JSON/LCOV/Cobertura,
- dynamic-analysis lanes like Miri-in-nextest,
- and downstream tools like mutation testing that already write structured result directories.

What is still missing is a shared, reviewable **test execution boundary** that keeps these truths separate instead of flattening them into one fake “test status” blob.

## What is missing
Rust still lacks one portable artifact family that can answer all of the following cleanly:
1. **What was the test subject?** Workspace/package/binary/test identity, with stable ids.
2. **What runner semantics applied?** libtest, nextest, custom harness, process-per-test, setup scripts, Miri lane, etc.
3. **What configuration was exercised?** Features/cfgs/targets/profiles/toolchains.
4. **What actually happened?** Pass/fail/skip/timeout/cancel, durations, exit reasons, per-test outputs, and attached logs.
5. **What specialized evidence attaches to the run?** Coverage, sanitizer output, replay packs, device-lab reports, mutation results, downstream-failure evidence.
6. **Was the result stable enough to trust?** Flake observations, reruns, and reason-coded infra versus subject failures.
7. **How should other consumers import it?** CI, release, policy, coverage, fuzzing, replay, and downstream tools should not all invent different unspoken subject ids.

Today those answers are scattered across unstable harness output, runner-specific JSON/JUnit, CI conventions, `mutants.out`, and local scripts.

## Ecosystem signals
- The **libtest JSON** goal says libtest is the default harness used by Cargo, that people had come to rely on programmatic output, and that Cargo could use it to support parallel execution, summary reporting, better messaging, and stronger custom-runner experiments like `cargo nextest` and `libtest-mimic`:  
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94 still lists **Finish the libtest json output experiment** among the active areas needing owners, which means the seam is still live rather than settled:  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- nextest’s docs explicitly provide machine-readable test lists, binary lists, JUnit output, experimental libtest-like JSON output for test runs, run ids, and binary ids. They also say they want more human-facing UI to become machine-readable over time:  
  https://nexte.st/docs/machine-readable/  
  https://nexte.st/docs/glossary/
- nextest’s Miri integration proves execution semantics matter: per-test processes can make Miri runs 3–4× faster, but they also lose visibility into races between tests sharing resources. That means runner semantics must remain part of the contract, not a hidden implementation detail:  
  https://nexte.st/docs/integrations/miri/
- `cargo-llvm-cov` already exports JSON/LCOV/Cobertura/Codecov/text/HTML and can run tests or reuse prior runs to emit different formats, which means coverage is already an attachable consumer lane rather than something that needs to own test identity itself:  
  https://docs.rs/crate/cargo-llvm-cov/latest/source/README.md
- `cargo-mutants` already writes `mutants.json`, `outcomes.json`, log files, and diff files, and documents that these are read by other programs while the run is in progress. That is a strong sign that specialized testing tools want a portable execution substrate, not just prettier console output:  
  https://mutants.rs/mutants-out.html  
  https://mutants.rs/list.html

## What “good” looks like
A worthy ecosystem contribution here would provide:
- a canonical inventory of test binaries, tests, and execution lanes;
- explicit runner and harness semantics instead of assuming `cargo test` behavior everywhere;
- result reports with stable ids, reason codes, and attachment slots;
- flake/rerun/infra posture that can be reviewed rather than guessed from CI retries;
- clear import boundaries for coverage, replay, fuzzing, device-lab, and downstream consumers;
- diffable packs and waivers that CI, release, and policy tools can consume.

The right contribution is **not** just another runner.
It is a shared **test execution evidence boundary** for the whole ecosystem.
