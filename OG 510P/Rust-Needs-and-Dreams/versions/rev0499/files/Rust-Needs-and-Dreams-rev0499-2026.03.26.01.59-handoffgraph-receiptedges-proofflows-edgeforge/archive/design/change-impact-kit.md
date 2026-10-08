# Design: Change Impact Kit (`cargo impact`)

## Goal
Define one portable, reviewable boundary for reasoning about **what changed**, **what semantic boundary it crossed**, **what actually needs to rebuild**, and **what could be relinked or reused instead of recompiled**.

This kit should sit between:
- raw diffs and build logs,
- Cargo fingerprint/build-analysis data,
- public-API / semver evidence,
- compile-time invalidation facts,
- and future relink-oriented Cargo/rustc work.

It is not a replacement compiler optimization.
It is the shared evidence layer that makes change-sensitive build behavior explainable and attachable.

## Why now
The upstream alignment is strong:
- The 2025H2 **Relink don’t Rebuild** goal explicitly targets avoiding reverse-dependency rebuilds when a crate’s public interface did not change.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo’s build-analysis work is now storing rebuild reasons on disk and exposing them with `cargo report rebuilds`.
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- Cargo’s FAQ still says after-the-fact rebuild explanation has historically been weak, forcing users into `CARGO_LOG` archaeology.
  https://doc.rust-lang.org/cargo/faq.html
- Cargo fingerprint docs explain that freshness today is a layered compromise over fingerprints, mtimes, dep-info, and partial environment capture.
  https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/fingerprint/index.html
- rustc’s incremental-compilation guide explains why naive dependency tracking yields false positives and how red-green marking separates “might be affected” from “actually changed”.
  https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html
- Build scripts remain a live invalidation wildcard because broad or missing `rerun-if-*` declarations can force conservative rebuilds.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html

Those signals all say the same thing: Rust now needs a **change-impact substrate**, not just more local logging.

## Design principles
1. **Separate change facts from rebuild facts.** A diff is not the same thing as the rebuild it triggered.
2. **Separate semantic classification from observed tool behavior.** Current Cargo/rustc behavior may be conservative; the kit must be able to say so.
3. **Keep confidence explicit.** Some impact judgments can be strong; others will remain approximate or lane-specific.
4. **Public API is important but not sufficient.** Implementation-only, inline/codegen-sensitive, build-script, feature, target, and toolchain changes all matter.
5. **Relinkability is its own truth.** “Did not need recompilation” is not the same as “needed no work at all.”
6. **Consume adjacent evidence instead of replacing it.** Build-cache, API, compile-time, and semantic-context artifacts remain inputs.
7. **Do not hide today’s conservatism.** v0 must preserve “required by current toolchain behavior” versus “required by semantic boundary change”.

## Core artifact family

### 1) `impact-subject/v0`
Identifies the before/after states under review.

Fields should include:
- subject id
- workspace/package selection
- target triple(s)
- profile / command class (`check`, `build`, `test`, `doc`, `clippy`, etc.)
- toolchain identity
- edition / cfg / feature posture
- before-state ref and after-state ref (git commit, filesystem snapshot, package version, or other)
- path-normalization/redaction rules

### 2) `change-slice/v0`
A normalized description of the concrete change inputs.

Fields should include:
- referenced subject
- changed files / manifests / lockfiles / generated artifacts / environment knobs
- optional item-level slices when available
- change classes such as:
  - `DOC_TEXT`
  - `FORMAT_ONLY`
  - `LOCAL_BODY_CHANGE`
  - `INLINE_OR_MONO_SENSITIVE_CHANGE`
  - `PUBLIC_SIGNATURE_CHANGE`
  - `LAYOUT_OR_METADATA_CHANGE`
  - `FEATURE_CFG_CHANGE`
  - `TOOLCHAIN_CHANGE`
  - `BUILD_SCRIPT_INPUT_CHANGE`
  - `PROC_MACRO_INPUT_CHANGE`
  - `UNKNOWN`
- source of truth (`git diff`, Cargo metadata diff, build-analysis observation, manual declaration, other)

### 3) `impact-lane-profile/v0`
Describes the lane in which impact is assessed.

Fields should include:
- build lane (`current-cargo`, `experimental-relink`, `analysis-only`, `custom`)
- incremental mode posture
- build-analysis availability
- whether API/semantic/compiler evidence was available
- confidence policy / fallback rules
- comparability notes with other lanes

### 4) `impact-classification-report/v0`
The semantic judgment about the change.

Fields should include:
- referenced change slices
- classification verdicts such as:
  - `NO_SEMANTIC_INTERFACE_CHANGE`
  - `LOCAL_CODEGEN_CHANGE`
  - `PUBLIC_INTERFACE_CHANGE`
  - `BUILD_CONTEXT_CHANGE`
  - `COMPILE_TIME_INVALIDATION_CHANGE`
  - `LAYOUT_OR_SYMBOL_CHANGE`
  - `INCONCLUSIVE`
- supporting evidence references
- confidence level (`high`, `medium`, `low`, `analysis-incomplete`)
- reason codes explaining why the classification was chosen
- notes about current-toolchain conservatism

### 5) `rebuild-scope-report/v0`
The required or observed scope of work.

Fields should include:
- directly affected units
- reverse dependencies and action classes:
  - `NO_ACTION`
  - `LOCAL_RECHECK_ONLY`
  - `LOCAL_RECOMPILE`
  - `RELINK_ONLY`
  - `REVERSE_DEP_RELINK`
  - `REVERSE_DEP_RECOMPILE`
  - `RERUN_BUILD_SCRIPT`
  - `RERUN_PROC_MACRO_DEP`
  - `INCONCLUSIVE`
