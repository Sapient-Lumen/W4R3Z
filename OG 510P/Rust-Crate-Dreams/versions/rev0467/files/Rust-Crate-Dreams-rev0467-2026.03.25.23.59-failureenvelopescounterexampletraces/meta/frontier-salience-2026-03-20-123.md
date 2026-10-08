# Frontier salience snapshot — 2026-03-20 (123)

This pass did **not** open another packaging lane, another generator wrapper, or another “safe FFI” umbrella.
It deepened **P-0121 ffi-boundary-conformance-kit** by making a more boring but more reusable boundary explicit:

- **a Rust project can truthfully say it has a C ABI, generated mobile bindings, panic containment, async callbacks, and a C++ or component-model story while still leaving downstream users unable to tell what ownership model, unwind policy, callback runtime, or verification strength they are actually depending on.**

## Main judgment

The sharper missing layer is no longer merely “binding generation + CI diffs”.
The sharper missing layer is an **ownership-transfer / unwind-posture / callback-execution / binding-coverage contract**.

Current Rust FFI substrate makes that specific:

1. The 2024 Edition now requires `unsafe extern` blocks, which makes boundary obligations explicit instead of ambient.
2. The Reference and RFC 2945 keep non-unwinding and unwind-capable ABIs distinct, so unwind posture is no longer honest as prose-only folklore.
3. `catch_unwind` remains a real boundary tool, but only for unwinding Rust panics.
4. The Nomicon still calls out that asynchronous callbacks must stop before their Rust-side target is destroyed, which is an explicit teardown rule.
5. UniFFI now has concrete runtime vocabulary for buffers, handles, callbacks, and future poll/cancel/free lifecycles.
6. UniFFI’s callback-interface docs say those interfaces are soft-deprecated and conceptually thread-safe outside Rust’s direct enforcement, which makes callback-thread posture especially worth surfacing explicitly.
7. Diplomat, `cxx`, `wit-bindgen`, and `cbindgen` all prove that the ecosystem has strong bridge/generation substrate but still not one shared receiver-facing contract.

That means the next worthy move is not another bindings generator.
It is one conservative crate family that can publish:

- **ownership-transfer truth**,
- **unwind-posture truth**,
- **callback-execution truth**,
- and **binding-coverage truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- whole-program ABI/compiler-flag coherence,
- package/release/publication truth,
- migration/review-pack governance,
- and specific Wasm/component or foreign-package shipping paths.

What it still lacked was one compact way to say:

- “this buffer is explicit-free while that one is borrowed call-only,”
- “this callback wrapper catches panics and forbids foreign unwind,”
- “this async surface is a poll/cancel/free continuation, not an ordinary callback,”
- and “these bindings exist, but only some are directly checked.”

That is a real receiver-facing product boundary, not another generator preference.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream test-support truth remains under-served.
5. **P-0121 ffi-boundary-conformance-kit** — materially stronger after this pass because Rust now has real bridge/generator substrate but still lacks a shared boundary contract above it.
6. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
7. **P-0039 i18n-icu-kit** — stronger after the latest contract pass, but still best when kept runtime-contract-focused.
8. **P-0454 ABI Coherence Profile Kit** — still important, but should remain whole-program/compiler-flag scoped rather than absorbing receiver-facing FFI contract truth.

## What changed in the archive

Added:
- `entries/2026-03-20-303.md`
- `meta/frontier-salience-2026-03-20-123.md`
- `meta/ffi-boundary-conformance-product-plan-2026-03-20.md`
- `meta/ffi-boundary-conformance-lane-boundaries-2026-03-20.md`
- `fixtures/ffi-boundary-conformance-kit/README.md`
- `fixtures/ffi-boundary-conformance-kit/ownership-transfer.receipt.schema.json`
- `fixtures/ffi-boundary-conformance-kit/unwind-posture.receipt.schema.json`
- `fixtures/ffi-boundary-conformance-kit/callback-execution.report.schema.json`
- `fixtures/ffi-boundary-conformance-kit/binding-coverage.report.schema.json`
- scenario families for explicit-free versus borrowed bytes, `extern "C"` wrapper versus unwind-capable exports, and mixed-strength multi-surface coverage

Updated:
- `README.md`
- `INDEX.md`
- `proposals/ffi-boundary-conformance-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy FFI-support contribution for Rust should now provide more than generated bindings and a release checklist.
It should provide:

- one explicit **ownership-transfer receipt**,
- one explicit **unwind-posture receipt**,
- one explicit **callback-execution report**,
- and one honest **binding-coverage report**.

## Freshness anchors

- Rust 2024 unsafe extern blocks — https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- Rust Reference external blocks — https://doc.rust-lang.org/reference/items/external-blocks.html
- RFC 2945 C-unwind ABI — https://rust-lang.github.io/rfcs/2945-c-unwind-abi.html
- `catch_unwind` docs — https://doc.rust-lang.org/std/panic/fn.catch_unwind.html
- Rustonomicon FFI guide — https://doc.rust-lang.org/nomicon/ffi.html
- UniFFI user guide — https://mozilla.github.io/uniffi-rs/
- `uniffi` crate docs — https://docs.rs/uniffi/latest/uniffi/
- UniFFI async internals — https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html
- UniFFI callback interfaces — https://mozilla.github.io/uniffi-rs/0.27/udl/callback_interfaces.html
- Diplomat book — https://rust-diplomat.github.io/diplomat/
- `cxx` docs — https://docs.rs/cxx/latest/cxx/
- `wit-bindgen` docs — https://docs.rs/wit-bindgen/latest/wit_bindgen/
- `cbindgen` docs — https://github.com/mozilla/cbindgen
