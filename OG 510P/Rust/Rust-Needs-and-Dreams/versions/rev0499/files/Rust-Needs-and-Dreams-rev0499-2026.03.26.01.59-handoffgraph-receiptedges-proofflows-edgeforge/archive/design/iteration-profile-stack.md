# Design: Iteration Profile Stack (Build-State Evidence + Debugger Experience + Workspace Environment)

## Goal
Treat **iteration profiles** as a first-class ecosystem seam.

Rust does not just need more “speed up your build” tips, one more dotfile preset, or a hidden IDE assistant that toggles knobs behind the curtain.
It needs a reviewable way to say:
- **which local workflow** we are optimizing (`fast-check`, `edit-run`, `step-debug`, `async-debug`, `CI-parity`, etc.),
- **which evidence** justified that choice,
- **which concrete settings and tool behaviors** were changed,
- **which debugging / fidelity / concurrency properties** were preserved or traded away,
- and **which downstream consumers** (editor, CI, bootstrap, support, assistant) may import that profile honestly.

The missing contribution is therefore **not** another build-speed blog post, universal dev profile, hot-reload daemon, or rust-analyzer tuning gist.
It is a thin `cargo iterprofile` / `iter-profile-pack/v0` layer that keeps **intent, evidence, realization, and observed consequences** separate.

## Why this seam matters now
Official Rust/Cargo signals are unusually aligned here:
- Rust’s March 20, 2026 challenges post says compile times are a universal productivity tax and explicitly says that anything reducing iteration time — including hot reloading and faster linking — has outsized leverage on development velocity.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 compiler-performance survey says the default `dev` profile’s full debuginfo increases disk usage and slows compilation/linking, reports benchmark wins from reducing debuginfo, says many developers are unaware of easy performance knobs, and says the Cargo team is considering a lower-debuginfo default plus a built-in debugging profile.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo’s profiles docs make the underlying tradeoff surface explicit: built-in and custom profiles, config-file overrides, `debug = "line-tables-only"|"limited"|"full"`, and `split-debuginfo` are already real supported levers rather than folklore.
  https://doc.rust-lang.org/cargo/reference/profiles.html
- The Cargo build-analysis goal is explicitly about recording rebuild reasons, CLI flags, profiles, environment variables, and run identifiers so developers and external tools can analyze build behavior over time.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Cargo build-dir-layout goal says the status quo still locks the whole build cache and that the intended future includes smaller units, reduced Cargo / rust-analyzer contention, a user-wide cache, and plugin-based cache exchange.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The March 13, 2026 call for testing build-dir layout v2 says many tools and processes still rely on unspecified build-dir details because features are missing, which is strong evidence that profile realization should be reviewable above Cargo internals rather than hidden in scripts.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo 1.94 says target-dir locking still has tricky cases, that `cargo report rebuild` / `cargo report sessions` are becoming more real, and that Cargo cannot be everything to everyone so plugins matter.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer’s configuration docs now make one especially telling workaround explicit: `rust-analyzer.cargo.targetDir` avoids lock contention by using a rust-analyzer-specific target directory, but does so at the cost of duplicated build artifacts.
  https://rust-analyzer.github.io/book/configuration.html
- The 2026 debugging survey says Rust debugging quality still varies materially by debugger family and operating system, that async debugging is not yet first-class, and that debugger support remains an active improvement area.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

Taken together, the ecosystem now has better **diagnostic evidence** and more **real tuning knobs**, but still lacks a portable way to publish and review the chosen **iteration tradeoff profile** itself.

