# Design: Native Edge C++ Lane Map (C ABI export, safe-common bridges, automated existing-codebase lanes, and external-build handoff)

## Goal
Make the archive more precise about **what kind of Rust↔C/C++ interop problem is actually being solved**.

Rust’s current native-adoption pressure is real, but the ecosystem still talks as if one word — “interop” — names one thing.
It does not.
A team exporting a compact C ABI, a team using `cxx` for a safe common Rust/C++ regime, a team using `autocxx` against a huge existing header forest, and a team handing results to CMake/Bazel/distro packaging are solving **different but linked** problems.

The worthy contribution here is therefore not one more bridge generator or one more provider helper.
It is a **portable lane map and evidence boundary** that lets the ecosystem compare these lanes honestly, import their artifacts, and stage improvements without pretending that one lane already covers the whole adoption story.

Read this together with:
- [`design/native-edge-stack.md`](./native-edge-stack.md)
- [`design/native-edge-pilot-program.md`](./native-edge-pilot-program.md)
- [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md)
- [`design/native-dependency-kit.md`](./native-dependency-kit.md)
- [`proposals/epic-native-edge-stack.md`](../proposals/epic-native-edge-stack.md)

## Why this note is needed now
The current official and ecosystem signals line up around one conclusion: Rust needs a better **native-adoption contract**, not just more point tools.

- The accepted 2025H1 Rust goal **Evaluate approaches for seamless interop between C++ and Rust** exists because adoption often requires using large, rich C++ APIs rather than replacing them outright.
- The 2025H2 **C++/Rust Interop Problem Space Mapping** effort says there are billions of lines of C++ representing enormous value, that full rewrites are not the near-term answer, and that existing libraries solve different slices of the space.
- The July 2025 goals update says the language team established that Rust should evolve toward a **first-class C++ interop story**, while also saying that different groups have materially different interop needs.
- Cargo’s roadmap issue to **reduce the need for users to write build scripts** says build scripts increase build time, bug risk, and dependency-review surface; native probing and `-sys` lanes remain one of the reasons they persist.
- The Cargo build-script docs still say `links` metadata is limited to one package per `links` value and metadata only flows to immediate dependents.
- The Rustonomicon still teaches FFI through C interfaces and says Rust cannot directly call into a C++ library.
- The current tool families are good but non-equivalent: `system-deps` makes some native requirements declarative in `Cargo.toml`; `pkg-config` shells out from `build.rs`; CXX deliberately carves out a safe common Rust/C++ regime; `autocxx` explicitly targets large existing C++ codebases with automation layered on CXX-style safety; and Corrosion is explicitly about integrating Cargo into existing CMake projects rather than replacing FFI tooling.

That is enough evidence to stop asking “what is the Rust C++ interop solution?” and start asking **which native lane is under review, which facts are shared, and which facts stay lane-specific?**

## The lane map

### Lane 1 — C ABI export/import lane
**What it is**
- Rust exports a C ABI or imports a native library through a C ABI.
- Common tools: handwritten `extern "C"`, `bindgen`, `cbindgen`, symbol-control tooling, package-manager or distro integration.

**Why it matters**
- This is still the broadest compatibility lane.
- It is often the smallest-review surface for regulated environments, legacy systems, distro packaging, and mixed-language repos that do not want a richer bridge yet.

**What the archive should preserve**
- exact boundary subject and generated-artifact provenance,
- ownership / lifetime / layout claims,
- exception / panic / thread / allocator posture,
- native-provider and link-plan facts,
- and downstream-consumable header/binding receipts.

**What it should not pretend**
- that C ABI alone captures richer C++ semantics,
- that generated headers automatically prove downstream build success,
- or that one successful Cargo build proves external-build or release readiness.

### Lane 2 — Safe-common C++ bridge lane
**What it is**
- The project deliberately stays within the common semantic regime that tools like CXX support.
- Boundary description is explicit and typed rather than inferred from arbitrary header surfaces.

**Why it matters**
- This is the cleanest current answer when a team wants stronger semantics than plain C FFI but can constrain itself to a reviewable shared subset.
- It is closer to an attachable evidence substrate than a header-scrape story.

**What the archive should preserve**
- bridge-module identity,
- generated Rust/C++ artifact provenance,
- required CXX release compatibility across generated sides,
- ownership and move/reference semantics at the boundary,
- and build-system assumptions for Cargo versus foreign-build use.

**What it should not pretend**
- that CXX covers arbitrary existing C++ APIs,
- that safe-common bridge success removes provider/link truth,
- or that a good bridge is the same as a complete large-codebase adoption plan.

### Lane 3 — Automated existing-codebase lane
**What it is**
- The project needs Rust to work against a large existing C++ surface with more automation.
- `autocxx` is the clearest live signal here: it explicitly targets large existing codebases, aims for CXX-style safety, and generates interfaces automatically from headers using a bindgen-derived path.

**Why it matters**
- This is the lane that most directly answers the adoption pressure from established organizations.
- It is also where boundary drift, generator/toolchain coupling, and partial-support truth get harder.

**What the archive should preserve**
- generator family and version,
- header/input provenance,
- unsupported / manual / lossy edge classes,
- cross-module or multi-binding-set posture,
- build-script / `libclang` / external-tooling requirements,
- and the difference between generated coverage and genuinely reviewed support.

**What it should not pretend**
- that automation removes the need for boundary review,
- that bindgen-derived reach means semantic equivalence,
- or that “worked on our codebase” is a portable interoperability verdict.

