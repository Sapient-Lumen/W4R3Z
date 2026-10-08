# Frontier salience scan — 2026-03-08 (fifth pass)

## Main judgment

This pass deliberately did **not** add another top-level proposal.

Instead, it argues that the archive’s next strong non-Cargo frontier to sharpen is a **debug support stack**:

1. **P-0486 Debuggability Support Contract Kit**
2. **P-0493 Source Path Hygiene & Debug Source Kit**
3. **P-0491 Debugger Visualizer Compatibility Kit**

## Why this frontier rose again

- The 2025 State of Rust survey still leaves debugging as a major productivity pain.
- The new Rust debugging survey 2026 shows the project still explicitly cares about debugger support quality, visualizers, async debugging, and evaluator ergonomics.
- Rust’s substrate is now richer than a vague “we need better debuggers” framing: Cargo profiles, rustc path remapping, debugger visualizers, and rustup component management all already exist.
- That makes the sharper gap a **support/review artifact layer** rather than a fresh debugger implementation wish list.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the best immediate incubation target because the pain is daily, the fixtures are obvious, and the per-run artifact story is easy to explain.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still extremely strategic because feature/version/duplicate-build causes remain under-explained, but it benefits from vocabulary sharing with P-0469.
3. **P-0486 Debuggability Support Contract Kit**
   - Rose because current Rust debugging substrate is strong enough that a support-posture / symbol-layout / diff receipt now looks like a genuinely buildable crate rather than an essay topic.
4. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Still very strong, but remains a little more workflow-boundary-sensitive than P-0469 and P-0486.
5. **P-0493 Source Path Hygiene & Debug Source Kit**
   - Stronger than before because path trimming/remapping and source-component lookup now clearly form their own support seam.
6. **P-0491 Debugger Visualizer Compatibility Kit**
   - Real and useful, but still narrower than the broader support-contract and source-lookup layers above it.

## Why P-0486 is the right way to sharpen debugging

The archive should resist “invent a better debugger” framing here.

P-0486 is stronger because:

- it provides something maintainers can actually ship to other people,
- it helps release review and support triage immediately,
- and it can define receipt vocabulary reused by the narrower P-0493 and P-0491 proposals.

## What should happen next

The best next debugging-oriented passes should prefer:

1. fixture/schema stubs for P-0486 and P-0493,
2. incubation-order notes that keep the three proposals distinct,
3. and evidence refreshes when Cargo/rustc path/debug surfaces change.

They should **not** immediately add another debugger-adjacent proposal unless the missing seam is clearly different from:

- broad debuggability support posture,
- source-path and source-component lookup,
- or embedded visualizer compatibility.

## Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo profiles: https://doc.rust-lang.org/cargo/reference/profiles.html
- Rust reference: debugger visualizers: https://doc.rust-lang.org/reference/attributes/debugger.html
- `rustc` remap-source-paths: https://doc.rust-lang.org/rustc/remap-source-paths.html
- rustup components: https://rust-lang.github.io/rustup/concepts/components.html
