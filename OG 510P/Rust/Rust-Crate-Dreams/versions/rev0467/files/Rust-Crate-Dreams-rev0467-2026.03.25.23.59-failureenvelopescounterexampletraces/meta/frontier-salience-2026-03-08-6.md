# Frontier salience scan — 2026-03-08 (sixth pass)

## Main judgment

This pass deliberately did **not** add another top-level proposal.

Instead, it argues that the archive’s next worthwhile frontier to sharpen is a **native build / build-script support stack**:

1. **P-0046 buildscript-ux-kit**
2. **P-0059 buildscript-testkit**
3. **P-0058 native-deps-kit**

## Why this frontier rose now

- The 2025 State of Rust survey still says resource usage (including slow compile times and storage usage) remains one of the important productivity problems.
- Cargo’s official docs still describe broad conservative build-script rerun behavior when authors do not narrow change detection.
- Cargo’s official FAQ still says after-the-fact rebuild diagnosis is not easy and mostly requires reading verbose fingerprint logs.
- Cargo 1.84 added `cargo::error`, but live Cargo issues show build-script failures are still often presented too noisily.
- `system-deps` and `vcpkg` prove that the ecosystem already has real native-dependency substrate, but not yet one boring cross-platform contract.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the strongest immediate incubation target because daily build pain plus per-run artifact value remain unusually clear.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still one of the highest-leverage explainability crates and closely coupled to P-0469.
3. **P-0486 Debuggability Support Contract Kit**
   - Still the strongest non-Cargo stack center because it turns real debugger substrate into a release/support artifact.
4. **P-0046 buildscript-ux-kit**
   - Rose sharply because the gap is concrete, current, horizontal, and still not solved upstream: users still need a concise, typed build-script failure/report layer.
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Remains very strong, but a little more boundary-sensitive than P-0046 and P-0486.
6. **P-0059 buildscript-testkit**
   - Strong because copied and rarely tested `build.rs` logic remains a recurring source of fragile native-build failures.
7. **P-0058 native-deps-kit**
   - Potentially epic, but broader and riskier; best incubated after the report and fixture layers above it are sharper.
8. **P-0493 Source Path Hygiene & Debug Source Kit**
   - Still real, but slightly narrower than the broad buildscript/native-support and debug-support centers above it.
9. **P-0491 Debugger Visualizer Compatibility Kit**
   - Still useful, but intentionally narrower than the broader support/posture layers above it.

## Why P-0046 is the right way to sharpen this frontier

The archive should resist two bad framings here:

- “build scripts are just bad, replace them wholesale”, and
- “`cargo::error` exists now, so the UX problem is solved.”

P-0046 is stronger because it provides something maintainers can ship to other people **now**:

- one concise summary of what failed,
- one typed report for tools and CI,
- one policy gate for workspace maintainers,
- and one support artifact that reduces screenshot-driven debugging.

That is easier to scope, easier to adopt, and a better foundation for P-0059 and P-0058.

## What should happen next

The best next native-build-oriented passes should prefer:

1. fixture/schema stubs for P-0046, P-0059, and P-0058,
2. shared report/receipt vocabulary across the three proposals,
3. proposal-file upgrades clarifying what each crate provides other people,
4. and evidence refreshes when Cargo’s build-script or build-analysis surfaces change.

They should **not** immediately add another buildscript/native-deps proposal unless the seam is clearly different from:

- build-script report/policy UX,
- hermetic build-script testing,
- or declarative native dependency contracts.

## Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ: https://doc.rust-lang.org/cargo/faq.html
- Cargo unstable warnings config: https://doc.rust-lang.org/cargo/reference/unstable.html#warnings
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- `system-deps` docs: https://docs.rs/system-deps/latest/system_deps/
- `vcpkg` docs: https://docs.rs/vcpkg/latest/vcpkg/
- Cargo issue #10159: https://github.com/rust-lang/cargo/issues/10159
- Cargo issue #15792: https://github.com/rust-lang/cargo/issues/15792
- Rust project goal: sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
