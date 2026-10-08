# Design: Proc-Macro Exit Stack 2026Q1 (`cargo macro-exit`, `macro-exit-pack/v0`)

## Goal
Promote a first-class Rust ecosystem frontier for **reducing unnecessary proc-macro burden without pretending proc macros are going away**.

The worthy contribution here is **not**:
- a replacement macro system,
- a “ban proc macros” campaign,
- an auto-transpiler from proc macros to `macro_rules!`,
- or a universal reflection trait.

It is the missing reviewable layer that says:

**which proc-macro burden exists today, what it costs to build and review, which lanes can realistically stay proc-macro-based, which lanes are becoming plausible declarative-macro candidates, which lanes may be better served by reflection/comptime, and what downstream maintainers may honestly plan or defer.**

Read this together with:
- [`design/macro-workflow-kit.md`](./macro-workflow-kit.md)
- [`gaps/macro-workflows-and-proc-macro-migration.md`](../gaps/macro-workflows-and-proc-macro-migration.md)
- [`gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`](../gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md)
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md)
- [`proposals/epic-proc-macro-exit-stack.md`](../proposals/epic-proc-macro-exit-stack.md)
- [`design/epic-contribution-ladder-2026.md`](./epic-contribution-ladder-2026.md)

## Why this seam matters now
Fresh official signals now line up around a real ecosystem opportunity rather than a speculative wishlist.

- The accepted macro-improvements goal explicitly aims to make `macro_rules!` cover many use cases that currently require proc macros, with the stated benefits of faster builds, simpler macros, and reduced dependency supply chains.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The reflection-and-comptime goal explicitly says proc-macro derives have historically been hard to debug and bootstrap, and positions reflection as a distinct path for some of the same problem families.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The 2026 flagship themes now place **prototype reflection** inside **Constify all the things**, which means reflection is no longer a purely userland curiosity.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025 compiler-performance survey says stabilizing language features could remove some build scripts or proc macros, and it calls out derive-proc-macro expansion as a place where incremental rebuild behavior is still not ideal.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Clippy/linting optimization goal still calls out proc-macro and expansion checking as active performance work, which means proc-macro burden is not only social or stylistic — it is part of the current tool-performance surface.
  https://rust-lang.github.io/rust-project-goals/2024h2/optimize-clippy.html
- Cargo and Cargo’s release/changelog docs now expose a little more proc-macro inventory surface (`cargo tree` marking proc-macro packages and `-e no-proc-macro`), but inventory is still not a workflow.
  https://doc.rust-lang.org/beta/releases.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- The Rust Reference still says proc macros run during compilation with the compiler’s available resources and therefore share Cargo build-script-like security concerns.
  https://doc.rust-lang.org/reference/procedural-macros.html

Taken together, those signals say Rust is opening multiple credible **proc-macro exit paths**:
- better declarative macros,
- more language support that erases workaround crates,
- reflection/comptime for some derive-heavy lanes,
- and better inventory/performance understanding for the proc macros that remain.

What Rust still lacks is the **reviewable transition layer above those paths**.

## What changed in the archive’s understanding
The archive already had two real ingredients:
- a solid **Macro Workflow Kit** for inventory / expansion / cost / debug / migration hints;
- and a solid **Reflection Transition** gap note for comparing proc-macro-heavy lanes with runtime reflection, visit-only inspection, schema tracing, and future compile-time reflection.

What it did **not** yet have was a clear statement that those notes now compose into a frontier with its own buildable shape.

The new reading is:
- [`design/macro-workflow-kit.md`](./macro-workflow-kit.md) owns today’s inventory, expansion, cost, and debugging truth;
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md) owns execution-authority and sandboxing posture;
- [`gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md`](../gaps/reflection-transition-lane-comparison-macro-burden-and-core-reflection-migration.md) names the cross-lane migration problem;
- **Proc-Macro Exit Stack** is the thin composition layer that keeps those truths separate while making transition plans reviewable.

## The missing distinction
A worthy contribution here must keep at least five truths explicit.

### 1) Proc-macro burden truth
- proc-macro crate identity
- macro kind (`derive`, `attribute`, `function_like`)
- direct vs transitive use
- dependency-weight posture (`syn`, `quote`, `proc-macro2`, etc.)
- expansion/cost/debug burden
- “must stay proc macro” versus “candidate for reduction” posture

### 2) Execution-authority truth
- compile-time execution surface
- file/network/process authority posture
- sandbox/capability posture
- declared versus ambient behavior
- review and risk imports

