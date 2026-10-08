# Design: Test Execution Pilot Program (`cargo testrun pilot`, `test-exec-pack/v0`)

## Goal
Make the archive’s testing work executable as a **ranked rollout plan** instead of a loose group of good ideas.

A worthy contribution here is not another runner, another dashboard, or another XML converter.
It is a staged program that proves Rust can share **test inventory truth, execution truth, config truth, runner-recording imports, and attachment truth** across increasingly specialized lanes.

## Why this needs its own design layer
The archive already had useful testing kits, but it still lacked a concrete execution order.
Current signals make that omission more serious:
- Rust’s 2026 roadmap now explicitly says **better test tooling** matters;
- upstream still wants a real default-harness programmatic-output path, not only prettier CLI text;
- `cargo test` still mixes libtest, doctests, and custom harness posture;
- nextest already exposes serious runner semantics plus persistent recordings;
- benchmark and doctest lanes are still part of the same composition problem;
- Cargo/external-tools boundaries still mean one JSON stream is not enough to describe the whole testing reality.

Sources:  
https://rust-lang.github.io/rust-project-goals/2026/flagships.html  
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html  
https://doc.rust-lang.org/cargo/commands/cargo-test.html  
https://doc.rust-lang.org/rustc/tests/index.html  
https://nexte.st/docs/design/architecture/recording-runs/  
https://doc.rust-lang.org/cargo/reference/external-tools.html

## Ranked pilot order

### Pilot 1 — Harness protocol lane
Use the default Rust harness surface to prove that capability/discovery reports can exist independently from final run results.

Must prove:
- tests, benches, and basic suite/case identity can be discovered portably;
- locations, markers, ignored posture, and instability can be declared explicitly;
- runners can import harness truth instead of scraping console conventions;
- custom-harness growth is not blocked by assuming libtest is the whole world.

Why first:
- it answers the upstream pressure directly;
- it gives later execution/result pilots a cleaner boundary;
- it prevents run packs from becoming an accidental mega-schema.

### Pilot 2 — Default-harness / nextest run-truth lane
Use ordinary Rust tests and prove that libtest-oriented and nextest-oriented runs can share one portable result boundary.

Must prove:
- stable subject, binary, and test ids can survive both discovery and execution;
- run profiles can preserve runner semantics without flattening them;
- JUnit, libtest-like JSON, and runner-native recordings can attach without becoming the only source of truth;
- flake/infra/retry notes remain visible.

Why second:
- it matches the strongest execution-facing upstream signal;
- it gives the stack a broadly adoptable starting point after capability/discovery truth;
- it avoids starting with niche assurance lanes.

### Pilot 3 — Config-bound CI lane
Run the same subject across a bounded set of feature/cfg/target/profile selections.

Must prove:
- `config-pack/v0` ids can attach cleanly to run reports;
- skipped or unprovisioned configs stay explicit;
- CI/review can compare run outcomes by config id instead of by job-name folklore;
- imported or detected configuration stays reviewable rather than hidden in runner storage.

Why third:
- it turns local test truth into CI truth;
- it gives coverage/fuzz/sanitizer consumers a stable base.

### Pilot 4 — Coverage + Miri attachment lane
Attach coverage and Miri results to shared test execution identity.

Must prove:
- coverage exports can attach without redefining the subject or runner;
- Miri lanes can declare the semantic tradeoff of process-per-test execution explicitly;
- attachment reports preserve what a passing lane does **not** prove;
- one PR/release can carry both execution truth and specialized evidence cleanly.

Why fourth:
- it proves the stack can support quality/assurance consumers without flattening them;
- it tests the archive’s claim that execution and specialized evidence must remain distinct.

### Pilot 5 — Replay / fuzz / mutation consumer lane
Attach at least one replay, fuzz, or mutation consumer to a shared run subject.

Must prove:
- specialized tools can publish their own artifacts while reusing shared run identity;
- failures and generated inputs can point back to a specific execution/config subject;
- tool-specific instability or incompleteness remains explicit;
- the stack does not collapse into “all testing is the same”.

Why fifth:
- it shows whether the substrate is genuinely extensible;
- it makes the archive’s broader testing map more credible.

### Pilot 6 — Downstream / device-lab lane
Use either reverse-dependency testing or hardware-backed runs as a harder consumer.

Must prove:
- cross-project and/or hardware-specific identities can still attach to the same culture of run evidence;
- infra failures remain distinguishable from subject failures;
- release/policy/support consumers can inspect one attached pack rather than many CI logs;
- the stack is useful beyond one repo’s unit tests.

Why sixth:
- it is strategically important, but heavier than the first five pilots;
- it proves the design can travel to ecosystem-scale and hardware-backed contexts.

## Shared schema discipline
Every pilot must keep these truths separate:
1. **harness capability/discovery** vs **execution/result truth**
2. **inventory** vs **execution**
3. **portable run reports** vs **runner-native recordings**
4. **runner semantics** vs **specialized evidence semantics**
5. **config identity** vs **result outcome**
6. **flake observation** vs **final policy verdict**
7. **portable summary** vs **large raw attachments**
8. **subject failure** vs **infra failure**

## Immediate archive consequences
Read this together with:
- [`design/harness-protocol-kit.md`](./harness-protocol-kit.md)
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- [`design/test-execution-evidence-stack.md`](./test-execution-evidence-stack.md)
- [`design/config-set-kit.md`](./config-set-kit.md)
- [`design/coverage-evidence-kit.md`](./coverage-evidence-kit.md)
- [`design/fuzzpack-kit.md`](./fuzzpack-kit.md)
- [`design/replay-kit.md`](./replay-kit.md)
- [`design/downstream-testing-kit.md`](./downstream-testing-kit.md)
- [`design/device-lab-kit.md`](./device-lab-kit.md)

The archive should now prefer:
- **harness/run-truth adapters before new runners**,
- **runner-recording imports before fake universal raw formats**,
- **config-bound evidence before giant CI dashboards**,
- and **specialized attachments that reuse shared ids** rather than redefining test identity locally.

## What should wait
Do **not** start with:
- a hosted universal Rust test dashboard,
- a fake cross-runner score or “quality index”,
- a demand that every testing tool emit the same raw format,
- or a new canonical runner meant to displace libtest and nextest at once.

Those may become consumers later.
They are not the core missing substrate.
