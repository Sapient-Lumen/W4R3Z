# Design: MIR Analysis Kit (`cargo mir`, `mir-pack/v0`)

## Goal
Define a semantics-aware MIR capture and analysis contract for Rust so tools built on `rustc_public` can exchange versioned artifacts with **explicit coverage and comparability truth** instead of coupling themselves to one compiler process, one nightly snapshot, or one project-specific JSON dump.

This should not replace `rustc_public`, the Rustc Librarification Project, `stable-mir-json`, or individual analyzers like Kani/KMIR/RBMC. It should make them easier to compose, diff, attach to CI, and reuse.

## References (signals)
- Accepted 2025H1 goal: publish StableMIR crate(s) to crates.io so tool developers can analyze compiled crates without depending directly on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- Rustc Librarification Project page: the effort is now framed as `rustc_public`, a SemVer-compliant API based on MIR for sophisticated external analyses.
  https://rust-lang.github.io/project-stable-mir/
- Compiler-team MCP #949: publish `rustc_public` v0.1 to crates.io with SemVer, multi-version support, and the `rustc_public` / `rustc_public_bridge` split.
  https://github.com/rust-lang/compiler-team/issues/949
- Nightly docs still describe `rustc_public` as a WIP public interface, explicitly unstable for now, and document separate `unstable` and `rustc_internal` escape-hatch modules.
  https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
  https://doc.rust-lang.org/beta/nightly-rustc/rustc_public/rustc_internal/index.html
- The current MIR module already exposes bodies, mono data, allocations, pretty-printing, and visitors — i.e. enough structure that downstream tools will increasingly want machine-facing reuse rather than custom drivers.
  https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/mir/index.html
- `stable-mir-json` is a real-world proof of demand for serialized MIR, but its architecture note says it is a compiler driver and currently uses both StableMIR and rustc internals.
  https://hackmd.io/%40cds-amal/SkgYPwTOuWg
- `cargo-semver-checks` needs more precise compiler-backed information and witness-based checking; contracts work explicitly wants compiler interfaces for external tools to retrieve annotations.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- MIR semantics themselves are still evolving: the move-elimination goal requires changing MIR move semantics and then teaching Miri to validate the new model.
  https://rust-lang.github.io/rust-project-goals/2025h2/mir-move-elimination.html

## Core components

### 1) `mir-subject/v0`
Describes **what** is being analyzed:
- workspace/package/crate identity
- selected targets / profiles / cfg context
- exact toolchain identity (`rustc` version/channel/commit where available)
- crate-selection scope (local crate only, local + selected externals, mono-root scope)
- semantic epoch identifiers when known (for example MIR semantics generation / producer schema version)

Design rule: no anonymous “snapshot of the crate” claims.

### 2) `mir-capture-profile/v0`
Describes **how** the capture was produced:
- capture lane (`rustc_public` only, `rustc_public` + `rustc_internal`, `stable-mir-json` bridge, other)
- requested data families (bodies, mono items, spans, alloc/statics, trait/impl data, contracts, pretty text, raw attachments)
- selection policy (all local bodies, reachability slice, mono roots, unsafe-reachable slice, size-budgeted sample)
- optimization / codegen / edition assumptions that materially affect interpretation
- raw-pass-through posture (whether upstream payloads are attached verbatim)

Design rule: capture policy must be portable and reviewable, not buried in tool-specific flags.

### 3) `mir-capability-profile/v0`
Declares **what the producer can honestly claim**:
- producer identity and version
- `rustc_public` / bridge version when applicable
- supported artifact families and query types
- stable versus unstable escape hatches used
- completeness posture by data family
- cross-version comparability claims and limits

This prevents consumers from mistaking “MIR-shaped output” for a complete or comparable artifact.

### 4) `mir-observation-report/v0`
Records **what was actually captured**:
- body / mono / allocation / span counts
- missing-data reasons (unsupported, filtered, bridge-only, budget-limited, failed extraction)
- attachment digests
- capture warnings (mixed lanes, partial fallback, semantic-epoch mismatch, truncated side tables)

Design rule: observation truth is separate from derived conclusions.

### 5) `mir-derived-graph/v0`
Portable machine-facing graph attachments, for example:
- callgraph / mono graph
- unsafe reachability graph
- drop / allocation / borrow-sensitive relation graphs
- summary metrics and node/edge counts

