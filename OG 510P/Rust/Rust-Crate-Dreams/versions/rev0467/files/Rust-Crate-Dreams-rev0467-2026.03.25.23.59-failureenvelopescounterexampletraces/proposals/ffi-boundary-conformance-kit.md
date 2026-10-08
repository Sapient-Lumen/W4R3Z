---
id: P-0121
title: FFI Boundary & Bindings Conformance Kit — interface-authority, projection-basis, derivative-parity, ownership-transfer, unwind-posture, callback-authority, callback-execution, callback-lifecycle, callback-completion, binding-coverage, layout-authority, error-channel, and projection-drift receipts
status: idea
domains: [ffi, sdk, tooling, release, interop, safety]
last_reviewed: 2026-03-23
evidence:
  - https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
  - https://doc.rust-lang.org/reference/items/external-blocks.html
  - https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
  - https://doc.rust-lang.org/std/panic/fn.catch_unwind.html
  - https://doc.rust-lang.org/nomicon/ffi.html
  - https://mozilla.github.io/uniffi-rs/
  - https://docs.rs/uniffi/latest/uniffi/
  - https://rust-diplomat.github.io/diplomat/
  - https://docs.rs/cxx/latest/cxx/
  - https://docs.rs/wit-bindgen/latest/wit_bindgen/
  - https://github.com/mozilla/cbindgen
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://cxx.rs/shared.html
  - https://cxx.rs/binding/result.html
  - https://mozilla.github.io/uniffi-rs/latest/internals/object_references.html
  - https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html
  - https://mozilla.github.io/uniffi-rs/latest/udl/errors.html
  - https://rust-diplomat.github.io/book/types.html
  - https://rust-diplomat.github.io/book/opaque.html
  - https://component-model.bytecodealliance.org/design/why-component-model.html
  - https://component-model.bytecodealliance.org/using-wit-resources.html
  - https://docs.rs/wit-bindgen/latest/wit_bindgen/macro.generate.html
---

# Problem

Rust no longer lacks FFI substrate.

What it still lacks is a **reviewable boundary contract** above that substrate.

Today a team can truthfully say all of the following at once:

- “we expose a C ABI,”
- “we also generate Swift/Kotlin/Python bindings,”
- “we catch panics at the boundary,”
- “we support callbacks / async,”
- and “we checked the generated bindings in CI,”

while still leaving another team unable to answer six boring but crucial questions:

1. **What ownership model actually crosses the boundary?**
2. **What happens if Rust panics or a foreign unwind reaches Rust?**
3. **Where do callbacks execute, and what teardown/unregister rules keep them sound?**
4. **Which binding surfaces are really checked versus merely generated or documented?**
5. **What representation actually crosses the boundary, and who is the source of truth for it?**
6. **How do errors, exceptions, and unexpected callback failures cross the boundary?**

The missing crate is therefore **not** another generator.
It is a conservative, adapter-friendly layer that turns boundary promises into receipts and reports.

# What it provides

An **FFI Boundary Contract Kit** that sits above existing generators and bridges and emits compact, diffable artifacts:

- `interface-authority.import.json`
  - what artifact is the primary authority for a boundary surface (`unsafe extern`, `cxx::bridge`, UDL/proc-macro metadata, Diplomat bridge, WIT package/world, or generated header/binding as derivative).
- `projection-basis.receipt.json`
  - what generated or emitted foreign artifact is being reviewed, which authority it projects from, which generator/backend/configuration shaped it, whether it is full, subset, renamed, backend-shaped, or packaging-only, and what still requires manual review.
- `derivative-parity.report.json`
  - whether a generated header/binding/custom section still faithfully reflects the primary authority, where backend attributes or config changed the receiver-facing surface, and which differences are informative versus receiver-visible risk.
- `ownership-transfer.receipt.json`
  - whether a boundary item is borrowed, copied, opaque-handle-based, explicit-free, reference-counted, or runtime-managed.
- `unwind-posture.receipt.json`
  - whether Rust panics are caught and translated, forced to abort, explicitly allowed via an unwind ABI, or still undeclared.
- `callback-authority.receipt.json`
  - what artifact defines the callback surface, which direction the boundary call crosses, and whether the callback surface is native, limited, or only an adapter recipe.
- `callback-execution.report.json`
  - whether callbacks run inline, on foreign threads, through runtime continuations, or via async future polling, plus what execution origin and completion path are claimed.
- `callback-lifecycle.receipt.json`
  - whether callbacks are cloned, freed, explicitly unregistered, cancellation-aware, or still exposed to late-call-after-drop/manual-review hazards.
