---
id: P-0508
title: Cargo Build Script Delegation Kit — unit-topology receipts, output-lane authority, override truth, and delegation drift bundles
status: idea
domains: [cargo, build-scripts, ffi, devtools, packaging, supportiveness]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://github.com/rust-lang/cargo/issues/14948
  - https://rust-lang.github.io/rfcs/2196-metabuild.html
---

# Problem

Cargo’s build-script world is no longer just “one handwritten `build.rs` that pokes the host and prints directives”.
The official substrate is now explicit enough that a missing crate can be planned in concrete review objects rather than folklore.

Current Cargo and Rust signals line up around the same shape:

- build scripts already expose **order-sensitive directives**, `OUT_DIR`, metadata passing, warning/error channels, and `links`-key overrides;
- Cargo’s external-tools surface already emits machine-readable build messages and build-script results;
- unstable Cargo now documents **metabuild**, **multiple build scripts**, and **any build script metadata**;
- the 2025 GSoC work explicitly connected the road toward reusable delegated build units to **multiple-build-scripts**, deterministic ordering, separate output directories, and metadata parameters in `Cargo.toml`;
- Cargo 1.93’s build-analysis notes explicitly say that any future artifact-dir handoff has to reason about **collision checking**, **locking discipline**, and **multiple build scripts within a single invocation**;
- and the Cargo team is actively trying to **reduce the need for users to write build scripts** in the first place.

That means the missing value is no longer another generic helper crate that hides `cc`, `bindgen`, or `pkg-config`.
The missing value is a crate that tells another engineer, reviewer, or downstream maintainer:

1. **which build units were intended to run**,
2. **in which deterministic order**,
3. **which unit produced which metadata / env / artifacts**,
4. **whether that came from live execution or from an override / delegated source**,
5. **what parts of the flow still depend on unstable substrate**, and
6. **what changed across releases or toolchains**.

That worthy crate is **Cargo Build Script Delegation Kit**.

# Sharper reading after the 2025–2026 Cargo changes

The 2025–2026 signal makes this lane stronger and narrower than before.

## 1. Build-script execution is becoming unit-shaped

The multiple-build-scripts work means a package can stop looking like one opaque imperative blob.
That creates a new review problem: which named unit ran, in what order, and which facts belong to which unit.

## 2. Delegation is no longer hypothetical

Metabuild, metadata parameters, and work toward delegating build logic into packages means build behavior can be declared, imported, split, or overridden.
A receiver needs a portable answer for which layer was authoritative.

## 3. Override paths are already first-class

Cargo config already allows `target.<triple>.<links>` overrides that skip a build script entirely and inject metadata directly.
That means “the build script succeeded” is not even the only honest success path anymore.

## 4. Artifact handoff is constrained by safety and collisions

Cargo 1.93’s notes make it plain that build-script artifact staging cannot just become arbitrary shared filesystem access.
Any worthy workflow crate has to model output lanes and collision authority explicitly.

## 5. Upstream wants fewer ad-hoc build scripts, not more

Because Cargo is exploring ways to reduce handwritten build scripts, the missing crate should live above today’s handwritten substrate and stay useful as more declarative forms arrive.

# Main judgment

A worthy crate here should provide a receiver-facing answer to five questions:

1. **Unit topology** — what build units exist, what class are they, and in what order are they supposed to execute?
2. **Output lane** — which metadata, env exports, generated files, or staged artifacts came from which unit?
3. **Override authority** — did those facts come from a live run, a `links` override, a metabuild/delegate package, or a conservative imported observation?
4. **Bridge posture** — where does the flow depend on unstable artifact staging, multi-script substrate, or fallback shims?
5. **Drift** — what changed across revisions, targets, or toolchains that materially changes support and review posture?

That is more valuable than another helper macro or a prettier log viewer.

# What it provides

- `delegate-contract.toml` — maintainer-declared build-unit intent, ordering constraints, parameter sources, expected outputs, and stable-vs-nightly posture.
- `delegate-plan.json` — normalized plan for all participating build units, including handwritten files, metabuild entries, and package delegates.
- `unit-topology.receipt.json` — named unit graph/order record with provenance for the ordering basis.
- `output-lane.receipt.json` — per-unit map of `OUT_DIR`, metadata exports, env exports, generated files, and staged-artifact surfaces.
- `override-authority.receipt.json` — statement of whether the authoritative facts came from live execution, `links` override config, delegate package policy, or imported Cargo observations.
- `delegate-observation.receipt.json` — raw observed execution facts captured from Cargo surfaces and supplemental logs.
- `delegate-bridge.report.json` — findings such as `unit_order_ok`, `artifact_bridge_required`, `collision_authority_missing`, `metadata_route_ambiguous`, `nightly_only_gap`, or `manual_review_required`.
- `delegation-drift.diff.json` — release-to-release or toolchain-to-toolchain changes in unit order, output lanes, override posture, or bridge posture.
- `delegate-fallback.plan.json` — conservative fallback such as inline the handwritten `build.rs`, ship a `links` override recipe, keep artifacts local to `OUT_DIR`, or postpone a nightly-only bridge.
- `build-script-support-bundle.manifest.json` — portable review bundle tying all of the above together.
- `cargo build-delegate snapshot`
- `cargo build-delegate doctor`
- `cargo build-delegate diff <old> <new>`
- `cargo build-delegate pack`
- `*.builddelegate.zip`

# First-class review objects for 0.1

## `unit-topology.receipt.json`

Should record at least:

- unit name / identity,
- unit class (`handwritten`, `metabuild`, `delegate-package`, `override-only`),
- deterministic order basis,
- parameter source,
- and whether the topology was declared, observed, or inferred.

## `output-lane.receipt.json`

Should record at least:

