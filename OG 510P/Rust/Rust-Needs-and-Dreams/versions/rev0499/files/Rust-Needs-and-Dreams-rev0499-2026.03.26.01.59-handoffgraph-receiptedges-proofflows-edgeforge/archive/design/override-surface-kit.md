# Design: Override Surface Kit (`cargo overridecheck`, `override-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **override surfaces** in Rust: unique dependency-graph hooks, process-global one-shot installs, replaceable/updateable hooks, thread/task-local defaults, guard-scoped defaults, and distributed registration / discovery surfaces.

This should help answer questions like:
- who is supposed to install this provider,
- when and how installation occurs,
- whether installation is unique, replaceable, layered, or collect-many,
- whether a default fallback exists and whether wrappers must delegate to it,
- whether thread-local or task-local scoped override is supported,
- how discovery/ordering works for distributed registration,
- how to reset or isolate state for tests,
- and what evidence demonstrates those claims.

It should **not** replace these mechanisms with one universal runtime.
It should make their semantics reviewable.

## References (signals)
- Externally Implementable Items is an active project-goal effort intended to make `#[panic_handler]`, global allocator, and similar features more like ordinary library features rather than compiler built-ins. That is a strong signal that override points are becoming more ecosystem-shaped design territory.
  https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- The Rust Reference says `#[panic_handler]` defines panic behavior and must be unique in the dependency graph; the attributes reference lists `global_allocator` as a runtime attribute. That is direct evidence that Rust already has first-class ambient override points at the language/runtime boundary.
  https://doc.rust-lang.org/reference/panic.html
  https://doc.rust-lang.org/reference/attributes.html
- `std::panic::set_hook` replaces the current panic hook, and `update_hook` atomically wraps the existing hook. That is direct evidence that replacement and composition semantics are public contracts here, not just implementation details.
  https://doc.rust-lang.org/std/panic/fn.set_hook.html
  https://doc.rust-lang.org/std/panic/fn.update_hook.html
- `std::alloc` exposes `#[global_allocator]`, documents its uniqueness, and separately exposes allocation-error hooks. That is evidence that allocator/provider slots and error hooks already form distinct override families.
  https://doc.rust-lang.org/std/alloc/index.html
  https://doc.rust-lang.org/beta/std/alloc/fn.set_alloc_error_hook.html
- `log::set_logger` is one-shot for the lifetime of the program; `tracing::subscriber::set_global_default` is also one-shot but explicitly acts as a fallback when no thread-local subscriber has been set, and `tracing` separately exposes scoped defaults. That is concrete evidence that scope and multiplicity are central semantics.
  https://docs.rs/log/latest/log/fn.set_logger.html
  https://docs.rs/tracing/latest/tracing/subscriber/fn.set_global_default.html
  https://docs.rs/tracing/latest/tracing/subscriber/index.html
- `inventory` and `linkme` provide decentralized registration/discovery patterns that are neither ordinary globals nor simple runtime hooks. That is evidence that distributed registration deserves first-class treatment.
  https://docs.rs/inventory
  https://docs.rs/linkme

## Design principles
1. **Slots before implementations.** Review starts from the installable/discoverable slot, not from a specific provider crate.
2. **Scope is public API.** Process-global, dependency-graph-unique, thread-local, task-local, guard-scoped, and collect-many are materially different promises.
3. **Lifecycle must be explicit.** Link-time, startup, lazy init, replace, update, reset, teardown, and test isolation belong in artifacts.
4. **Fallback/composition is not folklore.** “Calls previous hook”, “replaces default”, “acts as fallback”, and “must be installed by application code” are all contract material.
5. **Discovery deserves equal footing.** Distributed registries/slices are not second-class oddities; they are a distinct override/discovery family.
6. **Vectors over demos.** Init order, duplicate install, reset, fallback, and discovery-order behavior should be checked explicitly.
7. **No fake universal global model.** The kit should preserve real differences rather than smoothing them away.

## Artifact family

### 1) `override-surface/v0`
Top-level description of the override or discovery surface.

Fields:
- surface id
- owning crate / package / binary
- surface family (`handler`, `allocator-slot`, `hook`, `default-provider`, `scoped-default`, `distributed-registry`, `distributed-slice`, `other`)
- intended installer (`application`, `library-internal`, `platform glue`, `generated`, `downstream integrator`)
- primary scope/multiplicity reference
- primary lifecycle reference
- related adapters / registries / evidence

### 2) `provider-slot-profile/v0`
Describes the slot into which something is installed or discovered.

Fields:
- slot id and human label
- provider trait/type/function signature or attribute shape
- uniqueness or plurality expectation
- default/fallback behavior
- replacement / wrapping / chaining rules
- “library may install?” guidance
- side-effect expectations (logging, panic, allocation, I/O, registration)
- safety / platform / `no_std` notes where relevant

### 3) `install-lifecycle-profile/v0`
Describes how installation or update occurs.