- `callback-completion.report.json`
  - whether completion is inline, exactly-once, callback-based, channel-mediated, cancellation-aware, or still exposed to unexpected-error/manual-review hazards.
- `binding-coverage.report.json`
  - which foreign-language or runtime surfaces exist, how they are generated, and whether they were directly checked, merely generated, or left as docs-only/manual-review surfaces.
- `layout-authority.receipt.json`
  - whether a surface is shared by value, opaque and indirection-only, serialized, or canonical-ABI based, who defines it, and how that representation is checked.
- `error-channel.receipt.json`
  - whether failure crosses as a flat enum, structured result, exception, canonical result, callback result, or status channel, including panic and unexpected-failure posture.
- `projection-drift.report.json`
  - release-to-release changes in projected foreign surfaces, including renamed types/functions, changed exception/result lowering, hidden/subsetted items, changed custom-section/export posture, and whether the change is additive, receiver-visible, breaking, or manual-review-only.
- `ffi-contract-check.report.json`
  - joined warnings such as `borrow_exceeds_call_boundary`, `panic_policy_implicit`, `callback_teardown_undeclared`, `binding_surface_generated_but_unchecked`, `projection_subset_without_receiver_notice`, `backend_projection_nonuniform`, `layout_source_of_truth_implicit`, `error_payload_flattened`, and `manual_review_required`.
- `ffi-support-bundle.manifest.json`
  - one portable pack tying together authority, ownership, unwind, callback, layout, coverage, and error receipts for review or release comparison.
- `.fficontractbundle.zip`
  - one compact handoff artifact for CI, release review, downstream consumers, or an incident report.

# What the crate should provide other people

1. **One interface-authority receipt** instead of guessing whether Rust declarations, WIT, bridge modules, or generated headers are primary.
2. **One projection-basis receipt** instead of treating generated headers, bindings, and custom sections as self-explanatory.
3. **One derivative-parity report** instead of assuming a configured backend projection still matches the primary contract in all receiver-visible ways.
4. **One ownership-transfer receipt** instead of README folklore about who frees what.
5. **One unwind-posture receipt** instead of scattered `extern`, panic, and callback caveats.
6. **One callback-authority receipt** instead of guessing whether a callback surface is native, limited, or only an adapter recipe.
7. **One callback-execution report** instead of reverse-engineering thread/runtime assumptions from codegen and docs.
8. **One callback-lifecycle receipt** instead of vague “supports callbacks” language that omits unregister, cancellation, or late-call hazards.
9. **One callback-completion report** instead of vague “async callback support” language that hides exactly-once, cancellation, channel, or panic-on-unexpected-error obligations.
10. **One binding-coverage report** instead of assuming generated bindings equal checked bindings.
11. **One layout-authority receipt** instead of flattening shared structs, opaque handles, serialized buffers, and canonical ABI resources into one fake “type support” claim.
12. **One error-channel receipt** instead of flattening exceptions, flat enums, structured results, callback failures, and panic translation into one fake “returns errors” claim.
13. **One projection-drift report** that makes release-to-release foreign-surface change visible even when the primary authority looks superficially stable.
14. **One diffable contract** that can be compared across releases, languages, and adapter stacks.
15. **One portable bundle** that another reviewer can archive and diff without scraping generator output by hand.

# Persona / who it’s for

- SDK teams shipping one Rust core to multiple languages
- maintainers exposing Rust over a C ABI or C++ bridge
- teams using UniFFI or Diplomat who need reviewable ownership/runtime guarantees
- auditors and release reviewers who need one boring handoff artifact
- downstream integrators deciding whether an FFI surface is safe to adopt

# Users & user stories

- **Mobile SDK team**: “Show me whether Kotlin/Swift bindings are checked or just generated, and what ownership rules apply to byte buffers.”
- **Systems integrator**: “Tell me whether this C callback can arrive after object destruction, and whether the crate has a real unregister rule.”
- **C++ bridge maintainer**: “Separate safe `cxx` bridge facts from any looser C ABI surfaces we still publish.”
- **Release reviewer**: “Block a release if panic/unwind posture changed or a checked surface silently became generated-only.”
- **Runtime team**: “Tell me whether async foreign futures are poll/cancel/free style continuations or ordinary callbacks.”

# Prior art (and why it’s insufficient)