- whether the report is **semantic-required**, **current-toolchain-observed**, or **comparison-of-both**
- evidence strength and gaps
- reason-coded explanations

### 6) `relink-opportunity-report/v0`
Captures missed or realized reuse opportunities.

Fields should include:
- referenced subject and rebuild scope
- candidate downstream artifacts/units
- verdicts:
  - `RELINK_USED`
  - `RELINK_POSSIBLE_BUT_NOT_AVAILABLE`
  - `RECOMPILE_REQUIRED`
  - `UNKNOWN`
- why relink was or was not viable
- blocking reason classes such as:
  - `CURRENT_LANE_LACKS_SUPPORT`
  - `INTERFACE_BOUNDARY_CHANGED`
  - `INLINE_OR_MONO_EXPOSURE`
  - `FINGERPRINT_CONSERVATISM`
  - `BUILD_SCRIPT_OR_PROC_MACRO_CHURN`
  - `CONFIG_OR_TARGET_DRIFT`

### 7) `impact-diff-report/v0`
Compares two impact states or compares expectation vs observation.

Fields should include:
- old/new report references
- changed classifications
- changed rebuild scope
- changed relink opportunities
- newly inconclusive / newly explainable areas
- migration notes / suspected causes

### 8) `impact-pack/v0`
Attachable bundle containing:
- one `impact-subject`
- one or more `change-slice`
- one `impact-lane-profile`
- one or more `impact-classification-report`
- one or more `rebuild-scope-report`
- optional `relink-opportunity-report`
- optional raw attachments:
  - Cargo rebuild reports
  - fingerprint logs
  - API diffs
  - semantic-context query outputs
  - compile-time invalidation reports

## Reference UX
A reference implementation might expose:
- `cargo impact slice` — emit `change-slice/v0`
- `cargo impact classify` — emit `impact-classification-report/v0`
- `cargo impact scope` — emit `rebuild-scope-report/v0`
- `cargo impact relink` — emit `relink-opportunity-report/v0`
- `cargo impact diff` — compare expectations/observations across revisions
- `cargo impact pack` — bundle an `impact-pack/v0`

The first versions should prefer **adapter mode**:
- import `cargo report rebuilds`
- import API/semver evidence
- import compile-time invalidation facts
- optionally import raw fingerprint logs

## Theory of change
The important design move is to keep five truths separate:
1. **what concretely changed**,
2. **what semantic boundary it crossed**,
3. **what the current toolchain actually did**,
4. **what work was semantically required**,
5. **what could have been relinked or reused in a stronger lane**.

That separation matters because current Rust build pain often gets flattened into one fake story:
- “Cargo rebuilt too much”
- “incremental is flaky”
- “the cache missed”
- “the API changed”

Often those are different phenomena.
This kit gives them distinct artifacts so tools and humans can stop talking past one another.


## Shared stack role
This kit is now one leg of the archive’s shared **Build-State Evidence Stack**:
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md)
- [`design/build-state-evidence-pilot-program.md`](./build-state-evidence-pilot-program.md)

That means future revisions should treat Change Impact Kit as the **change-slice / semantic-boundary / rebuild-scope / relink-opportunity** layer, not as a cache dashboard or workflow coach.

## Adjacent kits and boundaries
- **Public API Kit** supplies one important signal: public-surface change. But change impact also needs non-API, config, and compile-time invalidation classes.
- **Build Cache Kit** owns persisted artifact layout, lock scope, and reuse verdicts. Change Impact Kit owns the classification of changes and the action scope they imply.
- **Build Doctor Kit** can consume impact reports to explain slow workflows. It should not replace the impact taxonomy.
- **Compile-Time Capabilities Kit** owns build-script/proc-macro authority and input surfaces. Change Impact Kit references those facts when compile-time invalidation widened rebuild scope.
- **Semantic Context Kit** can provide cross-crate or compiler-backed evidence; it remains an input plane, not the final impact verdict.

## Early pilots
1. **comment / formatting pilot**
   - prove that the kit can distinguish doc-only or formatting-only edits from semantic interface changes.
2. **non-inlinable body-change pilot**
   - compare current observed reverse-dependency rebuilds with a relink-oriented expectation.
3. **public signature pilot**
   - show a case where API evidence and rebuild-scope evidence line up cleanly.
4. **build-script churn pilot**
   - show a case where broad invalidation, not real interface change, caused large downstream work.
5. **feature/target/toolchain pilot**
   - ensure non-source changes remain first-class rather than being misfiled as “code changed”.

## Success criteria
- A maintainer can attach one pack that says both **what changed** and **why rebuild scope expanded**.
- Cargo rebuild-analysis outputs gain a portable downstream boundary instead of staying one-off CLI diagnostics.
- Future relink-oriented work can target an ecosystem-understood artifact model rather than inventing one privately.
- Build-cache and build-doctor tools stop overloading cache-hit/miss or wall-time as the only language for rebuild pain.

## Failure modes to avoid
- treating git diff as enough semantic evidence;
- pretending every unchanged public API means no downstream rebuild is needed;
- flattening observed Cargo behavior and idealized relink behavior into one verdict;
- hiding build-script/proc-macro invalidation under generic “dependency changed” language;
- or turning v0 into a speculative whole-program compiler oracle instead of an honest evidence layer.