- unit name,
- `OUT_DIR` identity,
- produced metadata keys,
- produced env exports,
- generated source/include paths,
- artifact staging path if any,
- and path-redaction / sharing posture.

## `override-authority.receipt.json`

Should record at least:

- authority route (`live-run`, `links-override`, `delegate-package`, `imported-json`, `manual-review`),
- target scope,
- reason the route was chosen,
- and limits on what the receipt can honestly claim.

## `delegation-drift.diff.json`

Should classify at least:

- `unit_added`,
- `unit_removed`,
- `unit_reordered`,
- `output_lane_changed`,
- `override_route_changed`,
- `artifact_bridge_changed`,
- `support_posture_changed`,
- `manual_review_required`.

# What the crate should provide other people

1. **A boring delegated-build contract** instead of tribal `build.rs` lore.
2. **A topology receipt** so reviewers can see exactly which build units exist and in what order they matter.
3. **An output-lane receipt** so generated headers, metadata, and staged artifacts stop blending together.
4. **Override truth** so downstream users know when Cargo config or delegate packages replaced live script execution.
5. **A bridge/fallback story** for teams who cannot rely on unstable multi-script or artifact-staging substrate.
6. **A diffable support bundle** for release review, regression triage, and target/toolchain comparison.

# Persona / who it’s for

- maintainers of `-sys` crates and generator-heavy crates,
- workspace owners centralizing repeated build-time logic,
- downstream packagers and distro engineers who rely on override or no-network builds,
- CI/tool authors who need durable machine-readable support artifacts,
- and reviewers trying to decide whether a delegated build setup is shippable rather than merely clever.

# Users & user stories

- **`-sys` maintainer**: “Show me whether my split build logic still emits the same metadata contract my dependents expect.”
- **Packager**: “Show me whether the authoritative source was a `links` override, not a live probe against the build host.”
- **Workspace owner**: “Compare the old single `build.rs` lane and the new multi-unit delegate lane without reading every log.”
- **Support engineer**: “Tell me whether the breakage came from reordered units, missing output-lane exports, or an unstable artifact bridge.”
- **Cargo-adjacent tool author**: “Give me one schema for delegated build behavior instead of making me reverse-engineer Cargo semantics from logs.”

# Prior art (and why it’s insufficient)

- Cargo’s build-script docs are the semantic truth source, but they are not a durable support contract.
- Cargo external-tools JSON gives raw machine-readable build events, but not a receiver-facing delegated-build bundle.
- `metabuild` and multiple-build-scripts give substrate for composition, not a reviewable topology/output/override contract.
- `links` overrides are real and useful, but Cargo does not package them into a reusable authority receipt for downstream support.
- The archive already has **P-0046 buildscript-ux-kit** for diagnosis and **P-0059 buildscript-testkit** for hermetic testing. Those remain adjacent, not replacements.

What remains missing is a crate that freezes the **delegated build contract** itself.

# Design goals

1. **Unit-first** — model build behavior as named units rather than one opaque `build.rs` blob.
2. **Order-explicit** — deterministic order must be reviewable because build-script directives are order sensitive.
3. **Output-lane explicit** — generated files, metadata keys, env exports, and staged artifacts must stay attributable.
4. **Override-honest** — skipping live execution via `links` overrides is a first-class route, not an embarrassment.
5. **Stable-first, nightly-aware** — the crate should already help on stable while making unstable dependencies explicit.
6. **Adjacent-lane honest** — do not collapse this lane into generic buildscript UX, target support, native-deps policy, or artifact-dependency adoption.

# MVP surface

- Minimal types: `DelegateContract`, `DelegatePlan`, `UnitTopologyReceipt`, `OutputLaneReceipt`, `OverrideAuthorityReceipt`, `DelegateObservationReceipt`, `DelegateBridgeReport`, `DelegationDriftDiff`, `DelegateFallbackPlan`, `BuildScriptSupportBundle`
- Minimal functions:
  - `capture_delegate_plan()`
  - `capture_unit_topology()`
  - `capture_output_lanes()`
  - `capture_override_authority()`
  - `diagnose_delegate_bridge()`
  - `diff_delegate_bundles()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `metabuild`
  - `artifact-bridge`

# Compatibility story

- Must remain useful on stable Cargo by capturing plans, observations, override routes, and fallback posture even when the full delegation dream is unavailable.
- Must preserve whether a fact came from live execution, imported Cargo JSON, config-based override, or conservative inference.
- Must remain valuable if Cargo later stabilizes more declarative build substrate, because teams will still need topology/output/authority receipts and drifts.
- Must integrate with other archive lanes instead of replacing them: buildscript UX for diagnosis, host/target topology for execution-lane truth, and native-deps/artifact lanes for downstream consumers.

# Conformance & fixtures

- a multi-script `-sys` package where deterministic order matters and output lanes must stay distinct,
- a package where `links` override config skips live execution but remains the authoritative metadata source,
- a delegate package whose upgrade reorders units and changes the support story,
- an artifact-bridge experiment where collision authority is required before a support claim is acceptable,
- and a parameter-source case where manifest metadata and imported observations disagree.

# Path to boring stability

1. Freeze the topology / output-lane / override vocabulary before automating manifest rewrites.
2. Start with capture, doctoring, diffing, and packing.
3. Keep stable-vs-nightly posture explicit in every bundle.
4. Prefer additive observation over magic interception.
5. Stay useful even if upstream Cargo eventually reduces handwritten build scripts dramatically.

# Why this could be epic

This crate would help other people reason about one of the messiest parts of the Rust packaging and interop story without asking Cargo to solve every adjacent problem first.
That makes it the right kind of epic: it sits above real substrate, turns invisible build-time behavior into durable review objects, and helps maintainer, downstream packager, CI owner, and ecosystem tool author all at once.