Design rule: keep derived graphs distinct from raw MIR capture so downstream tools can choose their level of trust and cost.

### 6) `mir-query-report/v0`
Structured answers to common downstream questions:
- “which unsafe blocks are reachable from public entrypoints?”
- “which mono instances dominate code size growth?”
- “which functions allocate / recurse / touch inline asm?”
- “which contract-annotated items appear in this slice?”

Each query report includes:
- query identity + parameters
- input artifact digests
- result items / metrics / spans
- caveats from capability/completeness posture
- reason codes explaining partial or non-results

Design rule: queries are first-class artifacts, not just CLI text.

### 7) `mir-diff-report/v0`
A structured comparison between two subjects, captures, or query reports:
- semantic epoch comparison
- producer/toolchain comparison
- comparable scope (`full`, `partial`, `none`)
- added/removed/changed items, bodies, graphs, or findings
- explicit incomparable reasons when exact comparison would be misleading

This is the crucial upgrade over ad hoc JSON diffing: **do not fabricate precision when MIR semantics changed**.

### 8) `mir-pack/v0`
Bundle format containing:
- `mir-subject/v0`
- `mir-capture-profile/v0`
- `mir-capability-profile/v0`
- `mir-observation-report/v0`
- optional `mir-derived-graph/v0`
- optional `mir-query-report/v0`
- optional `mir-diff-report/v0`
- optional raw upstream artifacts, logs, and pretty-printed MIR
- digests and integrity summary

This is the attachable unit for CI, bug reports, verification handoffs, and release evidence.

### 9) `cargo mir`
Reference UX:
- `cargo mir capture`
- `cargo mir query --kind <query>`
- `cargo mir diff`
- `cargo mir doctor`
- `cargo mir pack`

`cargo mir` should begin as an adapter / orchestrator / packer. It should not require upstreaming every interesting analysis into one mega-tool.

## Default policy
- **Artifact-first, not driver-first.**
- **Declare semantic epoch and capture lane explicitly.**
- **Keep raw capture, observations, derived graphs, and conclusions separate.**
- **Allow raw upstream payloads as attachments when normalization is incomplete.**
- **Prefer “partially comparable” over fake precision.**

## What the kit should provide to others
- **Semantic Context Kit:** a compiler-backed lower layer that can be attached rather than rebuilt.
- **Public API / SemVer tooling:** deeper facts for tricky type- or cross-crate-sensitive checks.
- **Safety Evidence Kit:** attachable unsafe reachability and contract-linked low-level evidence.
- **Formal-methods and research teams:** a portable handoff between extraction and proof / symbolic execution.
- **CI/release tooling:** diffable compiler-aware artifacts instead of custom logs.

## Overlap boundaries
- **Not Semantic Context Kit:** that kit is broader and cross-source; MIR Analysis Kit is the lower compiler-derived lane.
- **Not Public API Kit:** public-surface and semver conclusions stay there.
- **Not Safety Evidence Kit:** policy conclusions and waivers stay there.
- **Not Cargo Report Kit:** build/session/timing reports remain separate.
- **Not one blessed analyzer framework:** the kit standardizes handoff artifacts, not the entire analyzer ecosystem.

## Hard problems (explicitly scoped)
1. **Semantic drift in MIR itself**
   - the move-elimination work is evidence that MIR semantics can change; the kit must track epochs and comparability honestly.
2. **Coverage gaps in `rustc_public`**
   - the design must surface bridge/escape-hatch use instead of hiding it.
3. **Artifact size explosion**
   - mono-rich crates need slices, budgets, and attach-by-digest side tables.
4. **Identifier stability**
   - do not overpromise globally stable item identities where only scoped identities exist.
5. **Toolchain-version churn**
   - the whole point is to make churn reviewable rather than invisible.

## Evaluation plan
Pilot on:
1. a small workspace producing a `mir-pack/v0` with body + mono + span capture,
2. a `stable-mir-json` bridge adapter that emits the standard pack,
3. one derived query such as unsafe reachability or mono growth,
4. one CI flow diffing query reports across pull requests,
5. one downstream consumer in safety / semver / verification tooling.

Success bar:
- at least two independent producers can emit comparable pack components,
- one downstream consumer can use a pack without shelling out to the original driver,
- reviewers can tell when a diff is partial or incomparable,
- and tool authors can reduce ad hoc `rustc_private` coupling over time instead of re-creating bespoke export stacks.