### Lane 4 — Native-provider and link-plan lane
**What it is**
- The project’s main challenge is not boundary syntax but **how native code is found, selected, configured, and linked**.
- Common tools: `system-deps`, `pkg-config`, vendoring, `vcpkg`, `cmake`, external injection, provider overrides.

**Why it matters**
- Native adoption fails as often on provider ambiguity and link plans as on the boundary surface.
- Cargo itself is trying to reduce unstructured build-script reliance, which makes provider truth strategically important.

**What the archive should preserve**
- provider intent and fallback order,
- winning provider and reason,
- host-vs-target distinctions,
- include/lib/framework/tool facts,
- override and injection posture,
- and raw provider outputs as attachments rather than invisible implementation detail.

**What it should not pretend**
- that native-provider success proves boundary compatibility,
- that a `pkg-config` result is portable across environments,
- or that declarative metadata alone eliminates toolchain or sysroot constraints.

### Lane 5 — External-build and packaging handoff lane
**What it is**
- Native-edge truth must travel beyond Cargo into CMake/Bazel/Buck/Nix/distro packaging or similar systems.
- Corrosion is the clearest signal here: it integrates Cargo into existing CMake projects and documents both automatic and manual binding-attachment paths.

**Why it matters**
- This is where organizational adoption either becomes durable or falls back to repo-specific folklore.
- It is also where “works in Cargo” often stops being enough.

**What the archive should preserve**
- what a foreign build system is expected to ingest,
- what artifacts are generated versus imported,
- whether handoff is automatic, manual, or mixed,
- target/runtime/package identity at handoff time,
- and what support/release consumers may legitimately reuse.

**What it should not pretend**
- that a Cargo-native bridge report is automatically a packaging contract,
- that generated headers are the full foreign-build story,
- or that external consumers can safely scrape Cargo internals forever.

### Lane 6 — Watch lane for future first-class compiler/language interop
**What it is**
- The archive should keep a watch lane for upstream language/compiler motion that may change what is feasible or blessed over time.

**Why it matters**
- The official goals work is explicit that Rust wants a stronger long-term C++ interop story.
- But that future is not the same thing as today’s stable tool and build reality.

**What the archive should preserve**
- explicit `watch` / `pilot` / `promote` posture,
- what current tools already solve,
- what still depends on language/compiler evolution,
- and what should remain experimental rather than smuggled into present-tense support claims.

## Shared artifact spine
A credible ecosystem contribution should let these lanes share a thin evidence spine without flattening them.

Prefer a family like:
- `native-subject/v0` — the reviewed mixed-language subject
- `native-edge-lane-profile/v0` — which lane or lane-combination applies
- `ffi-pack/v0` — boundary truth and generated-artifact provenance
- `native-pack/v0` — provider, lock, and link-plan truth
- `native-handoff-report/v0` — what an external build/package consumer is expected to ingest
- `native-edge-diff-report/v0` — what changed across releases or revisions
- `native-edge-readiness-report/v0` — `promote` / `pilot` / `watch` / `defer` posture with explicit basis refs
- `native-edge-pack/v0` — a thin referenced join over the lower artifacts

The winning move is **not** one giant interop report.
It is a thin pack that keeps lane identity visible and imports lower artifacts by reference.

## Ranked execution ladder
1. **C ABI export/import first**
   - smallest honest surface,
   - best first proof of diffable boundary and handoff receipts.
2. **Provider/link second**
   - prove that native-provider truth can be reviewable without being confused for boundary truth.
3. **CXX safe-common third**
   - prove richer semantics while staying in a constrained, typed regime.
4. **autocxx / large-codebase fourth**
   - prove partial-support and generator-coupling honesty on a more demanding real-world lane.
5. **external-build handoff fifth**
   - prove non-Cargo consumers can import the artifacts without reverse-engineering local build glue.
6. **watch/promote language-facing lane sixth**
   - prove the archive can report “not ready yet” honestly while still mapping the path forward.

## What an epic contribution should look like in theory and practice
In theory, the epic contribution is a **portable interop review boundary**.
In practice, that means:
- it compares lanes without pretending they are the same lane;
- it keeps boundary truth, provider truth, and handoff truth distinct;
- it records generator and toolchain coupling explicitly;
- it diff-checks both semantic drift and build/handoff drift;
- it gives external build/package/safety consumers a bounded artifact to import;
- and it supports `watch` verdicts for upstream-first questions instead of forcing every problem into a crate right now.

A contribution meeting that bar would be worthy because it would make Rust adoption inside existing native estates **more legible, more reviewable, and less folklore-driven** without demanding that the ecosystem first converge on one bridge, one build system, or one package-manager story.

## Anti-goals
- No universal Rust ABI claim.
- No “C++ support score”.
- No one-true bridge generator.
- No flattening of C ABI, CXX, autocxx, provider resolution, and external-build handoff into one fake lane.
- No assumption that language/compiler aspirations are already present-tense ecosystem truth.

## References
- seamless Rust/C++ goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- C++/Rust interop problem-space mapping:
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- July 2025 goals update:
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Cargo roadmap issue to reduce build scripts:
  https://github.com/rust-lang/cargo/issues/14948
- Cargo build-script docs:
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Rustonomicon FFI chapter:
  https://doc.rust-lang.org/nomicon/ffi.html
- `system-deps`:
  https://docs.rs/system-deps/
- `pkg-config`:
  https://docs.rs/pkg-config
- CXX:
  https://cxx.rs/
- `autocxx`:
  https://google.github.io/autocxx/
- Corrosion:
  https://corrosion-rs.github.io/corrosion/
  https://corrosion-rs.github.io/corrosion/ffi_bindings.html