- `cbindgen` creates C/C++ headers from Rust code.
- `cxx` provides a safer Rust/C++ bridge.
- UniFFI generates multi-language bindings and exposes runtime support for handles, buffers, callbacks, and futures.
- Diplomat generates bindings for several foreign languages.
- `wit-bindgen` provides Rust bindings generation for the WebAssembly component model.
- The Rust Edition Guide, Reference, Nomicon, and panic/unwind docs make the safety obligations increasingly explicit.

What remains missing is a **single receiver-facing contract layer** that joins those truths without flattening them.

# Design goals

1. **Boundary-first** — focus on what crosses the foreign boundary, not on whole-program compiler flags or packaging alone.
2. **Adapter-friendly** — import facts from existing generators instead of replacing them.
3. **Ownership-explicit** — never let borrowed, explicit-free, handle-based, and copied-value stories collapse into one claim.
4. **Unwind-explicit** — panic and unwind policy must be reviewable per exported surface.
5. **Callback-honest** — execution origin, thread posture, and teardown assumptions must be first-class.
6. **Representation-honest** — keep shared by-value, opaque indirection-only, serialized, and canonical-ABI lanes separate.
7. **Error-honest** — keep flat enums, structured errors, exceptions, status channels, and panic translation visibly distinct.
8. **Coverage-honest** — distinguish `directly_checked` from `generated_only`, `packaging_only`, and `docs_only`.
9. **Conservative** — unknowns should stay unknown, not inferred away.

# Eleven first-class review objects

## 1. `interface-authority.import`

This artifact should answer:

- what boundary family is being described,
- what artifact is the primary source of truth,
- what artifacts are generated or derivative,
- whether authority is local, imported, or mixed,
- and where manual review still remains.

## 2. `projection-basis.receipt`

This artifact should answer:

- what generated or emitted foreign artifact is being described,
- which primary authority it projects from,
- what generator, backend, or config produced it,
- whether the projection is full, subset, renamed, backend-shaped, or packaging-only,
- and whether the derivative artifact is even intended to stand in for the boundary contract.

## 3. `derivative-parity.report`

This artifact should answer:

- whether the derivative artifact still faithfully reflects the primary authority,
- which renames, namespace moves, omitted items, backend-specific lowerings, or generated-only gaps were introduced,
- whether those differences are informational, receiver-visible, breaking, or manual-review-only,
- and what proof class backs that statement.

## 4. `ownership-transfer.receipt`

This artifact should answer:

- what surface or symbol is being described,
- whether ownership is borrowed, copied, opaque-handle-based, reference-counted, or explicit-free,
- which allocator or handle table owns heap-backed state,
- what release mechanism exists,
- and how long the foreign side may keep the value.

## 5. `unwind-posture.receipt`

This artifact should answer:

- which ABI family is in play,
- whether a Rust panic is caught and translated, aborts, or is allowed to unwind,
- whether foreign exceptions/unwinds are forbidden or allowed via an unwind ABI,
- and whether the containment strategy is explicit (`catch_unwind`, abort profile, generated runtime handler) or still implicit.

## 6. `callback-execution.report`

This artifact should answer:

- whether a callback is synchronous, event-driven, or future/continuation-based,
- where execution originates,
- what thread or runtime affinity is assumed,
- and whether completion is inline, may happen after return, or follows a future poll/cancel/free lifecycle.

## 7. `callback-lifecycle.receipt`

This artifact should answer:

- how callbacks are registered,
- whether clone/free hooks exist,
- whether unregister-before-drop is required,
- whether cancellation/drop callbacks exist,
- and whether late callback arrival after teardown remains possible or manual-review-only.

## 8. `binding-coverage.report`

This artifact should answer:

- which binding families or targets exist,
- how each one is generated,
- whether each one is directly checked, generated-only, packaging-only, docs-only, or still manual-review-required,
- and whether one surface has stronger guarantees than another.

## 9. `layout-authority.receipt`

This artifact should answer:

- whether the surface is shared by value, opaque and indirection-only, serialized, or canonical-ABI based,
- who is the source of truth for the representation,
- whether compile-time/static/interface checks exist,
- and whether by-value crossing is actually allowed.

## 10. `error-channel.receipt`

This artifact should answer:

- whether failure crosses as a flat enum, structured result, exception, callback result, canonical result, or status code,
- whether payload fidelity is code-only, message-only, flat-enum-only, or structured,
- how Rust panics are handled at the boundary,
- and what happens to unexpected callback or foreign-side failures.

# Recommended `0.1` command surface

