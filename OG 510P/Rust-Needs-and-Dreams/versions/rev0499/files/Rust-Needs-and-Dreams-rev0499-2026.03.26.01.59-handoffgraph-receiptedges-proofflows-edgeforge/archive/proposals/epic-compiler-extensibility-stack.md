# Epic Proposal: Compiler Extensibility Stack (`cargo toolcontract` + `tool-pack/v0`)

## Why this is worthy
Rust’s ecosystem increasingly needs **compiler-attached tools that can be reviewed like products instead of admired like demos**.

The signals are unusually aligned:
- Rust’s vision work explicitly recommends **doubling down on extensibility** beyond the earliest compilation stages and names Stable MIR / `build-std` as examples of the kind of access future tools will need.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025H1 StableMIR goal says the point is to enable analyzers, linters, dev environments, and other tools to work across Rust versions without binding directly to compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- The July 2025 project-goals update says the `stable_mir` crate became `rustc_public` and moved toward publication infrastructure and an MCP, which makes this feel less hypothetical and more like real ecosystem surface area.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The `cargo-semver-checks` goal shows the demand side plainly: the tool is strong enough to target Cargo integration, but it still needs better cross-crate visibility, more precise type information, and witness-generation support. The same page also explains why the older `semverver` path failed: compiler-internal API dependence was too costly to sustain.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Rust’s 2026 flagships explicitly include safety-critical lints in Clippy, public-API/supply-chain work, and Cargo plumbing directions, which means compiler-adjacent tooling is becoming more strategic rather than remaining peripheral.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s current direction still says plugins matter because Cargo cannot be everything to everyone.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

But the ecosystem still has no single honest handoff for **compiler-tool contract truth**.
That means maintainers, release reviewers, CI systems, editor integrations, and assurance consumers still have to reconstruct the answer from:
- rustdoc JSON lore,
- Clippy configuration and version coupling,
- nightly flags,
- custom drivers,
- ad hoc witness programs,
- hand-rolled derived graphs,
- and tool-specific CLI output that often hides scope and incompleteness.

The missing contribution is a thin portable layer above those pieces, not another universal plugin ABI and not a campaign to merge every worthy tool into Cargo.

## Proposal
Define a **Compiler Extensibility Stack** with:
- a reference companion CLI, `cargo toolcontract`;
- a thin linked bundle, `tool-pack/v0`;
- imported evidence from:
  - MIR Analysis artifacts,
  - Lint Governance artifacts,
  - Compile Guidance artifacts,
  - Conformance Traceability artifacts,
  - plus subject/config/toolchain attachments from repo / manifest / toolchain layers;
- stable compiler-tool-facing artifacts:
  - `tool-subject/v0`
  - `compiler-attachment-profile/v0`
  - `analysis-input-profile/v0`
  - `tool-capability-profile/v0`
  - `tool-result-report/v0`
  - `tool-consumer-handoff/v0`
  - `tool-pack/v0`

## Reference CLI shape
- `cargo toolcontract export`
  - emit `tool-subject/v0`, `compiler-attachment-profile/v0`, and `analysis-input-profile/v0` for one tool+subject lane
- `cargo toolcontract check`
  - emit `tool-capability-profile/v0` plus one or more `tool-result-report/v0` files from imported analyzer/lint/witness/guidance outputs
- `cargo toolcontract diff --against <prior-pack|ref|path>`
  - emit a reason-coded diff attachment comparing attachment lane, scope/configuration, capability posture, and result families
- `cargo toolcontract handoff`
  - emit `tool-consumer-handoff/v0` for CI/editor/release/policy/assurance consumers
- `cargo toolcontract pack`
  - produce `tool-pack/v0`
- `cargo toolcontract verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace `cargo-semver-checks`, Clippy, future `rustc_public` analyzers, rustdoc JSON tools, or future Cargo-native import paths.

## What `tool-pack/v0` should contain
- `manifest.json`
- `tool-subject.json`
- `compiler-attachment-profile.json`
- `analysis-input-profile.json`
- `tool-capability-profile.json`
- one or more `tool-result-report.json` attachments
- `tool-consumer-handoff.json`
- optional diff attachment
- imported MIR/lint/guidance/conformance attachments or pointers
- checksums, provenance, and generator identity
- optional support / release / policy / assurance consumer pointers

## Design principles
- **Attachment lane before glamour.** Every artifact starts by saying how it attached.
- **Subject/configuration is part of the result.** Package/workspace/target/profile/feature/toolchain scope cannot stay implicit.
- **Capability and stability stay separate.** A valuable nightly lane is still not a stable lane.
- **Result families stay distinct.** Lints, witnesses, derived graphs, guidance packs, fix packs, and conformance evidence must not collapse into one blob.
- **Companion products are legitimate.** “Useful but not merged into Cargo” is success, not failure.
- **Consumers import bounded conclusions.** CI, editors, release processes, policy, and assurance should each get explicit handoff boundaries.
- **Cargo-merger fantasies stay out of scope.** Possible future upstreaming is not the present support contract.

## Early implementation order
1. `cargo-semver-checks` / SemVer compatibility lane
2. safety-critical lint lane
3. `rustc_public` / MIR read-only analyzer lane
4. guidance / fix handoff lane
5. assurance / conformance consumer lane

That order follows the real ecosystem pressure: first prove a lane with live adoption and obvious value, then prove policy-heavy linting, then prove a more general compiler-export lane, then prove editor/CI handoff, and only after that widen toward high-assurance consumers.

## Non-goals
- a universal compiler plugin ABI;
- a promise that every worthy tool belongs inside Cargo;
- a fake “official tool” badge for anything that touches compiler data;
- one schema that tries to normalize every compiler-adjacent experiment at once;
- flattening witness generation, linting, semantic export, and assurance into one status light.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- how the tool attached;
- what exact subject and configuration it analyzed;
- what it could and could not honestly see;
- what artifact family it emitted;
- what a consumer may safely gate on;
- and what changed between tool runs or tool versions,

without scraping bespoke CLI output, reverse-engineering nightly flags, or inferring scope from issue threads and blog posts.

## Read this with
- `gaps/compiler-extensibility-analysis-lints-and-reviewable-tool-contracts.md`
- `design/compiler-extensibility-stack.md`
- `design/compiler-extensibility-pilot-program.md`
- `design/mir-analysis-kit.md`
- `design/lint-governance-stack.md`
- `design/compile-guidance-kit.md`
- `design/conformance-traceability-stack.md`
