# Design: Harness Protocol Pilot Program (`cargo harness pilot`, `harness-pilot-pack/v0`)

## Goal
Turn the archive’s new harness-protocol idea into a ranked rollout instead of another permanently-promising testing note.

A worthy contribution here is not a flag day where every Rust testing tool rewrites itself.
It is a staged program that proves harnesses can publish **capability truth, discovery truth, and adapter truth** in ways that real consumers can adopt incrementally.

## Why this needs a pilot layer
The primary sources now point in one direction:
- Rust created a Testing Team because the testing experience spans Cargo, libtest, rustdoc, IDEs, CI, and custom frameworks.
- The libtest JSON work is already trying to push more responsibility from harnesses to runners and explicitly anticipates custom-harness opt-in.
- `cargo bench` already acknowledges custom harnesses, while `#[bench]` remains unstable.
- Doctest execution details are explicitly not guaranteed forever.

Sources:
https://rust-lang.github.io/rfcs/3455-t-test.html
https://rust-lang.github.io/rfcs/3558-libtest-json.html
https://doc.rust-lang.org/cargo/commands/cargo-bench.html
https://doc.rust-lang.org/cargo/commands/cargo-test.html
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Ranked pilot order

### Pilot 1 — libtest capability/discovery lane
Use ordinary Rust tests and benches to prove that a default harness can publish a portable capability + discovery boundary.

Must prove:
- tests and benches can be listed through one discovery report,
- locations, ignored posture, and suite/case identity are representable,
- supported selection and execution modes can be declared explicitly,
- unstable capabilities remain visibly marked as unstable.

Why first:
- it attaches directly to current upstream work,
- it avoids inventing a parallel ecosystem entry point,
- it gives later adapters something stable to target.

### Pilot 2 — nextest adapter lane
Use nextest as the first serious runner consumer.

Must prove:
- adapter lossiness can be declared honestly,
- run/binary ids can map cleanly from discovery truth,
- runner-only semantics remain explicit instead of retroactively becoming “the harness standard”,
- richer UX can be layered on top of shared discovery.

Why second:
- nextest is the clearest real-world runner substrate,
- it tests whether the protocol is useful outside Cargo’s default flow.

### Pilot 3 — custom-framework opt-in lane
Use one nightly custom framework or stable harness-style framework to prove the contract is not libtest-only.

Must prove:
- subject discovery can come from a non-libtest lane,
- the contract can represent partial capability sets,
- custom frameworks can remain distinct without being second-class.

Why third:
- this is where the protocol either becomes real ecosystem infrastructure or collapses back into libtest-specific plumbing.

### Pilot 4 — benchmark lane
Use a benchmark-oriented consumer to prove test and bench worlds can share a contract without flattening them.

Must prove:
- benchmark subjects can be discovered portably,
- declared metric families stay explicit,
- the harness layer stops short of claiming benchmark-comparison policy,
- stable ecosystem benchmarking can attach without requiring nightly `#[bench]`.

Why fourth:
- it exercises the important stable-vs-nightly seam,
- it makes the contribution relevant to more than test execution alone.

### Pilot 5 — doctest / IDE lane
Use doctest posture plus a location-aware consumer.

Must prove:
- doctest support is declared through capabilities rather than folklore,
- location-bearing subjects can be imported by tools,
- instability or changing execution details remain visible.

Why fifth:
- it is strategically valuable but more subtle than the earlier lanes,
- it tests whether the protocol stays honest at the boundary with rustdoc-specific behavior.

## Shared schema discipline
Every pilot must keep these truths separate:
1. **capability** vs **result**
2. **discovery** vs **execution**
3. **harness semantics** vs **runner semantics**
4. **bench metrics declared** vs **benchmark comparisons concluded**
5. **doctest posture** vs **docproof / hosted-doc validation**
6. **portable summary** vs **tool-native raw attachments**

## Immediate archive consequences
Read this together with:
- [`design/harness-protocol-kit.md`](./harness-protocol-kit.md)
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- [`design/test-execution-evidence-stack.md`](./test-execution-evidence-stack.md)
- [`design/perf-labs.md`](./perf-labs.md)
- [`design/docproof-kit.md`](./docproof-kit.md)

The archive should now prefer:
- **capability/discovery adapters before new runners**,
- **bench/doctest honesty before fake universal test stories**,
- and **shared contracts before UI-only wrapper work**.