## `cargo ffi-contract capture`
Capture declared and imported boundary facts and emit:
- `interface-authority.import.json`
- `projection-basis.receipt.json`
- `derivative-parity.report.json`
- `ownership-transfer.receipt.json`
- `unwind-posture.receipt.json`
- `callback-execution.report.json`
- `callback-lifecycle.receipt.json`
- `binding-coverage.report.json`
- `layout-authority.receipt.json`
- `error-channel.receipt.json`

## `cargo ffi-contract check`
Run conservative policy checks and emit:
- `ffi-contract-check.report.json`

## `cargo ffi-contract diff`
Compare two bundles and emit:
- `projection-drift.report.json`
- `ffi-contract-diff.report.json`

## `cargo ffi-contract bundle`
Produce:
- `ffi-support-bundle.manifest.json`
- one compact `.fficontractbundle.zip`.

# Workspace split

- `ffi_contract_model`
- `ffi_contract_import_uniffi`
- `ffi_contract_import_diplomat`
- `ffi_contract_import_cbindgen`
- `ffi_contract_import_cxx`
- `ffi_contract_import_wit`
- `ffi_contract_check`
- `ffi_contract_pack`
- `cargo-ffi-contract`

# Discovery order

1. **Boundary-family import**
   - cbindgen headers / exported C ABI
   - `cxx::bridge`
   - UniFFI scaffolding / metadata / generated bindings
   - Diplomat bridge metadata
   - WIT/component model bindings
2. **Projection capture**
   - generated C/C++ headers and their config knobs
   - generated foreign-language bindings and whether generation stops short of build/package proof
   - backend-specific renames, namespaces, and lowerings
   - component/custom-section/export-macro emission details
3. **Representation capture**
   - shared by-value types
   - opaque handles / indirection-only types
   - serialized buffer lowerings
   - canonical ABI values and resources
4. **Ownership capture**
   - buffers
   - handles / opaque types
   - callback object references
   - explicit free / drop / handle-table conventions
5. **Unwind + error capture**
   - ABI family
   - `catch_unwind` wrappers
   - panic-abort assumptions
   - explicit `C-unwind` or equivalent unwind lanes
   - exception/result/status mapping
   - unexpected callback failure posture
6. **Callback capture**
   - sync vs async / continuation style
   - registration model
   - thread/runtime assumptions
   - unregister / teardown rules
7. **Coverage capture**
   - language targets
   - checked-in generated artifacts
   - CI generation and diff steps
   - packaging-only lanes
8. **Bundle and diff**
   - produce one small handoff artifact

# Compatibility story

- Must stay useful whether a project uses only a C ABI, only UniFFI, only Diplomat, only a C++ bridge, or a mixed stack.
- Should preserve whether facts are **imported from generator metadata**, **observed from checks**, **maintainer-declared**, or **manual-review-only**.
- Must remain useful even when one crate publishes stronger guarantees to one language than another.
- Should stay conservative around foreign exceptions, callback threading, and teardown rules when the substrate cannot prove them directly.

# Conformance & fixtures

- a borrowed-slice versus explicit-free buffer scenario,
- an `extern "C"` callback wrapper that catches panics versus a `C-unwind` lane,
- a callback-after-drop hazard scenario requiring explicit deregistration,
- and a mixed-surface package where UniFFI, Diplomat, or C headers have different check strength.

# Path to boring stability

- Stabilize the receipt/report vocabulary before adding more generators.
- Start by importing and classifying existing boundary facts rather than generating new bindings.
- Keep the first check set small and honest.
- Make mixed-strength coverage visible instead of pretending every generated surface is equally verified.

# Non-goals

- Not a replacement for UniFFI, Diplomat, cbindgen, cxx, or wit-bindgen.
- Not a whole-program ABI coherence checker; that stays separate from **P-0454**.
- Not a packaging or publish-certainty tool; that stays separate from package/publish lanes.
- Not a guarantee that foreign-language runtime behavior can always be inferred automatically.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that can capture one crate’s C/UniFFI/Diplomat/cxx/WIT boundary facts, emit four compact receipts/reports, and fail CI when ownership, unwind, callback, or coverage posture drifts without review.

# De-risk plan

1. Start with import + receipt generation, not generator replacement.
2. Focus first on C ABI + UniFFI + one additional bridge family.
3. Treat callback teardown and foreign-thread assumptions as explicit unknowns unless directly declared.
4. Validate on one library that mixes at least two boundary families.

# Architecture & API sketch