### 3) Transition-target truth
- declarative-macro candidate
- language-feature replacement candidate
- reflection/comptime candidate
- runtime reflection candidate
- visit-only / schema-tracing candidate
- “stay proc macro” candidate

### 4) Migration-confidence truth
- blocker list
- expected benefit class
- confidence level
- horizon (`now`, `watch`, `blocked on language/tooling`, `not recommended`)
- explicit forbidden conclusions

### 5) Consumer-handoff truth
- maintainer planning summary
- build/perf summary
- supply-chain/review summary
- docs/education summary
- assistant/editor summary

## What a worthy contribution would look like in theory and practice
In theory, the right contribution is a **thin transition contract**:
- narrow enough to stay honest,
- structured enough to survive CI, design review, release planning, and assistant consumption,
- and modest enough to avoid becoming the one true macro platform.

In practice, the worthy contribution looks like:
- a reference companion CLI, `cargo macro-exit`;
- one attachable bundle family, `macro-exit-pack/v0`;
- imports from Macro Workflow and Compile-Time Capabilities instead of schema imperialism;
- explicit target lanes for declarative, language-feature, reflection/comptime, or stay-proc-macro outcomes;
- and bounded renderers for build/perf, support/review, docs/teaching, and maintenance planning.

The MVP should be able to answer:
- which proc-macro burden exists in this crate/workspace today,
- which parts are direct versus transitive,
- which macro lanes are expensive or operationally awkward,
- which ones look plausibly reducible and why,
- which ones are blocked on language/tooling evolution,
- and what a maintainer may honestly plan now versus merely watch.

That is already a major ecosystem improvement over today’s combination of `cargo tree`, `cargo expand`, issue threads, release notes, and maintainer folklore.

## Proposed artifact family
### `macro-exit-subject/v0`
Identity of the crate/workspace/product and the specific macro burden under review.

### `macro-exit-imports/v0`
Pointers to imported:
- `macro-inventory/v0`
- `macro-cost-report/v0`
- `macro-debug-report/v0`
- compile-time capability/sandbox imports
- optional build-state or compatibility imports

### `macro-exit-targets/v0`
Named candidate targets for each burden slice:
- `stay-proc-macro`
- `declarative-macro`
- `language-feature`
- `reflection-comptime`
- `runtime-reflection`
- `visit-only`
- `schema-tracing`

### `macro-exit-plan/v0`
Why the proposed target is credible, what blockers exist, what benefit class is expected, and what evidence is still missing.

### `macro-exit-diff/v0`
What changed between two revisions:
- new proc-macro burden
- reduced burden
- reclassified target
- higher/lower confidence
- newly blocked/unblocked migration

### `macro-exit-pack/v0`
Bundle containing the above plus raw attachments from the Macro Workflow Kit.

## Ranked execution order
### 1) Inventory and burden lane
Prove:
- one real workspace can export a reviewable proc-macro inventory,
- distinguish direct from transitive burden,
- and surface heavyweight or awkward macro families without pretending all proc macros are bad.

### 2) Cost/debug lane
Prove:
- one real workspace can attach macro-cost and macro-debug evidence,
- and connect it to build/perf reasoning without flattening it into one “slow build” score.

### 3) Transition-target lane
Prove:
- one real subject can publish candidate target classes (`stay`, `declarative`, `language`, `reflection`, etc.),
- and explain blockers honestly.

### 4) Maintainer planning lane
Prove:
- one release-planning or roadmap consumer can import macro-exit evidence,
- and tell what is “migrate now”, “watch”, and “don’t touch”.

### 5) Security/review lane
Prove:
- one dependency-review or package-admission consumer can import execution-authority posture,
- without pretending the transition plan itself resolves the underlying security problem.

## What not to build
Do **not** build:
- an automatic proc-macro-to-`macro_rules!` converter;
- a hosted dashboard of “bad proc macros”;
- a universal reflection crate marketed as the answer to all derive-heavy workflows;
- or a mega-schema that silently redefines Macro Workflow, Compile-Time Capabilities, and Reflection Transition out of existence.

The point is a **reviewable transition layer**, not a new macro empire.

## Archive consequence
The archive should now treat **Proc-Macro Exit Stack** as the clearest next **compile-time/transition-shaping** move beneath:
- Macro Workflow,
- Compile-Time Capabilities,
- and Reflection Transition.

That does **not** make it the broad new #1 ecosystem need.
It does mean the repo now has enough substrate to say a concrete, worthy, machine-usable thing about reducing unnecessary proc-macro burden while the language and tooling are moving.