## What each substrate owns
### Build-State Evidence Stack
[`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md) owns:
- rebuild reasons,
- timing history,
- cache/reuse/duplication facts,
- lock/contention evidence,
- workflow-aware diagnosis.

Its question is:
> what actually happened in the build loop, and what evidence explains it?

### Debugger Experience / Debuggability
[`design/debugger-experience-kit.md`](./debugger-experience-kit.md) and [`design/debuggability-stack.md`](./debuggability-stack.md) own:
- debugger family/version/OS capability,
- visualizer support,
- async-debug posture,
- stepping / expression / inspection reality.

Their question is:
> what debugging experience is genuinely available for this toolchain/runtime/OS tuple?

### Workspace Environment Stack
[`design/workspace-environment-stack.md`](./workspace-environment-stack.md) owns:
- actual realization in manifests/config,
- rustup / toolchain / linker / env posture,
- editor and workspace command realization,
- credentials/native/runtime/tooling handoff.

Its question is:
> how is this profile actually realized on a developer machine, in an editor, or in CI?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. Which workflow is being optimized?
2. Which evidence justified the chosen profile?
3. Which concrete settings changed?
4. Which debug or fidelity capabilities were preserved, reduced, or intentionally split into another profile?
5. Which artifact duplication, contention, or CI drift consequences were accepted?
6. Which consumers are allowed to import the profile as a default?

If the stack cannot answer those six questions, it is still just advice.

## Suggested profile families
The archive should prefer **named, reviewable profile families** over one universal “fast dev” setting:

### A. `fast-check`
Optimize for rapid diagnostics and code navigation.
Typical levers may include:
- lower debuginfo,
- rust-analyzer-specific target dir or command overrides when justified,
- build-analysis opt-in,
- strong visibility into lock/contention tradeoffs.

### B. `edit-run`
Optimize for quick compile-and-run loops where debugger stepping is secondary.
Typical levers may include:
- lower debuginfo,
- faster linker,
- explicit run-focused command/profile selection,
- preserved backtrace posture.

### C. `step-debug`
Optimize for interactive debugger use.
Typical levers may include:
- full or richer debuginfo,
- split-debuginfo choice,
- explicit debugger-family support notes,
- willingness to accept slower compile/link loops.

### D. `async-debug`
A stricter version of `step-debug` that admits the extra runtime/debugger limitations around async inspection and should carry tuple-specific caveats rather than pretending the experience is equivalent.

### E. `ci-parity`
Optimize for keeping local developer loops close enough to CI/release conditions to avoid false confidence, while still staying distinct from release builds.

These are **review classes**, not a demand that Cargo upstream or every editor expose the same five profile names.

## Recommended execution posture
The next credible shared move is a ranked pilot sequence:
1. **fast-check lane** — prove the archive can express debuginfo / target-dir / check-command tradeoffs without hiding the costs.
2. **step-debug lane** — prove debugger requirements can stay explicit instead of silently riding on the default dev profile.
3. **edit-run lane** — prove linker and run-oriented tradeoffs can be attached to a named workflow.
4. **async-debug lane** — prove runtime/debugger caveats remain visible instead of being smoothed over.
5. **CI/bootstrap/support imports** — only after the local profiles are honest should they become starter/workenv/default/support artifacts.

That order matters.
The archive should not jump straight to one magical local-platform product.

## Design principles
1. **Workflow intent comes first.** A profile without an explicit goal is just knob cargo-culting.
2. **Diagnosis is not the profile.** Build Doctor may recommend; the chosen profile must still be reviewable as a separate artifact.
3. **Debug posture stays explicit.** Lower debuginfo, different split-debuginfo, or async-debug caveats must remain visible.
4. **Editor isolation is not free.** Avoiding contention by splitting target dirs is a real tradeoff, not a silent improvement.
5. **Local and CI defaults stay distinct until proven otherwise.** A productive local profile is not automatically the right bootstrap or support default.
6. **Profile realization must be reproducible.** Cargo profiles, config overrides, linker/env assumptions, rust-analyzer overrides, and toolchain dependencies must be attachable.
7. **Observed outcomes matter.** A proposed profile with no before/after observation is still speculation.

## What an epic contribution would look like in practice
A serious contribution here would publish a small family of linked artifacts such as:
- `iteration-intent/v0` — workflow family, priorities, preserved properties, accepted tradeoffs
- `iteration-profile/v0` — concrete config/profile/editor/linker/target-dir realization
- `iteration-profile-basis/v0` — imports from build-state evidence, debugger tuples, and workspace environment facts
- `iteration-profile-observation/v0` — before/after timings, rebuild-scope, lock-contention, disk-use, and debugging-viability observations

That contribution should:
- consume Cargo-native evidence instead of scraping logs,
- keep debuginfo/linker/target-dir/check-command choices visible,
- make debugger viability a first-class import,
- and let starter/bootstrap/workenv/support layers import a profile without pretending it is Cargo’s universal truth.

## Anti-goals
Do not turn this stack into:
- one universal fast-dev profile,
- one hidden assistant tuning layer,
- one new build daemon,
- one replacement for Cargo or rust-analyzer,
- or another performance-tips document that loses the exact chosen settings.

The stack is a **review boundary for iteration tradeoffs**, not a new local platform.