```rust
pub struct OwnershipTransferReceipt {
    pub surface: String,
    pub transfer_class: TransferClass,
    pub allocation_domain: AllocationDomain,
    pub release_mechanism: ReleaseMechanism,
}

pub fn capture_contract(root: &Path) -> Result<FfiContractBundle>;
pub fn check_contract(bundle: &FfiContractBundle) -> Vec<FfiFinding>;
pub fn diff_contracts(old: &FfiContractBundle, new: &FfiContractBundle) -> FfiDiffReport;
```

Bundle draft:
- `projection-basis.receipt.json`
- `derivative-parity.report.json`
- `ownership-transfer.receipt.json`
- `unwind-posture.receipt.json`
- `callback-execution.report.json`
- `binding-coverage.report.json`
- `ffi-contract-check.report.json`
- `notes.md`

# Security / safety model

- Never infer safe teardown from callback existence alone.
- Never infer unwind safety from a generated binding without an explicit boundary policy.
- Keep allocator ownership and free responsibilities explicit.
- Preserve weaker/manual-review states instead of collapsing them into success.

# Maintenance & governance plan

- Track official Rust FFI guidance (Edition Guide, Reference, Nomicon, panic/unwind docs).
- Track generator/runtime evolution in UniFFI, Diplomat, cxx, cbindgen, and WIT/component tooling.
- Keep schemas intentionally small and diff-friendly.
- Publish scenario fixtures that demonstrate mixed-strength and mixed-model boundaries.

# Milestones

## 0.1
- four core schemas
- capture/import for C ABI + UniFFI + one extra family
- conservative check report

## 0.2
- diffing
- bundle export
- stronger callback/runtime adapters

## 1.0
- stable schemas
- cross-generator imports
- public fixture corpus

# Open questions

- What is the smallest honest vocabulary for foreign-thread and callback teardown posture?
- How much ownership/unwind truth can be imported automatically versus declared manually?
- Which mixed-surface open-source crates make the best proving grounds?

# Sources

- Rust 2024 unsafe extern blocks: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- Rust Reference external blocks: https://doc.rust-lang.org/reference/items/external-blocks.html
- RFC 2945 C-unwind ABI: https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
- `catch_unwind` docs: https://doc.rust-lang.org/std/panic/fn.catch_unwind.html
- Rustonomicon FFI guide: https://doc.rust-lang.org/nomicon/ffi.html
- UniFFI user guide: https://mozilla.github.io/uniffi-rs/
- `uniffi` crate docs: https://docs.rs/uniffi/latest/uniffi/
- UniFFI async internals: https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html
- Diplomat book: https://rust-diplomat.github.io/diplomat/
- `cxx` docs: https://docs.rs/cxx/latest/cxx/
- `wit-bindgen` docs: https://docs.rs/wit-bindgen/latest/wit_bindgen/
- `cbindgen` docs: https://github.com/mozilla/cbindgen


# 2026-03-22 interop refresh — layout authority and error channels become first-class

This proposal is stronger now because current interop substrate no longer just differs by language target.
It differs by **representation authority** and **failure transport**.

A good `0.1` should therefore publish at least six explicit truths:

- ownership transfer,
- unwind posture,
- callback execution,
- binding coverage,
- layout authority,
- and error channel.

That is the smallest honest support surface that lets another team review a boundary without reverse-engineering generated glue.

See also: `meta/ffi-boundary-conformance-product-plan-2026-03-22.md` and `meta/ffi-boundary-conformance-lane-boundaries-2026-03-22.md`.


## 2026-03-23 callback authority / completion addendum

The archive now treats two more callback-layer objects as first-class:

1. `callback-authority.receipt.json`
2. `callback-completion.report.json`

Why these matter:

- **UniFFI** documents callback/foreign-trait ownership, exactly-once completion, dropped-future callbacks, and explicit unexpected-error mapping.
- **Diplomat** is intentionally unidirectional and says callback support in parameters is limited.
- **CXX** documents callbacks today but still treats direct async FFI as not implemented, with an adapter recipe over oneshot callbacks.
- **wit-bindgen** makes import/export directionality explicit, which means callback-like surfaces derive authority from world structure.

A worthy crate in this lane should therefore be able to say:

- what artifact defines the callback surface,
- which direction the callback crosses,
- whether the callback is native or adapter-mediated,
- what completion obligation exists,
- whether cancellation is wired,
- and how unexpected callback failures are surfaced.

That keeps “supports callbacks” from silently flattening one-way callback parameters, foreign-trait implementations, adapter-mediated async shims, and explicit future-completion hooks into the same claim.
