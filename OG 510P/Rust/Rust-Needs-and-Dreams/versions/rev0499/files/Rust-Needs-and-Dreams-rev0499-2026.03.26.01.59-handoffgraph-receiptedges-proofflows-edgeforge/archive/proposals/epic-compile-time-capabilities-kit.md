# Epic proposal: Compile-Time Capabilities Kit

## Thesis
One of the highest-leverage ecosystem contributions Rust could make now is a **shared authority substrate for compile-time code execution**.

Not just a sandbox. Not just a proc-macro experiment. Not just a build-script linter.

A real artifact family that can say, in a reviewable and machine-consumable way:
- what compile-time units exist,
- what lane each one runs in,
- what authority each one declares,
- what it actually touched,
- what its real input surface is,
- whether it is deterministic enough for stronger caching or reproducible-build workflows,
- and what was waived, overridden, or replaced by metadata.

## Why now
The ecosystem signals are converging:
- Rust’s sandboxed-build-scripts goal explicitly wants per-crate permissions, one future interface across build scripts and proc-macros, and possible remote-execution / hermetic-build benefits.
- The compiler-team is actively exploring WebAssembly proc-macros because the current native dynamic-library model has reproducibility and security hazards.
- The Rust Reference already states that proc-macros have the same security concerns as build scripts.
- Cargo already contains the seed of a “no execution” lane via `links` build-script overrides.
- Language work is trying to reduce dependence on proc-macros altogether by expanding what declarative macros can do.
- Build-performance and user-wide-cache work both benefit directly from knowing when compile-time execution is deterministic and portable.

In other words: the missing piece is no longer the motivation. It is the **reviewable integration layer**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://github.com/rust-lang/compiler-team/issues/876
- https://doc.rust-lang.org/reference/procedural-macros.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

## What should be built
A serious first version should ship:
1. canonical schemas for:
   - `ct-unit-manifest/v0`
   - `ct-execution-lane/v0`
   - `ct-capability-profile/v0`
   - `ct-input-surface/v0`
   - `ct-observation-report/v0`
   - `ct-determinism-report/v0`
   - `ct-diff-report/v0`
   - `ct-policy/v0`
   - `ct-waiver/v0`
   - `ct-profile-catalog/v0`
   - `ct-profile-fit-report/v0`
   - `ct-pack/v0`
2. a reference `cargo ct` implementation with:
   - inventory,
   - planning,
   - checking,
   - diffing,
   - built-in profile catalogs / profile-fit reports,
   - policy evaluation,
   - pack / verify flows
3. multiple execution backends / adapters:
   - ambient/native observation lane,
   - external sandbox wrapper lane,
   - wasm proc-macro lane when available,
   - metadata-override lane for `links` crates
4. baseline policies:
   - deny network by default,
   - narrow env by default,
   - distinct posture for build scripts vs proc-macros,
   - explicit waiver model
5. imports and integrations for:
   - Trust Signals,
   - Policy Kit,
   - Build Cache Kit,
   - Repro Build Kit,
   - Native Dependency Kit,
   - Macro Workflow Kit

## Initial pilots
- **Proc-macro-heavy app workspace** that wants reviewable authority and better build-repeatability.
- **`-sys` lane** that proves native probing can be represented without pretending it is the same as ordinary codegen.
- **Strict enterprise CI lane** that starts with deny-network / narrow-env defaults plus waivers.
- **Metadata override pilot** demonstrating that replacing some `links` scripts entirely is a first-class success mode, not a special case.
- **Profile ladder pilot** proving that observe → declare → narrow → sandbox / replace is a better adoption story than one all-or-nothing sandbox ask.

## Milestones
### Milestone 1: Inventory and language
- publish schemas for unit, lane, capability, and policy artifacts
- make host/target truth and override/no-run lanes explicit from day one

### Milestone 2: Observability and determinism
- emit observation and determinism reports from real builds
- record unsupported blind spots honestly
- diff drift across revisions

### Milestone 3: Policy and waivers
- support CI gating on stable reason codes
- support explicit waiver lifecycles
- support compile-time posture summaries for trust / review tooling

### Milestone 4: Broader execution lanes
- support richer sandbox backends
- plug in wasm proc-macro lanes where available
- prove that cache/repro tooling can consume determinism outputs

## Success metrics
- Teams can answer “what compile-time code ran?” without custom scripts.
- Compile-time authority drift becomes diffable in code review.
- Proc-macro and build-script policy becomes explainable instead of folkloric.
- More crates can move from ambient-native execution toward named higher profiles instead of vague aspirations.
- Cache and reproducibility work can consume explicit determinism facts instead of coarse heuristics.
- Compile-time execution stops being treated as one monolithic blob of trust.

## Archive fit
This proposal strengthens several already-important threads:
- **Policy Kit** consumes authority and waiver results.
- **Trust Signals Kit** gains a clearer compile-time evidence class.
- **Build Cache Kit** gains explicit idempotence and input-surface facts.
- **Repro Build Kit** gains upstream evidence about nondeterministic compile-time behavior.
- **Macro Workflow Kit** can stay focused on debugging, cost, and migration rather than permissions.
- **Build Extension Kit** can keep reducing the need for arbitrary execution.
- **Native Dependency Kit** gets a better story for which probes are necessary, declared, replaceable, or waivable.

That is why this could be an epic contribution: it does not just solve one tool. It gives the ecosystem a common way to reason about one of Rust’s most awkward and important authority surfaces.

The next execution refinement should now be a profile ladder as captured in [`design/compile-time-profile-ladder.md`](../design/compile-time-profile-ladder.md), so teams can target named compile-time postures instead of improvising their own maturity language.

## Relationship to the Compile-Time Surface stack
This proposal is now best understood as the **authority pillar** of the broader compile-time stack described in [`design/compile-time-surface-pilot-program.md`](../design/compile-time-surface-pilot-program.md).
That stack also needs structured replacement lanes (Build Extension), workflow/migration lanes (Macro Workflow), and lightweight share/repro lanes (ScriptKit). The epic value here is strongest when those layers stay distinct but composable.
