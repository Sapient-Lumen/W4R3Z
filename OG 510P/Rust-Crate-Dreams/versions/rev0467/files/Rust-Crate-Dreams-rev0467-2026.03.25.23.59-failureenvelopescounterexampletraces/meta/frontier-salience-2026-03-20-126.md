# Frontier salience snapshot — 2026-03-20 (126)

This pass did **not** promote another key-management service, another encrypted-envelope format, or another generic privacy/redaction lane.
It deepened **P-0037 secrets-kit** by making a more boring and more reusable boundary explicit:

- **a Rust app can import `secrecy`, `zeroize`, `keyring`, or even protected-memory crates and still leave another team unable to tell how secrets are actually revealed, persisted, materialized in memory, or exposed back out.**

## Main judgment

The sharper missing layer is no longer merely “provider chain plus typed secrets”.
The sharper missing layer is a **secret-handling contract** above wrappers, backends, and protected-memory primitives.

Current Rust substrate makes that specific:

1. `secrecy` explicitly promises explicit access, debug redaction, and zeroize-on-drop, while explicitly **not** claiming `mlock` / `mprotect` protection.
2. `secrecy` is also explicit that deserialization can introduce plaintext intermediates callers must clean up themselves.
3. `zeroize` gives portable zeroization guarantees, while equally clearly stopping short of register clearing or broader memory-protection claims.
4. `keyring` now exposes explicit per-platform store features, bring-your-own builders, and a platform-independent mock store that provides **no persistence**.
5. `secrets` provides meaningfully stronger protected-memory substrate (`mprotect`, guard pages, `mlock`, zero-on-drop), which makes “zeroize-only” versus “protected-memory” a real support boundary rather than a philosophical one.

That means the next worthy move is not another wrapper crate.
It is one conservative crate family that can publish:

- **revelation-path truth**,
- **persistence-posture truth**,
- **memory-posture truth**,
- and **export-posture truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- encrypted secret envelopes and policy,
- generic sensitive-data redaction,
- trust/risk scoring,
- and assorted configuration/runtime contract work.

What it still lacked was one compact way to say:

- “production uses a native store but tests use a mock with no persistence,”
- “the value is wrapped in `SecretBox<T>` only after passing through an env `String`,”
- “the promise is zeroize-on-drop, not protected memory,”
- and “serialization was explicitly opted back in even though debug is redacted by default.”

That is a real receiver-facing product boundary, not just another backend adapter.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream test-support truth remains under-served.
5. **P-0474 cargo-config-layer-receipt-kit** — still strong because Cargo config is now a real operational support surface.
6. **P-0124 schema-compatibility-workbench-kit** — still unusually strong because schema engines exist but one shared review contract above them still does not.
7. **P-0017 Trust Lens** — still unusually strong because reviewable dependency-trust posture is newly more buildable.
8. **P-0037 secrets-kit** — materially stronger after this pass because secret-handling truth now looks less like “pick a wrapper” and more like a receiver-facing contract another team could actually rely on.
9. **P-0121 ffi-boundary-conformance-kit** — still important and sharper, but should remain boundary-contract-first.

## What changed in the archive

Added:
- `entries/2026-03-20-306.md`
- `meta/frontier-salience-2026-03-20-126.md`
- `meta/secrets-kit-product-plan-2026-03-20.md`
- `meta/secrets-kit-lane-boundaries-2026-03-20.md`
- `fixtures/secrets-kit/revelation-path.receipt.schema.json`
- `fixtures/secrets-kit/persistence-posture.receipt.schema.json`
- `fixtures/secrets-kit/memory-posture.receipt.schema.json`
- `fixtures/secrets-kit/export-posture.report.schema.json`
- scenario families for plaintext-intermediate disclosure, keyring/mock persistence drift, serialization opt-ins, and protected-memory distinction

Updated:
- `README.md`
- `INDEX.md`
- `proposals/secrets-kit.md`
- `fixtures/secrets-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy secret-handling support contribution for Rust should now provide more than a provider chain, a secret wrapper, and a redaction story.
It should also provide:

- one explicit **revelation-path receipt**,
- one explicit **persistence-posture receipt**,
- one explicit **memory-posture receipt**,
- and one honest **export-posture report**.

## Freshness anchors

- `secrecy` docs — https://docs.rs/secrecy/latest/secrecy/
- `zeroize` docs — https://docs.rs/zeroize/latest/zeroize/
- `keyring` docs — https://docs.rs/keyring/latest/keyring/
- `secrets` docs — https://docs.rs/secrets/latest/secrets/