Fields:
- install phase (`link-time`, `startup`, `lazy-runtime`, `explicit-registration`, `scoped-guard`, `hybrid`)
- allowed actions (`install-once`, `replace`, `update-wrap`, `collect-many`, `take/reset`, `drop-guard`)
- failure modes on duplicate install / missing provider / reset
- ordering guarantees or non-guarantees
- teardown/reset/test-isolation support
- reentrancy / recursion caveats

### 4) `scope-multiplicity-profile/v0`
Captures where and how many providers may apply.

Fields:
- scope family (`dep-graph-unique`, `process-global-once`, `thread-local`, `task-local`, `guard-scoped`, `collect-many`, `hybrid`)
- precedence rules
- fallback chain behavior
- concurrency notes
- inheritance rules across threads/tasks if any
- test/process isolation caveats

### 5) `registry-discovery-profile/v0`
For distributed registration and discovery surfaces.

Fields:
- discovery mechanism (`explicit list`, `macro registration`, `linker section`, `inventory-style collection`, `other`)
- duplicate handling policy
- ordering expectations / non-guarantees
- iteration stability guarantees
- required link/build conditions
- feature-gate / target caveats

### 6) `override-adapter-profile/v0`
Describes wrappers and bridges between surfaces.

Fields:
- source surface(s)
- destination surface(s)
- whether previous/default provider is called through
- duplication / filtering / translation behavior
- allocation / locking / thread-local / lifetime caveats
- initialization-order sensitivity

### 7) `override-vector-set/v0`
Executable or reviewable vectors.

Kinds of vectors:
- duplicate-install vector
- install-before-use vector
- fallback-callthrough vector
- scoped-default vector
- reset/test-isolation vector
- distributed-discovery vector
- ordering / duplicate-registration vector
- cross-thread / cross-task default vector

### 8) `override-check-report/v0`
What actually ran and what was observed.

Fields:
- tool versions / environment
- vectors executed / skipped
- install failures observed
- discovery counts / ordering observations
- fallback / wrapper behavior observed
- unresolved caveats

### 9) `override-pack/v0`
Bundle containing the surface, profiles, vectors, report, and linked docs/migration notes.

## Tool shape
`cargo overridecheck` should be a thin orchestrator, not a new runtime.

Possible subcommands:
- `cargo overridecheck init` — scaffold `override-pack/v0`
- `cargo overridecheck check` — execute declared vectors and validate metadata
- `cargo overridecheck diff` — compare lifecycle/scope/fallback changes between versions
- `cargo overridecheck explain` — render a human-readable summary of install authority and discovery rules

## Initial pilot lanes
1. **`no_std` panic + allocator lane**
   - `#[panic_handler]`
   - `#[global_allocator]`
   - optional alloc-error-hook attachment for `std` binaries
2. **global diagnostics lane**
   - `log::set_logger`
   - `tracing::subscriber::set_global_default`
   - scoped defaults / fallback chains in `tracing`
   - `log` → `tracing` bridge described as adapter rather than handwaved compatibility
3. **distributed registry lane**
   - `inventory`
   - `linkme`
   - one real plugin/metric/flag registry pilot built on them

## Adoption path
### v0.1
- ship schema family
- ship one panic/allocator pilot, one log/tracing pilot, one distributed-registration pilot
- prove the kit can distinguish dep-graph uniqueness, process-global once, thread-local scopes, and collect-many discovery

### v0.2
- add diff/report tooling and test-isolation vectors
- add adapter profiles for wrapper / fallback / bridge cases
- document “library must not install this globally” posture where relevant

### v0.3
- integrate with Policy Kit / Compile-Time Capabilities Kit / Runtime Capability Kit where override points carry authority or build-time effects
- connect distributed registries to Plugin Surface Kit and Ecosystem Atlas Kit

### v1
- enough adopters that the schemas stop being toy examples
- enough negative cases captured that the kit prevents misleading “easy init” folklore

## Relation to neighboring kits
- **Compile-Time Capabilities Kit** governs authority used by `build.rs` and proc-macros; Override Surface Kit governs runtime/link-time install and discovery semantics.
- **Runtime Capability Kit** governs what ambient powers a running program has; this kit governs who installs ambient behavior providers and how they compose.
- **Plugin Surface Kit** governs host↔plugin contracts; this kit can describe distributed plugin-registration/discovery surfaces without absorbing host API shape.
- **Compile Guidance Kit** owns developer-facing diagnostics and extension hooks; this kit owns global/scoped provider slots and discovery posture.
- **Interop Commons Kit** helps define neutral shared types/traits; this kit helps publish neutral override/discovery semantics around such seams.

## Non-goals
- a universal service-locator crate,
- a recommendation that libraries should eagerly install globals,
- flattening link-time attributes, runtime hooks, scoped defaults, and distributed registries into one mechanism,
- or hiding initialization-order/test-isolation hazards behind ergonomic helper macros.
